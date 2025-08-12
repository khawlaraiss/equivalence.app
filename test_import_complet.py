#!/usr/bin/env python
"""
Script de test complet pour l'import Excel avec données réelles
"""

import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

import pandas as pd
from datetime import datetime
from dossiers.models import DossierTraite
from users.models import CustomUser

def test_import_complet():
    """Test complet de l'import avec données réelles"""
    
    excel_path = 'suivi -equivalence-14juillet2025-Stagiaire.xlsx'
    
    if not os.path.exists(excel_path):
        print(f"❌ Fichier {excel_path} non trouvé")
        return
    
    print(f"📁 Fichier trouvé: {excel_path}")
    
    try:
        df = pd.read_excel(excel_path, header=None)
        print(f"📊 Forme du fichier: {df.shape}")
        
        # Compter les dossiers valides
        dossiers_valides = 0
        dossiers_avec_reunions = 0
        dossiers_avec_avis = 0
        
        for index, row in df.iterrows():
            try:
                # Ignorer les lignes vides ou en-têtes
                if (pd.isna(row[0]) or 
                    str(row[0]).strip() == '' or 
                    str(row[0]).lower() in ['no.', 'nan', 'situation des dossiers'] or
                    not str(row[0]).replace('.', '').replace('bis', '').isdigit()):
                    continue
                
                numero = str(row[0]).strip()
                dossiers_valides += 1
                
                # Vérifier les réunions
                reunions_count = 0
                if not pd.isna(row[12]) and str(row[12]).strip() != '':
                    reunions_count += 1
                if not pd.isna(row[13]) and str(row[13]).strip() != '':
                    reunions_count += 1
                if not pd.isna(row[14]) and str(row[14]).strip() != '':
                    reunions_count += 1
                
                if reunions_count > 0:
                    dossiers_avec_reunions += 1
                
                # Vérifier l'avis de la commission
                if not pd.isna(row[10]) and str(row[10]).strip() != '':
                    dossiers_avec_avis += 1
                
                # Afficher un exemple de dossier
                if dossiers_valides == 1:
                    print(f"\n📋 Exemple de dossier (ligne {index + 1}):")
                    print(f"   Numéro: {numero}")
                    print(f"   Demandeur: {str(row[1]).strip() if not pd.isna(row[1]) else 'Non spécifié'}")
                    print(f"   Université: {str(row[7]).strip() if not pd.isna(row[7]) else 'Non spécifiée'}")
                    print(f"   Pays: {str(row[8]).strip() if not pd.isna(row[8]) else 'Non spécifié'}")
                    print(f"   Avis commission: {str(row[10]).strip() if not pd.isna(row[10]) else 'Non spécifié'}")
                    print(f"   Réunions: {reunions_count}")
                    
                    if reunions_count > 0:
                        print("   📅 Détails des réunions:")
                        if not pd.isna(row[12]) and str(row[12]).strip() != '':
                            print(f"      - 24 mars 2025: {str(row[12]).strip()}")
                        if not pd.isna(row[13]) and str(row[13]).strip() != '':
                            print(f"      - 13 mai 2025: {str(row[13]).strip()}")
                        if not pd.isna(row[14]) and str(row[14]).strip() != '':
                            print(f"      - 16 juin 2025: {str(row[14]).strip()}")
                
            except Exception as e:
                print(f"❌ Erreur ligne {index + 1}: {str(e)}")
        
        print(f"\n📈 Résumé des données:")
        print(f"   - Dossiers valides: {dossiers_valides}")
        print(f"   - Dossiers avec réunions: {dossiers_avec_reunions}")
        print(f"   - Dossiers avec avis: {dossiers_avec_avis}")
        
        # Vérifier les dossiers existants
        numeros_existants = []
        for index, row in df.iterrows():
            try:
                if (pd.isna(row[0]) or 
                    str(row[0]).strip() == '' or 
                    str(row[0]).lower() in ['no.', 'nan', 'situation des dossiers'] or
                    not str(row[0]).replace('.', '').replace('bis', '').isdigit()):
                    continue
                
                numero = str(row[0]).strip()
                if DossierTraite.objects.filter(numero=numero).exists():
                    numeros_existants.append(numero)
            except:
                continue
        
        print(f"   - Dossiers déjà existants: {len(numeros_existants)}")
        if numeros_existants:
            print(f"      Numéros: {numeros_existants[:5]}{'...' if len(numeros_existants) > 5 else ''}")
        
        dossiers_a_importer = dossiers_valides - len(numeros_existants)
        print(f"   - Dossiers à importer: {dossiers_a_importer}")
        
        if dossiers_a_importer > 0:
            print(f"\n🚀 Prêt pour l'import de {dossiers_a_importer} dossiers avec:")
            print(f"   ✅ Données complètes (candidats, universités, pays)")
            print(f"   ✅ Avis de la commission")
            print(f"   ✅ Réunions avec décisions réelles")
        else:
            print(f"\n⚠️ Tous les dossiers sont déjà importés")
            
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier: {str(e)}")

if __name__ == "__main__":
    test_import_complet() 