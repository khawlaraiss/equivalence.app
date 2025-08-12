#!/usr/bin/env python
import sqlite3
import os

def fix_database_v2():
    """Corrige la base de données en ajoutant la colonne criteres_fixes_supprimes"""
    
    db_path = 'db.sqlite3'
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier la structure de la table
        cursor.execute("PRAGMA table_info(dossiers_structureevaluationglobale)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'criteres_fixes_supprimes' not in columns:
            print("🔧 Ajout de la colonne criteres_fixes_supprimes...")
            
            # Ajouter la colonne
            cursor.execute("""
                ALTER TABLE dossiers_structureevaluationglobale 
                ADD COLUMN criteres_fixes_supprimes TEXT DEFAULT '[]'
            """)
            
            conn.commit()
            print("✅ Colonne ajoutée avec succès!")
        else:
            print("✅ La colonne existe déjà.")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Correction de la base de données (v2)...")
    if fix_database_v2():
        print("🎉 Base de données corrigée!")
    else:
        print("💥 Échec de la correction.") 