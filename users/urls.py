from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create-user/', views.create_user, name='create_user'),
    path('inscription/', views.inscription, name='inscription'),
    path('gestion/', views.gestion_utilisateurs, name='gestion_utilisateurs'),
    path('ajouter/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
    path('utilisateur/<int:user_id>/modifier/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('utilisateur/<int:user_id>/desactiver/', views.desactiver_utilisateur, name='desactiver_utilisateur'),
    path('utilisateur/<int:user_id>/supprimer/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    path('profile/', views.profile, name='profile'),
] 