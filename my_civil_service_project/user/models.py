from django.db import models


class Verification(models.Model):
    email = models.EmailField(max_length=100, unique=100)
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now=True)


class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)


class User(models.Model):
    """
    User model class
    """
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=8)
    name = models.CharField(max_length=100)
    mobile = models.BigIntegerField(unique=True)
    email = models.EmailField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.OneToOneField('self', on_delete=models.CASCADE,
                                      blank=True, null=True, related_name='create_user')
    updated_by = models.OneToOneField('self', on_delete=models.CASCADE,
                                      blank=True, null=True, related_name='update_user')
    role = models.ManyToManyField(Role, related_name='roles')
    is_deleted = models.BooleanField(editable=False, default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return False. This is a way of comparing User objects to
        authenticated users.
        """
        return False
    
    def __str__(self):
        return self.email
