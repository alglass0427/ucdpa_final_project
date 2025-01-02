from django.db import models

# Create your models here.
from django.contrib.auth.models import User   ###PREDIFINED Django USER Model
import uuid
import os


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True,blank=True) # One User has One Profile
    username = models.CharField(max_length=200 , null=True,blank=True)
    location = models.CharField(max_length=200 , null=True,blank=True)
    name = models.CharField(max_length=200 , null=True,blank=True)
    email = models.EmailField(max_length=200 , null=True,blank=True)
    short_intro = models.TextField(null=True,blank=True)
    bio  = models.TextField(null=True,blank=True)

    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True,editable=False)

    def __str__(self):
        return str(self.user.username)
    
    class Meta:
        ordering = ['name'] # "-" orders by descending


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