from django.test import TestCase

# Create your tests here.

from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Profile,Message
from .models import Group
from django.urls import reverse

class UserViewsTest(TestCase):



    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='password123'
        )
        self.profile, created = Profile.objects.get_or_create(user=self.user)
        self.manager_group, created = Group.objects.get_or_create(name='Manager')
        self.investor_group, created = Group.objects.get_or_create(name='Investor')

        
    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/index.html')

    def test_profiles_view(self):
        response = self.client.get(reverse('profiles'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profiles.html')
    
    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        
        
    def test_login_post_invalid_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username or Password is Incorrect')
    
    def test_register_user_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        
    def test_logout_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
    
    def test_edit_account_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('edit-account'))
        self.assertEqual(response.status_code, 200)
    
    def test_inbox_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('inbox'))
        self.assertEqual(response.status_code, 200)
    
    def test_create_message_view(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('create-message', args=[self.profile.id]), {
            'content': 'Hello!'
        })
        self.assertEqual(response.status_code, 200)  # Should redirect to profiles
    
    def test_delete_message_view(self):
        self.client.login(username='testuser', password='password123')

        # Create a message with all required fields
        message = Message.objects.create(
            sender=self.profile, 
            recipient=self.profile,  # Ensure recipient is set correctly
            name="Test Sender",
            email="test@example.com",
            subject="Test Subject",
            body="This is a test message."
        )

        # Delete the created message
        response = self.client.get(reverse('del_message', args=[str(message.id)]))
        
        # Verify the response and ensure the message is deleted
        # self.assertEqual(response.status_code, 200)  # Should redirect to inbox
        self.assertRedirects(response, reverse('inbox'))
        self.assertFalse(Message.objects.filter(id=message.id).exists())  # Ensure the message is deleted
