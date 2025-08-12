#!/usr/bin/env python
"""
Test complet pour diagnostiquer la suppression
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier
from users.models import CustomUser
from django.test import Client
from django.urls import reverse

def test_suppression_via_url():
    """Test de suppression via l'URL directement"""
    print("=== Test de Suppression via URL ===")
    
    try:
        # Créer un dossier de test
        dossier = Dossier.objects.create(
            titre="Dossier test suppression URL",
            description="Test de suppression via URL",
            statut='non_traite'
        )
        
        dossier_id = dossier.id
        print(f"✅ Dossier créé avec ID: {dossier_id}")
        
        # Créer un utilisateur admin
        admin_user = CustomUser.objects.create_user(
            username='admin_suppression',
            email='admin_suppression@test.com',
            password='testpass123',
            role='admin'
        )
        
        print(f"✅ Utilisateur admin créé: {admin_user.username}")
        
        # Créer un client et se connecter
        client = Client()
        login_success = client.login(username='admin_suppression', password='testpass123')
        print(f"✅ Connexion réussie: {login_success}")
        
        # Tester l'URL de suppression
        url = reverse('dossiers:supprimer_dossier', args=[dossier_id])
        print(f"✅ URL de suppression: {url}")
        
        # Faire une requête POST
        response = client.post(url, {
            'csrfmiddlewaretoken': 'test_token'
        })
        
        print(f"✅ Code de réponse: {response.status_code}")
        
        # Vérifier si le dossier a été supprimé
        try:
            Dossier.objects.get(id=dossier_id)
            print("❌ Le dossier existe encore après suppression")
            return False
        except Dossier.DoesNotExist:
            print("✅ Le dossier a bien été supprimé")
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_suppression_sans_admin():
    """Test de suppression sans être admin"""
    print("\n=== Test de Suppression sans Admin ===")
    
    try:
        # Créer un dossier de test
        dossier = Dossier.objects.create(
            titre="Dossier test sans admin",
            description="Test de suppression sans admin",
            statut='non_traite'
        )
        
        dossier_id = dossier.id
        print(f"✅ Dossier créé avec ID: {dossier_id}")
        
        # Créer un utilisateur non-admin
        user = CustomUser.objects.create_user(
            username='user_normal',
            email='user@test.com',
            password='testpass123',
            role='professeur'
        )
        
        print(f"✅ Utilisateur normal créé: {user.username}")
        
        # Créer un client et se connecter
        client = Client()
        login_success = client.login(username='user_normal', password='testpass123')
        print(f"✅ Connexion réussie: {login_success}")
        
        # Tester l'URL de suppression
        url = reverse('dossiers:supprimer_dossier', args=[dossier_id])
        response = client.post(url, {
            'csrfmiddlewaretoken': 'test_token'
        })
        
        print(f"✅ Code de réponse: {response.status_code}")
        
        # Vérifier si le dossier existe encore (il devrait exister car non-admin)
        try:
            Dossier.objects.get(id=dossier_id)
            print("✅ Le dossier existe encore (normal pour un non-admin)")
            return True
        except Dossier.DoesNotExist:
            print("❌ Le dossier a été supprimé (anormal pour un non-admin)")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_template_form():
    """Vérifier que le formulaire est bien dans le template"""
    print("\n=== Vérification du Formulaire dans le Template ===")
    
    try:
        with open("templates/dossiers/gestion_dossiers.html", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifications
        checks = [
            ('Formulaire POST', 'method="post"'),
            ('Action de suppression', 'supprimer_dossier'),
            ('Token CSRF', 'csrf_token'),
            ('Bouton submit', 'type="submit"'),
            ('Confirmation', 'confirm('),
        ]
        
        all_ok = True
        for check_name, check_value in checks:
            if check_value in content:
                print(f"  ✅ {check_name} présent")
            else:
                print(f"  ❌ {check_name} manquant")
                all_ok = False
        
        return all_ok
        
    except FileNotFoundError:
        print("❌ Template non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Test Complet de Suppression")
    print("=" * 60)
    
    # Tests
    tests = [
        ("Formulaire dans template", test_template_form),
        ("Suppression sans admin", test_suppression_sans_admin),
        ("Suppression avec admin", test_suppression_via_url),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Test: {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            results.append((test_name, False))
    
    # Résultats
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ OK" if result else "❌ ÉCHEC"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 Tous les tests sont passés !")
        print("Le problème pourrait être :")
        print("1. Vous n'êtes pas connecté en tant qu'administrateur")
        print("2. Cache du navigateur")
        print("3. Problème de permissions")
        print("\n🔧 Solutions :")
        print("1. Vérifiez que vous êtes connecté en tant qu'admin")
        print("2. Videz le cache (Ctrl+F5)")
        print("3. Essayez un autre navigateur")
    else:
        print("⚠️ Certains tests ont échoué.")
        print("Vérifiez les problèmes identifiés ci-dessus.")
    
    print("\n" + "=" * 60) 