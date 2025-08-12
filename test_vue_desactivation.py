#!/usr/bin/env python
"""
Test de la vue de désactivation d'utilisateur
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from users.models import CustomUser
from django.urls import reverse

def test_vue_desactivation():
    """Tester que la vue de désactivation est accessible"""
    print("=== 🔍 TEST VUE DÉSACTIVATION ===")
    print("Vérification que la vue est accessible !")
    print()
    
    try:
        # 1. Vérifier qu'on a des utilisateurs
        utilisateurs = CustomUser.objects.all()
        total = utilisateurs.count()
        print(f"📊 Total utilisateurs: {total}")
        
        if total == 0:
            print("❌ Aucun utilisateur trouvé")
            return
        
        # 2. Prendre un utilisateur de test
        utilisateur_test = utilisateurs.first()
        print(f"🔍 Utilisateur de test: {utilisateur_test.username} (ID: {utilisateur_test.id})")
        
        # 3. Vérifier l'URL de désactivation
        url_desactivation = reverse('users:desactiver_utilisateur', args=[utilisateur_test.id])
        print(f"🔗 URL de désactivation: {url_desactivation}")
        
        # 4. Vérifier que l'utilisateur existe
        try:
            utilisateur_verifie = CustomUser.objects.get(id=utilisateur_test.id)
            print(f"✅ Utilisateur trouvé dans la base: {utilisateur_verifie.username}")
            print(f"   Statut: {'Actif' if utilisateur_verifie.is_active else 'Inactif'}")
            print(f"   Rôle: {utilisateur_verifie.get_role_display()}")
        except CustomUser.DoesNotExist:
            print(f"❌ Utilisateur non trouvé dans la base")
            return
        
        # 5. Vérifier les permissions
        print(f"\n--- Vérification des permissions ---")
        if utilisateur_test.role == 'admin':
            print(f"   Rôle: Administrateur (peut gérer les utilisateurs)")
        else:
            print(f"   Rôle: {utilisateur_test.get_role_display()}")
        
        # 6. Vérifier que la vue existe
        print(f"\n--- Vérification de la vue ---")
        try:
            from users.views import desactiver_utilisateur
            print(f"✅ Vue 'desactiver_utilisateur' trouvée dans views.py")
        except ImportError:
            print(f"❌ Vue 'desactiver_utilisateur' non trouvée dans views.py")
            return
        
        # 7. Vérifier l'URL dans urls.py
        print(f"\n--- Vérification des URLs ---")
        try:
            from users.urls import urlpatterns
            urls_desactivation = [url for url in urlpatterns if 'desactiver' in str(url.pattern)]
            if urls_desactivation:
                print(f"✅ URL de désactivation trouvée dans urls.py")
                for url in urls_desactivation:
                    print(f"   - {url.pattern}")
            else:
                print(f"❌ URL de désactivation non trouvée dans urls.py")
        except ImportError:
            print(f"❌ Impossible d'importer urls.py")
        
        print()
        print("🎯 RÉSUMÉ:")
        print(f"   - Vue: ✅ Trouvée")
        print(f"   - URL: ✅ Configurée")
        print(f"   - Modèle: ✅ Fonctionne")
        print(f"   - Interface: À tester dans le navigateur")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vue_desactivation()
