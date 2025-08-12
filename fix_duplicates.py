#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import DossierTraite
from collections import defaultdict

def find_and_fix_duplicates():
    """Trouve et corrige les doublons dans les numéros de dossier"""
    
    # Récupérer tous les dossiers
    dossiers = DossierTraite.objects.all()
    
    # Grouper par numéro
    numero_groups = defaultdict(list)
    for dossier in dossiers:
        numero_groups[dossier.numero].append(dossier)
    
    # Identifier les doublons
    duplicates = {numero: dossiers for numero, dossiers in numero_groups.items() if len(dossiers) > 1}
    
    if not duplicates:
        print("Aucun doublon trouvé dans les numéros de dossier.")
        return
    
    print(f"Trouvé {len(duplicates)} numéros avec des doublons:")
    
    for numero, dossiers_list in duplicates.items():
        print(f"\nNuméro '{numero}' - {len(dossiers_list)} dossiers:")
        
        # Trier par date de création (le plus ancien en premier)
        dossiers_list.sort(key=lambda x: x.date_creation)
        
        for i, dossier in enumerate(dossiers_list):
            print(f"  {i+1}. ID: {dossier.id}, Demandeur: {dossier.demandeur_candidat}, Créé: {dossier.date_creation}")
        
        # Garder le premier (le plus ancien) et modifier les autres
        keep_dossier = dossiers_list[0]
        print(f"  → Garder le dossier ID {keep_dossier.id} (le plus ancien)")
        
        for i, dossier in enumerate(dossiers_list[1:], 1):
            # Modifier le numéro pour éviter le conflit
            new_numero = f"{numero}_duplicate_{i}"
            print(f"  → Modifier le dossier ID {dossier.id} avec le numéro '{new_numero}'")
            
            try:
                dossier.numero = new_numero
                dossier.save()
                print(f"    ✓ Dossier {dossier.id} modifié avec succès")
            except Exception as e:
                print(f"    ✗ Erreur lors de la modification du dossier {dossier.id}: {e}")

def check_current_state():
    """Vérifie l'état actuel de la base de données"""
    print("\n=== État actuel de la base de données ===")
    
    total_dossiers = DossierTraite.objects.count()
    print(f"Nombre total de dossiers: {total_dossiers}")
    
    # Vérifier les numéros uniques
    numeros = DossierTraite.objects.values_list('numero', flat=True)
    unique_numeros = set(numeros)
    print(f"Nombre de numéros uniques: {len(unique_numeros)}")
    
    if len(numeros) != len(unique_numeros):
        print("⚠️  Il y a encore des doublons!")
    else:
        print("✓ Tous les numéros sont uniques")

if __name__ == "__main__":
    print("=== Script de correction des doublons de dossiers ===")
    
    # Vérifier l'état initial
    check_current_state()
    
    # Corriger les doublons
    find_and_fix_duplicates()
    
    # Vérifier l'état final
    check_current_state()
    
    print("\n=== Script terminé ===") 