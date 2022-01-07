from django.shortcuts import render

# Create your views here.

from django.views import View
from django.http import HttpResponse, JsonResponse
import json


from .code import Base64
from .code import AI_Model

g_ai_model = AI_Model.AI_Model()


class image_echo(View):
    def post(self, request):
        assert request is not None

        json_request = json.loads(request.body)
        base64_string = json_request['image']
        
        return HttpResponse(json.dumps({ "result" : base64_string}))


class image_list_predict(View):
    m_ai_model = g_ai_model

    def post(self, request):
        assert request is not None

        json_request = json.loads(request.body)

        
        image_base64str_file_list = None
        def check_request_data():
            nonlocal image_base64str_file_list

            image_base64str_file_list = json_request['image_list']
            image_count = int(json_request['image_count'])

            if image_count != len(image_base64str_file_list):
                return False

        if check_request_data() == False:
            return HttpResponse(status=400)


        image_list = list()
        for image_base64str_file in image_base64str_file_list:
            image = Base64.base64str_file_to_image(image_base64str_file)
            image_list.append(image)
        
        image_base64str_file_list.clear()
        image_base64str_file_list = None
        

        predict_list = self.m_ai_model.predict_image_list(image_list)

        image_list.clear()
        image_list = None


        json_response_data = json.dumps({
            "predict_count" : str(len(predict_list)),
            "predict_list" : predict_list,
            })

        return HttpResponse(json_response_data)


