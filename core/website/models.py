from django.db import models
from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from website.validators import validate_phone_number
from accounts.models import Profile


User = get_user_model()


class ContactModel(models.Model):
    full_name = models.CharField(max_length=400)
    email = models.EmailField()
    phone_number = models.CharField(validators=[validate_phone_number])
    subject = models.CharField(max_length=300)
    content = models.TextField()
    is_seen = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)



class JobTitle(models.Model):
    title = models.CharField(max_length=250)

class TeamMembers(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    job_title = models.ManyToManyField(JobTitle)
    description = models.CharField(max_length=225)
    facebook_link = models.URLField(max_length=200, blank=True)
    twitter_link = models.URLField(max_length=200, blank=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)



    def clean(self):
        if not self.profile.user.is_superuser:
            raise ValidationError("Only superusers can create or update an instance.")
        
        if not self.profile.first_name or not self.profile.last_name :
            raise ValidationError("Please complete the profile of the selected user first.")

        if not self.pk and TeamMembers.objects.filter(profile=self.profile).exists():
            raise ValidationError("Each user can only create one instance.")

    def save(self, *args, **kwargs):
        self.clean() 
        super().save(*args, **kwargs)




class NewsLetter(models.Model):
    email = models.EmailField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email