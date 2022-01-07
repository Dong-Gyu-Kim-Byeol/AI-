# from django_multitenant.utils import set_current_tenant
    
class MultitenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_id = request.session.get('user')
        # print('------------- ' + str(user_id) + ' -------------')
        # set_current_tenant(user_id)
        
        return self.get_response(request)
