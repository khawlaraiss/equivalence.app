#!/usr/bin/env python
"""
Test simple de désactivation d'utilisateur
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from users.models import CustomUser

def test_simple_desactivation():
    """Test simple de désactivation"""
    print("=== 🧪 TEST SIMPLE DÉSACTIVATION ===")
    print("Test direct de la modification en base !")
    print()
    
    try:
        # 1. Lister tous les utilisateurs
        utilisateurs = CustomUser.objects.all()
        print(f"📊 Total utilisateurs: {utilisateurs.count()}")
        
        for user in utilisateurs:
            print(f"   - {user.username}: {user.get_role_display()} - {'Actif' if user.is_active else 'Inactif'}")
        
        # 2. Prendre un utilisateur non-admin pour le test
        utilisateur_test = utilisateurs.exclude(role='admin').filter(is_active=True).first()
        if not utilisateur_test:
            print("❌ Aucun utilisateur non-admin actif trouvé")
            return
            
        print(f"\n🔍 Utilisateur de test: {utilisateur_test.username}")
        print(f"   Rôle: {utilisateur_test.get_role_display()}")
        print(f"   Statut actuel: {'Actif' if utilisateur_test.is_active else 'Inactif'}")
        
        # 3. Tester la désactivation
        print(f"\n--- Test de désactivation ---")
        ancien_statut = utilisateur_test.is_active
        
        # Modifier le statut
        utilisateur_test.is_active = False
        utilisateur_test.save()
        
        # Recharger depuis la base
        utilisateur_test.refresh_from_db()
        nouveau_statut = utilisateur_test.is_active
        
        print(f"   Avant: {'Actif' if ancien_statut else 'Inactif'}")
        print(f"   Après: {'Actif' if nouveau_statut else 'Inactif'}")
        
        if nouveau_statut != ancien_statut:
            print(f"✅ Désactivation réussie !")
            
            # Remettre l'état initial
            utilisateur_test.is_active = ancien_statut
            utilisateur_test.save()
            print(f"✅ État initial restauré")
        else:
            print(f"❌ Échec de la désactivation")
        
        # 4. Vérifier les statistiques
        print(f"\n--- Vérification des statistiques ---")
        total_actifs = CustomUser.objects.filter(is_active=True).count()
        total_inactifs = CustomUser.objects.filter(is_active=False).count()
        
        print(f"   Utilisateurs actifs: {total_actifs}")
        print(f"   Utilisateurs inactifs: {total_inactifs}")
        print(f"   Total: {total_actifs + total_inactifs}")
        
        # 5. Vérifier que la vue existe
        print(f"\n--- Vérification de la vue ---")
        try:
            from users.views import desactiver_utilisateur
            print(f"✅ Vue 'desactiver_utilisateur' trouvée")
            
            # Vérifier la signature de la fonction
            import inspect
            sig = inspect.signature(desactiver_utilisateur)
            print(f"   Signature: {sig}")
            
        except ImportError as e:
            print(f"❌ Vue non trouvée: {e}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        print()
        print("🎯 TEST TERMINÉ")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_desactivation()

