from django_multitenant.utils import set_current_tenant
from middle_server.models import User
import json
class MultitenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        json_request = json.loads(request.body)
        
        user_id = json_request['user_id']
        user = User.objects.filter(pk=int(user_id))[0]
        set_current_tenant(user)

        return self.get_response(request)

