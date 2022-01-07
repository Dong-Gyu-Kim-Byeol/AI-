from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.http import HttpResponse,HttpResponseRedirect

from django.contrib import messages

from middle_server.models import User

from .login_forms import login_Form


def login_Index(request):
    if request.method == 'GET':
        form = login_Form()
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:
            user = User.objects.get(email = email)
            if password != user.password :
                messages.info(request,'비밀번호가 틀렸습니다')
                return HttpResponseRedirect('/')
            else :
                request.session['user'] = user.id
                return redirect('skycord:Main_Index')
    else :
        return HttpResponse(status=400)
    context = {'form': form}
    return render(request, 'login.html', context)

def logout(request):
    if request.session.get('user'):
        del request.session['user']

    return redirect('/')

def sign_up(request):
    if request.method == "GET":
        return render(request, 'sign_up.html')
    elif request.method =="POST":
        if request.POST.get('email') and request.POST.get('phone') and request.POST.get('password'):
            print("test")
            email = request.POST.get('email')
            password = request.POST.get('password')
            phone = request.POST.get('phone')
            try:
                user = User.objects.get(email=email)
                print(user.email)
                return redirect('/sign_up')
            except User.DoesNotExist:
                User.objects.create(email=email,password=password,phone=phone)
                return HttpResponseRedirect('/')
    else :
        HttpResponse('404 error')
