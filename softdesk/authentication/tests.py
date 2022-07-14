from django.urls import reverse_lazy, reverse
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

    def get_user_data(self, users, action):
        if action == 'list':
            return [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                } for user in users
            ]
        elif action == 'retrieve':
            return {
                'id': users.id,
                'username': users.username,
                'email': users.email,
            }


class TestUser(DataTest):
    url_list = reverse_lazy('user-list')
    url_detail = reverse_lazy('user-detail', args=[22])

    def test_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        expected = self.get_user_data(User.objects.all(), 'list')
        self.assertEqual(expected, response.json()['results'])

    def test_detail(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = self.get_user_data(User.objects.get(pk=self.user1.pk), 'retrieve')
        self.assertEqual(expected, response.json())

    def test_create(self):
        self.user1.delete()
        self.user2.delete()
        self.assertFalse(User.objects.exists())
        response = self.client.post(self.url_list, data={'username': 'Nouvel_utilisateur', 'password': 'toto1234'})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.exists())

    def test_register_too_short_username(self):
        response = self.client.post(reverse('register'), data={'username': 'Jo'})
        self.assertEqual(response.status_code, 400)

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
