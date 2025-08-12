#!/usr/bin/env python
"""
Test simple pour vérifier la suppression de dossiers
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier

def test_suppression_simple():
    """Test simple de suppression"""
    print("=== Test Simple de Suppression ===")
    
    try:
        # Créer un dossier de test
        dossier = Dossier.objects.create(
            titre="Dossier test suppression simple",
            description="Test de suppression simple",
            statut='non_traite'
        )
        
        dossier_id = dossier.id
        print(f"✅ Dossier créé avec ID: {dossier_id}")
        
        # Vérifier qu'il existe
        dossier_verif = Dossier.objects.get(id=dossier_id)
        print(f"✅ Dossier vérifié: {dossier_verif.titre}")
        
        # Supprimer le dossier
        dossier_verif.delete()
        print("✅ Dossier supprimé")
        
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

def test_template_elements():
    """Vérifier les éléments du template"""
    print("\n=== Vérification des Éléments du Template ===")
    
    try:
        with open("templates/dossiers/gestion_dossiers.html", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifications
        checks = [
            ('Token CSRF', 'csrfmiddlewaretoken'),
            ('Fonction JavaScript', 'function supprimerDossier'),
            ('Bouton de suppression', 'btn-outline-danger'),
            ('Icone poubelle', 'fas fa-trash'),
            ('Vérification admin', 'request.user.role == \'admin\''),
            ('Logs de débogage', 'console.log'),
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

def test_view_function():
    """Vérifier la fonction de vue"""
    print("\n=== Vérification de la Fonction de Vue ===")
    
    try:
        with open("dossiers/views.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifications
        checks = [
            ('Fonction supprimer_dossier', 'def supprimer_dossier'),
            ('Vérification admin', 'request.user.role != \'admin\''),
            ('Suppression en cascade', 'pieces_jointes.all().delete()'),
            ('Suppression du dossier', 'dossier.delete()'),
            ('Messages de succès', 'messages.success'),
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
        print("❌ Fichier views.py non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Test Simple de Suppression")
    print("=" * 50)
    
    # Tests
    tests = [
        ("Suppression simple", test_suppression_simple),
        ("Éléments du template", test_template_elements),
        ("Fonction de vue", test_view_function),
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
        print("Le bouton de suppression devrait maintenant fonctionner.")
        print("\n📝 Pour tester:")
        print("1. Allez sur http://localhost:8000/dossiers/gestion/")
        print("2. Connectez-vous en tant qu'administrateur")
        print("3. Cliquez sur le bouton rouge (poubelle)")
        print("4. Confirmez la suppression")
        print("5. Vérifiez la console (F12) pour les logs")
    else:
        print("⚠️ Certains tests ont échoué.")
    
    print("\n" + "=" * 50) 