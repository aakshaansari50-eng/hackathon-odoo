from django import forms
from django.contrib.auth.models import User
from .models import Asset, Booking, MaintenanceRequest, Profile, TransferRequest
class SignupForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput)
    class Meta: model=User; fields=['username','first_name','last_name','email','password']
    def save(self,commit=True):
        user=super().save(commit=False); user.set_password(self.cleaned_data['password'])
        if commit: user.save(); Profile.objects.create(user=user)
        return user
class StyledFormMixin:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values(): field.widget.attrs['class']='form-control'
class AssetForm(StyledFormMixin,forms.ModelForm):
    class Meta: model=Asset; fields=['asset_id','name','category','serial_number','purchase_date','cost','location','condition','status']
class BookingForm(StyledFormMixin,forms.ModelForm):
    class Meta: model=Booking; fields=['resource','start','end','purpose']; widgets={'start':forms.DateTimeInput(attrs={'type':'datetime-local'}),'end':forms.DateTimeInput(attrs={'type':'datetime-local'})}
class MaintenanceForm(StyledFormMixin,forms.ModelForm):
    class Meta: model=MaintenanceRequest; fields=['asset','issue']
class TransferForm(StyledFormMixin,forms.ModelForm):
    class Meta: model=TransferRequest; fields=['asset','target_user','reason']
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['asset'].queryset=Asset.objects.exclude(status__in=['RETIRED','DISPOSED','LOST'])
