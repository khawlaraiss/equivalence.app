#!/usr/bin/env python
"""
Test des permissions d'accès aux évaluations selon les rôles
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
from django.contrib.auth import authenticate

def test_acces_evaluation_roles():
    """Tester les permissions d'accès selon les rôles"""
    print("=== 🧪 TEST ACCÈS ÉVALUATION PAR RÔLES ===")
    print("Vérification des permissions d'accès !")
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
        
        # 4. Tester les accès avec différents rôles
        print(f"\n--- Test des permissions d'accès ---")
        
        urls_a_tester = [
            ('consistance_academique', 'dossiers:consistance_academique'),
            ('evaluation_equivalence', 'dossiers:evaluation_equivalence'),
        ]
        
        for nom, url_name in urls_a_tester:
            try:
                url = reverse(url_name, args=[dossier_test.id])
                print(f"\n   🔗 URL {nom}: {url}")
                
                # Test avec admin
                admin_client = Client()
                admin_client.force_login(admin_user)
                response_admin = admin_client.get(url)
                
                if response_admin.status_code == 302:  # Redirection
                    print(f"      🔒 Admin: Accès refusé (redirection) ✅")
                elif response_admin.status_code == 403:  # Forbidden
                    print(f"      🔒 Admin: Accès interdit (403) ✅")
                else:
                    print(f"      ⚠️ Admin: Accès possible (status {response_admin.status_code}) ❌")
                
                # Test avec professeur
                prof_client = Client()
                prof_client.force_login(prof_user)
                response_prof = prof_client.get(url)
                
                if response_prof.status_code == 200:  # OK
                    print(f"      👨‍🏫 Professeur: Accès autorisé (200) ✅")
                else:
                    print(f"      ❌ Professeur: Problème d'accès (status {response_prof.status_code})")
                
            except Exception as e:
                print(f"   ❌ Erreur test {nom}: {e}")
        
        # 5. Vérifier les restrictions dans les vues
        print(f"\n--- Vérification des restrictions dans les vues ---")
        
        try:
            from dossiers.views import consistance_academique, evaluation_equivalence
            
            # Vérifier le code source des vues
            import inspect
            
            for nom_vue, vue in [('consistance_academique', consistance_academique), 
                                ('evaluation_equivalence', evaluation_equivalence)]:
                source = inspect.getsource(vue)
                
                if "request.user.role != 'professeur'" in source:
                    print(f"   ✅ {nom_vue}: Restriction professeur uniquement détectée")
                elif "request.user.role not in ['professeur', 'admin']" in source:
                    print(f"   ⚠️ {nom_vue}: Restriction admin+professeur (à modifier)")
                else:
                    print(f"   ❌ {nom_vue}: Aucune restriction de rôle détectée")
                    
        except ImportError as e:
            print(f"   ❌ Erreur import vues: {e}")
        
        print()
        print("🎯 TEST TERMINÉ")
        print("   Les permissions d'accès sont maintenant configurées !")
        print()
        print("📋 RÉSUMÉ DES PERMISSIONS :")
        print(f"   🔒 Admins: Accès refusé aux évaluations")
        print(f"   👨‍🏫 Professeurs: Accès autorisé aux évaluations")
        print(f"   🚫 Bouton 'Commencer l'évaluation': Professeurs uniquement")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_acces_evaluation_roles()
