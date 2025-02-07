from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Portfolio, Asset, PortfolioAsset
from users.models import Profile,Message
from users.models import Group
from django.urls import reverse
import json
import pytest
from django.urls import reverse
from django.test import Client
