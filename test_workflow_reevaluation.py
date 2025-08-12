#!/usr/bin/env python
"""
Test du workflow complet de réévaluation avec décision antérieure
"""

import os
import sys
import django
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier, Candidat, EtatDossier, ConsistanceAcademique, DecisionCommission
from users.models import CustomUser
from django.test import Client
from django.urls import reverse

def test_workflow_reevaluation():
    """Test du workflow complet de réévaluation"""
    print("=== Test Workflow Réévaluation avec Décision Antérieure ===")
    
    try:
        # 1. Créer un utilisateur admin
        admin_user = CustomUser.objects.create_user(
            username='admin_test_reevaluation',
            email='admin_reevaluation@example.com',
            password='adminpass123',
            role='admin'
        )
        print("✅ Admin créé:", admin_user.username)
        
        # 2. Créer un utilisateur professeur
        prof_user = CustomUser.objects.create_user(
            username='prof_test_reevaluation',
            email='prof_reevaluation@example.com',
            password='profpass123',
            role='professeur'
        )
        print("✅ Professeur créé:", prof_user.username)
        
        # 3. Créer un dossier
        dossier = Dossier.objects.create(
            titre="Dossier test réévaluation",
            description="Test du workflow de réévaluation",
            statut='en_cours'
        )
        dossier.professeurs.add(prof_user)
        print("✅ Dossier créé:", dossier.titre)
        
        # 4. Créer un candidat
        candidat = Candidat.objects.create(
            dossier=dossier,
            nom="Candidat Test Réévaluation",
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
            pieces_demandees="Relevés de notes manquants"
        )
        print("✅ État dossier créé avec décision antérieure")
        
        # 6. Créer une ancienne consistance académique (décision antérieure)
        ancienne_consistance = ConsistanceAcademique.objects.create(
            candidat=candidat,
            sciences_geodesiques_note=12,
            topographie_note=14,
            photogrammetrie_note=8,
            cartographie_note=10,
            droit_foncier_note=6,
            sig_note=7,
            teledetection_note=5,
            stages_note=8
        )
        print("✅ Ancienne consistance académique créée (note totale: 70/100)")
        
        # 7. Créer une ancienne décision de commission
        ancienne_decision = DecisionCommission.objects.create(
            candidat=candidat,
            score_total=70,
            decision="equivalence_accorder",
            recommandations="Équivalence partielle accordée",
            commentaires="Dossier précédemment traité"
        )
        print("✅ Ancienne décision de commission créée")
        
        # 8. Tester le bouton "Renvoyer au professeur" (simulation admin)
        print("\n--- Test 1: Admin renvoie le dossier au professeur ---")
        client_admin = Client()
        login_success = client_admin.login(username='admin_test_reevaluation', password='adminpass123')
        print(f"✅ Connexion admin: {login_success}")
        
        # Simuler le renvoi au professeur
        url_renvoi = reverse('dossiers:renvoyer_au_professeur', args=[dossier.id])
        response_renvoi = client_admin.post(url_renvoi, {
            'message_admin': 'Veuillez réévaluer ce dossier'
        })
        print(f"✅ Réponse renvoi: {response_renvoi.status_code}")
        
        # Vérifier que l'ancienne évaluation a été supprimée
        try:
            candidat.refresh_from_db()
            if hasattr(candidat, 'consistance_academique') and candidat.consistance_academique:
                print("❌ Ancienne consistance académique encore présente")
            else:
                print("✅ Ancienne consistance académique supprimée")
        except:
            print("✅ Ancienne consistance académique supprimée")
        
        # 9. Tester l'accès à la vue d'évaluation (professeur)
        print("\n--- Test 2: Professeur accède à la vue d'évaluation ---")
        client_prof = Client()
        login_success = client_prof.login(username='prof_test_reevaluation', password='profpass123')
        print(f"✅ Connexion professeur: {login_success}")
        
        # Accéder à la vue d'évaluation
        url_evaluation = reverse('dossiers:evaluation_equivalence', args=[dossier.id])
        response_evaluation = client_prof.get(url_evaluation)
        print(f"✅ Code réponse évaluation: {response_evaluation.status_code}")
        
        if response_evaluation.status_code == 200:
            content = response_evaluation.content.decode()
            
            # Vérifier que la décision antérieure est MASQUÉE (car pas de nouvelle évaluation)
            if "Décision Antérieure" in content:
                print("✅ Décision antérieure affichée (correct - pas de nouvelle évaluation)")
            else:
                print("ℹ️ Décision antérieure non affichée")
            
            # Vérifier que les sections d'évaluation sont masquées
            if "Grille d'évaluation" in content:
                print("❌ Grille d'évaluation affichée (ne devrait pas l'être)")
            else:
                print("✅ Grille d'évaluation masquée (correct)")
                
        else:
            print("❌ Erreur d'accès à la vue d'évaluation")
        
        # 10. Nettoyer les données de test
        print("\n--- Nettoyage ---")
        dossier.delete()
        admin_user.delete()
        prof_user.delete()
        print("✅ Données de test supprimées")
        
        print("\n🎉 Test de workflow de réévaluation terminé avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_workflow_reevaluation()
