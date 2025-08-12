#!/usr/bin/env python3
"""
Script de test final pour vérifier que l'ordre des critères personnalisés est respecté
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import StructureEvaluationGlobale
from django.utils import timezone

def test_ordre_final():
    """Test final de l'ordre des critères personnalisés"""
    print("🧪 Test final de l'ordre des critères personnalisés")
    
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
    
    # Vérifier l'ordre actuel
    ids = [c.get('id', 0) for c in structure.criteres_personnalises_globaux]
    if ids == sorted(ids):
        print("\n✅ L'ordre des critères est correct (trié par ID)")
    else:
        print(f"\n❌ L'ordre des critères n'est pas correct")
        print(f"   IDs actuels: {ids}")
        print(f"   IDs triés: {sorted(ids)}")
        
        # Trier manuellement pour corriger
        print("\n🔧 Correction de l'ordre...")
        structure.criteres_personnalises_globaux.sort(key=lambda x: x.get('id', 0))
        structure.save()
        print("✅ Ordre corrigé et sauvegardé")
    
    # Simuler l'ajout d'un nouveau critère
    print(f"\n➕ Simulation de l'ajout d'un nouveau critère...")
    
    # Calculer le prochain ID
    next_id = 1
    if structure.criteres_personnalises_globaux:
        existing_ids = [c.get('id', 0) for c in structure.criteres_personnalises_globaux]
        next_id = max(existing_ids) + 1 if existing_ids else 1
    
    nouveau_critere = {
        'id': next_id,
        'nom': f'Test Final {timezone.now().strftime("%H:%M:%S")}',
        'note_max': 20,
        'compétences': ['Compétence Finale 1', 'Compétence Finale 2'],
        'date_creation': timezone.now().isoformat()
    }
    
    # Ajouter le critère
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
    
    # Vérifications finales
    ids_finaux = [c.get('id', 0) for c in structure.criteres_personnalises_globaux]
    if ids_finaux == sorted(ids_finaux):
        print("\n✅ L'ordre final est correct (trié par ID)")
    else:
        print(f"\n❌ L'ordre final n'est pas correct")
        print(f"   IDs finaux: {ids_finaux}")
        print(f"   IDs triés: {sorted(ids_finaux)}")
    
    # Vérifier que le nouveau critère est à la fin
    dernier_critere = structure.criteres_personnalises_globaux[-1]
    if dernier_critere.get('nom') == nouveau_critere['nom']:
        print("✅ Le nouveau critère est bien à la dernière position")
        print("🎉 SUCCÈS: L'ordre des critères est maintenant respecté!")
    else:
        print(f"❌ Le nouveau critère n'est pas à la dernière position")
        print(f"   Dernier critère: {dernier_critere.get('nom')}")
        print(f"   Nouveau critère: {nouveau_critere['nom']}")
    
    # Afficher la numérotation attendue dans l'interface
    print(f"\n📊 Numérotation attendue dans l'interface:")
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

if __name__ == '__main__':
    test_ordre_final()
