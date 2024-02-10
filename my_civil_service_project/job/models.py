from address.models import Address
from django.db import models
from user.models import User
from .constants import *


class WorkType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)


class Job(models.Model):
    """
    Job model class
    """
    id = models.AutoField(primary_key=True)
    work_type = models.ForeignKey(WorkType, on_delete=models.CASCADE, related_name=WORK)
    number_of_workers = models.IntegerField()
    work_date = models.DateField()
    working_days = models.IntegerField()
    work_pay = models.FloatField()
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name=JOB_ADDRESS, null=True)
    requestor = models.ForeignKey(User, on_delete=models.CASCADE, related_name=JOB_REQUESTOR, null=True)
    acceptor = models.ManyToManyField(User, related_name=JOB_ACCEPTOR, null=True, db_table=APPLIED_WORKER)
    job_status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   blank=True, null=True, related_name=CREATE_JOB)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   blank=True, null=True, related_name=UPDATE_JOB)
    is_deleted = models.BooleanField(editable=False, default=False)

