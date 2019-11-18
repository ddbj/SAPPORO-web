# coding: utf-8
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class WorkflowListViewTests(TestCase):
    # def test_not_authenticated(self):
    #     client = Client()
    #     client.logout()
    #     response = client.get(reverse("app:workflow_list"))
    #     self.assertEquals(response.status_code, 403)

    def test_authenticated(self):
        client = Client()
        user = User()
        user.username = "test_user"
        user.save()
        client.force_login(user)
        response = client.get(reverse("app:workflow_list"))
        self.assertEquals(response.status_code, 200)


class WorkflowDetailViewTests(TestCase):
    pass    # TODO fix
    # def test_not_authenticated(self):
    #     client = Client()
    #     client.logout()
    #     response = client.get(reverse("app:workflow_detail", kwargs={
    #         "workflow_unique_id": "workflow_unique_id"}))
    #     self.assertEquals(response.status_code, 403)

    # def test_authenticated(self):
    #     client = Client()
    #     user = User()
    #     user.username = "test_user"
    #     user.save()
    #     client.force_login(user)
    #     response = client.get(reverse("app:workflow_detail", kwargs={
    #         "workflow_unique_id": "workflow_unique_id"}))
    #     self.assertEquals(response.status_code, 200)
