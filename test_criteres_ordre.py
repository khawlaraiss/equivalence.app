#!/usr/bin/env python3
"""
Script de test pour vérifier l'ordre des critères personnalisés
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import StructureEvaluationGlobale
from django.utils import timezone

def test_ordre_criteres():
    """Test de l'ordre des critères personnalisés"""
    print("🧪 Test de l'ordre des critères personnalisés")
    
    # Récupérer ou créer la structure
    try:
        structure = StructureEvaluationGlobale.objects.filter(actif=True).latest('date_creation')
        print(f"✅ Structure trouvée: {structure.id}")
    except:
        print("❌ Aucune structure trouvée")
        return
    
    # Afficher les critères actuels
    print(f"\n📋 Critères personnalisés actuels ({len(structure.criteres_personnalises_globaux)}):")
    for i, critere in enumerate(structure.criteres_personnalises_globaux):
        print(f"  {i+1}. ID: {critere.get('id')} - {critere.get('nom')} ({critere.get('note_max')} points)")
    
    # Ajouter un nouveau critère de test
    nouveau_critere = {
        'id': len(structure.criteres_personnalises_globaux) + 1,
        'nom': f'Test Critère {timezone.now().strftime("%H:%M:%S")}',
        'note_max': 10,
        'compétences': ['Test Compétence'],
        'date_creation': timezone.now().isoformat()
    }
    
    structure.criteres_personnalises_globaux.append(nouveau_critere)
    
    # Trier par ID
    structure.criteres_personnalises_globaux.sort(key=lambda x: x.get('id', 0))
    
    # Sauvegarder
    structure.save()
    
    print(f"\n➕ Nouveau critère ajouté: {nouveau_critere['nom']}")
    
    # Afficher l'ordre final
    print(f"\n📋 Ordre final des critères ({len(structure.criteres_personnalises_globaux)}):")
    for i, critere in enumerate(structure.criteres_personnalises_globaux):
        print(f"  {i+1}. ID: {critere.get('id')} - {critere.get('nom')} ({critere.get('note_max')} points)")
    
    # Vérifier que l'ordre est correct
    ids = [c.get('id', 0) for c in structure.criteres_personnalises_globaux]
    if ids == sorted(ids):
        print("\n✅ L'ordre des critères est correct (trié par ID)")
    else:
        print(f"\n❌ L'ordre des critères n'est pas correct")
        print(f"   IDs actuels: {ids}")
        print(f"   IDs triés: {sorted(ids)}")

if __name__ == '__main__':
    test_ordre_criteres()
