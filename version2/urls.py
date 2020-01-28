from django.urls import path
from . import views

# home is where the survey actually takes place
# update refreshes the home page and sends data to server
urlpatterns = [
    path('', views.consent, name='version2-consent'),
    path('email/', views.email, name='version2-email'),
    path('instructions<int:respondent_id>/', views.instructions, name='version2-instructions'),
    path('home<int:q_id>/<int:respondent_id>/', views.home, name='version2-home'),
    path('feedback<int:q_id>/<int:respondent_id>/<int:correct>/<int:current_score>/', views.feedback, name='version2-feedback'),
    path('redir<int:q_id>/<int:respondent_id>/', views.redir, name='version2-redir'),
    path('leaderboard<int:score>/', views.leaderboard, name='version2-leaderboard'),
]