from django import forms
from middle_server.models import Farm


class Farm_Form(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['name']

        labels = {
            'name': '이름',
        }