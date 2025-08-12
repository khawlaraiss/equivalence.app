#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from django.db import connection
from django.db import migrations

def apply_migration_manually():
    """Applique manuellement la migration pour ajouter le champ competences_criteres_fixes"""
    
    with connection.cursor() as cursor:
        try:
            # Vérifier si la colonne existe déjà
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'dossiers_structureevaluationglobale' 
                AND column_name = 'competences_criteres_fixes'
            """)
            
            if not cursor.fetchone():
                print("Ajout de la colonne competences_criteres_fixes...")
                
                # Ajouter la colonne
                cursor.execute("""
                    ALTER TABLE dossiers_structureevaluationglobale 
                    ADD COLUMN competences_criteres_fixes JSON DEFAULT '{}'
                """)
                
                print("✅ Colonne competences_criteres_fixes ajoutée avec succès!")
            else:
                print("✅ La colonne competences_criteres_fixes existe déjà.")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout de la colonne: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Application manuelle de la migration...")
    success = apply_migration_manually()
    if success:
        print("🎉 Migration appliquée avec succès!")
    else:
        print("💥 Échec de la migration.") 