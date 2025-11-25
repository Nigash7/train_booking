#models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager 
from django.db import models        
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin

class UserManager(BaseUserManager): 
   def create_user(self, email, password=None, **extra_fields):
    if not email:
        raise ValueError("Users must have an email address")

    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

 
   def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        return self.create_user(email, password, **extra_fields)
 
class User(AbstractBaseUser, PermissionsMixin): 
    email = models.EmailField(unique=True) 
    name = models.CharField(max_length =100) 
    phone_number = models.CharField(max_length=15)

    address = models.TextField()
    age = models.PositiveIntegerField()
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'),('Other', 'Other')],
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True) 
    is_staff = models.BooleanField(default=False) 
    is_admin = models.BooleanField(default=False) 
    objects = UserManager() 
 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.email

# Create your models here.
