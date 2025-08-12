#!/usr/bin/env python
"""
Supprimer les dossiers de test
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier

def supprimer_dossiers_test():
    """Supprimer les dossiers de test"""
    print("=== Suppression des Dossiers de Test ===")
    
    try:
        # Supprimer les dossiers de test
        dossiers_test = Dossier.objects.filter(
            titre__icontains='test'
        )
        
        count = dossiers_test.count()
        print(f"✅ {count} dossiers de test trouvés")
        
        for dossier in dossiers_test:
            print(f"  - Suppression: ID {dossier.id} - {dossier.titre}")
            dossier.delete()
        
        print(f"✅ {count} dossiers de test supprimés")
        
        # Afficher les dossiers restants
        dossiers_restants = Dossier.objects.all().order_by('id')
        print(f"\n📋 Dossiers restants ({dossiers_restants.count()}):")
        
        for dossier in dossiers_restants:
            print(f"  - ID {dossier.id}: {dossier.titre}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧹 Nettoyage des Dossiers de Test")
    print("=" * 50)
    
    result = supprimer_dossiers_test()
    
    if result:
        print("\n✅ Nettoyage terminé !")
        print("Maintenant vous pouvez tester la suppression sur vos vrais dossiers.")
    else:
        print("\n❌ Erreur lors du nettoyage")
    
    print("\n" + "=" * 50) 