from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.http import HttpResponse

from middle_server.models import User
from middle_server.models import Farm
from middle_server.models import Raspberry

from skycord.app_views.device_management_views.raspberry_forms import Raspberry_Form

def Device_Management(request, farm_id):
    user_id = request.session.get('user')
    farm = Farm.objects.get(pk=farm_id)
    raspberry_list = Raspberry.objects.filter(farm=farm).order_by('name')

    context = {'farm': farm, 'raspberry_list': raspberry_list}
    return render(request, 'device_management/device_management.html', context)


def Device_Detail(request, farm_id, raspberry_id):
    user_id = request.session.get('user')
    # set_current_tenant(None)
    farm = Farm.objects.get(pk=farm_id)
    raspberry = Raspberry.objects.get(pk=raspberry_id)

    if request.method == 'POST':
        edit_raspberry = Raspberry_Form(request.POST or None, instance=raspberry)
        if edit_raspberry.is_valid():
            edit_raspberry.save()
            return redirect('skycord:Device_Management', farm_id)
    elif request.method == 'GET':
        
        form = Raspberry_Form()
    else :
        return HttpResponse(status=400)
    
    context = {'user_id': user_id, 'form': form, 'farm': farm, 'raspberry': raspberry}
    return render(request, 'device_management/device_detail.html', context)


def Device_Create(request, farm_id):
    user_id = request.session.get('user')
    farm = Farm.objects.filter(pk=farm_id)[0]
    # set_current_tenant(user)

    if request.method == 'POST':
        form = Raspberry_Form(request.POST)

        if form.is_valid():
            new_raspberry = form.save(commit=False)
            Raspberry.objects.create(farm=farm, name=new_raspberry.name)

            return redirect('skycord:Device_Management', farm_id)
    elif request.method == 'GET':
        form = Raspberry_Form()
    else :
        return HttpResponse(status=400)
    
    context = {'form': form}
    return render(request, 'device_management/device_create.html', context)


def Device_Delete(request, farm_id, raspberry_id):
    # set_current_tenant(None)
    Raspberry.objects.filter(pk=raspberry_id)[0].delete()

    return redirect('skycord:Device_Management', farm_id)