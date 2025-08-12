#!/usr/bin/env python
"""
Script de test pour vérifier les données de réunions dans le fichier Excel
"""

import pandas as pd

def test_reunions_excel():
    """Test des données de réunions dans le fichier Excel"""
    
    # Chemin vers le fichier Excel
    excel_path = 'suivi -equivalence-14juillet2025-Stagiaire.xlsx'
    
    try:
        # Lire le fichier Excel
        df = pd.read_excel(excel_path, header=None)
        print(f"📁 Fichier trouvé: {excel_path}")
        print(f"📊 Forme du fichier: {df.shape}")
        
        # Afficher les en-têtes des colonnes
        print("\n📋 En-têtes des colonnes:")
        for i in range(15):
            print(f"   Colonne {i}: {df.iloc[1, i]}")
        
        # Chercher les données de réunions
        print("\n🔍 Recherche des données de réunions:")
        
        reunions_trouvees = 0
        dossiers_avec_reunions = []
        
        for index, row in df.iterrows():
            try:
                # Ignorer les lignes vides ou en-têtes
                if (pd.isna(row[0]) or 
                    str(row[0]).strip() == '' or 
                    str(row[0]).lower() in ['no.', 'nan', 'situation des dossiers'] or
                    not str(row[0]).replace('.', '').replace('bis', '').isdigit()):
                    continue
                
                numero = str(row[0]).strip()
                reunions_dossier = []
                
                # Vérifier les colonnes de réunions
                if not pd.isna(row[12]) and str(row[12]).strip() != '':
                    reunions_dossier.append(f"24 mars 2025: {str(row[12]).strip()}")
                
                if not pd.isna(row[13]) and str(row[13]).strip() != '':
                    reunions_dossier.append(f"13 mai 2025: {str(row[13]).strip()}")
                
                if not pd.isna(row[14]) and str(row[14]).strip() != '':
                    reunions_dossier.append(f"16 juin 2025: {str(row[14]).strip()}")
                
                if reunions_dossier:
                    dossiers_avec_reunions.append({
                        'numero': numero,
                        'demandeur': str(row[1]).strip() if not pd.isna(row[1]) else f"Candidat {numero}",
                        'reunions': reunions_dossier
                    })
                    reunions_trouvees += len(reunions_dossier)
                    print(f"✅ Dossier {numero}: {len(reunions_dossier)} réunion(s)")
                    for reunion in reunions_dossier:
                        print(f"   📅 {reunion}")
                
            except Exception as e:
                print(f"❌ Erreur ligne {index + 1}: {str(e)}")
        
        print(f"\n📈 Résumé:")
        print(f"   - Dossiers avec réunions: {len(dossiers_avec_reunions)}")
        print(f"   - Total réunions trouvées: {reunions_trouvees}")
        
        if dossiers_avec_reunions:
            print(f"\n🎯 Dossiers avec réunions:")
            for dossier in dossiers_avec_reunions[:10]:  # Afficher les 10 premiers
                print(f"   📁 {dossier['numero']} - {dossier['demandeur']}")
                for reunion in dossier['reunions']:
                    print(f"      📅 {reunion}")
            
            if len(dossiers_avec_reunions) > 10:
                print(f"   ... et {len(dossiers_avec_reunions) - 10} autres dossiers")
        else:
            print("⚠️ Aucune réunion trouvée dans le fichier")
            
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier: {str(e)}")

if __name__ == "__main__":
    test_reunions_excel() 