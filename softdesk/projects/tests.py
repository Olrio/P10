from django.urls import reverse
from rest_framework.test import APITestCase
from projects.models import Projects, Issues, Contributors, Comments
from authentication.models import User


class DataTest(APITestCase):
    @staticmethod
    def format_datetime(value):
        return value.strftime("%Y/%m/%d %H:%M")

    @staticmethod
    def get_user_data(user):
        return [{"id": user.id,
                 "username": user.username,
                 "email": user.email}]

    @staticmethod
    def get_project_data(projects, action):
        if action == "list":
            return [
                {
                    "id": project.id,
                    "title": project.title,
                    "description": project.description,
                    "type": project.type,
                    "author_user_id": project.author_user_id.id,
                }
                for project in projects
            ]
        elif action == "retrieve":
            return {
                "id": projects.id,
                "title": projects.title,
                "description": projects.description,
                "type": projects.type,
                "issues": list(Issues.objects.filter(project_id=projects.id)),
            }

    def get_contributors_data(self, contributors, action):
        if action == "list":
            return [
                {
                    "id": contributor.id,
                    "user": contributor.user.id,
                    "role": contributor.role,
                }
                for contributor in contributors
            ]
        elif action == "retrieve":
            return {
                "id": contributors.id,
                "user": self.get_user_data(
                    User.objects.get(id=contributors.user.id)),
                "role": contributors.role,
            }

    def get_issues_data(self, issues, action):
        if action == "list":
            return [
                {
                    "id": issue.id,
                    "title": issue.title,
                    "desc": issue.desc,
                    "assignee_user_id": issue.assignee_user_id.id,
                    "author_user_id": issue.author_user_id.id,
                    "tag": issue.tag,
                    "priority": issue.priority,
                    "status": issue.status,
                    "created_time": self.format_datetime(issue.created_time),
                }
                for issue in issues
            ]
        elif action == "retrieve":
            return {
                "id": issues.id,
                "title": issues.title,
                "desc": issues.desc,
                "author_user_id": self.get_user_data(
                    User.objects.get(id=issues.author_user_id.id)
                ),
                "project_id": issues.project_id.id,
                "assignee_user_id": issues.assignee_user_id.id,
            }

    def get_comments_data(self, comments, action):
        if action == "list":
            return [
                {
                    "id": comment.id,
                    "description": comment.description,
                    "issue_id": comment.issue_id.id,
                    "author_user_id": comment.author_user_id.id,
                    "created_time": self.format_datetime(comment.created_time),
                }
                for comment in comments
            ]
        elif action == "retrieve":
            return {
                "id": comments.id,
                "description": comments.description,
                "issue_id": comments.issue_id.id,
                "author_user_id": comments.author_user_id.id,
                "created_time": self.format_datetime(comments.created_time),
            }

    def register(self, name, mail):
        url = reverse("signup")
        resp = self.client.post(
            url,
            {
                "username": name,
                "password": "secret1234",
                "password2": "secret1234",
                "email": mail,
            },
            format="json",
        )
        return User.objects.get(username=resp.json()["username"])

    def login(self, user):
        url = reverse("login")
        resp = self.client.post(
            url,
            {
                "username": user.username,
                "password": "secret1234",
            },
            format="json",
        )
        # verify that given a valid username and
        # password of a user, request returns two tokens
        self.assertTrue(resp.json()["refresh"] is not None)
        self.assertTrue(resp.json()["access"] is not None)
        return resp.json()


