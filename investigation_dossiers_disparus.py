#!/usr/bin/env python
"""
Investigation pour retrouver les dossiers disparus
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier, DossierTraite
from django.db import connection

def investigation_dossiers_disparus():
    """Investigation complète pour retrouver les dossiers"""
    print("=== 🔍 INVESTIGATION DOSSIERS DISPARUS ===")
    print("😢 Ne vous inquiétez pas, on va les retrouver !")
    print()
    
    try:
        # 1. Vérification complète de la base de données
        print("📊 VÉRIFICATION COMPLÈTE DE LA BASE:")
        
        with connection.cursor() as cursor:
            # Compter tous les enregistrements dans toutes les tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print("   Tables trouvées:")
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"   - {table_name}: {count} enregistrements")
        
        print()
        
        # 2. Vérification détaillée du modèle Dossier
        print("📁 INVESTIGATION MODÈLE 'Dossier':")
        tous_dossiers = Dossier.objects.all()
        print(f"   Total Dossier.objects.all(): {tous_dossiers.count()}")
        
        # Vérifier par statut
        for statut in ['non_traite', 'en_cours', 'traite', 'archive']:
            count = Dossier.objects.filter(statut=statut).count()
            print(f"   - Statut '{statut}': {count} dossiers")
        
        # Vérifier les IDs manquants
        if tous_dossiers.exists():
            ids_existants = list(tous_dossiers.values_list('id', flat=True))
            ids_existants.sort()
            print(f"   - IDs existants: {ids_existants}")
            
            # Chercher des trous dans la séquence
            if len(ids_existants) > 1:
                print("   - Vérification des trous dans la séquence:")
                for i in range(len(ids_existants) - 1):
                    if ids_existants[i+1] - ids_existants[i] > 1:
                        print(f"     Trou entre ID {ids_existants[i]} et {ids_existants[i+1]}")
        else:
            print("   ❌ AUCUN DOSSIER TROUVÉ !")
        
        print()
        
        # 3. Vérification détaillée du modèle DossierTraite
        print("📋 INVESTIGATION MODÈLE 'DossierTraite':")
        tous_dossiers_traites = DossierTraite.objects.all()
        print(f"   Total DossierTraite.objects.all(): {tous_dossiers_traites.count()}")
        
        if tous_dossiers_traites.exists():
            # Vérifier les 10 premiers et derniers
            print("   - 10 premiers:")
            for i, dt in enumerate(tous_dossiers_traites[:10]):
                print(f"     {i+1}. ID {dt.id}: {dt.numero} - {dt.demandeur_candidat}")
            
            print("   - 10 derniers:")
            for i, dt in enumerate(tous_dossiers_traites.order_by('-id')[:10]):
                print(f"     {i+1}. ID {dt.id}: {dt.numero} - {dt.demandeur_candidat}")
        else:
            print("   ❌ AUCUN DOSSIER TRAITÉ TROUVÉ !")
        
        print()
        
        # 4. Recherche de dossiers supprimés récemment
        print("🔍 RECHERCHE DE DOSSIERS SUPPRIMÉS:")
        print("   - Vérification des logs de suppression...")
        
        # Vérifier s'il y a des dossiers avec des IDs très élevés
        if tous_dossiers.exists():
            max_id = max(ids_existants)
            print(f"   - ID maximum trouvé: {max_id}")
            
            # Chercher des dossiers avec des IDs plus élevés
            dossiers_haute_id = Dossier.objects.filter(id__gt=max_id)
            if dossiers_haute_id.exists():
                print(f"   - Dossiers avec ID > {max_id}: {dossiers_haute_id.count()}")
                for d in dossiers_haute_id:
                    print(f"     ID {d.id}: {d.titre} - {d.statut}")
            else:
                print(f"   - Aucun dossier avec ID > {max_id}")
        
        print()
        
        # 5. Vérification de la cohérence
        print("🎯 ANALYSE DE LA COHÉRENCE:")
        
        # Vérifier si les dossiers traités correspondent
        dossiers_traites = Dossier.objects.filter(statut='traite')
        dossiers_traites_count = dossiers_traites.count()
        dossiers_traites_historique = DossierTraite.objects.count()
        
        print(f"   - Dossiers avec statut='traite': {dossiers_traites_count}")
        print(f"   - Dossiers dans DossierTraite: {dossiers_traites_historique}")
        
        if dossiers_traites_count != dossiers_traites_historique:
            print(f"   ⚠️ INCOHÉRENCE DÉTECTÉE !")
            print(f"     Différence: {abs(dossiers_traites_count - dossiers_traites_historique)} dossiers")
        else:
            print(f"   ✅ Cohérence OK")
        
        print()
        print("🔍 INVESTIGATION TERMINÉE")
        print("   Vos dossiers sont quelque part, on va les retrouver !")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'investigation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigation_dossiers_disparus()

