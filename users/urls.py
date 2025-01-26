from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('dashboard/', views.dashboard, name="dashboard"),
    # path('profile/<str:pk>', views.userProfile, name="user-profile"),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),
    # path('edit-account/', views.editAccount, name= "edit-account"),
    path('edit-account/<str:page>/', views.editAccount, name= "edit-account"),
    # path('get_bid_offer/', views.get_bid_offer, name= "get_bid_offer"),
    path('inbox/', views.inbox, name= "inbox"),
    path('message/<str:pk>/', views.viewMessage, name= "message"),
    path('create-message/<str:pk>/', views.createMessage, name= "create-message"),
    path('profiles/',views.profiles,name="profiles"),
]
