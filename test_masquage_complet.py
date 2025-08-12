#!/usr/bin/env python
"""
Test du masquage complet des sections d'évaluation
"""

import os
import sys
import django
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier, Candidat, EtatDossier
from users.models import CustomUser
from django.test import Client
from django.urls import reverse

def test_masquage_complet():
    """Test que toutes les sections d'évaluation sont masquées"""
    print("=== Test Masquage Complet des Sections ===")
    
    try:
        # 1. Créer un utilisateur professeur
        prof_user = CustomUser.objects.create_user(
            username='prof_test_masquage_complet',
            email='prof_masquage_complet@example.com',
            password='profpass123',
            role='professeur'
        )
        print("✅ Professeur créé:", prof_user.username)
        
        # 2. Créer un dossier
        dossier = Dossier.objects.create(
            titre="Dossier test masquage complet",
            description="Test du masquage complet des sections",
            statut='en_cours'
        )
        dossier.professeurs.add(prof_user)
        print("✅ Dossier créé:", dossier.titre)
        
        # 3. Créer un candidat
        candidat = Candidat.objects.create(
            dossier=dossier,
            nom="Candidat Test Masquage Complet",
            date_arrivee=date(2024, 1, 15),
            pays_origine="Maroc"
        )
        print("✅ Candidat créé:", candidat.nom)
        
        # 4. PAS de consistance académique (pas d'évaluation)
        print("✅ Aucune consistance académique créée")
        
        # 5. Tester l'accès à la vue d'évaluation
        print("\n--- Test de l'affichage des sections ---")
        client = Client()
        
        # Se connecter en tant que professeur
        login_success = client.login(username='prof_test_masquage_complet', password='profpass123')
        print(f"✅ Connexion professeur: {login_success}")
        
        # Accéder à la vue d'évaluation
        url = reverse('dossiers:evaluation_equivalence', args=[dossier.id])
        response = client.get(url)
        print(f"✅ Code réponse: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            
            # Vérifier que TOUTES les sections d'évaluation sont MASQUÉES
            sections_a_masquer = [
                "Résumé de l'interprétation",
                "Grille d'évaluation et interprétation des résultats",
                "Section Stages et professionnalisation",
                "Décision de la commission"
            ]
            
            sections_masquees = True
            for section in sections_a_masquer:
                if section in content:
                    print(f"❌ Section '{section}' affichée (ne devrait pas l'être)")
                    sections_masquees = False
                else:
                    print(f"✅ Section '{section}' masquée (correct)")
            
            # Vérifier que le tableau TOTAL n'est pas affiché
            if "TOTAL" in content and "0/100" in content:
                print("❌ Tableau TOTAL affiché (ne devrait pas l'être)")
                sections_masquees = False
            else:
                print("✅ Tableau TOTAL masqué (correct)")
            
            # Vérifier que la décision antérieure est affichée (si elle existe)
            if "Décision Antérieure" in content:
                print("✅ Décision antérieure affichée (correct)")
            else:
                print("ℹ️ Pas de décision antérieure (normal)")
            
            if sections_masquees:
                print("\n🎉 TOUTES les sections d'évaluation sont masquées !")
            else:
                print("\n⚠️ Certaines sections d'évaluation sont encore visibles")
                
        else:
            print("❌ Erreur d'accès à la vue d'évaluation")
        
        # 6. Nettoyer les données de test
        print("\n--- Nettoyage ---")
        dossier.delete()
        prof_user.delete()
        print("✅ Données de test supprimées")
        
        print("\n🎉 Test de masquage complet terminé !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_masquage_complet()

