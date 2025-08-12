#!/usr/bin/env python
"""
Test final pour vérifier le bouton de suppression après résolution des migrations
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier
from users.models import CustomUser

def test_suppression_complete():
    """Test complet de suppression d'un dossier"""
    print("=== Test complet de suppression ===")
    
    try:
        # Créer un dossier de test
        dossier = Dossier.objects.create(
            titre="Dossier de test final après migrations",
            description="Test du bouton de suppression après résolution des migrations",
            statut='non_traite'
        )
        
        dossier_id = dossier.id
        print(f"✅ Dossier créé avec ID: {dossier_id}")
        
        # Vérifier que le dossier existe
        dossier_verif = Dossier.objects.get(id=dossier_id)
        print(f"✅ Dossier vérifié: {dossier_verif.titre}")
        
        # Supprimer le dossier
        dossier_verif.delete()
        print("✅ Dossier supprimé")
        
        # Vérifier que le dossier n'existe plus
        try:
            Dossier.objects.get(id=dossier_id)
            print("❌ Erreur: Le dossier existe encore après suppression")
            return False
        except Dossier.DoesNotExist:
            print("✅ Confirmation: Le dossier a bien été supprimé")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

def test_template_final():
    """Test final des templates"""
    print("\n=== Test final des templates ===")
    
    templates_to_check = [
        "templates/dossiers/gestion_dossiers.html",
        "templates/dossiers/admin_dashboard.html"
    ]
    
    for template_path in templates_to_check:
        print(f"\n📄 Vérification de {template_path}:")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier le token CSRF
            if 'csrfmiddlewaretoken' in content:
                print("  ✅ Token CSRF présent")
            else:
                print("  ❌ Token CSRF manquant")
                return False
            
            # Vérifier la fonction JavaScript
            if 'function supprimerDossier(id)' in content:
                print("  ✅ Fonction JavaScript présente")
            else:
                print("  ❌ Fonction JavaScript manquante")
                return False
            
            # Vérifier les logs de débogage
            if 'console.log' in content:
                print("  ✅ Logs de débogage présents")
            else:
                print("  ❌ Logs de débogage manquants")
                return False
            
            # Vérifier la gestion d'erreurs
            if 'try {' in content and 'catch (error)' in content:
                print("  ✅ Gestion d'erreurs présente")
            else:
                print("  ❌ Gestion d'erreurs manquante")
                return False
                
        except FileNotFoundError:
            print(f"  ❌ Template non trouvé: {template_path}")
            return False
        except Exception as e:
            print(f"  ❌ Erreur lors de la lecture: {str(e)}")
            return False
    
    return True

def test_url_final():
    """Test final des URLs"""
    print("\n=== Test final des URLs ===")
    
    try:
        with open("dossiers/urls.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier l'URL de suppression
        if 'supprimer_dossier' in content:
            print("✅ URL de suppression configurée")
        else:
            print("❌ URL de suppression manquante")
            return False
        
        # Vérifier la vue associée
        if 'views.supprimer_dossier' in content:
            print("✅ Vue associée correctement")
        else:
            print("❌ Vue non associée")
            return False
        
        return True
        
    except FileNotFoundError:
        print("❌ Fichier urls.py non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la lecture: {str(e)}")
        return False

def test_view_final():
    """Test final de la vue"""
    print("\n=== Test final de la vue ===")
    
    try:
        with open("dossiers/views.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier la fonction
        if 'def supprimer_dossier(' in content:
            print("✅ Fonction supprimer_dossier présente")
        else:
            print("❌ Fonction supprimer_dossier manquante")
            return False
        
        # Vérifier la gestion des permissions
        if 'request.user.role != \'admin\'' in content:
            print("✅ Vérification des permissions admin")
        else:
            print("❌ Vérification des permissions manquante")
            return False
        
        # Vérifier la suppression en cascade
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
        print("❌ Fichier views.py non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la lecture: {str(e)}")
        return False

def test_database_final():
    """Test final de la base de données"""
    print("\n=== Test final de la base de données ===")
    
    try:
        # Vérifier que le modèle Dossier existe
        dossiers_count = Dossier.objects.count()
        print(f"✅ Modèle Dossier accessible ({dossiers_count} dossiers)")
        
        # Vérifier que le modèle CustomUser existe
        users_count = CustomUser.objects.count()
        print(f"✅ Modèle CustomUser accessible ({users_count} utilisateurs)")
        
        # Vérifier qu'il n'y a pas d'erreurs de migrations
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'dossiers_%'")
            tables = cursor.fetchall()
            print(f"✅ Tables dossiers trouvées: {len(tables)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'accès aux modèles: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Test final du bouton de suppression après résolution des migrations")
    print("=" * 70)
    
    # Tests
    tests = [
        ("Base de données", test_database_final),
        ("Configuration des URLs", test_url_final),
        ("Fonction de vue", test_view_final),
        ("Éléments des templates", test_template_final),
        ("Création et suppression", test_suppression_complete),
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
    print("\n" + "=" * 70)
    print("📊 RÉSULTATS FINAUX")
    print("=" * 70)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ OK" if result else "❌ ÉCHEC"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 70)
    
    if all_passed:
        print("🎉 Tous les tests sont passés avec succès !")
        print("Le bouton de suppression devrait maintenant fonctionner correctement.")
        print("\n📝 Instructions pour tester:")
        print("1. Ouvrez votre navigateur")
        print("2. Allez sur http://localhost:8000/dossiers/gestion/")
        print("3. Connectez-vous en tant qu'administrateur")
        print("4. Cliquez sur le bouton rouge (poubelle) à côté d'un dossier")
        print("5. Confirmez la suppression")
        print("6. Vérifiez les logs dans la console du navigateur (F12)")
        print("\n🔧 Si le bouton ne fonctionne toujours pas:")
        print("- Vérifiez que vous êtes connecté en tant qu'administrateur")
        print("- Videz le cache du navigateur (Ctrl+F5)")
        print("- Vérifiez la console du navigateur pour les erreurs")
    else:
        print("⚠️ Certains tests ont échoué.")
        print("Vérifiez les problèmes identifiés ci-dessus.")
    
    print("\n" + "=" * 70) 