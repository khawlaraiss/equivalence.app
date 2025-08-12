#!/usr/bin/env python
"""
Test simple de la suppression d'un dossier traité
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier
from users.models import CustomUser

def test_suppression_simple():
    """Test simple de la suppression"""
    print("=== Test Suppression Simple ===")
    
    try:
        # 1. Vérifier les dossiers traités existants
        dossiers_traites = Dossier.objects.filter(statut='traite')
        print(f"📊 Dossiers traités trouvés: {dossiers_traites.count()}")
        
        for dossier in dossiers_traites:
            print(f"  - ID: {dossier.id}, Titre: {dossier.titre}, Statut: {dossier.statut}")
        
        # 2. Tester la suppression du premier dossier traité
        if dossiers_traites.exists():
            dossier_a_supprimer = dossiers_traites.first()
            print(f"\n🗑️ Test suppression du dossier ID {dossier_a_supprimer.id}")
            
            # Sauvegarder les informations avant suppression
            titre_avant = dossier_a_supprimer.titre
            id_avant = dossier_a_supprimer.id
            
            # Supprimer le dossier
            dossier_a_supprimer.delete()
            print(f"✅ Dossier supprimé: {titre_avant} (ID: {id_avant})")
            
            # Vérifier que le dossier a été supprimé
            try:
                dossier_verif = Dossier.objects.get(id=id_avant)
                print(f"❌ Erreur: Dossier encore présent après suppression")
            except Dossier.DoesNotExist:
                print(f"✅ Confirmation: Dossier supprimé avec succès")
                
            # Vérifier le nombre de dossiers traités restants
            dossiers_restants = Dossier.objects.filter(statut='traite')
            print(f"📊 Dossiers traités restants: {dossiers_restants.count()}")
            
        else:
            print("ℹ️ Aucun dossier traité trouvé pour le test")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_suppression_simple()
