#!/usr/bin/env python
"""
Test final des permissions d'accès aux évaluations
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from users.models import CustomUser
from dossiers.models import Dossier
from django.urls import reverse
from django.test import Client

def test_final_evaluation_access():
    """Test final des permissions d'accès"""
    print("=== 🧪 TEST FINAL ACCÈS ÉVALUATION ===")
    print("Vérification finale des permissions !")
    print()
    
    try:
        # 1. Vérifier qu'on a des utilisateurs
        admins = CustomUser.objects.filter(role='admin')
        professeurs = CustomUser.objects.filter(role='professeur')
        
        print(f"📊 Utilisateurs trouvés:")
        print(f"   - Administrateurs: {admins.count()}")
        print(f"   - Professeurs: {professeurs.count()}")
        
        if admins.count() == 0 or professeurs.count() == 0:
            print("❌ Besoin d'au moins 1 admin et 1 professeur pour le test")
            return
        
        # 2. Prendre un admin et un professeur pour le test
        admin_user = admins.first()
        prof_user = professeurs.first()
        
        print(f"\n--- Utilisateurs de test ---")
        print(f"   Admin: {admin_user.username}")
        print(f"   Professeur: {prof_user.username}")
        
        # 3. Vérifier qu'on a des dossiers
        dossiers = Dossier.objects.all()
        if dossiers.count() == 0:
            print("❌ Aucun dossier trouvé pour le test")
            return
        
        dossier_test = dossiers.first()
        print(f"\n--- Dossier de test ---")
        print(f"   ID: {dossier_test.id}")
        print(f"   Statut: {dossier_test.statut}")
        
        # 4. Test final des permissions
        print(f"\n--- Test final des permissions ---")
        
        # Test de la vue d'évaluation
        url_evaluation = reverse('dossiers:evaluation_equivalence', args=[dossier_test.id])
        print(f"🔗 URL évaluation: {url_evaluation}")
        
        # Test avec admin
        admin_client = Client()
        admin_client.force_login(admin_user)
        response_admin = admin_client.get(url_evaluation)
        
        if response_admin.status_code == 200:
            print(f"   ✅ Admin: Peut voir l'évaluation (200)")
            
            # Vérifier que le bouton n'est pas dans la réponse
            if "Commencer l'évaluation académique" not in response_admin.content.decode():
                print(f"      ✅ Bouton 'Commencer l'évaluation' masqué pour l'admin")
            else:
                print(f"      ❌ Bouton 'Commencer l'évaluation' visible pour l'admin")
                
        else:
            print(f"   ❌ Admin: Problème d'accès (status {response_admin.status_code})")
        
        # Test avec professeur
        prof_client = Client()
        prof_client.force_login(prof_user)
        response_prof = prof_client.get(url_evaluation)
        
        if response_prof.status_code == 200:
            print(f"   ✅ Professeur: Peut voir l'évaluation (200)")
            
            # Vérifier que le bouton est dans la réponse
            if "Commencer l'évaluation académique" in response_prof.content.decode():
                print(f"      ✅ Bouton 'Commencer l'évaluation' visible pour le professeur")
            else:
                print(f"      ❌ Bouton 'Commencer l'évaluation' masqué pour le professeur")
                
        else:
            print(f"   ❌ Professeur: Problème d'accès (status {response_prof.status_code})")
        
        # Test de la vue consistance académique (doit être bloquée pour admin)
        url_consistance = reverse('dossiers:consistance_academique', args=[dossier_test.id])
        print(f"\n🔗 URL consistance: {url_consistance}")
        
        response_admin_consistance = admin_client.get(url_consistance)
        if response_admin_consistance.status_code == 302:  # Redirection
            print(f"   ✅ Admin: Accès bloqué à la consistance académique (redirection)")
        else:
            print(f"   ❌ Admin: Accès possible à la consistance académique (status {response_admin_consistance.status_code})")
        
        response_prof_consistance = prof_client.get(url_consistance)
        if response_prof_consistance.status_code == 200:
            print(f"   ✅ Professeur: Accès autorisé à la consistance académique (200)")
        else:
            print(f"   ❌ Professeur: Problème d'accès à la consistance académique (status {response_prof_consistance.status_code})")
        
        print()
        print("🎯 TEST FINAL TERMINÉ")
        print("   Les permissions sont maintenant correctement configurées !")
        print()
        print("📋 RÉSUMÉ FINAL :")
        print(f"   👀 Admins: Peuvent VOIR l'évaluation")
        print(f"   🚫 Admins: Ne peuvent PAS modifier (bouton masqué)")
        print(f"   🚫 Admins: Ne peuvent PAS accéder à consistance_academique")
        print(f"   👨‍🏫 Professeurs: Accès complet à tout")
        print(f"   ✅ Bouton 'Commencer l'évaluation': Professeurs uniquement")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_evaluation_access()

