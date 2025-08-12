from django.urls import path
from . import views

app_name = 'dossiers'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('gestion/', views.gestion_dossiers, name='gestion_dossiers'),
    path('ajouter/', views.ajouter_dossier, name='ajouter_dossier'),
    path('traites/', views.dossiers_traites, name='dossiers_traites'),
    path('recherche/', views.recherche_avancee, name='recherche_avancee'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/marquer-lues/', views.marquer_toutes_lues, name='marquer_toutes_lues'),
    path('notifications/<int:notification_id>/supprimer/', views.supprimer_notification, name='supprimer_notification'),

    path('rapports/', views.rapports_statistiques, name='rapports_statistiques'),
    path('dossier/<int:dossier_id>/', views.dossier_detail, name='dossier_detail'),
    path('dossier/<int:dossier_id>/traiter/', views.traiter_dossier, name='traiter_dossier'),
    path('dossier/<int:dossier_id>/affecter/', views.affecter_dossier, name='affecter_dossier'),
    path('dossier/<int:dossier_id>/rapport/', views.ajouter_rapport, name='ajouter_rapport'),
    path('dossier/<int:dossier_id>/evaluation/', views.evaluation_equivalence, name='evaluation_equivalence'),
    path('dossier/<int:dossier_id>/creer-evaluation/', views.creer_evaluation, name='creer_evaluation'),


    path('dossier/<int:dossier_id>/etat-dossier/', views.etat_dossier, name='etat_dossier'),
    path('dossier/<int:dossier_id>/consistance-academique/', views.consistance_academique, name='consistance_academique'),
    path('dossier/<int:dossier_id>/valider-et-transferer/', views.valider_et_transferer_dossier, name='valider_et_transferer_dossier'),
    path('dossier/<int:dossier_id>/renvoyer-au-professeur/', views.renvoyer_au_professeur, name='renvoyer_au_professeur'),
    path('dossier/<int:dossier_id>/export-pdf/', views.exporter_evaluation_pdf, name='exporter_evaluation_pdf'),
    path('dossier/<int:dossier_id>/modifier/', views.modifier_dossier, name='modifier_dossier'),
    path('dossier/<int:dossier_id>/supprimer/', views.supprimer_dossier, name='supprimer_dossier'),
    path('controle-fiche-evaluation/', views.controle_fiche_evaluation, name='controle_fiche_evaluation'),
    path('test-media/', views.test_media_file, name='test_media_file'),
    path('admin/dossiers/', views.admin_dossiers, name='admin_dossiers'),
    path('professeur/dossiers/', views.professeur_dossiers, name='professeur_dossiers'),

    # Dossiers traités
    path('dossiers-traites/', views.dossiers_traites_admin, name='dossiers_traites_admin'),
    path('dossiers-traites/ajouter/', views.ajouter_dossier_traite, name='ajouter_dossier_traite'),
    path('dossiers-traites/<int:dossier_id>/modifier/', views.modifier_dossier_traite, name='modifier_dossier_traite'),
    path('dossiers-traites/<int:dossier_id>/reunion/', views.ajouter_reunion_dossier, name='ajouter_reunion_dossier'),
    path('dossiers-traites/<int:dossier_id>/reunions/', views.voir_reunions_dossier, name='voir_reunions_dossier'),
    path('dossiers-traites/<int:dossier_id>/avis/', views.voir_avis_commission, name='voir_avis_commission'),
    path('dossiers-traites/<int:dossier_traite_id>/details/', views.voir_details_traitement, name='voir_details_traitement'),
    path('dossiers-traites/<int:dossier_traite_id>/renvoyer-au-professeur/', views.renvoyer_dossier_traite_au_professeur, name='renvoyer_dossier_traite_au_professeur'),
    path('dossiers-traites/<int:dossier_id>/supprimer/', views.supprimer_dossier_traite, name='supprimer_dossier_traite'),
    path('dossiers-traites/import-csv/', views.import_csv_dossiers, name='import_csv_dossiers'),
    path('dossiers-traites/import-csv-auto/', views.import_csv_auto, name='import_csv_auto'),
    path('dossiers-traites/creer-reunion-multiple/', views.creer_reunion_multiple, name='creer_reunion_multiple'),
    path('dossiers-traites/creer-reunion-form/', views.creer_reunion_form, name='creer_reunion_form'),
] 