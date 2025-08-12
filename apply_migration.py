#!/usr/bin/env python
import os
import sys
import django

# Ajouter le répertoire du projet au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    print("Application de la migration...")
    execute_from_command_line(['manage.py', 'migrate'])
    print("Migration terminée !") 