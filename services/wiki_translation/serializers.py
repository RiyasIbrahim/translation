from rest_framework import serializers
from .models import Project, Sentence
from datetime import datetime
from .validators import validate_target_language

class ProjectSerializer(serializers.ModelSerializer):
    
    #Setting it to read only, as we are not expecting the user to enter these
    created_on = serializers.DateTimeField(read_only=True)
    
    #Setting it to read only, as it is combination of title and lang
    project_id = serializers.CharField(read_only=True)

    class Meta:
        #Selecting the Model
        model = Project
        #Selecting field required for serialization
        fields = '__all__'
        extra_kwargs = {
            #Adding validation
            'target_language': {'validators': [validate_target_language]}
        }

    #Overriding the create function as we need add created_on and project_id
    def create(self, validated_data):
        article_title = validated_data.get('article_title')
        target_language = validated_data.get('target_language')

        # Set the project_id based on article_title and target_language
        project_id = f'{target_language.lower()}_{article_title.lower()}'

        # Set the current time as created_on
        created_on = datetime.now()

        # Add the created_on and project_id to the validated data
        validated_data['created_on'] = created_on
        validated_data['project_id'] = project_id

        # Call the create method of the parent serializer
        return super().create(validated_data)

class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        #Selecting the Model
        model = Sentence
        #Selecting field required for serialization
        fields = '__all__'

