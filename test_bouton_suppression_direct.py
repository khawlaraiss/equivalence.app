#!/usr/bin/env python
"""
Test direct pour diagnostiquer le problème du bouton de suppression
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

def test_suppression_direct():
    """Test direct de la suppression via l'URL"""
    print("=== Test Direct de Suppression ===")
    
    try:
        # Créer un dossier de test
        dossier = Dossier.objects.create(
            titre="Dossier de test pour suppression directe",
            description="Test de suppression directe",
            statut='non_traite'
        )
        
        dossier_id = dossier.id
        print(f"✅ Dossier créé avec ID: {dossier_id}")
        
        # Créer un client de test
        client = Client()
        
        # Créer un utilisateur admin
        admin_user = CustomUser.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
        print(f"✅ Utilisateur admin créé: {admin_user.username}")
        
        # Se connecter
        login_success = client.login(username='admin_test', password='testpass123')
        print(f"✅ Connexion réussie: {login_success}")
        
        # Tester l'URL de suppression
        url = reverse('dossiers:supprimer_dossier', args=[dossier_id])
        print(f"✅ URL de suppression: {url}")
        
        # Faire une requête POST
        response = client.post(url, {
            'csrfmiddlewaretoken': 'test_token'
        })
        
        print(f"✅ Code de réponse: {response.status_code}")
        print(f"✅ URL de redirection: {response.url if hasattr(response, 'url') else 'Aucune'}")
        
        # Vérifier si le dossier a été supprimé
        try:
            Dossier.objects.get(id=dossier_id)
            print("❌ Le dossier existe encore après suppression")
            return False
        except Dossier.DoesNotExist:
            print("✅ Le dossier a bien été supprimé")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

def test_template_rendering():
    """Test du rendu du template"""
    print("\n=== Test du Rendu du Template ===")
    
    try:
        client = Client()
        
        # Créer un utilisateur admin
        admin_user = CustomUser.objects.create_user(
            username='admin_template',
            email='admin_template@test.com',
            password='testpass123',
            role='admin'
        )
        
        # Se connecter
        client.login(username='admin_template', password='testpass123')
        
        # Tester la page de gestion des dossiers
        response = client.get(reverse('dossiers:gestion_dossiers'))
        
        print(f"✅ Code de réponse: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Vérifier les éléments clés
            checks = [
                ('Token CSRF', 'csrfmiddlewaretoken'),
                ('Fonction JavaScript', 'function supprimerDossier'),
                ('Bouton de suppression', 'btn-outline-danger'),
                ('Icone poubelle', 'fas fa-trash'),
            ]
            
            for check_name, check_value in checks:
                if check_value in content:
                    print(f"  ✅ {check_name} présent")
                else:
                    print(f"  ❌ {check_name} manquant")
                    return False
            
            return True
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

def test_user_permissions():
    """Test des permissions utilisateur"""
    print("\n=== Test des Permissions Utilisateur ===")
    
    try:
        # Créer différents types d'utilisateurs
        admin_user = CustomUser.objects.create_user(
            username='admin_perm',
            email='admin_perm@test.com',
            password='testpass123',
            role='admin'
        )
        
        prof_user = CustomUser.objects.create_user(
            username='prof_perm',
            email='prof_perm@test.com',
            password='testpass123',
            role='professeur'
        )
        
        # Créer un dossier de test
        dossier = Dossier.objects.create(
            titre="Dossier test permissions",
            description="Test des permissions",
            statut='non_traite'
        )
        
        client = Client()
        
        # Test avec admin
        client.login(username='admin_perm', password='testpass123')
        response = client.get(reverse('dossiers:gestion_dossiers'))
        print(f"✅ Admin - Code: {response.status_code}")
        
        # Test avec professeur
        client.login(username='prof_perm', password='testpass123')
        response = client.get(reverse('dossiers:gestion_dossiers'))
        print(f"✅ Professeur - Code: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

def test_url_patterns():
    """Test des patterns d'URL"""
    print("\n=== Test des Patterns d'URL ===")
    
    try:
        from django.urls import reverse, NoReverseMatch
        
        # Tester l'URL de suppression
        try:
            url = reverse('dossiers:supprimer_dossier', args=[1])
            print(f"✅ URL de suppression: {url}")
        except NoReverseMatch as e:
            print(f"❌ Erreur URL: {str(e)}")
            return False
        
        # Tester l'URL de gestion
        try:
            url = reverse('dossiers:gestion_dossiers')
            print(f"✅ URL de gestion: {url}")
        except NoReverseMatch as e:
            print(f"❌ Erreur URL: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Test Direct du Bouton de Suppression")
    print("=" * 60)
    
    # Tests
    tests = [
        ("Patterns d'URL", test_url_patterns),
        ("Permissions utilisateur", test_user_permissions),
        ("Rendu du template", test_template_rendering),
        ("Suppression directe", test_suppression_direct),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Test: {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur lors du test: {str(e)}")
            results.append((test_name, False))
    
    # Résultats finaux
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DU DIAGNOSTIC")
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
        print("Le problème pourrait être dans le navigateur ou le cache.")
        print("\n🔧 Solutions à essayer:")
        print("1. Videz le cache du navigateur (Ctrl+F5)")
        print("2. Essayez un autre navigateur")
        print("3. Vérifiez la console du navigateur (F12)")
        print("4. Vérifiez que JavaScript est activé")
    else:
        print("⚠️ Certains tests ont échoué.")
        print("Vérifiez les problèmes identifiés ci-dessus.")
    
    print("\n" + "=" * 60) 