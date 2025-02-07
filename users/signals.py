from django.db.models.signals import post_save ,  post_delete
# using signals with decorators
from django.dispatch import receiver
from .models import Profile , User ,  Group
from django.core.mail import send_mail , EmailMultiAlternatives
from django.conf import settings

@receiver(post_save,sender = User)
def createProfile(sender,instance,created, **kwargs):   ### create only exists if the Object is created in that instance
    print('Create Profile Signal triggered  . . . ')
    if created:                 # User is the Sender  -  so this checks if the User is created
        user = instance         #  
        profile = Profile.objects.create(
            user=user,
            username = user.username,
            email = user.email,
            name = f"{user.first_name} {user.last_name}"  , 
        )

        subject = 'Welcome to the Website'
        message = "Create a portfolio -  Hope you enjoy"

        
        subject = f"{profile.name} , Welcome to Portfolio Manager!"
        from_email = settings.EMAIL_HOST_USER
        to_email = [profile.email]
        text_content = "Create a portfolio -  Hope you enjoy."
        html_content = """
            <html>
                <body>
                    <h2 style="color: #4CAF50;">Welcome to Our Service!</h2>
                    <p>Create a portfolio -  Hope you enjoy. 💰💰💰💰</p>
                </body>
            </html>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()



@receiver(post_save, sender = Profile)
def updateUser(sender, instance, created , **kwargs):
    profile = instance
    user = profile.user
    if created == False:  ##THIS IS INCLUDED TO PREVENT THE SIGNALS TRIGGERING EACH OTHER 
        user.first_name = profile.name
        user.username = profile.username
        user.email = profile.email

        user.save()


@receiver(post_delete, sender = Profile)
def deleteUser(sender,instance, **kwargs):
    try:
        user = instance.user   ##   One to One   - - user.Profile is short hand for gettign the user from the Profile instance
        user.delete()
        print('Deleting user...')
    except:
        pass


