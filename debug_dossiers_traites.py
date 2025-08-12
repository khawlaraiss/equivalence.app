#!/usr/bin/env python
"""
Script de débogage pour vérifier les dossiers traités
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier
from django.core.paginator import Paginator

def debug_dossiers_traites():
    """Déboguer les dossiers traités"""
    print("=== Débogage Dossiers Traités ===")
    
    try:
        # 1. Compter tous les dossiers
        total_dossiers = Dossier.objects.count()
        print(f"📊 Total dossiers en base: {total_dossiers}")
        
        # 2. Compter les dossiers traités
        dossiers_traites = Dossier.objects.filter(statut='traite')
        total_traites = dossiers_traites.count()
        print(f"📊 Total dossiers traités: {total_traites}")
        
        # 3. Lister les 10 premiers dossiers traités avec leurs IDs
        print("\n🔍 10 premiers dossiers traités:")
        for i, dossier in enumerate(dossiers_traites[:10]):
            print(f"  {i+1}. ID: {dossier.id}, Titre: {dossier.titre}, Statut: {dossier.statut}")
        
        # 4. Vérifier si l'ID 44 existe
        try:
            dossier_44 = Dossier.objects.get(id=44)
            print(f"\n✅ Dossier ID 44 trouvé: {dossier_44.titre} (Statut: {dossier_44.statut})")
        except Dossier.DoesNotExist:
            print(f"\n❌ Dossier ID 44 NON trouvé")
            
            # Chercher les IDs autour de 44
            print("\n🔍 IDs autour de 44:")
            ids_autour = Dossier.objects.filter(id__range=(40, 50)).values_list('id', 'titre', 'statut')
            for dossier_id, titre, statut in ids_autour:
                print(f"  ID {dossier_id}: {titre} ({statut})")
        
        # 5. Vérifier la pagination
        print(f"\n📄 Test pagination:")
        paginator = Paginator(dossiers_traites, 10)  # 10 par page
        print(f"  Nombre de pages: {paginator.num_pages}")
        
        if paginator.num_pages > 0:
            page_1 = paginator.page(1)
            print(f"  Page 1 - Dossiers affichés: {len(page_1)}")
            print(f"  Page 1 - IDs: {[d.id for d in page_1]}")
        
        # 6. Vérifier les statuts des dossiers
        print(f"\n📊 Répartition par statut:")
        statuts = Dossier.objects.values_list('statut', flat=True).distinct()
        for statut in statuts:
            count = Dossier.objects.filter(statut=statut).count()
            print(f"  {statut}: {count}")
            
    except Exception as e:
        print(f"❌ Erreur lors du débogage: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_dossiers_traites()
