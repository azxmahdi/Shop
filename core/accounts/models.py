from django.db import models
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.conf import settings

from .validators import validate_phone_number



class UserType(models.IntegerChoices):
        customer = 1, _("customer")
        admin = 2, _("admin")
        superuser = 3, _("superuser")

class CustomUserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
    
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        
        extra_fields.setdefault("type", UserType.superuser.value)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    

    email = models.EmailField(max_length=225, unique=True)
    type = models.IntegerField(choices=UserType.choices, default=UserType.customer.value)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Profile(models.Model):
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)  # Important change: OneToOneField and primary_key=True
    first_name = models.CharField(max_length=250, blank=True) #allow blank
    last_name = models.CharField(max_length=250, blank=True) #allow blank
    phone_number = models.CharField(max_length=12, validators=[validate_phone_number], blank=True) #allow blank
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
    

    def save(self, *args, **kwargs):
        if not self.pk:  
            if Profile.objects.filter(user=self.user).exists():
                raise ValidationError("Each user can only create one instance.")
        
        super().save(*args, **kwargs)
    
    def full_name(self):
        return self.first_name + ' ' + self.last_name


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created and instance.type == UserType.customer.value:
        Profile.objects.create(user=instance, pk=instance.pk)  # Explicitly set pk to user's ID
