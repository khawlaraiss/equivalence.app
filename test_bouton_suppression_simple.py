#!/usr/bin/env python
"""
Test simple pour vérifier que le bouton de suppression fonctionne
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier

def test_suppression_dossiers():
    """Test de suppression des dossiers de test"""
    print("=== Test de Suppression des Dossiers ===")
    
    try:
        # Lister tous les dossiers
        dossiers = Dossier.objects.all()
        print(f"✅ Nombre total de dossiers: {dossiers.count()}")
        
        # Afficher les dossiers de test
        dossiers_test = Dossier.objects.filter(
            titre__icontains='test'
        )
        
        print(f"\n📋 Dossiers de test trouvés: {dossiers_test.count()}")
        
        for dossier in dossiers_test:
            print(f"  - ID {dossier.id}: {dossier.titre}")
        
        # Supprimer les dossiers de test
        if dossiers_test.exists():
            print(f"\n🗑️ Suppression de {dossiers_test.count()} dossiers de test...")
            dossiers_test.delete()
            print("✅ Dossiers de test supprimés")
        else:
            print("ℹ️ Aucun dossier de test à supprimer")
        
        # Vérifier le nombre final
        dossiers_final = Dossier.objects.all()
        print(f"✅ Nombre final de dossiers: {dossiers_final.count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_template_bouton():
    """Vérifier que le bouton de suppression est présent"""
    print("\n=== Vérification du Bouton de Suppression ===")
    
    try:
        with open("templates/dossiers/gestion_dossiers.html", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier que le bouton est présent (sans condition admin)
        if 'btn-outline-danger' in content and 'supprimerDossier' in content:
            print("✅ Bouton de suppression présent dans le template")
            return True
        else:
            print("❌ Bouton de suppression manquant")
            return False
            
    except FileNotFoundError:
        print("❌ Template non trouvé")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Test du Bouton de Suppression")
    print("=" * 50)
    
    # Tests
    tests = [
        ("Bouton dans template", test_template_bouton),
        ("Suppression dossiers", test_suppression_dossiers),
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
        print("🎉 Le bouton de suppression devrait maintenant fonctionner !")
        print("\n📝 Pour tester:")
        print("1. Allez sur http://localhost:8000/dossiers/gestion/")
        print("2. Cliquez sur le bouton rouge (poubelle) à côté d'un dossier")
        print("3. Confirmez la suppression")
        print("4. Le dossier devrait disparaître")
    else:
        print("⚠️ Certains tests ont échoué.")
    
    print("\n" + "=" * 50) 