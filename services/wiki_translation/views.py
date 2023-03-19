from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Project, Sentence
from .serializers import ProjectSerializer, SentenceSerializer
from .utils import getSummaryForTitles

# Create your views here.

#GET and POST REST API for path ""
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated]) #Help us check is the user is authenticated, else returns 401 UNAUTHORIZED
def project_view(request):
    user = request.user
    if (request.method == 'GET'):
        #If user is a super user, get all the object
        if (user.is_superuser):
            projects = Project.objects.all()
        #If user is of group Manager, then get the objects created by the user
        elif (user.groups.filter(name='Manager').exists()):
            projects = Project.objects.filter(created_by = user.id)
        #If user is of group Annotator, then get the objects that are assigned to the user
        elif (user.groups.filter(name='Annotator').exists()):
            projects = Project.objects.filter(assigned_to = user.id)
        #Else return 403
        else:
            return Response({'error': 'Not enough permission'}, status = status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(projects, many=True)
        #return the projects with return code 200
        return Response(serializer.data)
    elif (request.method == 'POST'):
        #Only add new project when the user is superuser or of group manager
        if (user.is_superuser or user.groups.filter(name='Manager').exists()):
            try:
                #Set the created_by field before saving with current user
                request.data["created_by"] = user.id
                serializer = ProjectSerializer(data=request.data)
                if (serializer.is_valid()):
                    project = serializer.save()
                    #After saving the project, add all sentences that project should have
                    add_sentence_for_project(project)
                    #Return the saved project and return with return code 201
                    return Response(serializer.data, status = status.HTTP_201_CREATED)
                #In case of invalid object, get Bad Request 400
                return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                #Return with error message to show the cause of failure
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Not enough permission'}, status = status.HTTP_403_FORBIDDEN)


#GET and PATCH REST API for path "project/<str:project_id>"
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])  #Help us check is the user is authenticated, else returns 401 UNAUTHORIZED
def single_project_view(request, project_id):
    user = request.user
    try:
        #If user is a super user, get the object
        if (user.is_superuser):
            project = Project.objects.get(project_id = project_id)
        #If user is of group Manager, then get the objects only if it is created by the user
        elif (user.groups.filter(name='Manager').exists()):
            project = Project.objects.get(project_id = project_id, created_by = user.id)
        #If user is of group Annotator, then get the objects only if it is assigned to the user
        elif (user.groups.filter(name='Annotator').exists()):
            project = Project.objects.get(project_id = project_id, assigned_to = user.id)
        #Else return 403
        else:
            return Response({'error': 'Not enough permission'}, status = status.HTTP_403_FORBIDDEN)
    except project.DoesNotExist:
        #Returns 404 as the Project is not present or it is not available for the user
        return Response(status = status.HTTP_404_NOT_FOUND)
    
    if (request.method == 'GET'):
        serializer = ProjectSerializer(project)
        #return the project with return code 200
        return Response(serializer.data)
    if (request.method == 'PATCH'):
        try:
            serializer = ProjectSerializer(project, data = request.data, partial=True)
            if (serializer.is_valid()):
                serializer.save()
                #Returns the update project with return code 200
                return Response(serializer.data)
            #In case of invalid object, get Bad Request 400
            return Response(serializer.data, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            #Return with error message to show the cause of failure with return code 500
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#GET and POST REST API for path "<str:project_id>/sentence"
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])  #Help us check is the user is authenticated, else returns 401 UNAUTHORIZED
def sentences_view(request, project_id):
    user = request.user
    try:
        #If user is a super user, get the object
        if (user.is_superuser):
            project = Project.objects.get(project_id = project_id)
        #If user is of group Manager, then get the objects only if it is created by the user
        elif (user.groups.filter(name='Manager').exists()):
            project = Project.objects.get(project_id = project_id, created_by = user.id)
        #If user is of group Annotator, then get the objects only if it is assigned to the user
        elif (user.groups.filter(name='Annotator').exists()):
            project = Project.objects.get(project_id = project_id, assigned_to = user.id)
        #Else return 403
        else:
            return Response({'error': 'Not enough permission'}, status = status.HTTP_403_FORBIDDEN)
    except project.DoesNotExist:
        #Returns 404 as the Project is not present or it is not available for the user
        return Response(status = status.HTTP_404_NOT_FOUND)
    
    if (request.method == 'GET'):
        #Get the sentence. Here we are not checking for authorization as we have already done it on Project
        sentences = Sentence.objects.filter(project=project)
        serializer = SentenceSerializer(sentences, many=True)
        #return the sentences with return code 200
        return Response(serializer.data)
    elif (request.method == 'POST'):
        try:
            serializer = SentenceSerializer(data = request.data)
            if (serializer.is_valid()):
                serializer.save()
                #Return the saved sentence and return with return code 201
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            #In case of invalid object, get Bad Request 400
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                #Return with error message to show the cause of failure with return code 500
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

