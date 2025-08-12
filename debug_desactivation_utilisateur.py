#!/usr/bin/env python
"""
Débogage de la désactivation d'utilisateur
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from users.models import CustomUser
from django.urls import reverse
from django.test import Client
from django.contrib.auth import authenticate

def debug_desactivation_utilisateur():
    """Déboguer la désactivation d'utilisateur"""
    print("=== 🔍 DÉBOGAGE DÉSACTIVATION UTILISATEUR ===")
    print("Vérification étape par étape !")
    print()
    
    try:
        # 1. Vérifier les utilisateurs
        utilisateurs = CustomUser.objects.all()
        total = utilisateurs.count()
        print(f"📊 Total utilisateurs: {total}")
        
        if total == 0:
            print("❌ Aucun utilisateur trouvé")
            return
        
        # 2. Trouver un utilisateur admin pour le test
        admin_user = utilisateurs.filter(role='admin', is_active=True).first()
        if not admin_user:
            print("❌ Aucun admin actif trouvé")
            return
            
        print(f"🔍 Admin de test: {admin_user.username} (ID: {admin_user.id})")
        print(f"   Email: {admin_user.email}")
        print(f"   Rôle: {admin_user.get_role_display()}")
        print(f"   Statut: {'Actif' if admin_user.is_active else 'Inactif'}")
        
        # 3. Trouver un utilisateur à désactiver (pas l'admin)
        utilisateur_a_desactiver = utilisateurs.exclude(id=admin_user.id).filter(is_active=True).first()
        if not utilisateur_a_desactiver:
            print("❌ Aucun utilisateur à désactiver trouvé")
            return
            
        print(f"\n🔍 Utilisateur à désactiver: {utilisateur_a_desactiver.username} (ID: {utilisateur_a_desactiver.id})")
        print(f"   Rôle: {utilisateur_a_desactiver.get_role_display()}")
        print(f"   Statut actuel: {'Actif' if utilisateur_a_desactiver.is_active else 'Inactif'}")
        
        # 4. Tester l'authentification
        print(f"\n--- Test 1: Authentification ---")
        user_auth = authenticate(username=admin_user.username, password='admin')
        if user_auth:
            print(f"✅ Authentification réussie pour {user_auth.username}")
        else:
            print(f"❌ Échec de l'authentification pour {admin_user.username}")
            # Essayer avec un mot de passe vide
            user_auth = authenticate(username=admin_user.username, password='')
            if user_auth:
                print(f"⚠️ Authentification réussie avec mot de passe vide")
            else:
                print(f"❌ Impossible d'authentifier l'admin")
                return
        
        # 5. Tester la vue directement
        print(f"\n--- Test 2: Test de la vue ---")
        try:
            from users.views import desactiver_utilisateur
            print(f"✅ Vue 'desactiver_utilisateur' importée avec succès")
            
            # Simuler une requête
            from django.test import RequestFactory
            from django.contrib.messages.storage.fallback import FallbackStorage
            from django.contrib.auth.models import AnonymousUser
            
            factory = RequestFactory()
            request = factory.post(f'/users/utilisateur/{utilisateur_a_desactiver.id}/desactiver/')
            
            # Simuler l'utilisateur connecté
            request.user = admin_user
            
            # Ajouter les messages
            setattr(request, 'session', {})
            messages = FallbackStorage(request)
            setattr(request, '_messages', messages)
            
            print(f"✅ Requête simulée créée")
            print(f"   URL: {request.path}")
            print(f"   Méthode: {request.method}")
            print(f"   Utilisateur: {request.user.username}")
            
        except Exception as e:
            print(f"❌ Erreur lors du test de la vue: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # 6. Vérifier l'URL
        print(f"\n--- Test 3: Vérification de l'URL ---")
        try:
            url_desactivation = reverse('users:desactiver_utilisateur', args=[utilisateur_a_desactiver.id])
            print(f"✅ URL générée: {url_desactivation}")
            
            # Vérifier que l'URL correspond au pattern attendu
            expected_url = f'/users/utilisateur/{utilisateur_a_desactiver.id}/desactiver/'
            if url_desactivation == expected_url:
                print(f"✅ URL correspond au pattern attendu")
            else:
                print(f"⚠️ URL différente du pattern attendu")
                print(f"   Attendu: {expected_url}")
                print(f"   Obtenu: {url_desactivation}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la génération de l'URL: {str(e)}")
        
        # 7. Test de la base de données
        print(f"\n--- Test 4: Test de la base de données ---")
        try:
            # Sauvegarder l'état actuel
            ancien_statut = utilisateur_a_desactiver.is_active
            print(f"   Statut avant modification: {'Actif' if ancien_statut else 'Inactif'}")
            
            # Modifier le statut
            utilisateur_a_desactiver.is_active = False
            utilisateur_a_desactiver.save()
            
            # Recharger depuis la base
            utilisateur_a_desactiver.refresh_from_db()
            nouveau_statut = utilisateur_a_desactiver.is_active
            
            print(f"   Statut après modification: {'Actif' if nouveau_statut else 'Inactif'}")
            
            if nouveau_statut != ancien_statut:
                print(f"✅ Modification en base réussie !")
                
                # Remettre l'état initial
                utilisateur_a_desactiver.is_active = ancien_statut
                utilisateur_a_desactiver.save()
                print(f"✅ État initial restauré")
            else:
                print(f"❌ Échec de la modification en base")
                
        except Exception as e:
            print(f"❌ Erreur lors du test de la base: {str(e)}")
        
        print()
        print("🎯 DIAGNOSTIC TERMINÉ")
        print("   Vérifiez les résultats ci-dessus pour identifier le problème.")
        
    except Exception as e:
        print(f"❌ Erreur lors du débogage: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_desactivation_utilisateur()

