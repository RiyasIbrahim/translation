from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import datetime
from .serializers import ProjectSerializer
from .models import Project, Sentence
from .views import project_view, single_project_view, sentences_view
from .utils import getSummaryForTitles

# Create your tests here.


class UtilTest(TestCase):

    def testSummaryToPara(self):
        summary = getSummaryForTitles("America")
        self.assertEqual(33, len(summary))

class ViewTest(APITestCase):
    
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='password'
        )
        self.manager = User.objects.create_user(
            username='manager',
            password='password'
        )
        self.manager_group = Group.objects.create(name='Manager')
        self.manager.groups.add(self.manager_group)
        self.annotator = User.objects.create_user(
            username='annotator',
            password='password'
        )
        self.annotator_group = Group.objects.create(name='Annotator')
        self.annotator.groups.add(self.annotator_group)
        self.project = Project.objects.create(
            article_title='India',
            target_language='te',
            created_by=self.manager,
            project_id='te_india',
            created_on=datetime.now(),
            assigned_to=self.annotator.id
        )
        self.project_serializer = ProjectSerializer(instance=self.project)
    
    def tearDown(self):
        User.objects.all().delete()
        Group.objects.all().delete()
        Project.objects.all().delete()
        Sentence.objects.all().delete()


    def test_superuser_can_view_all_projects(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse(project_view)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Project.objects.count())
        self.assertEqual(response.data, [self.project_serializer.data])

    def test_manager_can_view_own_projects(self):
        self.client.force_authenticate(user=self.manager)
        url = reverse(project_view)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Project.objects.filter(created_by=self.manager).count())
        self.assertEqual(response.data, [self.project_serializer.data])

    def test_annotator_can_view_assigned_projects(self):
        self.client.force_authenticate(user=self.annotator)
        url = reverse(project_view)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Project.objects.filter(assigned_to=self.annotator.id).count())
        self.assertEqual(response.data, [self.project_serializer.data])

    def test_unauthenticated_user_cannot_view_projects(self):
        url = reverse(project_view)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_view_projects(self):
        regular_user = User.objects.create_user(
            username='regular',
            password='password'
        )
        self.client.force_authenticate(user=regular_user)
        url = reverse(project_view)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_can_create_project(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse(project_view)
        data = {
            'article_title': 'India',
            'target_language': 'ta',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(response.data['article_title'], data['article_title'])
        self.assertEqual(response.data['target_language'], data['target_language'])
        self.assertEqual(response.data['created_by'], self.superuser.id)

    def test_get_project_success(self):
        url = reverse(single_project_view, args=[self.project.project_id])
        self.client.force_authenticate(user=self.manager)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['article_title'], self.project.article_title)

    def test_get_project_failure(self):
        project = Project.objects.create(article_title='India', target_language='ta', project_id='ta_india', created_by=self.manager, created_on=datetime.now())
        url = reverse(single_project_view, args=[project.project_id])
        self.client.force_authenticate(user=self.annotator)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_project_success(self):
        project = Project.objects.create(article_title='India', target_language='ta', project_id='ta_india', created_by=self.manager, created_on=datetime.now())
        url = reverse(single_project_view, args=[project.project_id])
        self.client.force_authenticate(user=self.manager)
        data = {'assigned_to': self.annotator.id}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['assigned_to'], data['assigned_to'])

    def test_patch_project_failure(self):
        project = Project.objects.create(article_title='India', target_language='ta', project_id='ta_india', created_by=self.manager, created_on=datetime.now())
        url = reverse(single_project_view, args=[project.project_id])
        self.client.force_authenticate(user=self.annotator)
        data = {'assigned_to': self.annotator.id}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_view_projects(self):
        url = reverse(single_project_view, args=[self.project.project_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_sentences_unauthorized(self):
        self.client.force_authenticate(user=None)
        url = reverse(sentences_view, args=[self.project.project_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        
    def test_get_sentences_super_user(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse(sentences_view, args=[self.project.project_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_get_sentences_manager(self):
        self.client.force_authenticate(user=self.manager)
        url = reverse(sentences_view, args=[self.project.project_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_get_sentences_annotator(self):
        project = Project.objects.create(article_title='India', target_language='ta', project_id='ta_india', created_by=self.manager, created_on=datetime.now())
        self.client.force_authenticate(user=self.annotator)
        url = reverse(sentences_view, args=[project.project_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    def test_post_sentence_unauthorized(self):
        self.client.force_authenticate(user=None)
        url = reverse(sentences_view, args=[self.project.project_id])
        response = self.client.post(url, {'original_sentence': 'Test sentence', 'project': self.project.project_id})
        self.assertEqual(response.status_code, 401)
        
    def test_post_sentence_super_user(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse(sentences_view, args=[self.project.project_id])
        response = self.client.post(url, {'original_sentence': 'Test sentence', 'project': self.project.project_id})
        self.assertEqual(response.status_code, 201)
        
    def test_post_sentence_manager(self):
        self.client.force_authenticate(user=self.manager)
        url = reverse(sentences_view, args=[self.project.project_id])
        response = self.client.post(url, {'original_sentence': 'Test sentence', 'project': self.project.project_id})
        self.assertEqual(response.status_code, 201)
        
    def test_post_sentence_annotator(self):
        project = Project.objects.create(article_title='India', target_language='ta', project_id='ta_india', created_by=self.manager, created_on=datetime.now())
        self.client.force_authenticate(user=self.annotator)
        url = reverse(sentences_view, args=[project.project_id])
        response = self.client.post(url, {'original_sentence': 'Test sentence', 'project': self.project.project_id})
        self.assertEqual(response.status_code, 404)