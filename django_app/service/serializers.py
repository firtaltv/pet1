import datetime

from rest_framework import serializers
from users.models import User
from .models import Schedule, Slot, Massage


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'pk',
            'last_name',
            'first_name',
        )


class ScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'pk',
            'days',
            'therapist',
            'start_time',
            'end_time',
            'valid_from',
            'valid_to',
            'force_create',
        )
        model = Schedule

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['therapist'] = UserSerializer(instance.therapist).data
        return ret


class SlotSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'pk',
            'therapist',
            'start_time',
            'end_time',
            'is_active',
            'eventId',
        )
        model = Slot


class MassageSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'pk',
            'slot',
            'client',
            'start_time',
            'end_time',
            'eventId',
            'therapist',
            'slot_eventId'
        )
        model = Massage

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Find slot's eventId and therapist
        ret['slot_eventId'] = SlotSerializer(instance.slot).data["eventId"]
        ret['therapist'] = SlotSerializer(instance.slot).data["therapist"]
        return ret
