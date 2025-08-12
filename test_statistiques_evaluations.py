#!/usr/bin/env python3
"""
Test des statistiques des évaluations avec les 5 types de décisions
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import DecisionCommission
from django.db.models import Count

def test_statistiques_evaluations():
    print("=== 🧪 TEST STATISTIQUES ÉVALUATIONS ===")
    
    # Compter toutes les décisions par type
    decisions_par_type = DecisionCommission.objects.values('decision').annotate(
        count=Count('decision')
    ).order_by('decision')
    
    print(f"\n📊 Décisions par type:")
    total = 0
    for decision in decisions_par_type:
        count = decision['count']
        decision_type = decision['decision']
        total += count
        
        # Afficher le nom français
        if decision_type == 'equivalence_accorder':
            nom_fr = "Équivalence accordée"
        elif decision_type == 'completement_dossier':
            nom_fr = "Complètement de dossier"
        elif decision_type == 'invitation_soutenance':
            nom_fr = "Invitation soutenance"
        elif decision_type == 'invitation_concours':
            nom_fr = "Invitation concours"
        elif decision_type == 'non_equivalent':
            nom_fr = "Non équivalent"
        else:
            nom_fr = decision_type
            
        print(f"   {nom_fr}: {count}")
    
    print(f"\n🎯 Total des évaluations: {total}")
    
    # Vérifier que tous les types sont présents
    types_attendus = [
        'equivalence_accorder',
        'completement_dossier', 
        'invitation_soutenance',
        'invitation_concours',
        'non_equivalent'
    ]
    
    types_trouves = [d['decision'] for d in decisions_par_type]
    
    print(f"\n🔍 Vérification des types:")
    for type_attendu in types_attendus:
        if type_attendu in types_trouves:
            print(f"   ✅ {type_attendu}")
        else:
            print(f"   ❌ {type_attendu} (manquant)")
    
    # Calculer la moyenne des scores
    if total > 0:
        moyenne = DecisionCommission.objects.aggregate(
            moyenne=django.db.models.Avg('score_total')
        )['moyenne']
        print(f"\n📈 Score moyen: {moyenne:.1f}/100")
    else:
        print(f"\n📈 Score moyen: Aucune évaluation")
    
    print(f"\n🎯 TEST TERMINÉ")

if __name__ == '__main__':
    test_statistiques_evaluations()
