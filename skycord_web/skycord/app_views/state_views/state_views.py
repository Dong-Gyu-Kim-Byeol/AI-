from middle_server.models import User
from middle_server.models import Farm
from middle_server.models import Raspberry
from middle_server.models import Original_image as Original_Image
from middle_server.models import Split_image as Split_Image
from django.db.models import Q
from django.shortcuts import render

from django.http import HttpResponse

g_search_original_image_max_count = 20

def Main_Index(request):
    user_id = request.session.get('user')
    user = User.objects.filter(pk=user_id)[0]
    farm_list = Farm.objects.filter(user=user).order_by('name')
    
    class Farm_Health:
        id = None
        name = None
        is_health = None
        image_id = None

    farm_health_list = []

    for farm in farm_list:
        device_list = Raspberry.objects.values_list('id', named=True).filter(farm=farm)
        
        is_health = True
        not_health_split_image_id = 0

        for device in device_list:
            original_image_list = Original_Image.objects.values_list('id', named=True).filter(raspberry=device.id)
            original_image_list = original_image_list.order_by('-date')
            original_image_list = original_image_list[ : g_search_original_image_max_count]

            for original_image in original_image_list:
                not_health_split_image_list = Split_Image.objects.only('predict_value').filter(Q(original_image=original_image.id) & ~Q(predict_value='H'))
                if not_health_split_image_list:
                    not_health_split_image_id = not_health_split_image_list[0].id
                    is_health = False
                    break
            
            if is_health == False:
                break
        
        if is_health == False:
            farm_health = Farm_Health()
            farm_health.id = farm.id
            farm_health.name = farm.name
            farm_health.is_health = is_health
            farm_health.image_id = not_health_split_image_id

            farm_health_list.append(farm_health)

    context = {"farm_health_list":farm_health_list}
    return render(request, 'main.html', context)

def Farm_State(request):
    user_id = request.session.get('user')
    user = User.objects.filter(pk=user_id)[0]
    farm_list = Farm.objects.filter(user=user).order_by('name')
    
    class Farm_Health:
        id = None
        name = None
        is_health = None

    farm_health_list = []

    for farm in farm_list:
        device_list = Raspberry.objects.values_list('id', named=True).filter(farm=farm)
        
        is_health = True

        for device in device_list:
            original_image_list = Original_Image.objects.values_list('id', named=True).filter(raspberry=device.id)
            original_image_list = original_image_list.order_by('-date')
            original_image_list = original_image_list[ : g_search_original_image_max_count]

            for original_image in original_image_list:
                not_health_split_image_list = Split_Image.objects.only('predict_value').filter(Q(original_image=original_image.id) & ~Q(predict_value='H'))
                if not_health_split_image_list:
                    is_health = False
                    break
            
            if is_health == False:
                break
        
        farm_health = Farm_Health()
        farm_health.id = farm.id
        farm_health.name = farm.name
        farm_health.is_health = is_health

        farm_health_list.append(farm_health)

    context = {"farm_health_list":farm_health_list}
    return render(request, 'farm_state.html', context)

def Device_State(request, farm_id):
    user_id = request.session.get('user')
    user = User.objects.filter(pk=user_id)[0]

    farm = Farm.objects.values_list('name', named=True).filter(pk=farm_id)[0]
    farm_name = farm.name

    device_list = Raspberry.objects.filter(farm=farm_id).order_by('name')
    
    class Device_Health:
        id = None
        name = ""
        is_health = None

    device_health_list = []

    for device in device_list:
        is_health = True
        original_image_list = Original_Image.objects.values_list('id', named=True).filter(raspberry=device.id)
        original_image_list = original_image_list.order_by('-date')
        original_image_list = original_image_list[ : g_search_original_image_max_count]

        for original_image in original_image_list:
            not_health_split_image_list = Split_Image.objects.only('predict_value').filter(Q(original_image=original_image.id) & ~Q(predict_value='H'))
            if not_health_split_image_list:
                is_health = False
                break
        
        device_health = Device_Health()
        device_health.id = device.id
        device_health.name = device.name
        device_health.is_health = is_health
        
        device_health_list.append(device_health)

    context = {"farm_name": farm_name,
                "device_health_list": device_health_list}
    return render(request, 'device_state.html', context)


def Device_Image_List(request, device_id):
    user_id = request.session.get('user')
    user = User.objects.filter(pk=user_id)[0]
    device = Raspberry.objects.filter(pk=device_id)[0]
    
    disease_types = {'D01': '궤양병',
                    'D04': '잎곰팡이병',
                    'D05': '점무늬병',
                    'H': '정상',
                    'P03': '아메리카잎굴파리'}

    class Show_Image:
        id = None
        predict_value = None
        date = None

    show_image_list = []

    original_image_list = Original_Image.objects.values_list('id', 'date', named=True).filter(raspberry=device.id)
    original_image_list = original_image_list.order_by('-date')
    original_image_list = original_image_list[:g_search_original_image_max_count]

    for original_image in original_image_list:
            
        not_health_split_image_list = Split_Image.objects.only('predict_value').filter(Q(original_image=original_image.id) & ~Q(predict_value='H'))
        if not_health_split_image_list:
            for not_health_split_image in not_health_split_image_list:
                show_image = Show_Image()
                show_image.date = original_image.date

                show_image.id = not_health_split_image.id
                show_image.predict_value = disease_types[not_health_split_image.predict_value]
        
                show_image_list.append(show_image)

    context = {"show_image_list":show_image_list}
    return render(request, 'device_image_list.html', context)


def Split_Image_Show(request, split_image_id):
    user_id = request.session.get('user')

    split_image = Split_Image.objects.values_list('split_image', named=True).get(pk=split_image_id)

    return HttpResponse(split_image.split_image, content_type="image/png")