#!/usr/bin/env python
"""
Test pour diagnostiquer pourquoi le bouton de suppression ne fonctionne pas
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier

def test_dossiers_existants():
    """Vérifier les dossiers existants"""
    print("=== Dossiers Existants ===")
    
    try:
        dossiers = Dossier.objects.all().order_by('id')
        print(f"✅ Nombre total de dossiers: {dossiers.count()}")
        
        for dossier in dossiers:
            print(f"  - ID {dossier.id}: {dossier.titre} (Statut: {dossier.statut})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_template_javascript():
    """Vérifier le JavaScript dans le template"""
    print("\n=== Vérification du JavaScript ===")
    
    try:
        with open("templates/dossiers/gestion_dossiers.html", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifications importantes
        checks = [
            ('Fonction supprimerDossier', 'function supprimerDossier'),
            ('Token CSRF', 'csrfmiddlewaretoken'),
            ('Bouton de suppression', 'btn-outline-danger'),
            ('Icone poubelle', 'fas fa-trash'),
            ('Console.log', 'console.log'),
            ('Try-catch', 'try {'),
            ('Form submission', 'form.submit()'),
        ]
        
        all_ok = True
        for check_name, check_value in checks:
            if check_value in content:
                print(f"  ✅ {check_name} présent")
            else:
                print(f"  ❌ {check_name} manquant")
                all_ok = False
        
        # Vérifier la structure complète de la fonction
        if 'function supprimerDossier(id)' in content:
            print("  ✅ Structure de fonction correcte")
        else:
            print("  ❌ Structure de fonction incorrecte")
            all_ok = False
        
        return all_ok
        
    except FileNotFoundError:
        print("❌ Template non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_url_pattern():
    """Vérifier l'URL de suppression"""
    print("\n=== Vérification de l'URL ===")
    
    try:
        with open("dossiers/urls.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'supprimer_dossier' in content:
            print("✅ URL de suppression configurée")
            return True
        else:
            print("❌ URL de suppression manquante")
            return False
            
    except FileNotFoundError:
        print("❌ Fichier urls.py non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_view_function():
    """Vérifier la fonction de vue"""
    print("\n=== Vérification de la Vue ===")
    
    try:
        with open("dossiers/views.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'def supprimer_dossier(' in content:
            print("✅ Fonction supprimer_dossier présente")
            return True
        else:
            print("❌ Fonction supprimer_dossier manquante")
            return False
            
    except FileNotFoundError:
        print("❌ Fichier views.py non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Diagnostic du Bouton de Suppression")
    print("=" * 60)
    
    # Tests
    tests = [
        ("Dossiers existants", test_dossiers_existants),
        ("JavaScript dans template", test_template_javascript),
        ("Pattern d'URL", test_url_pattern),
        ("Fonction de vue", test_view_function),
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
        print("🎉 Tous les éléments sont présents !")
        print("Le problème pourrait être :")
        print("1. JavaScript désactivé dans le navigateur")
        print("2. Cache du navigateur")
        print("3. Erreur dans la console (F12)")
        print("\n🔧 Solutions à essayer :")
        print("1. Ouvrez la console (F12) et cliquez sur le bouton")
        print("2. Videz le cache (Ctrl+F5)")
        print("3. Essayez un autre navigateur")
    else:
        print("⚠️ Certains éléments sont manquants.")
        print("Vérifiez les problèmes identifiés ci-dessus.")
    
    print("\n" + "=" * 60) 