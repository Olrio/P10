from django.urls import reverse_lazy, reverse
from rest_framework.test import APITestCase
from projects.models import Projects, Issues, Contributors
from django.contrib.auth.models import User


class DataTest(APITestCase):

    def get_user_data(self, user):
        return [{
            'id': user.id,
            'username': user.username,
            'email': user.email
        }]

    def get_project_data(self, projects, action):
        if action == 'list':
            return [
                {
                    'id': project.id,
                    'title': project.title,
                    'description': project.description,
                    'type': project.type,
                } for project in projects
            ]
        elif action == 'retrieve':
            return {
                'id': projects.id,
                'title': projects.title,
                'description': projects.description,
                'type': projects.type,
                'issues': list(Issues.objects.filter(project_id=projects.id)),
            }

    def get_contributors_data(self, contributors, action):
        if action == 'list':
            return [
                {
                    'id': contributor.id,
                    'user': contributor.user.id,
                    'role': contributor.role,
                } for contributor in contributors
            ]
        elif action == 'retrieve':
            return {
                    'id': contributors.id,
                    'user': self.get_user_data(User.objects.get(id=contributors.user.id)),
                    'role': contributors.role,
            }

    def register(self, name, mail):
        url = reverse('signup')
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
    url_list = reverse('projects-list')

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
                                                         'type': 'BACK_END',
                                                         })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Projects.objects.count(), projects_count+1)

    def test_update(self):
        user = self.register('Tournesol', 'tryphon@herge.com')
        token = self.login(user)
        project_initial = Projects.objects.create(
            title="Projet de Thournysaule",
            author=user,
            description="Le dernier projet totalement fou de l'ami Tryphon !",
            type="BACK_END",
            id=3)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        response = self.client.put(reverse(
            'projects-detail', args=[project_initial.pk]), data={
            "author": project_initial.author,
            "description": project_initial.description,
            "type": project_initial.type,
            "title": "Projet de Tournesol"})
        project_final = Projects.objects.get(id=3)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(project_initial.title == project_final.title)

    def test_delete(self):
        # we create three different users (project_author, issue_author, issue_assignee)
        # one project and one issue
        user = self.register('Tournesol', 'tryphon@herge.com')
        user_author = self.register('Dupont', 'dupont@mail.com')
        user_assignee = self.register('Seraphin_Lampion', 'lampion@assur.com')
        token = self.login(user)
        project = Projects.objects.create(title="Projet de Tournesol", author=user)
        issue = Issues.objects.create(
            title="Probl??me de titre",
            desc="Il y a manifestement une grosse erreur dans le titre du projet",
            tag="erreur de script",
            project=project,
            author=user_author,
            assignee=user_assignee
        )
        # verify that project and issue are created
        self.assertTrue(Projects.objects.filter(title="Projet de Tournesol").exists())
        self.assertTrue(Issues.objects.filter(title="Probl??me de titre").exists())
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        response = self.client.delete(reverse('projects-detail', args=[project.pk]))
        self.assertEqual(response.status_code, 204)
        # verify that project and issue are deleted
        self.assertFalse(Projects.objects.filter(title="Projet de Tournesol").exists())
        self.assertFalse(Issues.objects.filter(title="Probl??me de titre").exists())


class TestContributors(DataTest):
    url_list = reverse('contributors-list', args=(1,))
    url_detail = reverse('contributors-detail', args=(1, 1))

    def test_list(self):
        user1 = self.register('Tournesol', 'tryphon@herge.com')
        user2 = self.register('Haddock', 'archibald@herge.com')
        token = self.login(user1)
        project1 = Projects.objects.create(title="Projet Test1", author=user1, id=1)
        project2 = Projects.objects.create(title="Projet Test2", author=user2, id=2)
        contributors1 = Contributors.objects.create(user=user1, project=project1, role='AUTHOR')
        contributors2 = Contributors.objects.create(user=user2, project=project2)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        expected = self.get_contributors_data(Contributors.objects.filter(project=project1), 'list')
        expected_false = self.get_contributors_data(Contributors.objects.filter(project=project2), 'list')
        self.assertEqual(expected, response.json()['results'])
        self.assertNotEqual(expected_false, response.json()['results'])

    def test_detail(self):
        user1 = self.register('Tournesol', 'tryphon@herge.com')
        user2 = self.register('Haddock', 'archibald@herge.com')
        token = self.login(user1)
        project1 = Projects.objects.create(title="Projet Test1", author=user1, id=1)
        project2 = Projects.objects.create(title="Projet Test2", author=user2, id=2)
        contributors1 = Contributors.objects.create(user=user1, project=project1, role='AUTHOR')
        contributors2 = Contributors.objects.create(user=user2, project=project2)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = self.get_contributors_data(Contributors.objects.get(pk=contributors1.pk), 'retrieve')
        expected_false = self.get_contributors_data(Contributors.objects.get(pk=contributors2.pk), 'retrieve')
        self.assertEqual(expected, response.json())
        self.assertNotEqual(expected_false, response.json())

    def test_create(self):
        user1 = self.register('Tournesol', 'tryphon@herge.com')
        user2 = self.register('Haddock', 'archibald@herge.com')
        token = self.login(user1)
        project1 = Projects.objects.create(title="Projet Test1", author=user1, id=1)
        contributors1 = Contributors.objects.create(user=user1, project=project1, role='AUTHOR')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        contributors_count = Contributors.objects.count()
        response = self.client.post(self.url_list, data={'user': user2.pk,
                                                         'role': 'CONTRIBUTOR',
                                                         })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Contributors.objects.count(), contributors_count+1)

    def test_update(self):
        user1 = self.register('Tournesol', 'tryphon@herge.com')
        user2 = self.register('Haddock', 'archibald@herge.com')
        token = self.login(user1)
        project1 = Projects.objects.create(title="Projet Test1", author=user1, id=1)
        contributors1 = Contributors.objects.create(user=user1, project=project1, role='AUTHOR')
        contributors2 = Contributors.objects.create(user=user2, project=project1, role='AUTHOR', id=22)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        contributors2_initial = Contributors.objects.get(id=22)
        response = self.client.put(reverse(
            'contributors-detail', args=(1, contributors2_initial.pk)), data={
            "user": user2.id,
            "role": 'CONTRIBUTOR',
        })
        contributors2_final = Contributors.objects.get(id=22)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(contributors2_initial.role == contributors2_final.role)

    def test_delete(self):
        user1 = self.register('Tournesol', 'tryphon@herge.com')
        user2 = self.register('Haddock', 'archibald@herge.com')
        project1 = Projects.objects.create(title="Projet Test1", author=user1, id=1)
        contributors1 = Contributors.objects.create(user=user1, project=project1, role='AUTHOR')
        contributors2 = Contributors.objects.create(user=user2, project=project1, role='AUTHOR', id=22)
        token = self.login(user1)
        # verify that contributor 'Haddock / Projet Test1' is created'
        self.assertTrue(Contributors.objects.filter(id=22).exists())
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        response = self.client.delete(reverse('contributors-detail', args=(1, contributors2.pk)))
        self.assertEqual(response.status_code, 204)
        # verify that contributor 'Haddock / Projet Test1' is deleted
        self.assertFalse(Contributors.objects.filter(id=22).exists())










