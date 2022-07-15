from django.urls import reverse_lazy, reverse
from rest_framework.test import APITestCase
from projects.models import Projects, Issues
from django.contrib.auth.models import User


class DataTest(APITestCase):

    def get_project_data(self, projects, action):
        if action == 'list':
            return [
                {
                    'id': project.id,
                    'title': project.title,
                    'author': project.author.id,
                } for project in projects
            ]
        elif action == 'retrieve':
            return {
                'id': projects.id,
                'title': projects.title,
                'author': projects.author.id,
                'issues': list(Issues.objects.filter(project_id=projects.id)),
            }

    def register(self, name, mail):
        url = reverse('register')
        resp = self.client.post(url, {
            'username': name,
            'password': 'secret1234',
            'password2': 'secret1234',
            'email': mail
        }, format='json')
        return User.objects.get(username=resp.json()['username'])

    def login(self, user):
        url = reverse('login')
        resp = self.client.post(url, {
            'username': user.username,
            'password': 'secret1234',
        }, format='json')
        # verify that given a valid username and password of a user, request returns two tokens
        self.assertTrue(resp.json()['refresh'] is not None)
        self.assertTrue(resp.json()['access'] is not None)
        return resp.json()


class TestProjects(DataTest):
    url_list = reverse_lazy('projects-list')

    def test_list(self):
        user1 = self.register('Tournesol', 'tryphon@herge.com')
        user2 = self.register('Haddock', 'archibald@herge.com')
        token = self.login(user2)
        project1 = Projects.objects.create(title="Projet Test1", author=user1, id=1)
        project2 = Projects.objects.create(title="Projet Test2", author=user1, id=2)
        project3 = Projects.objects.create(title="Projet Test3", author=user2, id=3)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        expected = self.get_project_data(Projects.objects.filter(author=user2.id), 'list')
        self.assertEqual(expected, response.json()['results'])

    def test_detail(self):
        user = self.register('Tournesol', 'tryphon@herge.com')
        token = self.login(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        project = Projects.objects.create(title="Projet Test", author=user, id=3)
        response = self.client.get(reverse('projects-detail', kwargs={'pk': project.pk}))
        self.assertEqual(response.status_code, 200)
        expected = self.get_project_data(Projects.objects.get(pk=project.pk), 'retrieve')
        self.assertEqual(expected, response.json())

    def test_create(self):
        user = self.register('Tournesol', 'tryphon@herge.com')
        token = self.login(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        projects_count = Projects.objects.count()
        response = self.client.post(self.url_list, data={'title': 'Nouveau projet',
                                                         'author': user.id,
                                                         'description': 'RAS',
                                                         'type': 'Software',
                                                         })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Projects.objects.count(), projects_count+1)

    def test_update(self):
        user = self.register('Tournesol', 'tryphon@herge.com')
        token = self.login(user)
        project_initial = Projects.objects.create(title="Projet de Thournysaule", author=user, id=3)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        response = self.client.patch(reverse(
            'projects-detail', args=[project_initial.pk]), data={"title": "Projet de Tournesol"})
        project_final = Projects.objects.get(id=3)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(project_initial.title == project_final.title)

    def test_delete(self):
        user = self.register('Tournesol', 'tryphon@herge.com')
        token = self.login(user)
        project = Projects.objects.create(title="Projet de Tournesol", author=user)
        self.assertTrue(Projects.objects.filter(title="Projet de Tournesol").exists())
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        response = self.client.delete(reverse('projects-detail', args=[project.pk]))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Projects.objects.filter(title="Projet de Tournesol").exists())










