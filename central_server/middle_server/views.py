from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.db import models
from .models import User, Farm, Raspberry, Original_image, Split_image
from django.views.decorators.csrf import csrf_exempt
import PIL
import io
import base64
import json
import requests
import PIL.Image
import datetime
@csrf_exempt
def communication(request):
    def split_image(image, row_split_count, column_split_count):
        assert image is not None
        assert isinstance(image, PIL.Image.Image)

        assert row_split_count is not None
        assert isinstance(row_split_count, int)
        assert row_split_count is not 0

        assert column_split_count is not None
        assert isinstance(column_split_count, int)
        assert column_split_count is not 0

        image_width = image.size[0]  # width
        image_height = image.size[1]  # height

        split_row_im_list = []
        split_row_image_height = int(image_height / row_split_count)
        area_row = [0, None, image_width, None]

        for height in range(0, image_height, split_row_image_height):
            area_row[1] = height
            area_row[3] = height + split_row_image_height
            if area_row[3] > image_height:
                break

            split_row_im_list.append(image.crop(area_row))

        split_image_list = []
        split_column_image_width = int(image_width / column_split_count)
        area_column = [None, 0, None, split_row_image_height]

        for split_row_im in split_row_im_list:
            for width in range(0, image_width, split_column_image_width):
                area_column[0] = width
                area_column[2] = width + split_column_image_width
                if area_column[2] > image_width:
                    break

                split_image_list.append(split_row_im.crop(area_column))

        return split_image_list

    def go_to_DB(json_request, AI_response_predict_list, base64_split_image_list, image_count):
        original_image_bytesIO=io.BytesIO(base64.b64decode(json_request['image'].encode('utf-8'))).getvalue()
        raspberry_object = Raspberry.objects.get(id=int(json_request['raspberry_id']))
        original_image_table = Original_image.objects.create(raspberry=raspberry_object, original_image=original_image_bytesIO,split_count=image_count)

        for image, predict in zip(base64_split_image_list, AI_response_predict_list):
            split_image_bytesIO = io.BytesIO(base64.b64decode(image.encode('utf-8'))).getvalue()
            split_image_table = Split_image.objects.create(original_image=original_image_table, split_image=split_image_bytesIO, predict_value=predict)

    def decoding_image(utf_image):
        base64_image = utf_image.encode('utf-8')
        PIL_image = PIL.Image.open(io.BytesIO(base64.b64decode(base64_image)))
        return PIL_image
    def encoding_image(PIL_image):
        img_byte_arr = io.BytesIO()
        PIL_image.save(img_byte_arr, format='PNG',optimize=True)
        base64_image = base64.b64encode(img_byte_arr.getvalue())
        base64_string_image = base64_image.decode('utf-8')
        return base64_string_image
    def send_to_AIserver(utf_image):
        decoding_img = decoding_image(utf_image)
        split_image_list = split_image(decoding_img, 2, 2)
        base64_split_image_list = []
        size = 256
        for image in split_image_list:
            img = image.resize((size,size))
            base64_split_image_list.append(encoding_image(img))
        image_count = str(len(base64_split_image_list))
        data = {"image_list": base64_split_image_list,
                "image_count": image_count}
        data = json.dumps(data)
        
        json_response = requests.post('http://203.250.114.199:8020/ai/tomato_disease_type/image_list_predict/', data=data)
        AI_response = json.loads(json_response.text)
        if(len(base64_split_image_list)==len(AI_response['predict_list']) and image_count == AI_response['predict_count']):
            return AI_response['predict_list'], base64_split_image_list, int(image_count)
        else:
            return None
    def post_image():
        json_request = json.loads(request.body)
        AI_response_predict_list, base64_split_image_list, image_count = send_to_AIserver(json_request['image'])
        go_to_DB(json_request, AI_response_predict_list, base64_split_image_list, image_count)
        return HttpResponse(200)
    if request.method == "POST":
        return post_image()
    elif request.method == "GET":
        return HttpResponse("Hello World!!")
def settings(request,email,pwd,phone,farm_name,rasp_name):
    if request.method == "GET":
       user=User.objects.create(email = email, password = pwd, phone = phone)
       farm=Farm.objects.create(user=user,name=farm_name)
       rasp=Raspberry.objects.create(farm=farm,name=rasp_name)
       return HttpResponse(300)
def deleteDB(request,user_id,farm_id,rasp_id):
    if request.method == "GET":
        Raspberry.objects.get(id=rasp_id).delete()
        Farm.objects.get(id=farm_id).delete()
        User.objects.get(id=user_id).delete()
        return HttpResponse(300)
