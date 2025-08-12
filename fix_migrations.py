#!/usr/bin/env python
"""
Script pour résoudre automatiquement le conflit de migrations
"""

import os
import sys
import django
import subprocess

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

def fix_migrations():
    """Résoudre le conflit de migrations"""
    print("🔧 Résolution du conflit de migrations...")
    
    try:
        # Supprimer les migrations conflictuelles
        migrations_to_remove = [
            "dossiers/migrations/0022_add_competences_criteres_fixes.py",
            "dossiers/migrations/0022_structureevaluationglobale_competences_criteres_fixes.py",
            "dossiers/migrations/0023_add_criteres_fixes_supprimes.py"
        ]
        
        for migration_file in migrations_to_remove:
            if os.path.exists(migration_file):
                os.remove(migration_file)
                print(f"✅ Supprimé: {migration_file}")
        
        # Créer une nouvelle migration propre
        print("📝 Création d'une nouvelle migration...")
        result = subprocess.run([
            sys.executable, "manage.py", "makemigrations", "dossiers"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Nouvelle migration créée avec succès")
            print(result.stdout)
        else:
            print("❌ Erreur lors de la création de la migration:")
            print(result.stderr)
            return False
        
        # Appliquer les migrations
        print("🚀 Application des migrations...")
        result = subprocess.run([
            sys.executable, "manage.py", "migrate"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migrations appliquées avec succès")
            print(result.stdout)
            return True
        else:
            print("❌ Erreur lors de l'application des migrations:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Script de résolution des migrations")
    print("=" * 50)
    
    success = fix_migrations()
    
    if success:
        print("\n🎉 Conflit de migrations résolu avec succès !")
        print("Vous pouvez maintenant tester le bouton de suppression.")
    else:
        print("\n❌ Échec de la résolution des migrations.")
        print("Vérifiez les erreurs ci-dessus.")
    
    print("\n" + "=" * 50) 