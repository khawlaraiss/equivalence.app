#!/usr/bin/env python3
"""
Script pour nettoyer et supprimer tous les critères de test ajoutés
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import StructureEvaluationGlobale

def nettoyer_criteres_test():
    """Nettoyer tous les critères de test ajoutés"""
    print("🧹 Nettoyage des critères de test...")
    
    # Récupérer la structure
    try:
        structure = StructureEvaluationGlobale.objects.filter(actif=True).latest('date_creation')
        print(f"✅ Structure trouvée: {structure.id}")
    except:
        print("❌ Aucune structure trouvée")
        return
    
    # Afficher l'état initial
    print(f"\n📋 État initial des critères ({len(structure.criteres_personnalises_globaux)}):")
    for i, critere in enumerate(structure.criteres_personnalises_globaux):
        print(f"  {i+1}. ID: {critere.get('id')} - {critere.get('nom')} ({critere.get('note_max')} points)")
    
    # Identifier les critères à supprimer (tous sauf les 2 premiers)
    criteres_a_garder = []
    criteres_a_supprimer = []
    
    for critere in structure.criteres_personnalises_globaux:
        nom = critere.get('nom', '')
        if nom in ['inform', 'Gouvernance'] and critere.get('id') in [1, 2]:
            criteres_a_garder.append(critere)
            print(f"✅ Garder: {nom} (ID: {critere.get('id')})")
        else:
            criteres_a_supprimer.append(critere)
            print(f"🗑️ Supprimer: {nom} (ID: {critere.get('id')})")
    
    # Mettre à jour la structure
    structure.criteres_personnalises_globaux = criteres_a_garder
    
    # Sauvegarder
    structure.save()
    
    print(f"\n✅ Nettoyage terminé!")
    print(f"   Critères supprimés: {len(criteres_a_supprimer)}")
    print(f"   Critères conservés: {len(criteres_a_garder)}")
    
    # Afficher l'état final
    print(f"\n📋 État final des critères ({len(structure.criteres_personnalises_globaux)}):")
    for i, critere in enumerate(structure.criteres_personnalises_globaux):
        print(f"  {i+1}. ID: {critere.get('id')} - {critere.get('nom')} ({critere.get('note_max')} points)")
    
    # Vérifier la numérotation dans l'interface
    print(f"\n📊 Numérotation dans l'interface:")
    print("Critères fixes (1-7):")
    print("  1. Sciences géodésiques")
    print("  2. Topographie") 
    print("  3. Photogrammétrie")
    print("  4. Cartographie")
    print("  5. Droit foncier")
    print("  6. SIG")
    print("  7. Télédétection")
    
    print("\nCritères personnalisés (8+):")
    for i, critere in enumerate(structure.criteres_personnalises_globaux):
        numero_interface = i + 8
        print(f"  {numero_interface}. {critere.get('nom')}")
    
    print("\n🎉 Nettoyage terminé! La structure est revenue à l'état initial.")

if __name__ == '__main__':
    nettoyer_criteres_test()


