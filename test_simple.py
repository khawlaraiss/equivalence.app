#!/usr/bin/env python
"""
Script de test simple pour l'import Excel
"""

import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

import pandas as pd
from datetime import datetime

def test_simple():
    """Test simple de lecture du fichier Excel"""
    
    excel_path = 'suivi -equivalence-14juillet2025-Stagiaire.xlsx'
    
    if not os.path.exists(excel_path):
        print(f"❌ Fichier {excel_path} non trouvé")
        return
    
    print(f"📁 Fichier trouvé: {excel_path}")
    
    try:
        df = pd.read_excel(excel_path, header=None)
        print(f"📊 Forme du fichier: {df.shape}")
        
        # Afficher les premières lignes
        print("\n📋 Premières lignes:")
        for i in range(min(5, len(df))):
            row = df.iloc[i]
            print(f"Ligne {i+1}: {row[0]} | {row[1]} | {row[7]} | {row[8]} | {row[10]} | {row[12]} | {row[13]} | {row[14]}")
        
        # Compter les dossiers valides
        dossiers_valides = 0
        for index, row in df.iterrows():
            if (not pd.isna(row[0]) and 
                str(row[0]).strip() != '' and 
                str(row[0]).lower() not in ['no.', 'nan', 'situation des dossiers'] and
                str(row[0]).replace('.', '').replace('bis', '').isdigit()):
                dossiers_valides += 1
        
        print(f"\n📈 Dossiers valides trouvés: {dossiers_valides}")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    test_simple() 