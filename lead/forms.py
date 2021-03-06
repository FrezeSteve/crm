from django import forms
from .models import Lead, Task, Reminder
from django.contrib.auth.forms import AuthenticationForm, AdminPasswordChangeForm, PasswordChangeForm
from django.utils import timezone


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'password'
        }
    ))


class UserChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super(UserChangeForm, self).__init__(user, *args, **kwargs)

    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'username'}))
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'password'
            }
        ))
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'password'
            }
        ))


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ('status', 'source', 'assigned', 'name', 'phonenumber', 'location', 'email', 'description',)

        widgets = {
            'status': forms.Select(attrs={'class': 'custom-select', 'required': 'required'}),
            'source': forms.Select(attrs={'class': 'custom-select', 'required': 'required'}),
            'assigned': forms.Select(attrs={'class': 'custom-select', 'required': 'required'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'phonenumber': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'required': 'required'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description')

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'required': 'required'}),
        }


class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ('dueDate', 'dueTime', 'email')

        widgets = {
            'dueDate': forms.DateInput(format='%Y:%d:%m',
                                       attrs={'class': 'form-control',
                                              'required': 'required',
                                              'type': 'date',
                                              #  'value': timezone.datetime.now().strftime('%Y-%d-%m'),
                                              'min': timezone.datetime.today().strftime('%Y-%m-%d')}),
            'dueTime': forms.TimeInput(format='%H:%M',
                                       attrs={'class': 'form-control',
                                              'required': 'required',
                                              'type': 'time',
                                              'placeholder': ''.format(timezone.now().time())}),
        }


class UserEditForm(forms.Form):
    image = forms.ImageField(
        label='',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'custom-file-input'
            })
    )
    email = forms.CharField(
        max_length=100, required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    phonenumber = forms.CharField(
        label='', required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    pass

