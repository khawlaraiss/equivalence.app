#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

import pandas as pd
from dossiers.models import DossierTraite

def test_import():
    # Chemin vers le fichier Excel
    excel_file = 'suivi -equivalence-14juillet2025-Stagiaire.xlsx'
    
    if not os.path.exists(excel_file):
        print(f'Fichier Excel non trouvé: {excel_file}')
        return
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(excel_file, header=None)
        print(f'Fichier Excel lu avec succès. Dimensions: {df.shape}')
        
        # Afficher les premières lignes
        print("\nPremières lignes du fichier:")
        for i in range(min(5, len(df))):
            print(f"Ligne {i}: {list(df.iloc[i, :10])}")
        
        # Tester l'import d'une ligne
        if len(df) > 0:
            row = df.iloc[0]
            print(f"\nTest d'import de la première ligne:")
            print(f"Données: {list(row[:15])}")
            
            # Créer un dossier traité de test
            dossier = DossierTraite.objects.create(
                numero=str(row[0]).strip() if not pd.isna(row[0]) else "TEST-001",
                demandeur=str(row[1]).strip() if not pd.isna(row[1]) else "Test Demandeur",
                reference=str(row[2]).strip() if not pd.isna(row[2]) else "REF-TEST",
                date_envoi=str(row[3]).strip() if not pd.isna(row[3]) else "Date non spécifiée",
                reference_reception=str(row[4]).strip() if not pd.isna(row[4]) else "",
                date_reception=str(row[5]).strip() if not pd.isna(row[5]) else "Date non spécifiée",
                diplome=str(row[6]).strip() if not pd.isna(row[6]) else "Diplôme non spécifié",
                universite=str(row[7]).strip() if not pd.isna(row[7]) else "Université non spécifiée",
                pays=str(row[8]).strip() if not pd.isna(row[8]) else "Pays non spécifié",
                date_avis=str(row[9]).strip() if not pd.isna(row[9]) else "",
                avis_commission=str(row[10]).strip() if not pd.isna(row[10]) else "Avis non spécifié",
                reunions=[]
            )
            print(f"Dossier créé avec succès: {dossier.numero}")
            
            # Supprimer le dossier de test
            dossier.delete()
            print("Dossier de test supprimé")
        
    except Exception as e:
        print(f'Erreur: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_import() 