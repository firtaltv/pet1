from django.contrib import admin
from .models import Schedule, Slot
import pytz

utc = pytz.UTC


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('therapist', 'days', 'start_time', 'end_time',)
    list_filter = ('therapist',)

    # def has_add_permission(self, request):
    #     return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('therapist', 'start_time', 'end_time',)
    list_filter = ()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False
