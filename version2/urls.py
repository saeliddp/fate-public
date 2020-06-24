from django.urls import path
from . import views

# home is where the survey actually takes place
# update refreshes the home page and sends data to server
urlpatterns = [
    path('', views.instructions, name='version2-instructions'),
    path('export-users/', views.exportUsers, name='version2-export-users'),
    path('export-responses/', views.exportResponses, name='version2-export-responses'),
    path('home<int:q_id>/<int:respondent_id>/', views.home, name='version2-home'),
    path('feedback<int:q_id>/<int:respondent_id>/<int:correct>/<int:current_score>/', views.feedback, name='version2-feedback'),
    path('feedback_five<int:q_id>/<int:respondent_id>/<int:correct>/<int:current_score>/', views.feedback_five, name='version2-feedback_five'),
    path('redir<int:q_id>/<int:respondent_id>/', views.redir, name='version2-redir'),
    path('leaderboard<int:score>/', views.leaderboard, name='version2-leaderboard'),
]