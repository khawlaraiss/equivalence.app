#!/usr/bin/env python
"""
Script de test pour vérifier l'import de l'avis de commission
"""

import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

import pandas as pd
from datetime import datetime
from dossiers.models import DossierTraite

def test_avis_commission():
    """Test de l'import de l'avis de commission"""
    
    excel_path = 'suivi -equivalence-14juillet2025-Stagiaire.xlsx'
    
    if not os.path.exists(excel_path):
        print(f"❌ Fichier {excel_path} non trouvé")
        return
    
    print(f"📁 Fichier trouvé: {excel_path}")
    
    try:
        df = pd.read_excel(excel_path, header=None)
        print(f"📊 Forme du fichier: {df.shape}")
        
        # Analyser les avis de commission
        avis_trouves = 0
        avis_exemples = []
        
        for index, row in df.iterrows():
            try:
                # Ignorer les lignes vides ou en-têtes
                if (pd.isna(row[0]) or 
                    str(row[0]).strip() == '' or 
                    str(row[0]).lower() in ['no.', 'nan', 'situation des dossiers'] or
                    not str(row[0]).replace('.', '').replace('bis', '').isdigit()):
                    continue
                
                numero = str(row[0]).strip()
                
                # Vérifier l'avis de commission (colonne 10)
                if not pd.isna(row[10]) and str(row[10]).strip() != '':
                    avis = str(row[10]).strip()
                    avis_trouves += 1
                    
                    if len(avis_exemples) < 3:  # Garder seulement 3 exemples
                        avis_exemples.append({
                            'numero': numero,
                            'avis': avis
                        })
                
            except Exception as e:
                continue
        
        print(f"\n📋 Résultats de l'analyse:")
        print(f"   - Avis de commission trouvés: {avis_trouves}")
        
        if avis_exemples:
            print(f"\n📝 Exemples d'avis de commission:")
            for i, exemple in enumerate(avis_exemples, 1):
                print(f"   {i}. Dossier {exemple['numero']}:")
                print(f"      Avis: {exemple['avis']}")
                print()
        
        # Vérifier les dossiers déjà importés
        dossiers_importes = DossierTraite.objects.count()
        dossiers_avec_avis = DossierTraite.objects.exclude(avis_commission="Avis non spécifié").count()
        
        print(f"📊 État de la base de données:")
        print(f"   - Dossiers traités importés: {dossiers_importes}")
        print(f"   - Dossiers avec avis de commission: {dossiers_avec_avis}")
        
        if dossiers_avec_avis > 0:
            print(f"\n✅ L'import de l'avis de commission fonctionne correctement!")
            print(f"   {dossiers_avec_avis} dossiers ont un avis de commission importé")
        else:
            print(f"\n⚠️ Aucun avis de commission importé dans la base de données")
            print(f"   Vous devez d'abord faire l'import automatique")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    test_avis_commission() 