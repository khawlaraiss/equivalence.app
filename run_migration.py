import os
import sys
import django

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from django.core.management import call_command

print("Application de la migration...")
try:
    call_command('migrate')
    print("✅ Migration appliquée avec succès !")
except Exception as e:
    print(f"❌ Erreur lors de la migration : {e}") 