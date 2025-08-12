#!/usr/bin/env python
"""
Test simple du bouton de suppression
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

def test_creation_et_suppression():
    """Test simple de création et suppression"""
    print("=== Test Création et Suppression ===")
    
    try:
        # Créer un dossier de test
        dossier = Dossier.objects.create(
            titre="Dossier test bouton",
            description="Test du bouton de suppression",
            statut='non_traite'
        )
        
        dossier_id = dossier.id
        print(f"✅ Dossier créé: ID {dossier_id}")
        
        # Vérifier qu'il existe
        dossier_verif = Dossier.objects.get(id=dossier_id)
        print(f"✅ Dossier vérifié: {dossier_verif.titre}")
        
        # Supprimer directement
        dossier_verif.delete()
        print("✅ Dossier supprimé directement")
        
        # Vérifier qu'il n'existe plus
        try:
            Dossier.objects.get(id=dossier_id)
            print("❌ Erreur: Le dossier existe encore")
            return False
        except Dossier.DoesNotExist:
            print("✅ Confirmation: Le dossier a bien été supprimé")
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_via_url():
    """Test via l'URL de suppression"""
    print("\n=== Test via URL ===")
    
    try:
        # Créer un utilisateur de test
        user = CustomUser.objects.create_user(
            username='test_user_bouton',
            email='test_bouton@example.com',
            password='testpass123',
            role='professeur'
        )
        
        print(f"✅ Utilisateur créé: {user.username}")
        
        # Créer un dossier de test
        dossier = Dossier.objects.create(
            titre="Dossier test URL",
            description="Test via URL",
            statut='non_traite'
        )
        
        dossier_id = dossier.id
        print(f"✅ Dossier créé: ID {dossier_id}")
        
        # Créer un client et se connecter
        client = Client()
        login_success = client.login(username='test_user_bouton', password='testpass123')
        print(f"✅ Connexion: {login_success}")
        
        # Tester l'URL de suppression
        url = reverse('dossiers:supprimer_dossier', args=[dossier_id])
        print(f"✅ URL: {url}")
        
        # Faire une requête POST
        response = client.post(url, {
            'csrfmiddlewaretoken': 'test_token'
        })
        
        print(f"✅ Code réponse: {response.status_code}")
        
        if response.status_code == 302:
            print(f"✅ Redirection vers: {response.url}")
        elif response.status_code == 200:
            print("✅ Page affichée")
        else:
            print(f"⚠️ Code inattendu: {response.status_code}")
        
        # Vérifier si le dossier a été supprimé
        try:
            Dossier.objects.get(id=dossier_id)
            print("❌ Le dossier existe encore")
            return False
        except Dossier.DoesNotExist:
            print("✅ Le dossier a été supprimé via URL")
            return True
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_acces_page():
    """Test d'accès à la page de gestion"""
    print("\n=== Test Accès Page ===")
    
    try:
        client = Client()
        
        # Test sans connexion
        response = client.get(reverse('dossiers:gestion_dossiers'))
        print(f"✅ Sans connexion: {response.status_code}")
        
        if response.status_code == 302:
            print(f"✅ Redirection vers: {response.url}")
        
        # Créer un utilisateur et se connecter
        user = CustomUser.objects.create_user(
            username='test_access',
            email='test_access@example.com',
            password='testpass123',
            role='professeur'
        )
        
        login_success = client.login(username='test_access', password='testpass123')
        print(f"✅ Connexion réussie: {login_success}")
        
        # Test avec connexion
        response = client.get(reverse('dossiers:gestion_dossiers'))
        print(f"✅ Avec connexion: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Page accessible")
            return True
        else:
            print(f"⚠️ Code inattendu: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Test Simple du Bouton")
    print("=" * 50)
    
    # Tests
    tests = [
        ("Création et suppression directe", test_creation_et_suppression),
        ("Accès à la page", test_acces_page),
        ("Suppression via URL", test_via_url),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Test: {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            results.append((test_name, False))
    
    # Résultats
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ OK" if result else "❌ ÉCHEC"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 Tous les tests sont passés !")
        print("\n🔧 Le problème pourrait être :")
        print("1. Vous n'êtes pas connecté")
        print("2. Cache du navigateur")
        print("3. Problème de session")
        print("\n📝 Solutions :")
        print("1. Connectez-vous d'abord")
        print("2. Videz le cache (Ctrl+F5)")
        print("3. Essayez un autre navigateur")
    else:
        print("⚠️ Certains tests ont échoué.")
        print("Vérifiez les problèmes identifiés ci-dessus.")
    
    print("\n📋 Instructions :")
    print("1. Allez sur http://localhost:8000/")
    print("2. Connectez-vous")
    print("3. Allez sur http://localhost:8000/dossiers/gestion/")
    print("4. Cliquez sur le bouton rouge")
    print("5. Confirmez la suppression")
    
    print("\n" + "=" * 50) 