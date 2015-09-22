from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class GoRequestForm(forms.Form):
	email          = forms.CharField(max_length = 200, widget = forms.TextInput(attrs={'class' : 'form-control'}))
	scm_url        = forms.CharField(max_length = 200, required = True, widget = forms.TextInput(attrs={'class' : 'form-control'}))
	text           = forms.CharField(max_length = 200, required = False, widget = forms.Textarea(attrs={'class' : 'form-control'}))

class GoReviewForm(forms.Form):
	email          = forms.CharField(max_length = 200, widget = forms.TextInput(attrs={'class' : 'form-control'}))
	text           = forms.CharField(max_length = 200, required = False, widget = forms.Textarea(attrs={'class' : 'form-control'}))

