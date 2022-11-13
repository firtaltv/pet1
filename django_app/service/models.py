import pytz
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms import MultipleChoiceField
from django.utils.translation import gettext_lazy as _

from users.models import User

utc = pytz.UTC


class ChoiceArrayField(ArrayField):
    """ Helper for multiple choice field """

    def formfield(self, **kwargs):
        defaults = {
            'form_class': MultipleChoiceField,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class Schedule(models.Model):
    class Week(models.TextChoices):
        MONDAY = 1, _('Monday')
        TUESDAY = 2, _('Tuesday')
        WEDNESDAY = 3, _('Wednesday')
        THURSDAY = 4, _('Thursday')
        FRIDAY = 5, _('Friday')
        SATURDAY = 6, _('Saturday')
        SUNDAY = 7, _('Sunday')

    days = ChoiceArrayField(
        base_field=models.CharField(max_length=10, choices=Week.choices),
        default=list,
        size=10,
        blank=True,
        help_text='List of integers [1, 3]',
    )
    therapist = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='schedules_therapist', verbose_name='Therapist')
    start_time = models.TimeField(verbose_name='Start time', help_text='10:00')
    end_time = models.TimeField(verbose_name='End time', help_text='10:00')
    valid_from = models.DateField(verbose_name='Valid from', help_text='2022-09-15')
    valid_to = models.DateField(verbose_name='Valid to', help_text='2022-10-15')
    force_create = models.BooleanField(default=False, verbose_name='Force create')

    def __str__(self):
        return f'{self.therapist.username}\'s schedule'

    class Meta:
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        ordering = ('therapist', 'start_time',)


class Slot(models.Model):
    therapist = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Therapist')
    start_time = models.DateTimeField(verbose_name='Start time')
    end_time = models.DateTimeField(verbose_name='End time')
    is_active = models.BooleanField(default=True, verbose_name='Is active')
    eventId = models.CharField(max_length=1024, verbose_name='Event ID', null=True, blank=True)

    class Meta:
        verbose_name = 'Slot'
        verbose_name_plural = 'Slots'
        ordering = ('start_time',)


class Massage(models.Model):
    slot = models.ForeignKey(Slot, related_name='slot', on_delete=models.CASCADE, verbose_name='Slot')
    client = models.ForeignKey(User, related_name='client', on_delete=models.CASCADE, verbose_name='Client')
    start_time = models.DateTimeField(verbose_name='Start time')
    end_time = models.DateTimeField(verbose_name='End time')
    eventId = models.CharField(max_length=1024, verbose_name='Event ID', null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Is active')

    class Meta:
        verbose_name = 'Massage'
        verbose_name_plural = 'Massages'
        ordering = ('start_time',)
