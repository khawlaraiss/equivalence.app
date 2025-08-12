import pandas as pd
import os
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Analyser le fichier Excel pour extraire les universités et pays uniques'

    def handle(self, *args, **options):
        # Chemin vers le fichier Excel
        excel_file = os.path.join(settings.BASE_DIR, 'suivi -equivalence-14juillet2025-Stagiaire.xlsx')
        
        if not os.path.exists(excel_file):
            self.stdout.write(
                self.style.ERROR(f'Fichier Excel non trouvé: {excel_file}')
            )
            return
        
        try:
            # Lire le fichier Excel sans en-têtes pour voir la structure réelle
            df = pd.read_excel(excel_file, header=None)
            
            self.stdout.write(
                self.style.SUCCESS(f'Fichier Excel lu avec succès. Dimensions: {df.shape}')
            )
            
            # Afficher les premières lignes pour comprendre la structure
            self.stdout.write("\n" + "="*80)
            self.stdout.write("STRUCTURE DU FICHIER EXCEL:")
            self.stdout.write("="*80)
            
            # Afficher les 10 premières lignes
            for i in range(min(10, len(df))):
                self.stdout.write(f"\nLigne {i}:")
                for j in range(min(15, len(df.columns))):
                    value = df.iloc[i, j]
                    if pd.notna(value):
                        self.stdout.write(f"  Colonne {j}: {value}")
            
            # Chercher les lignes qui contiennent des informations sur les universités et pays
            self.stdout.write("\n" + "="*80)
            self.stdout.write("RECHERCHE D'INFORMATIONS SUR UNIVERSITÉS ET PAYS:")
            self.stdout.write("="*80)
            
            # Parcourir toutes les lignes pour trouver des informations pertinentes
            universites = set()
            pays = set()
            
            for i in range(len(df)):
                for j in range(len(df.columns)):
                    value = str(df.iloc[i, j]).strip()
                    if pd.notna(df.iloc[i, j]) and value != 'nan':
                        # Chercher des mots-clés pour les universités
                        if any(keyword in value.lower() for keyword in ['université', 'universite', 'university', 'institut', 'école', 'ecole', 'faculty', 'college']):
                            universites.add(value)
                        
                        # Chercher des mots-clés pour les pays
                        if any(keyword in value.lower() for keyword in ['maroc', 'algerie', 'tunisie', 'france', 'canada', 'belgique', 'suisse', 'allemagne', 'italie', 'espagne', 'pays-bas', 'royaume-uni', 'etats-unis', 'chine', 'japon', 'inde', 'egypte', 'liban', 'jordanie', 'syrie', 'irak', 'iran', 'arabie', 'turquie', 'russie', 'ukraine', 'pologne', 'hongrie', 'roumanie', 'bulgarie', 'grece', 'portugal', 'bresil', 'argentine', 'chili', 'mexique', 'australie', 'nouvelle-zelande']):
                            pays.add(value)
            
            # Afficher les résultats
            if universites:
                self.stdout.write("\nUNIVERSITÉS TROUVÉES:")
                for univ in sorted(universites):
                    self.stdout.write(f"  - {univ}")
            
            if pays:
                self.stdout.write("\nPAYS TROUVÉS:")
                for p in sorted(pays):
                    self.stdout.write(f"  - {p}")
            
            # Analyser les colonnes spécifiques mentionnées dans le code d'import
            self.stdout.write("\n" + "="*80)
            self.stdout.write("ANALYSE DES COLONNES SPÉCIFIQUES:")
            self.stdout.write("="*80)
            
            # Colonne 8 (diplôme), 9 (université), 10 (pays) selon le code d'import
            if len(df.columns) > 10:
                self.stdout.write(f"\nColonne 8 (Diplôme):")
                for i in range(len(df)):
                    value = df.iloc[i, 8]
                    if pd.notna(value):
                        self.stdout.write(f"  Ligne {i}: {value}")
                
                self.stdout.write(f"\nColonne 9 (Université):")
                for i in range(len(df)):
                    value = df.iloc[i, 9]
                    if pd.notna(value):
                        self.stdout.write(f"  Ligne {i}: {value}")
                
                self.stdout.write(f"\nColonne 10 (Pays):")
                for i in range(len(df)):
                    value = df.iloc[i, 10]
                    if pd.notna(value):
                        self.stdout.write(f"  Ligne {i}: {value}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de la lecture du fichier Excel: {e}')
            ) 