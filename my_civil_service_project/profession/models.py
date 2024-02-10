from django.db import models
from job.models import WorkType
from user.models import User


class Profession(models.Model):
    """
    Profession model class
    mapped by : WorkerDetail - many to one mapping
    """

    id = models.AutoField(primary_key=True)
    profession = models.ForeignKey(WorkType, on_delete=models.CASCADE, related_name='work_type', null=True)
    work_experience = models.FloatField()
    expected_salary = models.IntegerField()
    is_available = models.BooleanField(default=True)
    gender = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   blank=True, null=True, related_name='create_profession')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   blank=True, null=True, related_name='update_profession')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workerdetails", null=True)
    is_deleted = models.BooleanField(editable=False, default=False)
