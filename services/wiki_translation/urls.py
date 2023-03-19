from django.urls import path
from .views import project_view, sentences_view, single_sentence_view, login_api, getUsers, token_refresh_api, single_project_view

#Controller: Routes to view with match patterns
urlpatterns = [
    path('', project_view),
    path('login/', login_api),
    path('login/refresh/', token_refresh_api),
    path('<str:project_id>/sentence', sentences_view),
    path('sentence/<int:sentence_id>', single_sentence_view),
    path('users/', getUsers),
    path('project/<str:project_id>', single_project_view)
]