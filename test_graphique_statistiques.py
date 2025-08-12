#!/usr/bin/env python3
"""
Test des statistiques et du graphique des rapports
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier, DecisionCommission
from users.models import CustomUser
from django.urls import reverse
from django.test import Client

def test_statistiques_rapports():
    print("=== 🧪 TEST STATISTIQUES RAPPORTS ===")
    
    # Vérifier les utilisateurs
    try:
        admin = CustomUser.objects.get(username='admin')
        print(f"✅ Admin trouvé: {admin.username}")
    except CustomUser.DoesNotExist as e:
        print(f"❌ Erreur utilisateur: {e}")
        return
    
    # Compter les dossiers par statut
    total_dossiers = Dossier.objects.count()
    dossiers_non_traites = Dossier.objects.filter(statut='non_traite').count()
    dossiers_en_cours = Dossier.objects.filter(statut='en_cours').count()
    dossiers_traites = Dossier.objects.filter(statut='traite').count()
    
    print(f"\n📊 Dossiers par statut:")
    print(f"   Total: {total_dossiers}")
    print(f"   Non traités: {dossiers_non_traites}")
    print(f"   En cours: {dossiers_en_cours}")
    print(f"   Traités: {dossiers_traites}")
    
    # Compter les décisions par type
    total_evaluations = DecisionCommission.objects.count()
    evaluations_completes = DecisionCommission.objects.filter(decision='equivalence_accorder').count()
    evaluations_conditionnelles = DecisionCommission.objects.filter(decision='completement_dossier').count()
    evaluations_invitation_soutenance = DecisionCommission.objects.filter(decision='invitation_soutenance').count()
    evaluations_invitation_concours = DecisionCommission.objects.filter(decision='invitation_concours').count()
    evaluations_refusees = DecisionCommission.objects.filter(decision='non_equivalent').count()
    
    print(f"\n📊 Décisions par type:")
    print(f"   Équivalence accordée: {evaluations_completes}")
    print(f"   Complètement dossier: {evaluations_conditionnelles}")
    print(f"   Invitation soutenance: {evaluations_invitation_soutenance}")
    print(f"   Invitation concours: {evaluations_invitation_concours}")
    print(f"   Non équivalent: {evaluations_refusees}")
    print(f"   Total: {total_evaluations}")
    
    # Calculer la moyenne des scores
    if total_evaluations > 0:
        moyenne_score = DecisionCommission.objects.aggregate(
            moyenne=django.db.models.Avg('score_total')
        )['moyenne']
        print(f"\n📈 Score moyen: {moyenne_score:.1f}/100")
    else:
        print(f"\n📈 Score moyen: Aucune évaluation")
    
    # Tester l'accès à la page des rapports
    client = Client()
    client.force_login(admin)
    
    print(f"\n🔗 Test accès page rapports:")
    response = client.get(reverse('dossiers:rapports_statistiques'))
    print(f"   Status: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Vérifier que les données sont bien affichées
        print(f"\n🔍 Vérification du contenu:")
        
        # Vérifier les statistiques générales
        if str(total_dossiers) in content:
            print(f"   ✅ Total dossiers affiché: {total_dossiers}")
        else:
            print(f"   ❌ Total dossiers non affiché")
            
        if str(dossiers_non_traites) in content:
            print(f"   ✅ Non traités affiché: {dossiers_non_traites}")
        else:
            print(f"   ❌ Non traités non affiché")
            
        if str(dossiers_en_cours) in content:
            print(f"   ✅ En cours affiché: {dossiers_en_cours}")
        else:
            print(f"   ❌ En cours non affiché")
            
        if str(dossiers_traites) in content:
            print(f"   ✅ Traités affiché: {dossiers_traites}")
        else:
            print(f"   ❌ Traités non affiché")
        
        # Vérifier les statistiques des évaluations
        if str(evaluations_completes) in content:
            print(f"   ✅ Équivalence accordée affiché: {evaluations_completes}")
        else:
            print(f"   ❌ Équivalence accordée non affiché")
            
        if str(evaluations_conditionnelles) in content:
            print(f"   ✅ Complètement dossier affiché: {evaluations_conditionnelles}")
        else:
            print(f"   ❌ Complètement dossier non affiché")
            
        if str(evaluations_invitation_soutenance) in content:
            print(f"   ✅ Invitation soutenance affiché: {evaluations_invitation_soutenance}")
        else:
            print(f"   ❌ Invitation soutenance non affiché")
            
        if str(evaluations_invitation_concours) in content:
            print(f"   ✅ Invitation concours affiché: {evaluations_invitation_concours}")
        else:
            print(f"   ❌ Invitation concours non affiché")
            
        if str(evaluations_refusees) in content:
            print(f"   ✅ Non équivalent affiché: {evaluations_refusees}")
        else:
            print(f"   ❌ Non équivalent non affiché")
        
        # Vérifier que le graphique est présent
        if 'dossiersChart' in content:
            print(f"   ✅ Canvas graphique présent")
        else:
            print(f"   ❌ Canvas graphique manquant")
            
        if 'Chart.js' in content:
            print(f"   ✅ Chart.js chargé")
        else:
            print(f"   ❌ Chart.js non chargé")
    
    print(f"\n🎯 TEST TERMINÉ")

if __name__ == '__main__':
    test_statistiques_rapports()
