# coding: utf-8
from django.contrib.auth.models import User  # NOQA
from django.test import Client, TestCase  # NOQA
from django.urls import reverse  # NOQA


class HomeViewTests(TestCase):
    pass    # TODO fix
    # def test_not_authenticated(self):
    #     client = Client()
    #     client.logout()
    #     response = client.get(reverse("app:home"))
    #     self.assertEquals(response.status_code, 200)

    # def test_authenticated(self):
    #     client = Client()
    #     user = User()
    #     user.username = "test_user"
    #     user.save()
    #     client.force_login(user)
    #     response = client.get(reverse("app:home"))
    #     self.assertEquals(response.status_code, 200)
