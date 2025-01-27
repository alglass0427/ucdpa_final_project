from .models import Message

def inbox_count(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(recipient=request.user.profile, is_read=False).count()
        print ("MESSAGES",count)
        return {'inbox_count': count}
    return {'inbox_count': 0}