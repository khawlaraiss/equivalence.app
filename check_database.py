#!/usr/bin/env python
import sqlite3
import os

def check_database():
    """Vérifie l'état de la base de données"""
    
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
        columns = cursor.fetchall()
        
        print("📋 Structure de la table dossiers_structureevaluationglobale:")
        for column in columns:
            print(f"  - {column[1]} ({column[2]}) - Default: {column[4]}")
        
        # Vérifier si la colonne existe
        column_names = [column[1] for column in columns]
        if 'competences_criteres_fixes' in column_names:
            print("✅ La colonne competences_criteres_fixes existe")
            
            # Vérifier le contenu
            cursor.execute("SELECT competences_criteres_fixes FROM dossiers_structureevaluationglobale LIMIT 1")
            result = cursor.fetchone()
            print(f"📄 Contenu: {result[0] if result else 'Aucune donnée'}")
        else:
            print("❌ La colonne competences_criteres_fixes n'existe pas")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Vérification de la base de données...")
    check_database() 