from django.forms import ModelForm
from .models import Profile , Cash
from django.core.exceptions import ValidationError
from django import forms


class CashForm(ModelForm,forms.Form):
    # file = forms.FileField()
    class Meta:
        model  = Cash
        # fields = '__all__'
        fields = ['name','group','email','username','location','bio','short_intro','gender','balance']
                
        #           ]
   # adds css Classes to the ClassForm

    def __init__(self,*args,**kwargs):
        super(CashForm,self).__init__(*args,**kwargs)
        for name,field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
                })
