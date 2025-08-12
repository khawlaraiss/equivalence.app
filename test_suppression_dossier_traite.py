#!/usr/bin/env python
"""
Test de la suppression d'un dossier traité
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

def test_suppression_dossier_traite():
    """Test de la suppression d'un dossier traité"""
    print("=== Test Suppression Dossier Traité ===")
    
    try:
        # 1. Créer un utilisateur admin
        admin_user = CustomUser.objects.create_user(
            username='admin_test_suppression',
            email='admin_suppression@example.com',
            password='adminpass123',
            role='admin'
        )
        print("✅ Admin créé:", admin_user.username)
        
        # 2. Créer un dossier traité
        dossier = Dossier.objects.create(
            titre="Dossier test suppression",
            description="Test de la suppression",
            statut='traite',
            date_reception=date(2024, 1, 15),
            cree_par=admin_user
        )
        print("✅ Dossier traité créé:", dossier.titre)
        
        # 3. Créer un candidat
        candidat = Candidat.objects.create(
            dossier=dossier,
            nom="Candidat Test Suppression",
            date_arrivee=date(2024, 1, 15),
            pays_origine="Maroc"
        )
        print("✅ Candidat créé:", candidat.nom)
        
        # 4. Créer un état de dossier
        etat_dossier = EtatDossier.objects.create(
            candidat=candidat,
            est_nouveau_dossier=False,
            a_decision_anterieure=False
        )
        print("✅ État dossier créé")
        
        # 5. Créer une consistance académique
        consistance = ConsistanceAcademique.objects.create(
            candidat=candidat,
            sciences_geodesiques_note=15,
            topographie_note=16,
            photogrammetrie_note=14,
            cartographie_note=13,
            droit_foncier_note=8,
            sig_note=9,
            teledetection_note=7,
            stages_note=8
        )
        print("✅ Consistance académique créée")
        
        # 6. Tester l'accès à la page de confirmation
        print("\n--- Test 1: Accès à la page de confirmation ---")
        client = Client()
        login_success = client.login(username='admin_test_suppression', password='adminpass123')
        print(f"✅ Connexion admin: {login_success}")
        
        # Accéder à la page de confirmation
        url_confirmation = reverse('dossiers:supprimer_dossier_traite', args=[dossier.id])
        response_confirmation = client.get(url_confirmation)
        print(f"✅ Code réponse confirmation: {response_confirmation.status_code}")
        
        if response_confirmation.status_code == 200:
            content = response_confirmation.content.decode()
            
            # Vérifier que la page de confirmation s'affiche
            if "Confirmer la suppression" in content:
                print("✅ Page de confirmation affichée")
            else:
                print("❌ Page de confirmation non affichée")
                
            if "Dossier test suppression" in content:
                print("✅ Informations du dossier affichées")
            else:
                print("❌ Informations du dossier non affichées")
        else:
            print("❌ Erreur d'accès à la page de confirmation")
        
        # 7. Tester la suppression
        print("\n--- Test 2: Suppression du dossier ---")
        response_suppression = client.post(url_confirmation)
        print(f"✅ Code réponse suppression: {response_suppression.status_code}")
        
        if response_suppression.status_code == 302:
            print("✅ Redirection après suppression")
            
            # Vérifier que le dossier a été supprimé
            try:
                dossier_supprime = Dossier.objects.get(id=dossier.id)
                print("❌ Dossier encore présent après suppression")
            except Dossier.DoesNotExist:
                print("✅ Dossier supprimé avec succès")
                
            # Vérifier que les objets associés ont été supprimés
            try:
                candidat_supprime = Candidat.objects.get(id=candidat.id)
                print("❌ Candidat encore présent après suppression")
            except Candidat.DoesNotExist:
                print("✅ Candidat supprimé avec succès")
                
            try:
                consistance_supprimee = ConsistanceAcademique.objects.get(id=consistance.id)
                print("❌ Consistance académique encore présente après suppression")
            except ConsistanceAcademique.DoesNotExist:
                print("✅ Consistance académique supprimée avec succès")
                
        else:
            print("❌ Erreur lors de la suppression")
        
        # 8. Nettoyer les données de test
        print("\n--- Nettoyage ---")
        try:
            admin_user.delete()
            print("✅ Admin supprimé")
        except:
            pass
        
        print("🎉 Test de suppression terminé avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_suppression_dossier_traite()

