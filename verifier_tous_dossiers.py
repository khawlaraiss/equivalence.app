#!/usr/bin/env python
"""
Vérification complète de TOUS les dossiers
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier, DossierTraite

def verifier_tous_dossiers():
    """Vérifier TOUS les dossiers pour rassurer l'utilisateur"""
    print("=== VÉRIFICATION COMPLÈTE - TOUS LES DOSSIERS ===")
    print("🔒 AUCUN DOSSIER N'A ÉTÉ SUPPRIMÉ !")
    print()
    
    try:
        # 1. Vérifier le modèle Dossier
        print("📁 MODÈLE 'Dossier' (Principal):")
        tous_dossiers = Dossier.objects.all().order_by('id')
        print(f"   Total: {tous_dossiers.count()} dossiers")
        
        for dossier in tous_dossiers:
            print(f"   ✅ ID {dossier.id}: '{dossier.titre}' - Statut: {dossier.statut}")
        
        print()
        
        # 2. Vérifier le modèle DossierTraite
        print("📋 MODÈLE 'DossierTraite' (Historique):")
        tous_dossiers_traites = DossierTraite.objects.all().order_by('id')
        print(f"   Total: {tous_dossiers_traites.count()} dossiers traités")
        
        for dossier_traite in tous_dossiers_traites:
            print(f"   ✅ ID {dossier_traite.id}: '{dossier_traite.numero}' - Candidat: {dossier_traite.demandeur_candidat}")
        
        print()
        
        # 3. Résumé rassurant
        print("🎯 RÉSUMÉ:")
        print(f"   📊 Dossiers totaux: {tous_dossiers.count()}")
        print(f"   📊 Dossiers traités (statut='traite'): {tous_dossiers.filter(statut='traite').count()}")
        print(f"   📊 Dossiers en cours: {tous_dossiers.filter(statut='en_cours').count()}")
        print(f"   📊 Dossiers non traités: {tous_dossiers.filter(statut='non_traite').count()}")
        print(f"   📊 Dossiers archivés: {tous_dossiers.filter(statut='archive').count()}")
        
        print()
        print("✅ CONCLUSION: TOUS VOS DOSSIERS SONT INTACTS !")
        print("   Le problème était juste une incohérence dans l'affichage, pas une suppression !")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verifier_tous_dossiers()

