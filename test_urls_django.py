#!/usr/bin/env python
"""
Test des URLs Django
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

def test_urls_django():
    """Tester les URLs Django"""
    print("=== 🔗 TEST URLS DJANGO ===")
    print("Vérification des URLs et de la configuration !")
    print()
    
    try:
        # 1. Vérifier la configuration Django
        from django.conf import settings
        print(f"✅ Django configuré")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   SECRET_KEY: {'Défini' if settings.SECRET_KEY else 'Non défini'}")
        
        # 2. Vérifier les URLs principales
        from django.urls import reverse
        print(f"\n--- URLs principales ---")
        
        try:
            url_login = reverse('users:login')
            print(f"✅ Login: {url_login}")
        except Exception as e:
            print(f"❌ Login: {e}")
        
        try:
            url_gestion = reverse('users:gestion_utilisateurs')
            print(f"✅ Gestion utilisateurs: {url_gestion}")
        except Exception as e:
            print(f"❌ Gestion utilisateurs: {e}")
        
        try:
            url_dashboard = reverse('dossiers:dashboard')
            print(f"✅ Dashboard: {url_dashboard}")
        except Exception as e:
            print(f"❌ Dashboard: {e}")
        
        # 3. Vérifier l'URL de désactivation
        print(f"\n--- URL de désactivation ---")
        try:
            # Tester avec un ID fictif
            url_desactivation = reverse('users:desactiver_utilisateur', args=[999])
            print(f"✅ Désactivation: {url_desactivation}")
            
            # Vérifier le pattern
            if '999' in url_desactivation:
                print(f"✅ Pattern URL correct")
            else:
                print(f"⚠️ Pattern URL incorrect")
                
        except Exception as e:
            print(f"❌ Désactivation: {e}")
        
        # 4. Vérifier les modèles
        print(f"\n--- Vérification des modèles ---")
        from users.models import CustomUser
        
        try:
            users_count = CustomUser.objects.count()
            print(f"✅ CustomUser: {users_count} utilisateurs")
            
            # Lister quelques utilisateurs
            users_sample = CustomUser.objects.all()[:5]
            for user in users_sample:
                print(f"   - {user.username}: {user.get_role_display()} - {'Actif' if user.is_active else 'Inactif'}")
                
        except Exception as e:
            print(f"❌ CustomUser: {e}")
        
        # 5. Vérifier la vue de désactivation
        print(f"\n--- Vérification de la vue ---")
        try:
            from users.views import desactiver_utilisateur
            print(f"✅ Vue 'desactiver_utilisateur' trouvée")
            
            # Vérifier les décorateurs
            import inspect
            sig = inspect.signature(desactiver_utilisateur)
            print(f"   Signature: {sig}")
            
            # Vérifier si c'est une fonction ou une méthode
            if hasattr(desactiver_utilisateur, '__name__'):
                print(f"   Nom: {desactiver_utilisateur.__name__}")
            else:
                print(f"   Type: {type(desactiver_utilisateur)}")
                
        except ImportError as e:
            print(f"❌ Vue non trouvée: {e}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # 6. Instructions de test
        print(f"\n--- Instructions de test ---")
        print(f"1. Démarrez le serveur Django:")
        print(f"   python manage.py runserver")
        print(f"")
        print(f"2. Testez dans le navigateur:")
        print(f"   - http://localhost:8000/users/login/")
        print(f"   - http://localhost:8000/users/gestion/")
        print(f"")
        print(f"3. Vérifiez que le bouton de désactivation:")
        print(f"   - S'affiche correctement")
        print(f"   - Affiche une confirmation au clic")
        print(f"   - Envoie une requête POST")
        
        print()
        print("🎯 TEST TERMINÉ")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_urls_django()

