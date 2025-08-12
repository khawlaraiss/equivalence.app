#!/usr/bin/env python
"""
Test simple pour vérifier le bouton de suppression des dossiers
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier
from users.models import CustomUser

def test_template_suppression():
    """Test du template de suppression"""
    print("=== Test du template de suppression ===")
    
    # Lire le template pour vérifier les éléments nécessaires
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
        
        # Vérifier la soumission du formulaire
        if 'form.submit()' in content:
            print("✅ Soumission de formulaire trouvée")
        else:
            print("❌ Soumission de formulaire manquante")
            return False
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Template non trouvé : {template_path}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du template : {str(e)}")
        return False

def test_admin_dashboard_template():
    """Test du template admin_dashboard"""
    print("\n=== Test du template admin_dashboard ===")
    
    template_path = "templates/dossiers/admin_dashboard.html"
    
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
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Template non trouvé : {template_path}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du template : {str(e)}")
        return False

def test_url_patterns():
    """Test des patterns d'URL"""
    print("\n=== Test des patterns d'URL ===")
    
    template_path = "dossiers/urls.py"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier la présence de l'URL de suppression
        if 'supprimer_dossier' in content:
            print("✅ URL de suppression trouvée dans urls.py")
        else:
            print("❌ URL de suppression manquante dans urls.py")
            return False
        
        # Vérifier la vue associée
        if 'views.supprimer_dossier' in content:
            print("✅ Vue supprimer_dossier associée")
        else:
            print("❌ Vue supprimer_dossier non associée")
            return False
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Fichier urls.py non trouvé : {template_path}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier : {str(e)}")
        return False

def test_view_function():
    """Test de la fonction de vue"""
    print("\n=== Test de la fonction de vue ===")
    
    template_path = "dossiers/views.py"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier la présence de la fonction
        if 'def supprimer_dossier(' in content:
            print("✅ Fonction supprimer_dossier trouvée")
        else:
            print("❌ Fonction supprimer_dossier manquante")
            return False
        
        # Vérifier la gestion des permissions
        if 'request.user.role != \'admin\'' in content:
            print("✅ Vérification des permissions admin")
        else:
            print("❌ Vérification des permissions admin manquante")
            return False
        
        # Vérifier la suppression des pièces jointes
        if 'pieces_jointes.all().delete()' in content:
            print("✅ Suppression des pièces jointes")
        else:
            print("❌ Suppression des pièces jointes manquante")
            return False
        
        # Vérifier la suppression du dossier
        if 'dossier.delete()' in content:
            print("✅ Suppression du dossier")
        else:
            print("❌ Suppression du dossier manquante")
            return False
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Fichier views.py non trouvé : {template_path}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier : {str(e)}")
        return False

def test_database_suppression():
    """Test de suppression en base de données"""
    print("\n=== Test de suppression en base de données ===")
    
    # Créer un dossier de test
    try:
        dossier = Dossier.objects.create(
            titre="Dossier de test pour suppression DB",
            description="Test de suppression en base de données",
            statut='non_traite'
        )
        
        dossier_id = dossier.id
        print(f"✅ Dossier de test créé (ID: {dossier_id})")
        
        # Supprimer le dossier
        dossier.delete()
        print("✅ Dossier supprimé")
        
        # Vérifier que le dossier n'existe plus
        try:
            Dossier.objects.get(id=dossier_id)
            print("❌ Erreur : Le dossier existe encore après suppression")
            return False
        except Dossier.DoesNotExist:
            print("✅ Confirmation : Le dossier a bien été supprimé")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test de suppression : {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Test simple du bouton de suppression des dossiers")
    print("=" * 60)
    
    # Tests des templates
    template_ok = test_template_suppression()
    admin_template_ok = test_admin_dashboard_template()
    
    # Tests des URLs et vues
    urls_ok = test_url_patterns()
    view_ok = test_view_function()
    
    # Test de la base de données
    db_ok = test_database_suppression()
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 60)
    
    if template_ok:
        print("✅ Template gestion_dossiers : OK")
    else:
        print("❌ Template gestion_dossiers : ÉCHEC")
    
    if admin_template_ok:
        print("✅ Template admin_dashboard : OK")
    else:
        print("❌ Template admin_dashboard : ÉCHEC")
    
    if urls_ok:
        print("✅ Patterns d'URL : OK")
    else:
        print("❌ Patterns d'URL : ÉCHEC")
    
    if view_ok:
        print("✅ Fonction de vue : OK")
    else:
        print("❌ Fonction de vue : ÉCHEC")
    
    if db_ok:
        print("✅ Suppression en base : OK")
    else:
        print("❌ Suppression en base : ÉCHEC")
    
    all_tests_passed = template_ok and admin_template_ok and urls_ok and view_ok and db_ok
    
    if all_tests_passed:
        print("\n🎉 Tous les tests sont passés avec succès !")
        print("Le bouton de suppression devrait fonctionner correctement.")
    else:
        print("\n⚠️ Certains tests ont échoué.")
        print("Vérifiez les problèmes identifiés ci-dessus.")
    
    print("\n" + "=" * 60) 