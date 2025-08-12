#!/usr/bin/env python
"""
Script de test pour vérifier la fonctionnalité d'ajout de compétences
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import StructureEvaluationGlobale
from django.utils import timezone

def test_competences():
    """Test de la fonctionnalité d'ajout de compétences"""
    print("=== TEST DE LA FONCTIONNALITÉ D'AJOUT DE COMPÉTENCES ===")
    
    # Récupérer la structure active
    try:
        structure = StructureEvaluationGlobale.objects.filter(actif=True).latest('date_creation')
        print(f"✅ Structure trouvée: {structure}")
        print(f"📋 Critères personnalisés actuels: {structure.criteres_personnalises_globaux}")
        
        # Ajouter un critère de test
        nouveau_critere = {
            'id': len(structure.criteres_personnalises_globaux) + 1,
            'nom': 'Test Critère',
            'note_max': 10,
            'compétences': []
        }
        
        structure.criteres_personnalises_globaux.append(nouveau_critere)
        print(f"➕ Critère ajouté: {nouveau_critere}")
        
        # Ajouter une compétence de test
        structure.criteres_personnalises_globaux[-1]['compétences'].append('Test Compétence')
        print(f"➕ Compétence ajoutée: {structure.criteres_personnalises_globaux[-1]['compétences']}")
        
        # Sauvegarder
        structure.save()
        print("💾 Structure sauvegardée")
        
        # Recharger pour vérifier
        structure.refresh_from_db()
        print(f"🔄 Structure rechargée: {structure.criteres_personnalises_globaux}")
        
        print("✅ Test réussi!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_competences() 