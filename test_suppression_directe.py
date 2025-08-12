#!/usr/bin/env python
"""
Test de suppression directe d'un dossier
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier

def test_suppression_directe():
    """Test de suppression directe d'un dossier"""
    print("=== Test de Suppression Directe ===")
    
    try:
        # Créer un dossier de test
        dossier = Dossier.objects.create(
            titre="Dossier à supprimer",
            description="Test de suppression directe",
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

def test_suppression_multiple():
    """Test de suppression de plusieurs dossiers"""
    print("\n=== Test de Suppression Multiple ===")
    
    try:
        # Créer plusieurs dossiers de test
        dossiers_crees = []
        for i in range(3):
            dossier = Dossier.objects.create(
                titre=f"Dossier test {i+1}",
                description=f"Test de suppression multiple {i+1}",
                statut='non_traite'
            )
            dossiers_crees.append(dossier)
            print(f"✅ Dossier créé: ID {dossier.id}")
        
        # Supprimer tous les dossiers créés
        for dossier in dossiers_crees:
            dossier.delete()
            print(f"✅ Dossier ID {dossier.id} supprimé")
        
        # Vérifier qu'ils n'existent plus
        for dossier in dossiers_crees:
            try:
                Dossier.objects.get(id=dossier.id)
                print(f"❌ Erreur: Le dossier ID {dossier.id} existe encore")
                return False
            except Dossier.DoesNotExist:
                print(f"✅ Confirmation: Le dossier ID {dossier.id} a bien été supprimé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Test de Suppression Directe")
    print("=" * 50)
    
    # Tests
    tests = [
        ("Suppression directe", test_suppression_directe),
        ("Suppression multiple", test_suppression_multiple),
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
        print("🎉 La suppression fonctionne côté serveur !")
        print("Le problème est dans le JavaScript du navigateur.")
        print("\n📝 Pour tester le bouton :")
        print("1. Allez sur http://localhost:8000/dossiers/gestion/")
        print("2. Cliquez sur le bouton rouge (poubelle)")
        print("3. Vous devriez voir une alerte avec l'ID du dossier")
        print("4. Confirmez la suppression")
        print("5. Le dossier devrait disparaître")
    else:
        print("⚠️ La suppression ne fonctionne pas côté serveur.")
    
    print("\n" + "=" * 50) 