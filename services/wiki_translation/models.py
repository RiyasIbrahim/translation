from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#Model : Project
class Project(models.Model):

    #Title with max length 150 chars
    article_title = models.CharField(max_length = 150)

    #Language with max length 3 chars
    target_language = models.CharField(max_length = 3)

    #Project id is created while serializing as language_title. This is the primary key. and max length is 154
    project_id = models.CharField(primary_key = True, max_length=154)

    #Automatically stores the creation time during serialization
    created_on = models.DateTimeField()

    #Foreign Key that links Project to User. All Project Models created by a user is also deleted when the user is deleted
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    #Stores the user id of the assignee. It call be null
    assigned_to = models.BigIntegerField(null=True)

    def __str__(self) -> str:
        return self.project_id

#Model : Sentence
class Sentence(models.Model):

    #Foreign key that links Sentences to Project Model. All Sentence Models that are in a Project is also deleted when the Project is deleted.
    #Stored as project_id in the DB
    project = models.ForeignKey(Project, on_delete = models.CASCADE, db_column = "project_id")

    #Primary key of Sentence Model.
    sentence_id = models.BigAutoField(primary_key=True)

    #Stores the original sentences
    original_sentence = models.TextField()

    #Stores the translated sentences, It can also null or blank
    translated_sentence = models.TextField(blank=True, null=True)

    #Automatically stores the creation time during serialization
    created_on = models.DateTimeField(auto_now_add=True)

