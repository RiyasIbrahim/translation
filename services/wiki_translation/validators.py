from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy

#Validation for language
def validate_target_language(language):
    valid_languages = ['bn', 'gu', 'hi', 'kn', 'ml', 'mr', 'ne', 'or', 'pa', 'si', 'ta', 'te', 'ur']

    if language not in valid_languages:
        raise ValidationError(gettext_lazy('%(language)s is not a valid target language. Valid options are : %(valid_languages)s'),
                              params = {'language': language, 'valid_languages': ', '.join(valid_languages)})