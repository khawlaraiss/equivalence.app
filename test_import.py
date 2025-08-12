#!/usr/bin/env python
"""
Script de test pour l'import Excel des dossiers traités
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

import pandas as pd
from datetime import datetime
from dossiers.models import DossierTraite
from users.models import CustomUser

def test_excel_import():
    """Test de l'import du fichier Excel"""
    
    # Chemin vers le fichier Excel
    excel_path = 'suivi -equivalence-14juillet2025-Stagiaire.xlsx'
    
    if not os.path.exists(excel_path):
        print(f"❌ Fichier {excel_path} non trouvé")
        return
    
    print(f"📁 Fichier trouvé: {excel_path}")
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(excel_path, header=None)
        print(f"📊 Forme du fichier: {df.shape}")
        
        # Compter les lignes avec des numéros de dossier
        lignes_valides = 0
        numeros_trouves = []
        
        for index, row in df.iterrows():
            try:
                # Ignorer les lignes vides, en-têtes ou non numériques
                if (pd.isna(row[0]) or 
                    str(row[0]).strip() == '' or 
                    str(row[0]).lower() in ['no.', 'nan', 'situation des dossiers'] or
                    not str(row[0]).replace('.', '').replace('bis', '').isdigit()):
                    continue
                
                numero = str(row[0]).strip()
                numeros_trouves.append(numero)
                lignes_valides += 1
                
                print(f"✅ Ligne {index + 1}: Numéro {numero}")
                
            except Exception as e:
                print(f"❌ Erreur ligne {index + 1}: {str(e)}")
        
        print(f"\n📈 Résumé:")
        print(f"   - Lignes valides trouvées: {lignes_valides}")
        print(f"   - Numéros de dossier: {numeros_trouves}")
        
        # Vérifier les dossiers existants
        dossiers_existants = DossierTraite.objects.filter(numero__in=numeros_trouves)
        print(f"   - Dossiers déjà existants: {dossiers_existants.count()}")
        
        # Simuler l'import
        dossiers_a_importer = lignes_valides - dossiers_existants.count()
        print(f"   - Dossiers à importer: {dossiers_a_importer}")
        
        if dossiers_a_importer > 0:
            print(f"\n🚀 Prêt pour l'import de {dossiers_a_importer} dossiers")
        else:
            print(f"\n⚠️ Aucun nouveau dossier à importer")
            
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier: {str(e)}")

if __name__ == "__main__":
    test_excel_import() 