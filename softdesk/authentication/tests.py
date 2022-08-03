from django.urls import reverse_lazy, reverse
from rest_framework.test import APITestCase
from projects.models import Projects
from authentication.models import User


class DataTest(APITestCase):

    user1 = None
    user2 = None

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="Tintin", pk=22)
        cls.user2 = User.objects.create(username="Milou", pk=23)
        cls.project1 = Projects.objects.create(
            title="Projet 1", author_user_id=cls.user1, pk=22
        )
        cls.project2 = Projects.objects.create(
            title="Projet 2", author_user_id=cls.user2, pk=23
        )

    @staticmethod
    def get_user_data(users, action):
        if action == "list":
            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
                for user in users
            ]
        elif action == "retrieve":
            return {
                "id": users.id,
                "username": users.username,
                "email": users.email,
            }


class TestUser(DataTest):
    url_list = reverse_lazy("user-list")
    url_detail = reverse_lazy("user-detail", args=[22])

    def test_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        expected = self.get_user_data(User.objects.all(), "list")
        self.assertEqual(expected, response.json()["results"])

    def test_detail(self):
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = self.get_user_data(
            User.objects.get(pk=self.user1.pk), "retrieve")
        self.assertEqual(expected, response.json())

    def test_update_list(self):
        response = self.client.patch(
            self.url_list, data={"username": "Utilisateur_2222"}
        )
        self.assertEqual(response.status_code, 405)

    def test_update_detail(self):
        response = self.client.patch(
            self.url_detail, data={"username": "Utilisateur_2222"}
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_list(self):
        response = self.client.delete(self.url_list)
        self.assertEqual(response.status_code, 405)

    def test_delete_detail(self):
        self.assertTrue(User.objects.filter(pk=22).exists())
        self.client.delete(self.url_detail)
        self.assertFalse(User.objects.filter(pk=22).exists())

    def test_register(self):
        count_user = User.objects.all().count()
        url = reverse("signup")
        resp = self.client.post(
            url,
            {
                "username": "UserToto",
                "password": "toto1234",
                "password2": "toto1234",
                "email": "toto2222@toto.com",
            },
            format="json",
        )
        # validation of registration process
        self.assertEqual(resp.status_code, 201)
        # verify there's one more instance of User
        self.assertEqual(User.objects.all().count(), count_user + 1)
        return User.objects.get(username=resp.json()["username"])

    def test_register_too_short_username(self):
        response = self.client.post(reverse("signup"), data={"username": "Jo"})
        self.assertEqual(response.status_code, 400)

    def test_login(self):
        self.test_register()
        url = reverse("login")
        resp = self.client.post(
            url,
            {
                "username": "UserToto",
                "password": "toto1234",
            },
            format="json",
        )
        # verify that given a valid username and password
        # of a user, request returns two tokens
        self.assertTrue(resp.json()["refresh"] is not None)
        self.assertTrue(resp.json()["access"] is not None)
        return resp.json()
