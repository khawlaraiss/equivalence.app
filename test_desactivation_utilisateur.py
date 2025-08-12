#!/usr/bin/env python
"""
Test de la désactivation d'utilisateur
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from users.models import CustomUser

def test_desactivation_utilisateur():
    """Tester la désactivation d'utilisateur"""
    print("=== 🧪 TEST DÉSACTIVATION UTILISATEUR ===")
    print("Vérification que la désactivation fonctionne !")
    print()
    
    try:
        # 1. Vérifier qu'on a des utilisateurs
        utilisateurs = CustomUser.objects.all()
        total = utilisateurs.count()
        print(f"📊 Total utilisateurs: {total}")
        
        if total == 0:
            print("❌ Aucun utilisateur trouvé")
            return
        
        # 2. Trouver un utilisateur actif à désactiver
        utilisateur_actif = utilisateurs.filter(is_active=True).first()
        if not utilisateur_actif:
            print("❌ Aucun utilisateur actif trouvé")
            return
            
        print(f"🔍 Utilisateur de test: {utilisateur_actif.username}")
        print(f"   Statut actuel: {'Actif' if utilisateur_actif.is_active else 'Inactif'}")
        
        # 3. Tester la désactivation
        print(f"\n--- Test 1: Désactivation ---")
        ancien_statut = utilisateur_actif.is_active
        utilisateur_actif.is_active = False
        utilisateur_actif.save()
        
        # Recharger depuis la base
        utilisateur_actif.refresh_from_db()
        nouveau_statut = utilisateur_actif.is_active
        
        if nouveau_statut != ancien_statut:
            print(f"✅ Désactivation réussie !")
            print(f"   Avant: {'Actif' if ancien_statut else 'Inactif'}")
            print(f"   Après: {'Actif' if nouveau_statut else 'Inactif'}")
        else:
            print(f"❌ Échec de la désactivation")
        
        # 4. Tester la réactivation
        print(f"\n--- Test 2: Réactivation ---")
        ancien_statut = utilisateur_actif.is_active
        utilisateur_actif.is_active = True
        utilisateur_actif.save()
        
        # Recharger depuis la base
        utilisateur_actif.refresh_from_db()
        nouveau_statut = utilisateur_actif.is_active
        
        if nouveau_statut != ancien_statut:
            print(f"✅ Réactivation réussie !")
            print(f"   Avant: {'Actif' if ancien_statut else 'Inactif'}")
            print(f"   Après: {'Actif' if nouveau_statut else 'Inactif'}")
        else:
            print(f"❌ Échec de la réactivation")
        
        # 5. Vérifier les statistiques
        print(f"\n--- Test 3: Vérification des statistiques ---")
        total_actifs = CustomUser.objects.filter(is_active=True).count()
        total_inactifs = CustomUser.objects.filter(is_active=False).count()
        
        print(f"   Utilisateurs actifs: {total_actifs}")
        print(f"   Utilisateurs inactifs: {total_inactifs}")
        print(f"   Total: {total_actifs + total_inactifs}")
        
        if total_actifs + total_inactifs == total:
            print(f"✅ Statistiques cohérentes")
        else:
            print(f"❌ Incohérence dans les statistiques")
        
        print()
        print("🎯 CONCLUSION:")
        print("   Si les tests 1 et 2 sont réussis,")
        print("   alors la désactivation/réactivation fonctionne !")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_desactivation_utilisateur()

