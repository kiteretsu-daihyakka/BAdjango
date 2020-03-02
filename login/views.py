from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.views.generic import View
from .forms import AuthForm,UserForm
from django.contrib import messages
from django.contrib.auth.models import User as UserModel
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.

# def login(request):
#     return render(request,'login/loginPage.html')
def frgtPwd(request):
    # send_mail(
    #     'Subject blah blah ',
    #     "that's fckin working!!",
    #     'seeyouatthetop42@gmail.com',
    #     ['seeyouatthetop42@yahoo.com','viraj0118@gmail.com','parmarapurva1999@gmail.com'],
    #     fail_silently=False
    # )
    return render(request,'login/forgotPwd.html')


def newPwd(request):
    try:
        usr = UserModel.objects.get(password=request.POST['passwrd'],secque=request.POST['secque'],secqans=request.POST['secans'])
        # if request.user.password==request.POST['passwrd'] & usr.secque== & usr.secqans==:
        if usr is not None:
            return render(request, 'login/newPwd.html')
    except ObjectDoesNotExist:
        messages.info(request,'Invalid credentials.')
    return redirect('login:chngPwd')

def logoutview(request):
    logout(request)
    # request.user=''
    return redirect('login:log_in')
def changePwd(request):
    return render(request,'login/changePwd.html')
def savenewpwd(request):
    messages.info(request,'Password changed successfully.')
    usr=UserModel.objects.get(email=request.user.email)
    usr.password=request.POST['passwd']
    usr.save()
    login(request,usr)
    return redirect('admm:profile')


def loginview(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        # nwpassword=
        # user=authenticate(username=username,password=password)
        try:
            userObj=UserModel.objects.get(email=email,password=password)
            # if user is not None:
            # messages.info(request,'coming here..')
            if userObj.is_active:
                login(request, userObj)
                # if usrObj.roleid == 3:

                return redirect('admm:index')
            messages.info(request,'User is locked.')
        except ObjectDoesNotExist:
            messages.info(request,'Invalid username or password.')
        # return redirect('login:login')
    if request.user.is_authenticated:
        return render(request,'login/logoutfirst.html')
    return render(request,'login/loginPage.html')

class AuthFormView(View):
    form_class=AuthForm
    template_name='login/loginPage.html'

    def get(self,request):
        form=self.form_class(None)
        return render(request,self.template_name,{'form':form})

    def post(self,request):
        form=self.form_class(request.POST)
        try:
            if form.is_valid():
            # user=form.save(commit=False)
            #cleaned (normalized) data
            # username = form.cleaned_data['email']
            # password = form.cleaned_data['password']
            # user.set_password(password)
            # username=form.cleaned_data['username']
            # password=form.cleaned_data['password']
            # user = authenticate(username=username,password=password)
            # user = UserModel.objects.get(username=username)
            # if user.username == 'virajchetan':
                #if user.is_active:
                # login(request, user)
            # messages.info(request,str(user.email))
                # messages.info(request,str(password))
                # return redirect('admm:index')
                messages.info(request,'ehy')
        except Exception as e:
            messages.info(request,e)
        return redirect('login:login')
    # return render()

class UserFormView(View):
    form_class=UserForm
    template_name='login/loginPage.html'

    #display blank form
    def get(self,request):
        form=self.form_class(None)
        return render(request,self.template_name,{'form':form})

    def post(self,request):
        form=self.form_class(request.POST)

        if form.is_valid():

            user=form.save(commit=False)

            #cleaned (normalized) data
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user.set_password(password)
            user.save()

            #returns user objects if credentials are correct
            user=authenticate(email=email,password=password)
            if user is not None:
                if user.is_active:
                    login(request,user)
                    return redirect('admm:index')
        return redirect('login:login')

























