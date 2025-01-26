from .models import Profile
from django.db.models import Q
from django.core.paginator import Paginator , PageNotAnInteger, EmptyPage

def searchProfiles(request):
    search_query = ''

    if request.GET.get('search_query'): #search_query is the "name =" on the form
        search_query = request.GET.get('search_query')

    print("SEARCH : ",search_query )

    if not search_query:
        print("No search query provided. Returning all profiles.")
        print("SEARCH : ",search_query )
        profiles = Profile.objects.all()  # Or return [] if you want to show no results
        return profiles, search_query

    # skills = Skill.objects.filter(name__icontains = search_query)
    
    profiles = Profile.objects.distinct().filter(
        Q(name__icontains = search_query)| ##__icontains is is not case sensitive -->> BEFORE THE __icontains the filed vlaue from the table is entered  -  in this case "name"
        Q(short_intro__icontains = search_query)|
        Q(bio__icontains = search_query)

        ) ##__icontains is not case sensitive -->> BEFORE THE __icontains the filed vlaue from the table is entered  -  in this case "name"
    print("Profiles matched:", profiles)
       
    return profiles , search_query





def paginateProfiles(request,profiles,results):
    page =   request.GET.get('page')
    # results =  3
    paginator  = Paginator(profiles,results)

    try:
        profiles  = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        profiles  = paginator.page(page)

    except EmptyPage:
        page = paginator.num_pages # get last pages
        profiles  = paginator.page(page)

    leftIndex = (int(page) - 1)
    if leftIndex < 1:
        leftIndex = 1

    rightIndex = (int(page) + 2)   
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1
    
    ##create a range of buttons you I want to see At A time
    custom_range = range(leftIndex,rightIndex)
    return custom_range , profiles