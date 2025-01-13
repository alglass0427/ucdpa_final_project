from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile , Message
from django.core.exceptions import ValidationError
from django import forms

# ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif']
# MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        ###django documenttion -   password1 then password2 is password confirm
        fields = ['first_name','username','email','password1','password2']
        labels = {
            'first_name':'Name'
        }

    def __init__(self,*args,**kwargs):
        super(CustomUserCreationForm,self).__init__(*args,**kwargs)

        # adds css Classes to the ClassForm

        for name,field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
                })


class ProfileForm(ModelForm,forms.Form):
    # file = forms.FileField()
    class Meta:
        model  = Profile
        # fields = '__all__'
        fields = ['name','email','username','location','bio','short_intro','gender'
                
                  ]
   # adds css Classes to the ClassForm

    def __init__(self,*args,**kwargs):
        super(ProfileForm,self).__init__(*args,**kwargs)
        for name,field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
                })


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['name', 'email' , 'subject', 'body']

    def __init__(self,*args,**kwargs):
        super(MessageForm,self).__init__(*args,**kwargs)
        for name,field in self.fields.items():
            field.widget.attrs.update({'class':'input'})