#!/usr/bin/env python
"""
Test du serveur Django
"""

import os
import sys
import django
import requests
import time

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

def test_serveur_django():
    """Tester si le serveur Django fonctionne"""
    print("=== 🌐 TEST SERVEUR DJANGO ===")
    print("Vérification que le serveur répond !")
    print()
    
    try:
        # 1. Vérifier que Django est configuré
        from django.conf import settings
        print(f"✅ Django configuré")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        # 2. Vérifier les URLs
        from django.urls import reverse
        try:
            url_login = reverse('users:login')
            print(f"✅ URL login: {url_login}")
        except Exception as e:
            print(f"❌ Erreur URL login: {e}")
        
        try:
            url_gestion = reverse('users:gestion_utilisateurs')
            print(f"✅ URL gestion: {url_gestion}")
        except Exception as e:
            print(f"❌ Erreur URL gestion: {e}")
        
        # 3. Tester la connexion au serveur
        print(f"\n--- Test de connexion au serveur ---")
        base_url = "http://localhost:8000"
        
        try:
            # Test de la page d'accueil
            response = requests.get(f"{base_url}/", timeout=5)
            print(f"✅ Page d'accueil accessible (code: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"❌ Impossible de se connecter au serveur sur {base_url}")
            print(f"   Le serveur Django n'est peut-être pas démarré")
            print(f"   Démarrez-le avec: python manage.py runserver")
        except requests.exceptions.Timeout:
            print(f"⚠️ Timeout lors de la connexion")
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
        
        # 4. Vérifier les modèles
        print(f"\n--- Vérification des modèles ---")
        from users.models import CustomUser
        from dossiers.models import Dossier, DossierTraite
        
        try:
            users_count = CustomUser.objects.count()
            print(f"✅ Modèle CustomUser: {users_count} utilisateurs")
        except Exception as e:
            print(f"❌ Erreur modèle CustomUser: {e}")
        
        try:
            dossiers_count = Dossier.objects.count()
            print(f"✅ Modèle Dossier: {dossiers_count} dossiers")
        except Exception as e:
            print(f"❌ Erreur modèle Dossier: {e}")
        
        try:
            dossiers_traites_count = DossierTraite.objects.count()
            print(f"✅ Modèle DossierTraite: {dossiers_traites_count} dossiers traités")
        except Exception as e:
            print(f"❌ Erreur modèle DossierTraite: {e}")
        
        # 5. Instructions pour tester
        print(f"\n--- Instructions de test ---")
        print(f"1. Démarrez le serveur Django:")
        print(f"   python manage.py runserver")
        print(f"")
        print(f"2. Ouvrez votre navigateur et allez sur:")
        print(f"   http://localhost:8000/users/login/")
        print(f"")
        print(f"3. Connectez-vous avec un compte admin")
        print(f"4. Allez sur 'Gestion des Utilisateurs'")
        print(f"5. Testez le bouton de désactivation")
        
        print()
        print("🎯 TEST TERMINÉ")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_serveur_django()

