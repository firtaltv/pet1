from django.urls import path
from .views import (
                    TherapistScheduleRetrieveAPIView,
                    TherapistSlotListAPIView,
                    TherapistScheduleCreateAPIView,
                    )

app_name = 'service'

urlpatterns = [
    path('schedule/therapist/<int:pk>/', TherapistScheduleRetrieveAPIView.as_view(), name='therapist_schedule_object'),
    path('schedule/create/', TherapistScheduleCreateAPIView.as_view(), name='therapist_schedule_create'),
    path('slots/therapist/<int:pk>/', TherapistSlotListAPIView.as_view(), name='therapist_slot_list'),
]
