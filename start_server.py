#!/usr/bin/env python
import os
import sys
import django
import subprocess

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

def start_server():
    print("🚀 Démarrage du serveur Django...")
    print("📁 Répertoire de travail:", os.getcwd())
    print("📄 Fichier manage.py trouvé:", os.path.exists('manage.py'))
    
    try:
        # Démarrer le serveur Django
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'runserver'])
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        print("🔄 Tentative de démarrage alternatif...")
        
        try:
            # Alternative avec subprocess
            subprocess.run([sys.executable, 'manage.py', 'runserver'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur subprocess: {e}")
        except Exception as e:
            print(f"❌ Erreur générale: {e}")

if __name__ == '__main__':
    start_server() 