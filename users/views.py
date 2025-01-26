from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages
from django.http import HttpResponse , JsonResponse
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm , ProfileForm ,  MessageForm
from .models import Profile
from portfolios.models import Asset
from portfolios.utils import get_latest_price
from .utils import searchProfiles,paginateProfiles
import json
# Create your views here.

def index(request):
    context = {}
    return render(request, 'users/index.html', context)

def profiles(request):
    profiles, search_query = searchProfiles(request)
    custom_range, profiles = paginateProfiles(request, profiles, 3)
    # profiles = Profile.objects.all()
    context = {'profiles':profiles,'search_query':search_query, 'custom_range': custom_range}
    for profile in profiles:
        print("NAME: ", profile.name, "GROUP: ", profile.group.name )

    print ('END OF VIEW')
    return render(request, 'users/profiles.html', context)

def loginPage(request):

    page = 'login'
    
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username  = request.POST['username'].lower()
        password  = request.POST['password']
        print(f"Email: {username} Password : {password}")
        try:
            user = User.objects.get(username = username)
            print(user)
        except:
            messages.error(request,"Username does not Exist")
        
        user = authenticate(request,username = username , password = password)

        if user is not None:
            login(request,user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'dashboard')
        else:
            messages.error(request,"Username or Password is Incorrect")


    context = {'page':page}
    return render(request, 'users/login_register.html', context)


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user =form.save(commit=False)  ##Saving and holing an instance of it 
            user.username = user.username.lower() #   then converts the instance of the user to lower case
            user.save()  ##then performs the save

            messages.success(request, "User Account Created!")

            login(request, user)
            return redirect('edit-account')                 
        
        else:
            messages.error(request , "An Error has occured")


    context = {'page':page , 'form':form}
    return render(request, 'users/login_register.html' , context)


@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    messages.info(request,"User was logged out")
    return redirect('login')



@login_required(login_url='login')
def editAccount (request,page=None):
    # page = kwargs.get('page',None)
    profile = request.user.profile
    print(profile)
    form  = ProfileForm(instance=profile)

    if request.method  == 'POST':
        form = ProfileForm(request.POST,request.FILES, instance= profile)
        if form.is_valid():
            form.save()

            return redirect ('dashboard')
    
    # form = ProfileForm()
    context = {'form':form,'page':page}
    return render(request, 'users/profile_form.html', context)



@login_required(login_url='login')
def inbox (request):
    profile = request.user.profile
    messageRequests = profile.messages.all()  ## "messages" in this case is The related name from the Model -   no need for _set
    unreadCount = messageRequests.filter(is_read=False).count()
    context = {'messageRequests':messageRequests,'unreadCount':unreadCount}
    return render(request, 'users/inbox.html', context)


# @login_required(login_url='login')
@login_required(login_url='login')
def viewMessage (request,pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
    context = {'message': message, 'profile':profile}

    ##{{message.name}}
    return render(request, 'users/message.html', context)

def createMessage (request,pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm

    try:
        sender = request.user.profile
    except:
        sender = None
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()

            messages.success(request,"Your message was sent successfully!")
            return redirect('profiles')
    
    context = {'recipient':recipient , 'form':form}

    ##{{message.name}}
    return render(request, 'users/message-form.html', context)



