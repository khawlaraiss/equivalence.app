#!/usr/bin/env python
"""
Script pour vérifier si les dossiers ont été importés avec leurs avis de commission
"""

import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import DossierTraite

def verifier_import():
    """Vérifier les dossiers importés et leurs avis"""
    
    dossiers = DossierTraite.objects.all()
    total = dossiers.count()
    
    print(f"📊 Total dossiers traités dans la base: {total}")
    
    if total == 0:
        print("❌ Aucun dossier importé. Vous devez d'abord faire l'import automatique.")
        return
    
    print("\n📋 Dossiers avec avis de commission:")
    print("=" * 60)
    
    dossiers_avec_avis = 0
    
    for dossier in dossiers[:10]:  # Afficher seulement les 10 premiers
        print(f"\n📁 Dossier {dossier.numero} - {dossier.demandeur_candidat}")
        print(f"   Université: {dossier.universite}")
        print(f"   Pays: {dossier.pays}")
        
        if dossier.avis_commission and dossier.avis_commission != "Avis non spécifié":
            print(f"   ✅ Avis: {dossier.avis_commission}")
            dossiers_avec_avis += 1
        else:
            print(f"   ❌ Pas d'avis")
        
        print("-" * 40)
    
    print(f"\n📈 Résumé:")
    print(f"   - Total dossiers: {total}")
    print(f"   - Dossiers avec avis: {dossiers_avec_avis}")
    print(f"   - Dossiers sans avis: {total - dossiers_avec_avis}")
    
    if dossiers_avec_avis == 0:
        print(f"\n⚠️ Aucun avis de commission trouvé dans la base de données.")
        print(f"   Vous devez faire l'import automatique pour importer les avis depuis le fichier Excel.")

if __name__ == "__main__":
    verifier_import() 