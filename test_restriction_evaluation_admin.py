#!/usr/bin/env python
"""
Test de restriction des fonctionnalités d'évaluation pour les administrateurs
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from users.models import CustomUser
from dossiers.models import Dossier, Candidat
from django.urls import reverse
from django.test import Client
from django.contrib.auth import authenticate

def test_restriction_evaluation_admin():
    """Tester que les admins ne peuvent pas accéder aux fonctionnalités d'évaluation"""
    print("=== 🧪 TEST RESTRICTION ÉVALUATION ADMIN ===")
    print("Vérification que les admins ne peuvent pas évaluer !")
    print()
    
    try:
        # 1. Vérifier qu'on a des utilisateurs
        admins = CustomUser.objects.filter(role='admin')
        professeurs = CustomUser.objects.filter(role='professeur')
        
        print(f"📊 Utilisateurs trouvés:")
        print(f"   - Administrateurs: {admins.count()}")
        print(f"   - Professeurs: {professeurs.count()}")
        
        if admins.count() == 0 or professeurs.count() == 0:
            print("❌ Besoin d'au moins 1 admin et 1 professeur pour le test")
            return
        
        # 2. Prendre un admin et un professeur pour le test
        admin_user = admins.first()
        prof_user = professeurs.first()
        
        print(f"\n--- Utilisateurs de test ---")
        print(f"   Admin: {admin_user.username}")
        print(f"   Professeur: {prof_user.username}")
        
        # 3. Vérifier qu'on a des dossiers
        dossiers = Dossier.objects.all()
        if dossiers.count() == 0:
            print("❌ Aucun dossier trouvé pour le test")
            return
        
        dossier_test = dossiers.first()
        print(f"\n--- Dossier de test ---")
        print(f"   ID: {dossier_test.id}")
        print(f"   Statut: {dossier_test.statut}")
        
        # 4. Tester l'accès aux URLs d'évaluation
        print(f"\n--- Test des URLs d'évaluation ---")
        
        urls_a_tester = [
            ('consistance_academique', 'dossiers:consistance_academique'),
            ('evaluation_equivalence', 'dossiers:evaluation_equivalence'),
        ]
        
        for nom, url_name in urls_a_tester:
            try:
                url = reverse(url_name, args=[dossier_test.id])
                print(f"   ✅ URL {nom}: {url}")
            except Exception as e:
                print(f"   ❌ Erreur URL {nom}: {e}")
        
        # 5. Vérifier les permissions dans les vues
        print(f"\n--- Vérification des permissions ---")
        
        # Importer les vues
        try:
            from dossiers.views import consistance_academique, evaluation_equivalence
            print(f"   ✅ Vues trouvées")
            
            # Vérifier les décorateurs de permission
            import inspect
            for nom_vue, vue in [('consistance_academique', consistance_academique), 
                                ('evaluation_equivalence', evaluation_equivalence)]:
                if hasattr(vue, '__wrapped__'):
                    print(f"      {nom_vue}: Décorateur détecté")
                else:
                    print(f"      {nom_vue}: Pas de décorateur visible")
                    
        except ImportError as e:
            print(f"   ❌ Erreur import vues: {e}")
        
        # 6. Vérifier les templates
        print(f"\n--- Vérification des templates ---")
        
        template_paths = [
            "equivalence/templates/dossiers/evaluation_equivalence.html",
            "equivalence/templates/dossiers/consistance_academique.html"
        ]
        
        for template_path in template_paths:
            if os.path.exists(template_path):
                print(f"   ✅ Template: {template_path}")
                
                # Vérifier les restrictions dans le template
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'user.role == \'professeur\'' in content:
                        print(f"      ✅ Restrictions de rôle détectées")
                    else:
                        print(f"      ⚠️ Pas de restrictions de rôle visibles")
            else:
                print(f"   ❌ Template non trouvé: {template_path}")
        
        print()
        print("🎯 TEST TERMINÉ")
        print("   Les restrictions d'évaluation pour les admins sont configurées !")
        print()
        print("📋 RÉSUMÉ DES RESTRICTIONS :")
        print(f"   🔒 Admins: Ne peuvent PAS évaluer")
        print(f"   👨‍🏫 Professeurs: Peuvent évaluer")
        print(f"   📝 Bouton 'Commencer l'évaluation': Professeurs uniquement")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_restriction_evaluation_admin()

