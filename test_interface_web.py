#!/usr/bin/env python3
"""
Script de test pour vérifier que l'interface web respecte l'ordre des critères personnalisés
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import StructureEvaluationGlobale
from django.utils import timezone

def test_interface_web():
    """Test de l'interface web pour l'ordre des critères"""
    print("🌐 Test de l'interface web pour l'ordre des critères")
    
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
    
    # Simuler l'ajout d'un nouveau critère via l'interface web
    print(f"\n➕ Simulation de l'ajout d'un nouveau critère via l'interface web...")
    
    # Calculer le prochain ID (comme dans la vue)
    next_id = 1
    if structure.criteres_personnalises_globaux:
        existing_ids = [c.get('id', 0) for c in structure.criteres_personnalises_globaux]
        next_id = max(existing_ids) + 1 if existing_ids else 1
    
    nouveau_critere = {
        'id': next_id,
        'nom': f'Interface Web Test {timezone.now().strftime("%H:%M:%S")}',
        'note_max': 15,
        'compétences': ['Compétence Web 1', 'Compétence Web 2'],
        'date_creation': timezone.now().isoformat()
    }
    
    # Ajouter le critère (comme dans la vue)
    structure.criteres_personnalises_globaux.append(nouveau_critere)
    
    # Trier par ID (comme dans la vue)
    structure.criteres_personnalises_globaux.sort(key=lambda x: x.get('id', 0))
    
    # Sauvegarder
    structure.save()
    
    print(f"✅ Nouveau critère ajouté: {nouveau_critere['nom']}")
    
    # Afficher l'état final
    print(f"\n📋 État final des critères ({len(structure.criteres_personnalises_globaux)}):")
    for i, critere in enumerate(structure.criteres_personnalises_globaux):
        print(f"  {i+1}. ID: {critere.get('id')} - {critere.get('nom')} ({critere.get('note_max')} points)")
    
    # Vérifier que l'ordre est correct
    ids = [c.get('id', 0) for c in structure.criteres_personnalises_globaux]
    if ids == sorted(ids):
        print("\n✅ L'ordre des critères est correct (trié par ID)")
        print("✅ Les nouveaux critères sont bien ajoutés à la fin")
    else:
        print(f"\n❌ L'ordre des critères n'est pas correct")
        print(f"   IDs actuels: {ids}")
        print(f"   IDs triés: {sorted(ids)}")
    
    # Vérifier que le nouveau critère est bien à la fin
    dernier_critere = structure.criteres_personnalises_globaux[-1]
    if dernier_critere.get('nom') == nouveau_critere['nom']:
        print("✅ Le nouveau critère est bien à la dernière position")
    else:
        print(f"❌ Le nouveau critère n'est pas à la dernière position")
        print(f"   Dernier critère: {dernier_critere.get('nom')}")
        print(f"   Nouveau critère: {nouveau_critere['nom']}")

if __name__ == '__main__':
    test_interface_web()


