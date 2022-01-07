from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.http import HttpResponse

from middle_server.models import User
from middle_server.models import Farm

from skycord.app_views.farm_management_views.farm_forms import Farm_Form

def Farm_Management(request):
    user_id = request.session.get('user')
    farm_list = Farm.objects.filter(user_id=user_id).order_by('name')

    context = {'farm_list': farm_list}
    return render(request, 'farm_management/farm_management.html', context)


def Farm_Detail(request, farm_id):
    # set_current_tenant(None)
    farm = Farm.objects.get(pk=farm_id)

    if request.method == 'POST':
        edit_farm = Farm_Form(request.POST or None, instance=farm)
        if edit_farm.is_valid():
            edit_farm.save()
            return redirect('skycord:Farm_Management')
    elif request.method == 'GET':
        
        form = Farm_Form()
    else :
        return HttpResponse(status=400)
    
    context = {'form': form, 'farm': farm}
    return render(request, 'farm_management/farm_detail.html', context)


def Farm_Create(request):
    user_id = request.session.get('user')
    user = get_object_or_404(User, pk=user_id)
    # set_current_tenant(user)

    if request.method == 'POST':
        form = Farm_Form(request.POST)

        if form.is_valid():
            new_farm = form.save(commit=False)
            Farm.objects.create(user=user, name=new_farm.name)

            return redirect('skycord:Farm_Management')
    elif request.method == 'GET':
        form = Farm_Form()
    else :
        return HttpResponse(status=400)
    
    context = {'form': form}
    return render(request, 'farm_management/farm_create.html', context)


def Farm_Delete(request, farm_id):
    # set_current_tenant(None)
    Farm.objects.filter(pk=farm_id).delete()

    return redirect('skycord:Farm_Management')