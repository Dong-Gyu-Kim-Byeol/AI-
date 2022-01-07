from django import forms
from middle_server.models import Raspberry


class Raspberry_Form(forms.ModelForm):
    class Meta:
        model = Raspberry
        fields = ['name']

        labels = {
            'name': '이름',
        }