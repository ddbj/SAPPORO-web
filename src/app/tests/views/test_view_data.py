# coding: utf-8
from django.contrib.auth.models import User  # NOQA
from django.test import Client, TestCase  # NOQA
from django.urls import reverse  # NOQA


class DataListViewTests(TestCase):
    pass    # TODO fix
    # def test_not_authenticated(self):
    #     client = Client()
    #     client.logout()
    #     response = client.get(reverse("app:data_list"))
    #     self.assertEquals(response.status_code, 403)

    # def test_authenticated(self):
    #     client = Client()
    #     user = User()
    #     user.username = "test_user"
    #     user.save()
    #     client.force_login(user)
    #     response = client.get(reverse("app:data_list"))
    #     self.assertEquals(response.status_code, 200)


class DataDetailViewTests(TestCase):
    pass    # TODO fix
    # def test_not_authenticated(self):
    #     client = Client()
    #     client.logout()
    #     response = client.get(reverse("app:data_detail", kwargs={
    #         "data_unique_id": "data_unique_id"}))
    #     self.assertEquals(response.status_code, 403)

    # def test_authenticated(self):
    #     client = Client()
    #     user = User()
    #     user.username = "test_user"
    #     user.save()
    #     client.force_login(user)
    #     response = client.get(reverse("app:data_detail", kwargs={
    #         "data_unique_id": "data_unique_id"}))
    #     self.assertEquals(response.status_code, 200)
