from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.contrib import messages
from django.http import HttpResponse , JsonResponse
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm , ProfileForm
from .models import Profile
from portfolios.models import Asset
from portfolios.utils import get_latest_price
import json
# Create your views here.

def index(request):
    context = {}
    return render(request, 'users/index.html', context)


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
def editAccount (request):
    profile = request.user.profile
    print(profile)
    form  = ProfileForm(instance=profile)

    if request.method  == 'POST':
        form = ProfileForm(request.POST,request.FILES, instance= profile)
        if form.is_valid():
            form.save()

            return redirect ('dashboard')
    
    # form = ProfileForm()
    context = {'form':form}
    return render(request, 'users/profile_form.html', context)



@login_required(login_url='login')
def dashboard(request):
    profile = request.user.profile
    portfolios = profile.portfolio_set.all()
    if portfolios.count() == 0:
        messages.info(request, "You must create a portfolio before proceeding.")
        return redirect('portfolios')  # Redirect to the page for managing portfolios

    assets = Asset.get_assets_by_ticker()
    print(assets)
    context = {'profile' : profile , 'portfolios': portfolios, 'assets' : assets }
    return render(request, 'users/dashboard.html', context)

# @csrf_exempt
def get_bid_offer(request):
    if request.method == 'POST':
        print("Request Body:", request.body)
        # data = request.get_json() # retrieve the data sent from JavaScript
        data = json.loads(request.body)
        print("Parsed Data:", data)
        print(f"Ticker : {data}")
        ticker = data['ticker']
        if ticker  ==  "":
            return JsonResponse({'last_quote': "NA" , "message": "Please Select a ticker to refresh prices!", "category": "success"})
    else:
        # If using a GET request, retrieve portfolio from the query string
        ticker = request.args.get('ticker')
    print(ticker)
    last_quote = get_latest_price(ticker)
    # return jsonify({"message": "Asset added successfully!", "category": "success"}), 201
    return JsonResponse({'last_quote': last_quote , "message": "Asset added successfully!", "category": "success"})



