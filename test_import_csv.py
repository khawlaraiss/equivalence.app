#!/usr/bin/env python3
"""
Test de la fonctionnalité d'import CSV
"""

import os
import sys
import django
import tempfile
import csv

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import DossierTraite
from users.models import CustomUser
from django.urls import reverse
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

def test_import_csv():
    print("=== 🧪 TEST IMPORT CSV ===")
    
    # Vérifier les utilisateurs
    try:
        admin = CustomUser.objects.get(username='admin')
        print(f"✅ Admin trouvé: {admin.username}")
    except CustomUser.DoesNotExist as e:
        print(f"❌ Erreur utilisateur: {e}")
        return
    
         # Compter les dossiers avant l'import
     dossiers_avant = DossierTraite.objects.count()
     
     print(f"\n📊 État avant import:")
     print(f"   Dossiers traités: {dossiers_avant}")
    
         # Créer un fichier CSV de test avec les vrais champs du modèle DossierTraite
     csv_content = """numero,demandeur_candidat,reference,date_envoi,date_reception,diplome,universite,pays,avis_commission
 TEST001,Jean Dupont,REF001,2025-01-15,2025-01-20,Master Informatique,sorbonne,france,Équivalence accordée
 TEST002,Marie Smith,REF002,2025-01-10,2025-01-18,Ingénieur Civil,epfl,suisse,Équivalence conditionnelle
 TEST003,Carlos Garcia,REF003,2025-01-12,2025-01-19,Licence Mathématiques,autre,mexique,Non équivalent"""
    
    # Créer un fichier temporaire
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(csv_content)
        temp_file_path = temp_file.name
    
    try:
        # Lire le fichier et créer un SimpleUploadedFile
        with open(temp_file_path, 'rb') as f:
            csv_file = SimpleUploadedFile(
                'test_dossiers.csv',
                f.read(),
                content_type='text/csv'
            )
        
        # Tester l'accès à la page d'import
        client = Client()
        client.force_login(admin)
        
        print(f"\n🔗 Test accès page import CSV:")
        response = client.get(reverse('dossiers:import_csv_dossiers'))
        print(f"   Status: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Vérifier que le formulaire est présent
            if 'csv_file' in content:
                print(f"   ✅ Formulaire d'upload présent")
            else:
                print(f"   ❌ Formulaire d'upload manquant")
                
            if 'Importer des Dossiers depuis CSV' in content:
                print(f"   ✅ Titre de la page affiché")
            else:
                print(f"   ❌ Titre de la page manquant")
        
        # Tester l'import du fichier CSV
        print(f"\n🔗 Test import fichier CSV:")
        
        with open(temp_file_path, 'rb') as f:
            response = client.post(reverse('dossiers:import_csv_dossiers'), {
                'csv_file': SimpleUploadedFile(
                    'test_dossiers.csv',
                    f.read(),
                    content_type='text/csv'
                )
            })
        
        print(f"   Status: {response.status_code} {'✅' if response.status_code == 302 else '❌'}")
        
        if response.status_code == 302:
            print(f"   ✅ Redirection après import (succès)")
            
                         # Vérifier que les dossiers ont été créés
             dossiers_apres = DossierTraite.objects.count()
             
             print(f"\n📊 État après import:")
             print(f"   Dossiers traités: {dossiers_apres} (+{dossiers_apres - dossiers_avant})")
            
                         # Vérifier les nouveaux dossiers
             nouveaux_dossiers = DossierTraite.objects.filter(numero__startswith='TEST')
             print(f"\n🔍 Nouveaux dossiers créés:")
             for dossier in nouveaux_dossiers:
                 print(f"   ✅ {dossier.numero} - {dossier.demandeur_candidat}")
                 print(f"      Référence: {dossier.reference}")
                 print(f"      Diplôme: {dossier.diplome}")
                 print(f"      Université: {dossier.universite}")
                 print(f"      Pays: {dossier.pays}")
                 print(f"      Avis: {dossier.avis_commission}")
             
             # Nettoyer les données de test
             print(f"\n🧹 Nettoyage des données de test...")
             nouveaux_dossiers.delete()
            
            print(f"   ✅ Données de test supprimées")
            
        else:
            print(f"   ❌ Échec de l'import")
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                print(f"   Contenu de la réponse: {content[:200]}...")
    
    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            print(f"   ✅ Fichier temporaire supprimé")
    
    print(f"\n🎯 TEST TERMINÉ")

if __name__ == '__main__':
    test_import_csv()