#GET and PATCH REST API for path "sentence/<int:sentence_id>"
@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])  #Help us check is the user is authenticated, else returns 401 UNAUTHORIZED
def single_sentence_view(request, sentence_id):
    
    try:
        #Get the sentence with sentence id
        sentence = Sentence.objects.get(sentence_id = sentence_id)
    except sentence.DoesNotExist:
        #Returns 404 as the Sentence is not present
        return Response(status = status.HTTP_404_NOT_FOUND)
    
    user = request.user
    project_id = sentence.project
    try:
        #If user is a super user, get the object
        if (user.is_superuser):
            project = Project.objects.get(project_id = project_id)
        #If user is of group Manager, then get the objects only if it is created by the user
        elif (user.groups.filter(name='Manager').exists()):
            project = Project.objects.get(project_id = project_id, created_by = user.id)
        #If user is of group Annotator, then get the objects only if it is assigned to the user
        elif (user.groups.filter(name='Annotator').exists()):
            project = Project.objects.get(project_id = project_id, assigned_to = user.id)
        #Else return 403
        else:
            return Response({'error': 'Not enough permission'}, status = status.HTTP_403_FORBIDDEN)
    except project.DoesNotExist:
        #Returns 403 as the Project is not available for the user
        return Response({'error': 'Not enough permission'}, status = status.HTTP_403_FORBIDDEN)
    
    if (request.method == 'GET'):
        serializer = SentenceSerializer(sentence)
        #return the sentence with return code 200
        return Response(serializer.data)
    if (request.method == 'PATCH'):
        try:
            serializer = SentenceSerializer(sentence, data = request.data, partial=True)
            if (serializer.is_valid()):
                serializer.save()
                #Return the saved sentence and return with return code 200
                return Response(serializer.data)
            #In case of invalid object, get Bad Request 400
            return Response(serializer.data, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            #Return with error message to show the cause of failure with return code 500
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#POST REST API for path "login/"
@api_view(['POST'])
def login_api(request):
    #Consumes(FORM_DATA)
    username = request.POST.get('username')
    password = request.POST.get('password')

    #Checks authentication
    user = authenticate(request, username=username, password=password)
    #If user is valid, generates the access token and returns with return code 200
    if user is not None:
        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(data)

    else:
        return Response({'error': 'Contact Admin Team for account creation'}, status=status.HTTP_401_UNAUTHORIZED)
    
#POST REST API for path "login/refresh"
#TODO: Currently not used
@api_view(['POST'])
def token_refresh_api(request):
    refresh_token = request.data.get('refresh_token')

    if not refresh_token:
        return Response({'error': 'refresh_token field is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        new_access_token = str(token.access_token)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'access_token': new_access_token}, status=status.HTTP_200_OK)
    
#GET REST API for path "users/"
@api_view(['GET'])
@permission_classes([IsAuthenticated])  #Help us check is the user is authenticated, else returns 401 UNAUTHORIZED
def getUsers(request):

    #Get all the user from DB
    users = User.objects.all()

    all_user_data = {}
    for user in users:
        all_user_data[user.id] = {
            "name": user.username,
            #canAdd is need to disable the button in the frontend(react)
            "canAdd": 1 if user.is_superuser or user.groups.filter(name='Manager').exists() else 0
        }
    
    user_data = {
        'current_user' : request.user.id, #Set the current user id
        'users' : all_user_data
    }
    #Return the user data with return code 200
    return Response(user_data)
    
    

def add_sentence_for_project(project : Project):
    summary_list = getSummaryForTitles(project.article_title)
    for summary in summary_list:
        sentence = Sentence(project = project, original_sentence = summary.strip(), translated_sentence = '')
        try:
            sentence.save()
        except IntegrityError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
