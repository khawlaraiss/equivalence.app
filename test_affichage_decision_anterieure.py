#!/usr/bin/env python
"""
Test de l'affichage des décisions antérieures
"""

import os
import sys
import django
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier, Candidat, EtatDossier, ConsistanceAcademique
from users.models import CustomUser
from django.test import Client
from django.urls import reverse

def test_affichage_decision_anterieure():
    """Test de l'affichage des décisions antérieures sans évaluation actuelle"""
    print("=== Test Affichage Décision Antérieure ===")
    
    try:
        # 1. Créer un utilisateur professeur
        prof_user = CustomUser.objects.create_user(
            username='prof_test_affichage',
            email='prof_affichage@example.com',
            password='profpass123',
            role='professeur'
        )
        print("✅ Professeur créé:", prof_user.username)
        
        # 2. Créer un dossier
        dossier = Dossier.objects.create(
            titre="Dossier test affichage décision antérieure",
            description="Test de l'affichage sans évaluation",
            statut='en_cours'
        )
        dossier.professeurs.add(prof_user)
        print("✅ Dossier créé:", dossier.titre)
        
        # 3. Créer un candidat
        candidat = Candidat.objects.create(
            dossier=dossier,
            nom="Candidat Test Affichage",
            date_arrivee=date(2024, 1, 15),
            pays_origine="Maroc"
        )
        print("✅ Candidat créé:", candidat.nom)
        
        # 4. Créer un état de dossier avec décision antérieure SEULEMENT
        etat_dossier = EtatDossier.objects.create(
            candidat=candidat,
            est_nouveau_dossier=False,
            a_decision_anterieure=True,
            date_decision_anterieure=date(2024, 1, 10),
            decision_anterieure="Équivalence partielle accordée. Complètement de dossier demandé.",
            pieces_demandees="Relevés de notes manquants, programme détaillé des cours"
        )
        print("✅ État dossier créé avec décision antérieure")
        
        # 5. PAS de consistance académique (pas d'évaluation actuelle)
        print("✅ Aucune consistance académique créée (simulation d'un dossier sans évaluation)")
        
        # 6. Tester la vue d'évaluation
        print("\n--- Test de la vue d'évaluation ---")
        client = Client()
        
        # Se connecter en tant que professeur
        login_success = client.login(username='prof_test_affichage', password='profpass123')
        print(f"✅ Connexion professeur: {login_success}")
        
        # Accéder à la vue d'évaluation
        url = reverse('dossiers:evaluation_equivalence', args=[dossier.id])
        response = client.get(url)
        print(f"✅ Code réponse évaluation: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Vérifier que la décision antérieure est affichée
            if "Décision Antérieure" in content:
                print("✅ Décision antérieure affichée")
            else:
                print("❌ Décision antérieure non affichée")
            
            # Vérifier que la grille d'évaluation n'est PAS affichée
            if "Grille d'évaluation et interprétation des résultats" in content:
                print("❌ Grille d'évaluation affichée (ne devrait pas l'être)")
            else:
                print("✅ Grille d'évaluation non affichée (correct)")
            
            # Vérifier que le bouton "Commencer l'évaluation" est affiché
            if "Commencer l'évaluation académique" in content:
                print("✅ Bouton 'Commencer l'évaluation' affiché")
            else:
                print("❌ Bouton 'Commencer l'évaluation' non affiché")
            
            # Vérifier le message explicatif
            if "Pourquoi la grille d'évaluation n'est pas visible" in content:
                print("✅ Message explicatif affiché")
            else:
                print("❌ Message explicatif non affiché")
                
        else:
            print("❌ Erreur d'accès à la vue d'évaluation")
        
        # 7. Nettoyer les données de test
        print("\n--- Nettoyage ---")
        dossier.delete()
        prof_user.delete()
        print("✅ Données de test supprimées")
        
        print("\n🎉 Test d'affichage terminé avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_affichage_decision_anterieure()

