from middle_server.models import User
from middle_server.models import Farm
from middle_server.models import Raspberry
from middle_server.models import Original_image
from middle_server.models import Split_image
from django.db.models import Q
from django.shortcuts import render

def get_ras_list(request):
    user_id = request.session.get('user')
    if user_id:
        user = User.objects.get(pk=user_id)
        farm_list = Farm.objects.filter(Q(user=user)).order_by('id')
        device = Raspberry.objects.filter(farm_id=farm_list)
        have_H = 0
        raspberry_list=[]
        for farm in farm_list:
            raspberry_list.append(Raspberry.objects.filter(Q(farm=farm)).order_by('id'))

    context = {"device": device,
               "device_state": have_H,
               "farm_list":farm_list,
               "ras_list": raspberry_list
               }
    print(raspberry_list)
    return render(request, 'farm_list.html', context)