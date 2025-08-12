#!/usr/bin/env python
"""
Script de test pour vérifier le bouton de suppression dans l'interface web
"""

import os
import sys
import django
import requests
from bs4 import BeautifulSoup

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier
from users.models import CustomUser

def test_interface_suppression():
    """Test de l'interface de suppression via le web"""
    print("=== Test de l'interface de suppression ===")
    
    # Créer un utilisateur admin de test
    admin, created = CustomUser.objects.get_or_create(
        username='admin_test_web',
        defaults={
            'email': 'admin_web@test.com',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created:
        admin.set_password('test123')
        admin.save()
        print("✅ Utilisateur admin de test créé")
    else:
        print("ℹ️ Utilisateur admin de test existe déjà")
    
    # Créer un dossier de test
    dossier = Dossier.objects.create(
        titre="Dossier de test pour interface web",
        description="Ce dossier est créé pour tester le bouton de suppression dans l'interface web",
        statut='non_traite'
    )
    
    print(f"✅ Dossier de test créé : {dossier.titre} (ID: {dossier.id})")
    
    # Simuler une session web
    session = requests.Session()
    
    # URL de base (ajustez selon votre configuration)
    base_url = "http://localhost:8000"
    
    try:
        # 1. Se connecter
        print("🔐 Tentative de connexion...")
        login_url = f"{base_url}/users/login/"
        login_data = {
            'username': 'admin_test_web',
            'password': 'test123'
        }
        
        response = session.post(login_url, data=login_data)
        
        if response.status_code == 200:
            print("✅ Connexion réussie")
        else:
            print(f"❌ Échec de connexion (status: {response.status_code})")
            return False
        
        # 2. Accéder à la page de gestion des dossiers
        print("📄 Accès à la page de gestion des dossiers...")
        gestion_url = f"{base_url}/dossiers/gestion/"
        response = session.get(gestion_url)
        
        if response.status_code == 200:
            print("✅ Page de gestion accessible")
            
            # Analyser le HTML pour vérifier la présence du bouton de suppression
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Chercher le bouton de suppression pour notre dossier
            bouton_suppression = soup.find('button', {
                'onclick': f'supprimerDossier({dossier.id})'
            })
            
            if bouton_suppression:
                print("✅ Bouton de suppression trouvé dans l'interface")
                
                # Vérifier la présence du token CSRF
                csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
                if csrf_token:
                    print("✅ Token CSRF présent")
                else:
                    print("❌ Token CSRF manquant")
                    return False
                
                # 3. Tester la suppression via POST
                print("🗑️ Test de suppression via POST...")
                supprimer_url = f"{base_url}/dossiers/dossier/{dossier.id}/supprimer/"
                
                # Récupérer le token CSRF
                csrf_value = csrf_token.get('value')
                
                supprimer_data = {
                    'csrfmiddlewaretoken': csrf_value
                }
                
                response = session.post(supprimer_url, data=supprimer_data)
                
                if response.status_code == 302:  # Redirection après suppression
                    print("✅ Suppression réussie (redirection détectée)")
                    
                    # Vérifier que le dossier a bien été supprimé
                    try:
                        Dossier.objects.get(id=dossier.id)
                        print("❌ Erreur : Le dossier existe encore après suppression")
                        return False
                    except Dossier.DoesNotExist:
                        print("✅ Confirmation : Le dossier a bien été supprimé")
                        return True
                else:
                    print(f"❌ Échec de suppression (status: {response.status_code})")
                    return False
            else:
                print("❌ Bouton de suppression non trouvé dans l'interface")
                return False
        else:
            print(f"❌ Impossible d'accéder à la page de gestion (status: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur. Assurez-vous que le serveur Django est démarré.")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test : {str(e)}")
        return False

def test_javascript_suppression():
    """Test du JavaScript de suppression"""
    print("\n=== Test du JavaScript de suppression ===")
    
    # Lire le template pour vérifier le JavaScript
    template_path = "templates/dossiers/gestion_dossiers.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier la présence de la fonction JavaScript
        if 'function supprimerDossier(id)' in content:
            print("✅ Fonction JavaScript supprimerDossier trouvée")
        else:
            print("❌ Fonction JavaScript supprimerDossier manquante")
            return False
        
        # Vérifier la présence du token CSRF
        if 'csrfmiddlewaretoken' in content:
            print("✅ Token CSRF présent dans le template")
        else:
            print("❌ Token CSRF manquant dans le template")
            return False
        
        # Vérifier la création du formulaire
        if 'document.createElement(\'form\')' in content:
            print("✅ Création de formulaire dynamique trouvée")
        else:
            print("❌ Création de formulaire dynamique manquante")
            return False
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Template non trouvé : {template_path}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du template : {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Test complet du bouton de suppression des dossiers")
    print("=" * 60)
    
    # Test du JavaScript
    js_ok = test_javascript_suppression()
    
    # Test de l'interface web
    web_ok = test_interface_suppression()
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 60)
    
    if js_ok:
        print("✅ JavaScript de suppression : OK")
    else:
        print("❌ JavaScript de suppression : ÉCHEC")
    
    if web_ok:
        print("✅ Interface web de suppression : OK")
    else:
        print("❌ Interface web de suppression : ÉCHEC")
    
    if js_ok and web_ok:
        print("\n🎉 Tous les tests sont passés avec succès !")
        print("Le bouton de suppression fonctionne correctement.")
    else:
        print("\n⚠️ Certains tests ont échoué.")
        print("Vérifiez les problèmes identifiés ci-dessus.")
    
    print("\n" + "=" * 60) 