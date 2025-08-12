#!/usr/bin/env python
"""
Test simple pour vérifier la suppression
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
            titre="Dossier test final",
            description="Test de suppression final",
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

def test_dossiers_existants():
    """Lister les dossiers existants"""
    print("\n=== Dossiers Existants ===")
    
    try:
        dossiers = Dossier.objects.all().order_by('id')
        print(f"✅ Nombre total de dossiers: {dossiers.count()}")
        
        for dossier in dossiers:
            print(f"  - ID {dossier.id}: {dossier.titre}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Test Simple Final")
    print("=" * 50)
    
    # Tests
    tests = [
        ("Dossiers existants", test_dossiers_existants),
        ("Suppression simple", test_suppression_simple),
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
        print("🎉 La suppression fonctionne !")
        print("Le bouton devrait maintenant fonctionner.")
        print("\n📝 Pour tester :")
        print("1. Allez sur http://localhost:8000/dossiers/gestion/")
        print("2. Cliquez sur le bouton rouge (poubelle)")
        print("3. Confirmez la suppression")
        print("4. Le dossier devrait disparaître")
    else:
        print("⚠️ La suppression ne fonctionne pas.")
    
    print("\n" + "=" * 50) 