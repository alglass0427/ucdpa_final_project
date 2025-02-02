from django.db import models

# Create your models here.
from django.contrib.auth.models import User   ###PREDIFINED Django USER Model
from django.contrib.auth.models import Group
import uuid
import os


class Profile(models.Model):

    def allowed_groups():
    # Example: dynamically filter based on certain conditions
        return {'name__in': Group.objects.values_list('name', flat=True)}

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Rather not say', 'Rather not say'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True,blank=True) # One User has One Profile
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to=allowed_groups
    )

    username = models.CharField(max_length=200 , null=True,blank=True)
    balance = models.FloatField(null=False,default=0)
    location = models.CharField(max_length=200 , null=True,blank=True)
    name = models.CharField(max_length=200 , null=True,blank=True)
    email = models.EmailField(max_length=200 , null=True,blank=True)
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default='Male',
    )
    short_intro = models.TextField(null=True,blank=True)
    bio  = models.TextField(null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)    	
    def __str__(self):
        return f"{str(self.name)} ({str(self.user.username)})"
    
    def save(self, *args, **kwargs):
        if not self.group:  # If no group is set, assign default
            self.group, _ = Group.objects.get_or_create(name="Investor")
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['username'] # "-" orders by descending


class Message(models.Model):
    sender = models.ForeignKey(Profile,on_delete=models.SET_NULL,null=True,blank=True)
    recipient = models.ForeignKey(Profile,on_delete=models.SET_NULL,null=True,blank=True,related_name="messages")
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    subject = models.CharField(max_length=200, null=True, blank=True)
    body = models.TextField()
    is_read = models.BooleanField(default=False,null=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True,editable=False)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.subject)
    
    class Meta:
        ordering = ['is_read','-created']