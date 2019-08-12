from django.db import models

# Create your models here.

class Cds_Fleet(models.Model):
    airline = models.CharField(max_length=10)
    tailsign = models.CharField(max_length=10)
    ac_type = models.CharField(max_length=10)
    wisp = models.CharField(max_length=10)
    wisp_status = models.CharField(max_length=10, blank=True, null=True)
    vlan = models.CharField(max_length=10)
    bc_type = models.CharField(max_length=10, blank=True, null=True)
    ant_type = models.CharField(max_length=10, blank=True, null=True)
    wap_type = models.CharField(max_length=10, blank=True, null=True)
    gen1_status = models.CharField(max_length=10, blank=True, null=True)
    gen1_eis_date = models.CharField(max_length=10, blank=True, null=True)
    gen1_xid = models.CharField(max_length=10, blank=True, null=True)
    gen1_ip = models.CharField(max_length=10, blank=True, null=True)
    gen3_status = models.CharField(max_length=10, blank=True, null=True)
    gen3_eis_date = models.CharField(max_length=10, blank=True, null=True)
    gen3_xid = models.CharField(max_length=10, blank=True, null=True)
    gen3_ip = models.CharField(max_length=10, blank=True, null=True)
    xid_reported = models.CharField(max_length=10, blank=True, null=True)
    map_lbp = models.CharField(max_length=50, blank=True, null=True)
    map_reported = models.CharField(max_length=50, blank=True, null=True)
    optfile_reported = models.CharField(max_length=50, blank=True, null=True)
    gcs_mdm_version = models.CharField(max_length=50, blank=True, null=True)
    reported_time = models.CharField(max_length=50, blank=True, null=True)
    bcsla_patch = models.CharField(max_length=50, blank=True, null=True)
    whitelist_version = models.CharField(max_length=50, blank=True, null=True)
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'cds_fleet'



class Cds_Fleet_bak(models.Model):
    airline = models.CharField(max_length=10)
    tailsign = models.CharField(max_length=10)
    ac_type = models.CharField(max_length=10)
    wisp = models.CharField(max_length=10)
    wisp_status = models.CharField(max_length=10, blank=True, null=True)
    vlan = models.CharField(max_length=10)
    bc_type = models.CharField(max_length=10, blank=True, null=True)
    ant_type = models.CharField(max_length=10, blank=True, null=True)
    wap_type = models.CharField(max_length=10, blank=True, null=True)
    gen1_status = models.CharField(max_length=10, blank=True, null=True)
    gen1_eis_date = models.CharField(max_length=10, blank=True, null=True)
    gen1_xid = models.CharField(max_length=10, blank=True, null=True)
    gen1_ip = models.CharField(max_length=10, blank=True, null=True)
    gen3_status = models.CharField(max_length=10, blank=True, null=True)
    gen3_eis_date = models.CharField(max_length=10, blank=True, null=True)
    gen3_xid = models.CharField(max_length=10, blank=True, null=True)
    gen3_ip = models.CharField(max_length=10, blank=True, null=True)
    xid_reported = models.CharField(max_length=10, blank=True, null=True)
    map_lbp = models.CharField(max_length=50, blank=True, null=True)
    map_reported = models.CharField(max_length=50, blank=True, null=True)
    optfile_reported = models.CharField(max_length=50, blank=True, null=True)
    gcs_mdm_version = models.CharField(max_length=50, blank=True, null=True)
    reported_time = models.CharField(max_length=50, blank=True, null=True)
    bcsla_patch = models.CharField(max_length=50, blank=True, null=True)
    whitelist_version = models.CharField(max_length=50, blank=True, null=True)
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'cds_fleet_bak'