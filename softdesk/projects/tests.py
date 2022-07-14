from django.urls import reverse_lazy, reverse
from rest_framework.test import APITestCase
from projects.models import Projects, Issues
from django.contrib.auth.models import User


class DataTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="Tintin")
        cls.user2 = User.objects.create(username="Milou")
        cls.project1 = Projects.objects.create(title="Projet 1", author=cls.user1)
        cls.project2 = Projects.objects.create(title="Projet 2", author=cls.user2)

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


class TestProjects(DataTest):
    url_list = reverse_lazy('projects-list')
    # url_detail = reverse_lazy('projects-detail', args=[22])

    def test_list(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        expected = self.get_project_data(Projects.objects.all(), 'list')
        self.assertEqual(expected, response.json()['results'])

    def test_detail(self):
        response = self.client.get(reverse('projects-detail', kwargs={'pk': self.project1.pk}))
        self.assertEqual(response.status_code, 200)
        expected = self.get_project_data(Projects.objects.get(pk=self.project1.pk), 'retrieve')
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










