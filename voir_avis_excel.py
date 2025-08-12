#!/usr/bin/env python
"""
Script pour voir le contenu réel des avis de commission dans le fichier Excel
"""

import pandas as pd

def voir_avis_excel():
    """Voir les avis de commission dans le fichier Excel"""
    
    excel_path = 'suivi -equivalence-14juillet2025-Stagiaire.xlsx'
    
    try:
        df = pd.read_excel(excel_path, header=None)
        print(f"📊 Forme du fichier: {df.shape}")
        
        print("\n📋 Avis de commission trouvés dans le fichier Excel:")
        print("=" * 80)
        
        for index, row in df.iterrows():
            try:
                # Ignorer les lignes vides ou en-têtes
                if (pd.isna(row[0]) or 
                    str(row[0]).strip() == '' or 
                    str(row[0]).lower() in ['no.', 'nan', 'situation des dossiers'] or
                    not str(row[0]).replace('.', '').replace('bis', '').isdigit()):
                    continue
                
                numero = str(row[0]).strip()
                demandeur = str(row[1]).strip() if not pd.isna(row[1]) else "Non spécifié"
                
                # Avis de commission (colonne 10)
                avis = ""
                if not pd.isna(row[10]) and str(row[10]).strip() != '':
                    avis = str(row[10]).strip()
                
                if avis:  # Afficher seulement les dossiers avec un avis
                    print(f"\n📁 Dossier {numero} - {demandeur}")
                    print(f"   Avis de commission: {avis}")
                    print("-" * 60)
                
            except Exception as e:
                continue
        
        print(f"\n✅ Analyse terminée")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")

if __name__ == "__main__":
    voir_avis_excel() 