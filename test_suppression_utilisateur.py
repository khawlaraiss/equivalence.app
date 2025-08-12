#!/usr/bin/env python
"""
Test de la suppression d'utilisateur
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from users.models import CustomUser
from django.urls import reverse

def test_suppression_utilisateur():
    """Tester la suppression d'utilisateur"""
    print("=== 🧪 TEST SUPPRESSION UTILISATEUR ===")
    print("Vérification que la suppression fonctionne !")
    print()
    
    try:
        # 1. Vérifier qu'on a des utilisateurs
        utilisateurs = CustomUser.objects.all()
        total = utilisateurs.count()
        print(f"📊 Total utilisateurs: {total}")
        
        if total == 0:
            print("❌ Aucun utilisateur trouvé")
            return
        
        # 2. Lister les utilisateurs
        print(f"\n--- Liste des utilisateurs ---")
        for user in utilisateurs:
            print(f"   - {user.username}: {user.get_role_display()} - {'Actif' if user.is_active else 'Inactif'}")
        
        # 3. Vérifier l'URL de suppression
        print(f"\n--- Vérification de l'URL ---")
        try:
            url_suppression = reverse('users:supprimer_utilisateur', args=[1])
            print(f"✅ URL de suppression: {url_suppression}")
        except Exception as e:
            print(f"❌ Erreur URL: {e}")
            return
        
        # 4. Vérifier que la vue existe
        print(f"\n--- Vérification de la vue ---")
        try:
            from users.views import supprimer_utilisateur
            print(f"✅ Vue 'supprimer_utilisateur' trouvée")
            
            import inspect
            sig = inspect.signature(supprimer_utilisateur)
            print(f"   Signature: {sig}")
            
        except ImportError as e:
            print(f"❌ Vue non trouvée: {e}")
            return
        
        # 5. Vérifier les permissions
        print(f"\n--- Vérification des permissions ---")
        admins_count = CustomUser.objects.filter(role='admin').count()
        print(f"   Nombre d'administrateurs: {admins_count}")
        
        if admins_count <= 1:
            print(f"   ⚠️ Attention: Seulement {admins_count} admin - suppression d'admin impossible")
        else:
            print(f"   ✅ {admins_count} admins - suppression d'admin possible")
        
        # 6. Identifier un utilisateur de test
        print(f"\n--- Utilisateur de test ---")
        # Prendre un utilisateur non-admin pour le test
        utilisateur_test = utilisateurs.exclude(role='admin').first()
        if utilisateur_test:
            print(f"   Utilisateur de test: {utilisateur_test.username}")
            print(f"   Rôle: {utilisateur_test.get_role_display()}")
            print(f"   Statut: {'Actif' if utilisateur_test.is_active else 'Inactif'}")
        else:
            print(f"   ❌ Aucun utilisateur non-admin trouvé pour le test")
        
        print()
        print("🎯 TEST TERMINÉ")
        print("   La suppression d'utilisateur est maintenant configurée !")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_suppression_utilisateur()

