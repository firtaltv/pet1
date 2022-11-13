from datetime import datetime, timedelta
from typing import List, Dict

import pytz
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST
from users.models import User

from .models import Schedule, Slot
from .serializers import ScheduleSerializer, SlotSerializer

utc = pytz.UTC


class TherapistScheduleRetrieveAPIView(RetrieveAPIView):
    """
    Get schedule for any Therapist
    """

    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(therapist__id=self.kwargs["pk"])


class TherapistSlotListAPIView(ListAPIView):
    """
    Get list of all slots for any therapist
    """

    queryset = Slot.objects.all()
    serializer_class = SlotSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            therapist__id=self.kwargs["pk"],
            start_time__gte=utc.localize(datetime.now()),
        )


class TherapistScheduleCreateAPIView(CreateAPIView):
    """
    Create schedule for any therapist
    """

    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(therapist__id=self.kwargs["pk"])

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        for item in serializer.initial_data["days"]:
            if type(item) is not int:
                return Response(status=HTTP_400_BAD_REQUEST, data='Days field MUST be a list of integers [1-7]')
        serializer.is_valid(raise_exception=True)
        slots_info = self.get_slots_info(serializer.validated_data)
        if not serializer.validated_data["force_create"]:
            data = self.get_response_conflict_data(slots_info)
            if data:
                return Response(status=HTTP_409_CONFLICT, data=data)

        self.create(request, *args, **kwargs)
        updated_slots_dates = self.update_self_slots(serializer.validated_data, slots_info["self_slots_to_update"])
        self.create_slots(serializer.validated_data, slots_info["slot_to_create_dates"])
        response_data = self.get_response_data(slots_info, updated_slots_dates)
        return Response(status=HTTP_201_CREATED, data=response_data)

    @staticmethod
    def get_response_conflict_data(slots_info: Dict):
        if not len(slots_info['other_slots_occupied_dates']) and not len(slots_info['self_slots_occupied']):
            return None
        else:
            slots_occupied_dates = list(map(lambda x: x.strftime('%Y-%m-%d'), slots_info['other_slots_occupied_dates']))
            data = {
                "slots_occupied_dates": slots_occupied_dates
            }
        return data

    @staticmethod
    def get_response_data(slots_info: Dict, updated_slots_dates: List[datetime.date]) -> Dict:
        response_data = {
            "updated_slot_dates": list(),
            "created_slot_dates": list()
        }
        if len(updated_slots_dates):
            updated_dates = list(map(lambda x: x.strftime('%Y-%m-%d'), updated_slots_dates))
            response_data["updated_slot_dates"] = updated_dates
        if len(slots_info["slot_to_create_dates"]):
            created_dates = list(map(lambda x: x.strftime('%Y-%m-%d'), slots_info["slot_to_create_dates"]))
            response_data["created_slot_dates"] = created_dates
        return response_data

    @staticmethod
    def create_slots(serializer: Dict, slots_to_create_dates: List[datetime.date]) -> None:
        """
        Validating and creating slots
        """
        therapist = User.objects.get(id=serializer["therapist"].id)
        slots_to_create = list()
        for slot_date in slots_to_create_dates:
            slots_to_create.append(
                {
                    "start_time": datetime.combine(slot_date, serializer["start_time"], tzinfo=pytz.UTC),
                    "end_time": datetime.combine(slot_date, serializer["end_time"], tzinfo=pytz.UTC),
                    "therapist": therapist
                }
            )
        obj_list = [Slot(**data_dict) for data_dict in slots_to_create]
        Slot.objects.bulk_create(obj_list)

    def get_slots_info(self, serializer: Dict) -> Dict:
        """
        Validating and creating lists of slots for updating and/or creating
        """

        slots_info = {
            "self_slots_to_update": list(),
            "self_slots_occupied": list(),
            "other_slots_occupied_dates": list(),
            "slot_to_create_dates": list(),
        }
        list_of_dates = self.get_slot_dates(serializer)
        self_slots, other_slots_dates = self.split_slots_by_owner(list_of_dates, serializer["therapist"].id)
        self_slots_dates = self.get_slots_dates(self_slots)

        if serializer["force_create"]:
            for slot_date in list_of_dates:
                for slot in self_slots:
                    if slot_date in self_slots_dates and slot not in slots_info["self_slots_to_update"]:
                        slots_info["self_slots_to_update"].append(slot)
                    continue
                if slot_date in other_slots_dates:
                    continue
                elif slot_date not in self_slots_dates and slot_date not in other_slots_dates:
                    slots_info["slot_to_create_dates"].append(slot_date)
            return slots_info

        else:
            for slot_date in list_of_dates:
                for slot in self_slots:
                    if slot.start_time.date() == slot_date:
                        slots_info["self_slots_to_update"].append(slot)
                    continue
                if slot_date in other_slots_dates:
                    slots_info["other_slots_occupied_dates"].append(slot_date)
                elif slot_date not in self_slots_dates and slot_date not in other_slots_dates:
                    slots_info["slot_to_create_dates"].append(slot_date)
            return slots_info

    @staticmethod
    def get_slot_dates(serializer: Dict):
        list_of_dates = list()
        for day in range(0, (serializer["valid_to"] - serializer["valid_from"]).days + 1):
            if (serializer["valid_from"] + timedelta(days=day)).isoweekday() in list(map(int, serializer["days"])):
                list_of_dates.append(serializer["valid_from"] + timedelta(days=day))
        return list_of_dates

    @staticmethod
    def split_slots_by_owner(list_of_days: List, therapist: User):
        """
        Splitting all occupied slots by their owners (self, other)
        """

        self_slots = []
        other_slots_dates = []
        occupied_slots = list(Slot.objects.filter(start_time__date__in=list_of_days))

        for slot in occupied_slots:
            if slot.therapist.id == therapist:
                self_slots.append(slot)
            else:
                other_slots_dates.append(slot.start_time.date())
        return self_slots, other_slots_dates

    @staticmethod
    def get_slots_dates(slots_list: List) -> List:
        slots_dates = list()
        for slot in slots_list:
            slots_dates.append(slot.start_time.date())
        return slots_dates

    def update_self_slots(self, serializer: Dict, self_slots_to_update: List[Slot]) -> List[datetime.date]:
        slots_to_update = list()
        self_slots_to_update_dates = self.get_slots_dates(self_slots_to_update)
        queryset = Slot.objects.filter(start_time__date__in=self_slots_to_update_dates)
        for slot in queryset:
            # Massage shift check here
            date = slot.start_time.date()
            if (slot.start_time.time() == serializer["start_time"]
                    and slot.end_time.time() == serializer["end_time"]):
                continue
            else:
                slot.start_time = datetime.combine(date, serializer["start_time"], tzinfo=pytz.UTC)
                slot.end_time = datetime.combine(date, serializer["end_time"], tzinfo=pytz.UTC)
                slots_to_update.append(slot)
        if len(slots_to_update):
            Slot.objects.bulk_update(slots_to_update, ['start_time', 'end_time'])
        return self.get_slots_dates(slots_to_update)
