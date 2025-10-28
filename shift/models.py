from django.db import models
from employee.models import Employee

class Shift(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    tolerance_in = models.IntegerField(default=0)
    tolerance_out = models.IntegerField(default=0)

    class Meta:
        unique_together = ('name', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"



class ShiftSchedule(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.employee.id_karyawan} - {self.date} ({self.shift.name})"