class TestProjects(DataTest):
    url_list = reverse("projects-list")

    def test_list(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        token = self.login(user1)
        project1 = Projects.objects.create(
            title="Projet Test1",
            author_user_id=user1,
            id=1
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        project2 = Projects.objects.create(
            title="Projet Test2",
            author_user_id=user2,
            id=2
        )
        Contributors.objects.create(
            user=user2,
            project=project2,
            role="AUTHOR")
        project3 = Projects.objects.create(
            title="Projet Test3",
            author_user_id=user2,
            id=3
        )
        Contributors.objects.create(
            user=user2,
            project=project3,
            role="AUTHOR")
        Contributors.objects.create(
            user=user1,
            project=project3,
            role="CONTRIBUTOR")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        # user1 is author of project1 and contributor to project3
        # user1 can access to project1 and project3 in view list
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        expected = self.get_project_data(
            Projects.objects.filter(contributors__user=user1), "list"
        )
        self.assertEqual(expected, response.json()["results"])

    def test_detail(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        token = self.login(user1)
        project1 = Projects.objects.create(
            title="Projet Test1",
            author_user_id=user1,
            id=1
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        project2 = Projects.objects.create(
            title="Projet Test2",
            author_user_id=user2,
            id=2
        )
        Contributors.objects.create(
            user=user2,
            project=project2,
            role="AUTHOR")
        project3 = Projects.objects.create(
            title="Projet Test3", author_user_id=user2, id=3
        )
        Contributors.objects.create(
            user=user2,
            project=project3,
            role="AUTHOR")
        Contributors.objects.create(
            user=user1,
            project=project3,
            role="CONTRIBUTOR")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        # user1 is author of project1 and contributor to project3
        # user1 can only access to project1 in view detail
        response1 = self.client.get(
            reverse("projects-detail", kwargs={"pk": project1.pk})
        )
        response2 = self.client.get(
            reverse("projects-detail", kwargs={"pk": project3.pk})
        )
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 403)
        expected1 = self.get_project_data(
            Projects.objects.get(pk=project1.pk), "retrieve"
        )
        expected2 = self.get_project_data(
            Projects.objects.get(pk=project3.pk), "retrieve"
        )
        self.assertEqual(expected1, response1.json())
        self.assertNotEqual(expected2, response2.json())

    def test_create(self):
        user = self.register("Tournesol", "tryphon@herge.com")
        token = self.login(user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        projects_count = Projects.objects.count()
        response = self.client.post(
            self.url_list,
            data={
                "title": "Nouveau projet",
                "author_user_id": user.id,
                "description": "RAS",
                "type": "BACK_END",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Projects.objects.count(), projects_count + 1)

    def test_update(self):
        user = self.register("Tournesol", "tryphon@herge.com")
        token = self.login(user)
        project_initial = Projects.objects.create(
            title="Projet de Thournysaule",
            author_user_id=user,
            description="Le dernier projet totalement fou de l'ami Tryphon !",
            type="BACK_END",
            id=3,
        )
        Contributors.objects.create(user=user, project=project_initial)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.put(
            reverse("projects-detail", args=[project_initial.pk]),
            data={
                "author_user_id": project_initial.author_user_id.id,
                "description": project_initial.description,
                "type": project_initial.type,
                "title": "Projet de Tournesol",
            },
        )
        project_final = Projects.objects.get(id=3)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(project_initial.title == project_final.title)

    def test_delete(self):
        # we create three different users
        # (project_author, issue_author, issue_assignee)
        # one project and one issue
        user = self.register("Tournesol", "tryphon@herge.com")
        user_author = self.register("Dupont", "dupont@mail.com")
        user_assignee = self.register("Seraphin_Lampion", "lampion@assur.com")
        token = self.login(user)
        project = Projects.objects.create(
            title="Projet de Tournesol", author_user_id=user
        )
        Contributors.objects.create(user=user, project=project)
        Issues.objects.create(
            title="Problème de titre",
            desc="Il y a manifestement une grosse erreur "
                 "dans le titre du projet",
            tag="erreur de script",
            project_id=project,
            author_user_id=user_author,
            assignee_user_id=user_assignee,
        )
        # verify that project and issue are created
        self.assertTrue(Projects.objects.filter(
            title="Projet de Tournesol").exists())
        self.assertTrue(Issues.objects.filter(
            title="Problème de titre").exists())
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(
            reverse("projects-detail", args=[project.pk]))
        self.assertEqual(response.status_code, 204)
        # verify that project and issue are deleted
        self.assertFalse(Projects.objects.filter(
            title="Projet de Tournesol").exists())
        self.assertFalse(Issues.objects.filter(
            title="Problème de titre").exists())


class TestContributors(DataTest):
    url_list = reverse("contributors-list", args=(1,))
    url_detail = reverse("contributors-detail", args=(1, 1))

    def test_list(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        token = self.login(user1)
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        project2 = Projects.objects.create(
            title="Projet Test2", author_user_id=user2, id=2
        )
        Projects.objects.create(
            title="Projet Test3",
            author_user_id=user1,
            id=3)
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        Contributors.objects.create(
            user=user2,
            project=project2,
            role="AUTHOR")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        expected = self.get_contributors_data(
            Contributors.objects.filter(project=project1), "list"
        )
        expected_false = self.get_contributors_data(
            Contributors.objects.filter(project=project2), "list"
        )
        self.assertEqual(expected, response.json()["results"])
        self.assertNotEqual(expected_false, response.json()["results"])

    def test_create(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        token = self.login(user1)
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        contributors_count = Contributors.objects.count()
        response = self.client.post(
            self.url_list,
            data={
                "user": user2.pk,
                "role": "CONTRIBUTOR",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Contributors.objects.count(), contributors_count + 1)

    def test_delete(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        contributors2 = Contributors.objects.create(
            user=user2,
            project=project1,
            role="AUTHOR",
            id=22
        )
        token = self.login(user1)
        # verify that contributor 'Haddock / Projet Test1' is created
        self.assertTrue(Contributors.objects.filter(id=22).exists())
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(
            reverse("contributors-detail", args=(1, contributors2.pk))
        )
        self.assertEqual(response.status_code, 204)
        # verify that contributor 'Haddock / Projet Test1' is deleted
        self.assertFalse(Contributors.objects.filter(id=22).exists())


class TestIssues(DataTest):
    url_list = reverse("issues-list", args=(1,))
    url_detail = reverse("issues-detail", args=(1, 1))

    def test_list(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        token = self.login(user1)
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        project2 = Projects.objects.create(
            title="Projet Test2", author_user_id=user2, id=2
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        Contributors.objects.create(
            user=user2,
            project=project2)
        Issues.objects.create(
            title="Big Bug 1 ?",
            author_user_id=user1,
            id=1,
            assignee_user_id=user2,
            project_id=project1,
        )
        Issues.objects.create(
            title="Big Bug 2 ?",
            author_user_id=user1,
            id=2,
            assignee_user_id=user2,
            project_id=project2,
        )
        Issues.objects.create(
            title="Big Bug 3 ?",
            author_user_id=user2,
            id=3,
            assignee_user_id=user2,
            project_id=project1,
        )
        Issues.objects.create(
            title="Big Bug 4 ?",
            author_user_id=user2,
            id=4,
            assignee_user_id=user2,
            project_id=project2,
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        expected = self.get_issues_data(
            Issues.objects.filter(project_id=project1), "list"
        )
        expected_false = self.get_issues_data(
            Issues.objects.filter(project_id=project2), "list"
        )
        self.assertEqual(expected, response.json()["results"])
        self.assertNotEqual(expected_false, response.json()["results"])

    def test_detail(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        token = self.login(user1)
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        project2 = Projects.objects.create(
            title="Projet Test2", author_user_id=user2, id=2
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        Contributors.objects.create(
            user=user2,
            project=project2)
        issue1 = Issues.objects.create(
            title="Big Bug 1 ?",
            author_user_id=user1,
            id=1,
            assignee_user_id=user2,
            project_id=project1,
        )
        issue2 = Issues.objects.create(
            title="Big Bug 2 ?",
            author_user_id=user2,
            id=2,
            assignee_user_id=user2,
            project_id=project2,
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = self.get_issues_data(
            Issues.objects.get(pk=issue1.pk), "retrieve")
        expected_false = self.get_issues_data(
            Issues.objects.get(pk=issue2.pk), "retrieve"
        )
        self.assertEqual(expected, response.json())
        self.assertNotEqual(expected_false, response.json())

    def test_create(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        token = self.login(user1)
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        Issues.objects.create(
            title="Big Bug 1 ?",
            author_user_id=user1,
            id=1,
            assignee_user_id=user2,
            project_id=project1,
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        issues_count = Issues.objects.count()
        response = self.client.post(
            self.url_list,
            data={
                "title": "Big Bug 2",
                "desc": "Description du problème",
                "author_user_id": user2,
                "id": 2,
                "assignne_user_id": user2,
                "project_id": project1,
                "tag": "BUG",
                "priority": "MEDIUM",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Issues.objects.count(), issues_count + 1)

    def test_update(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        token = self.login(user1)
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        Issues.objects.create(
            title="Big Bug 1 ?",
            author_user_id=user1,
            id=1,
            assignee_user_id=user2,
            project_id=project1,
            tag="BUG",
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        issue1_initial = Issues.objects.get(id=1)
        response = self.client.put(
            reverse("issues-detail", args=(1, issue1_initial.pk)),
            data={
                "title": "New title",
                "desc": "Description du problème",
                "tag": "BUG",
                "priority": "MEDIUM",
            },
        )
        issue1_final = Issues.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(issue1_initial.title, issue1_final.title)

    def test_delete(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        issue1 = Issues.objects.create(
            title="Big Bug 1 ?",
            author_user_id=user1,
            id=1,
            assignee_user_id=user2,
            project_id=project1,
        )
        token = self.login(user1)
        self.assertTrue(Issues.objects.filter(id=1).exists())
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(
            reverse("issues-detail", args=(1, issue1.pk)))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Issues.objects.filter(id=1).exists())


class TestComments(DataTest):
    url_list = reverse("comments-list", args=(1, 1))
    url_detail = reverse("comments-detail", args=(1, 1, 1))

    def test_list(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        token = self.login(user1)
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        project2 = Projects.objects.create(
            title="Projet Test2", author_user_id=user2, id=2
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        issue1 = Issues.objects.create(
            title="Big Bug 1 ?",
            author_user_id=user1,
            id=1,
            assignee_user_id=user2,
            project_id=project1,
        )
        issue2 = Issues.objects.create(
            title="Big Bug 2 ?",
            author_user_id=user1,
            id=2,
            assignee_user_id=user2,
            project_id=project2,
        )
        Comments.objects.create(
            description="Comment 1", issue_id=issue1, author_user_id=user1
        )
        Comments.objects.create(
            description="Comment 2", issue_id=issue1, author_user_id=user1
        )
        Comments.objects.create(
            description="Comment 3", issue_id=issue1, author_user_id=user2
        )
        Comments.objects.create(
            description="Comment 4", issue_id=issue2, author_user_id=user1
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, 200)
        expected = self.get_comments_data(
            Comments.objects.filter(issue_id=issue1), "list"
        )
        expected_false = self.get_comments_data(
            Comments.objects.filter(issue_id=issue2), "list"
        )
        self.assertEqual(expected, response.json()["results"])
        self.assertNotEqual(expected_false, response.json()["results"])

    def test_detail(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        token = self.login(user1)
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        project2 = Projects.objects.create(
            title="Projet Test2", author_user_id=user2, id=2
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        issue1 = Issues.objects.create(
            title="Big Bug 1 ?",
            author_user_id=user1,
            id=1,
            assignee_user_id=user2,
            project_id=project1,
        )
        issue2 = Issues.objects.create(
            title="Big Bug 2 ?",
            author_user_id=user2,
            id=2,
            assignee_user_id=user2,
            project_id=project2,
        )
        comment1 = Comments.objects.create(
            description="Comment 1", issue_id=issue1, author_user_id=user1
        )
        Comments.objects.create(
            description="Comment 2", issue_id=issue1, author_user_id=user1
        )
        comment3 = Comments.objects.create(
            description="Comment 3", issue_id=issue1, author_user_id=user2
        )
        Comments.objects.create(
            description="Comment 4", issue_id=issue2, author_user_id=user1
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, 200)
        expected = self.get_comments_data(
            Comments.objects.get(pk=comment1.pk), "retrieve"
        )
        expected_false = self.get_comments_data(
            Comments.objects.get(pk=comment3.pk), "retrieve"
        )
        self.assertEqual(expected, response.json())
        self.assertNotEqual(expected_false, response.json())

    def test_create(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        token = self.login(user1)
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        issue1 = Issues.objects.create(
            title="Big Bug 1 ?",
            author_user_id=user1,
            id=1,
            assignee_user_id=user2,
            project_id=project1,
        )
        Comments.objects.create(
            description="Comment 1", issue_id=issue1, author_user_id=user1
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        comments_count = Comments.objects.count()
        response = self.client.post(
            self.url_list,
            data={
                "description": "My new comment",
                "author_user_id": user1,
                "issue_id": issue1,
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comments.objects.count(), comments_count + 1)

    def test_update(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        token = self.login(user1)
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        issue1 = Issues.objects.create(
            title="Big Bug 1 ?",
            author_user_id=user1,
            id=1,
            assignee_user_id=user2,
            project_id=project1,
            tag="BUG",
        )
        Comments.objects.create(
            description="Commenture",
            issue_id=issue1,
            author_user_id=user1,
            id=1
        )
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        comment1_initial = Comments.objects.get(id=1)
        response = self.client.put(
            reverse("comments-detail", args=(1, 1, comment1_initial.pk)),
            data={
                "description": "Commentaire",
            },
        )
        comment1_final = Comments.objects.get(id=1)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(
            comment1_initial.description, comment1_final.description)

    def test_delete(self):
        user1 = self.register("Tournesol", "tryphon@herge.com")
        user2 = self.register("Haddock", "archibald@herge.com")
        project1 = Projects.objects.create(
            title="Projet Test1", author_user_id=user1, id=1
        )
        Contributors.objects.create(
            user=user1,
            project=project1,
            role="AUTHOR")
        issue1 = Issues.objects.create(
            title="Big Bug 1 ?",
            author_user_id=user1,
            id=1,
            assignee_user_id=user2,
            project_id=project1,
        )
        comment1 = Comments.objects.create(
            description="Commenture",
            issue_id=issue1,
            author_user_id=user1,
            id=1
        )
        token = self.login(user1)
        self.assertTrue(Comments.objects.filter(id=1).exists())
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token["access"])
        response = self.client.delete(
            reverse("comments-detail", args=(1, 1, comment1.pk))
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Comments.objects.filter(id=1).exists())
