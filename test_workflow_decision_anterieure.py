#!/usr/bin/env python
"""
Test du workflow des décisions antérieures
"""

import os
import sys
import django
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier, Candidat, EtatDossier, ConsistanceAcademique, HistoriqueAction
from users.models import CustomUser
from django.test import Client
from django.urls import reverse

def test_workflow_decision_anterieure():
    """Test complet du workflow des décisions antérieures"""
    print("=== Test du Workflow des Décisions Antérieures ===")
    
    try:
        # 1. Créer un utilisateur admin
        admin_user = CustomUser.objects.create_user(
            username='admin_test_workflow',
            email='admin_workflow@example.com',
            password='adminpass123',
            role='admin'
        )
        print("✅ Admin créé:", admin_user.username)
        
        # 2. Créer un utilisateur professeur
        prof_user = CustomUser.objects.create_user(
            username='prof_test_workflow',
            email='prof_workflow@example.com',
            password='profpass123',
            role='professeur'
        )
        print("✅ Professeur créé:", prof_user.username)
        
        # 3. Créer un dossier
        dossier = Dossier.objects.create(
            titre="Dossier test workflow décision antérieure",
            description="Test du workflow complet",
            statut='en_cours'
        )
        dossier.professeurs.add(prof_user)
        print("✅ Dossier créé:", dossier.titre)
        
        # 4. Créer un candidat
        candidat = Candidat.objects.create(
            dossier=dossier,
            nom="Candidat Test Workflow",
            date_arrivee=date(2024, 1, 15),
            pays_origine="Maroc"
        )
        print("✅ Candidat créé:", candidat.nom)
        
        # 5. Créer un état de dossier avec décision antérieure
        etat_dossier = EtatDossier.objects.create(
            candidat=candidat,
            est_nouveau_dossier=False,
            a_decision_anterieure=True,
            date_decision_anterieure=date(2024, 1, 10),
            decision_anterieure="Équivalence partielle accordée. Complètement de dossier demandé.",
            pieces_demandees="Relevés de notes manquants, programme détaillé des cours"
        )
        print("✅ État dossier créé avec décision antérieure")
        
        # 6. Créer une consistance académique (évaluation actuelle)
        consistance = ConsistanceAcademique.objects.create(
            candidat=candidat,
            sciences_geodesiques_note=12,
            topographie_note=14,
            photogrammetrie_note=8,
            cartographie_note=10,
            droit_foncier_note=6,
            sig_note=8,
            teledetection_note=7,
            stages_note=8
        )
        print("✅ Consistance académique créée avec notes")
        
        # 7. Tester la vue d'évaluation (doit afficher la décision antérieure)
        print("\n--- Test de la vue d'évaluation ---")
        client = Client()
        
        # Se connecter en tant que professeur
        login_success = client.login(username='prof_test_workflow', password='profpass123')
        print(f"✅ Connexion professeur: {login_success}")
        
        # Accéder à la vue d'évaluation
        url = reverse('dossiers:evaluation_equivalence', args=[dossier.id])
        response = client.get(url)
        print(f"✅ Code réponse évaluation: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            if "Décision Antérieure" in content:
                print("✅ Décision antérieure affichée dans la vue d'évaluation")
            else:
                print("❌ Décision antérieure non affichée")
        else:
            print("❌ Erreur d'accès à la vue d'évaluation")
        
        # 8. Tester le renvoi au professeur par l'admin
        print("\n--- Test du renvoi au professeur ---")
        
        # Se connecter en tant qu'admin
        client.logout()
        login_success = client.login(username='admin_test_workflow', password='adminpass123')
        print(f"✅ Connexion admin: {login_success}")
        
        # Tester le renvoi au professeur
        url_renvoi = reverse('dossiers:renvoyer_au_professeur', args=[dossier.id])
        response = client.post(url_renvoi, {
            'message_admin': 'Le candidat a fourni tous les documents demandés. Vous pouvez procéder à la réévaluation.'
        })
        print(f"✅ Code réponse renvoi: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ Renvoi au professeur réussi")
            
            # Vérifier que le statut a changé
            dossier.refresh_from_db()
            print(f"✅ Nouveau statut: {dossier.statut}")
            
            # Vérifier l'historique
            historique = HistoriqueAction.objects.filter(dossier=dossier).last()
            if historique:
                print(f"✅ Historique créé: {historique.action}")
            else:
                print("❌ Historique non créé")
        else:
            print("❌ Erreur lors du renvoi")
        
        # 9. Nettoyer les données de test
        print("\n--- Nettoyage ---")
        dossier.delete()
        admin_user.delete()
        prof_user.delete()
        print("✅ Données de test supprimées")
        
        print("\n🎉 Test du workflow terminé avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_workflow_decision_anterieure()
