from django import forms
from middle_server.models import User
from django.contrib.auth.hashers import check_password

class login_Form(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']

        labels = {
            'email': '이메일',
            'password' : '비밀번호',
        }
