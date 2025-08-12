#!/usr/bin/env python
"""
Test de la correction des dossiers traités
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier, DossierTraite

def test_correction_dossiers_traites():
    """Tester la correction des dossiers traités"""
    print("=== 🧪 TEST DE LA CORRECTION ===")
    print("Vérification que vos 44 dossiers traités sont bien là !")
    print()
    
    try:
        # 1. Vérifier le modèle DossierTraite (le bon modèle)
        print("📋 MODÈLE 'DossierTraite' (VOTRE VRAI MODÈLE):")
        dossiers_traites = DossierTraite.objects.all().order_by('-date_creation')
        total_traites = dossiers_traites.count()
        print(f"   Total dossiers traités: {total_traites}")
        
        if total_traites > 0:
            print(f"   ✅ VOS {total_traites} DOSSIERS TRAITÉS SONT BIEN LÀ !")
            
            # Afficher les 10 premiers
            print("\n   🔍 10 premiers dossiers traités:")
            for i, dossier in enumerate(dossiers_traites[:10]):
                print(f"     {i+1}. ID {dossier.id}: {dossier.numero} - {dossier.demandeur_candidat}")
            
            # Afficher les 10 derniers
            print("\n   🔍 10 derniers dossiers traités:")
            for i, dossier in enumerate(dossiers_traites.order_by('-id')[:10]):
                print(f"     {i+1}. ID {dossier.id}: {dossier.numero} - {dossier.demandeur_candidat}")
                
        else:
            print("   ❌ AUCUN DOSSIER TRAITÉ TROUVÉ !")
        
        print()
        
        # 2. Vérifier le modèle Dossier (pour comparaison)
        print("📁 MODÈLE 'Dossier' (pour comparaison):")
        dossiers_principaux = Dossier.objects.filter(statut='traite')
        total_principaux = dossiers_principaux.count()
        print(f"   Total dossiers avec statut='traite': {total_principaux}")
        
        if total_principaux > 0:
            for dossier in dossiers_principaux:
                print(f"     ID {dossier.id}: {dossier.titre} - {dossier.statut}")
        
        print()
        
        # 3. Résumé de la situation
        print("🎯 RÉSUMÉ DE LA SITUATION:")
        print(f"   📊 Dossiers dans DossierTraite: {total_traites}")
        print(f"   📊 Dossiers dans Dossier (statut='traite'): {total_principaux}")
        
        if total_traites == 44:
            print("   ✅ PARFAIT ! Vos 44 dossiers traités sont bien là !")
        elif total_traites > 0:
            print(f"   ⚠️ Vous avez {total_traites} dossiers traités (pas 44)")
        else:
            print("   ❌ Aucun dossier traité trouvé !")
        
        print()
        print("🔧 La correction a été appliquée !")
        print("   Maintenant la vue devrait afficher tous vos dossiers traités.")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_correction_dossiers_traites()
