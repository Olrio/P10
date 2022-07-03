from django.test import TestCase
from django.urls import reverse_lazy
from rest_framework.test import APITestCase
from projects.models import Projects
from django.contrib.auth.models import User


class DataTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="Tintin", pk=22)
        cls.user2 = User.objects.create(username="Milou", pk=23)
        cls.project1 = Projects.objects.create(title="Projet 1", author=cls.user1, pk=22)
        cls.project2 = Projects.objects.create(title="Projet 2", author=cls.user2, pk=23)


class TestProjects(DataTest):
    url_list = reverse_lazy('projects-list')
    url_detail = reverse_lazy('projects-detail', args=[22])

    def test_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        expected = [
            {
                'id': self.project1.pk,
                'title': self.project1.title,
                'author': self.user1.id,
            },
            {
                'id': self.project2.pk,
                'title': self.project2.title,
                'author': self.user2.id,
            }
        ]
        self.assertEqual(expected, response.json())

    def test_detail(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = {
            'id': self.project1.pk,
            'title': self.project1.title,
            'author': self.user1.id,
        }
        self.assertEqual(expected, response.json())

    def test_create(self):
        self.project1.delete()
        self.project2.delete()
        self.assertFalse(Projects.objects.exists())
        response = self.client.post(self.url_list, data={'title': 'Nouveau projet'})
        self.assertEqual(response.status_code, 405)
        self.assertFalse(Projects.objects.exists())

    def test_update(self):
        response = self.client.patch(self.url_list, data={"id": 22, "title": "Test project 2222"})
        self.assertEqual(response.status_code, 405)

    def test_delete(self):
        response = self.client.delete(self.url_list)
        self.assertEqual(response.status_code, 405)


class TestUser(DataTest):
    url_list = reverse_lazy('user-list')
    url_detail = reverse_lazy('user-detail', args=[22])

    def test_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        expected = [
            {
                'id': self.user1.pk,
                'username': self.user1.username,
            },
            {
                'id': self.user2.pk,
                'username': self.user2.username,
            }
        ]
        self.assertEqual(expected, response.json())

    def test_detail(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = {
            'id': self.user1.pk,
            'username': self.user1.username,
        }
        self.assertEqual(expected, response.json())

    def test_create(self):
        self.user1.delete()
        self.user2.delete()
        self.assertFalse(User.objects.exists())
        response = self.client.post(self.url_list, data={'username': 'Nouvel_utilisateur', 'password': 'toto1234'})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.exists())

    def test_update_list(self):
        response = self.client.patch(self.url_list, data={"username": "Utilisateur_2222"})
        self.assertEqual(response.status_code, 405)

    def test_update_detail(self):
        response = self.client.patch(self.url_detail, data={"username": "Utilisateur_2222"})
        self.assertEqual(response.status_code, 200)

    def test_delete_list(self):
        response = self.client.delete(self.url_list)
        self.assertEqual(response.status_code, 405)

    def test_delete_detail(self):
        self.assertTrue(User.objects.filter(pk=22).exists())
        self.client.delete(self.url_detail)
        self.assertFalse(User.objects.filter(pk=22).exists())







