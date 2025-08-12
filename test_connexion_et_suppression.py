#!/usr/bin/env python
"""
Test de connexion et suppression directe
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

def test_connexion_utilisateur():
    """Vérifier l'état de connexion"""
    print("=== Test de Connexion ===")
    
    try:
        # Créer un utilisateur de test
        user = CustomUser.objects.create_user(
            username='test_user_suppression',
            email='test@example.com',
            password='testpass123',
            role='professeur'
        )
        
        print(f"✅ Utilisateur créé: {user.username} (rôle: {user.role})")
        
        # Créer un client et se connecter
        client = Client()
        login_success = client.login(username='test_user_suppression', password='testpass123')
        
        print(f"✅ Connexion réussie: {login_success}")
        
        # Tester l'accès à la page de gestion
        response = client.get(reverse('dossiers:gestion_dossiers'))
        print(f"✅ Accès gestion_dossiers: {response.status_code}")
        
        return client, user
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return None, None

def test_suppression_directe(client, user):
    """Test de suppression directe"""
    print("\n=== Test de Suppression Directe ===")
    
    try:
        # Créer un dossier de test
        dossier = Dossier.objects.create(
            titre="Dossier test suppression directe",
            description="Test de suppression directe",
            statut='non_traite'
        )
        
        dossier_id = dossier.id
        print(f"✅ Dossier créé avec ID: {dossier_id}")
        
        # Tester l'URL de suppression
        url = reverse('dossiers:supprimer_dossier', args=[dossier_id])
        print(f"✅ URL de suppression: {url}")
        
        # Faire une requête POST avec CSRF
        response = client.post(url, {
            'csrfmiddlewaretoken': 'test_token'
        })
        
        print(f"✅ Code de réponse: {response.status_code}")
        
        if response.status_code == 302:  # Redirection
            print(f"✅ Redirection vers: {response.url}")
        elif response.status_code == 200:
            print("✅ Page affichée (pas de redirection)")
        else:
            print(f"⚠️ Code inattendu: {response.status_code}")
        
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

def test_acces_page_gestion():
    """Tester l'accès à la page de gestion"""
    print("\n=== Test Accès Page Gestion ===")
    
    try:
        client = Client()
        
        # Test sans connexion
        response = client.get(reverse('dossiers:gestion_dossiers'))
        print(f"✅ Sans connexion: {response.status_code}")
        
        if response.status_code == 302:
            print(f"✅ Redirection vers: {response.url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_dossiers_disponibles():
    """Lister les dossiers disponibles"""
    print("\n=== Dossiers Disponibles ===")
    
    try:
        dossiers = Dossier.objects.all().order_by('id')
        print(f"✅ Nombre total de dossiers: {dossiers.count()}")
        
        if dossiers.count() > 0:
            print("📋 Dossiers disponibles:")
            for dossier in dossiers[:5]:  # Afficher les 5 premiers
                print(f"  - ID {dossier.id}: {dossier.titre}")
            
            if dossiers.count() > 5:
                print(f"  ... et {dossiers.count() - 5} autres")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Test de Connexion et Suppression")
    print("=" * 60)
    
    # Tests
    tests = [
        ("Accès page gestion", test_acces_page_gestion),
        ("Dossiers disponibles", test_dossiers_disponibles),
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
    
    # Test de connexion et suppression
    print(f"\n🧪 Test: Connexion et Suppression")
    print("-" * 40)
    
    client, user = test_connexion_utilisateur()
    if client and user:
        result = test_suppression_directe(client, user)
        results.append(("Connexion et Suppression", result))
    else:
        results.append(("Connexion et Suppression", False))
    
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
        print("\n🔧 Diagnostic du problème :")
        print("1. Vérifiez que vous êtes connecté")
        print("2. Videz le cache du navigateur (Ctrl+F5)")
        print("3. Vérifiez les logs du serveur")
        print("4. Essayez un autre navigateur")
    else:
        print("⚠️ Certains tests ont échoué.")
        print("Vérifiez les problèmes identifiés ci-dessus.")
    
    print("\n📝 Instructions de test manuel :")
    print("1. Allez sur http://localhost:8000/dossiers/gestion/")
    print("2. Vérifiez que vous voyez la liste des dossiers")
    print("3. Cliquez sur le bouton rouge (poubelle)")
    print("4. Confirmez la suppression")
    print("5. Vérifiez que le dossier disparaît")
    
    print("\n" + "=" * 60) 