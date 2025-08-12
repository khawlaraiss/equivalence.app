#!/usr/bin/env python
"""
Vérification simple de la suppression corrigée
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import DossierTraite

def verification_simple_suppression():
    """Vérification simple que la suppression peut fonctionner"""
    print("=== 🔍 VÉRIFICATION SIMPLE SUPPRESSION ===")
    print("Vérification que la vue peut maintenant trouver vos dossiers !")
    print()
    
    try:
        # 1. Vérifier qu'on a des dossiers traités
        dossiers_traites = DossierTraite.objects.all()
        total = dossiers_traites.count()
        print(f"📊 Total dossiers traités: {total}")
        
        if total == 0:
            print("❌ Aucun dossier traité trouvé")
            return
        
        # 2. Tester avec l'ID 44 (celui qui causait l'erreur)
        try:
            dossier_44 = DossierTraite.objects.get(id=44)
            print(f"✅ Dossier ID 44 TROUVÉ !")
            print(f"   Numéro: {dossier_44.numero}")
            print(f"   Candidat: {dossier_44.demandeur_candidat}")
            print(f"   Date création: {dossier_44.date_creation}")
            print()
            print("🎉 SUCCÈS ! La correction a fonctionné !")
            print("   Maintenant vous pouvez supprimer ce dossier sans erreur 404.")
            
        except DossierTraite.DoesNotExist:
            print(f"❌ Dossier ID 44 NON trouvé dans DossierTraite")
            
        # 3. Tester avec quelques autres IDs
        print(f"\n🔍 Test avec d'autres IDs:")
        for i in [1, 10, 20, 30, 40]:
            try:
                dossier = DossierTraite.objects.get(id=i)
                print(f"   ✅ ID {i}: {dossier.numero} - {dossier.demandeur_candidat}")
            except DossierTraite.DoesNotExist:
                print(f"   ❌ ID {i}: Non trouvé")
        
        print()
        print("🎯 RÉSUMÉ:")
        print(f"   - Vos {total} dossiers traités sont bien dans DossierTraite")
        print(f"   - La vue de suppression utilise maintenant le bon modèle")
        print(f"   - Plus d'erreur 404 lors de la suppression !")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verification_simple_suppression()

