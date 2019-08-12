from django.db import models

# Create your models here.

class DartOpsReport(models.Model):
    operator = models.CharField(max_length=20)
    aircraft = models.CharField(max_length=20)
    aircraft_type = models.CharField(max_length=20)
    flight_type = models.CharField(max_length=50)
    antenna_type = models.CharField(max_length=50)
    xid = models.IntegerField(null=True)
    bc_gen = models.CharField(max_length=20)
    flight_id = models.IntegerField(null=True,unique=True)
    flight_num = models.CharField(default='0000', max_length=20)
    excluded = models.BooleanField()
    exclusion_reason = models.CharField(null=True, max_length=255)
    departure_airport = models.CharField(null=True, max_length=20)
    arrival_airport = models.CharField(null=True, max_length=20)
    departure_time = models.DateTimeField(null=True)
    arrival_time = models.DateTimeField(null=True)
    flight_time = models.IntegerField(null=True)
    connected_sec = models.IntegerField(null=True)
    connected_sec_expected = models.IntegerField(null=True)
    avail_raw = models.FloatField(null=True)
    avail_calibrated = models.FloatField(null=True)
    latency = models.FloatField(null=True)
    latency_std = models.FloatField(null=True)
    packet_loss = models.FloatField(null=True)
    packet_loss_std = models.FloatField(null=True)
    beam_switch_count = models.IntegerField(null=True)
    beam_switch_average_sec = models.IntegerField(null=True)
    beam_switch_excluded_sec = models.IntegerField(null=True)
    kbpu = models.FloatField(null=True)
    device_count = models.IntegerField(null=True)
    generated_time = models.DateTimeField(auto_now=True)
    spare_field2 = models.CharField(null=True, max_length=10)
    spare_field3 = models.CharField(null=True, max_length=10)
    spare_field4 = models.CharField(null=True, max_length=10)
    spare_field5 = models.CharField(null=True, max_length=10)
    spare_field6 = models.CharField(null=True, max_length=10)
    spare_field7 = models.CharField(null=True, max_length=10)
    spare_field8 = models.CharField(null=True, max_length=10)

    class Meta:
        db_table = 'dart_ops_report'
        verbose_name = 'dart_ops_report'
        managed = True


    