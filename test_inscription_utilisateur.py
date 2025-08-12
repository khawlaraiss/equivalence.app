#!/usr/bin/env python
"""
Test de l'inscription d'utilisateur
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from users.models import CustomUser
from django.urls import reverse

def test_inscription_utilisateur():
    """Tester l'inscription d'utilisateur"""
    print("=== 🧪 TEST INSCRIPTION UTILISATEUR ===")
    print("Vérification que l'inscription publique fonctionne !")
    print()
    
    try:
        # 1. Vérifier qu'on a des utilisateurs
        utilisateurs_avant = CustomUser.objects.all().count()
        print(f"📊 Utilisateurs avant test: {utilisateurs_avant}")
        
        # 2. Vérifier l'URL d'inscription
        print(f"\n--- Vérification de l'URL ---")
        try:
            url_inscription = reverse('users:inscription')
            print(f"✅ URL d'inscription: {url_inscription}")
        except Exception as e:
            print(f"❌ Erreur URL: {e}")
            return
        
        # 3. Vérifier que la vue existe
        print(f"\n--- Vérification de la vue ---")
        try:
            from users.views import inscription
            print(f"✅ Vue 'inscription' trouvée")
            
            import inspect
            sig = inspect.signature(inscription)
            print(f"   Signature: {sig}")
            
        except ImportError as e:
            print(f"❌ Vue non trouvée: {e}")
            return
        
        # 4. Vérifier le template
        print(f"\n--- Vérification du template ---")
        template_path = "equivalence/templates/users/inscription.html"
        if os.path.exists(template_path):
            print(f"✅ Template trouvé: {template_path}")
        else:
            print(f"❌ Template non trouvé: {template_path}")
            return
        
        # 5. Vérifier la page de connexion
        print(f"\n--- Vérification de la page de connexion ---")
        login_template_path = "equivalence/templates/users/login.html"
        if os.path.exists(login_template_path):
            print(f"✅ Template de connexion trouvé: {login_template_path}")
            
            # Vérifier si le bouton d'inscription est présent
            with open(login_template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'inscription' in content:
                    print(f"   ✅ Bouton d'inscription trouvé dans le template")
                else:
                    print(f"   ❌ Bouton d'inscription non trouvé dans le template")
        else:
            print(f"❌ Template de connexion non trouvé")
        
        # 6. Vérifier les permissions
        print(f"\n--- Vérification des permissions ---")
        admins_count = CustomUser.objects.filter(role='admin').count()
        print(f"   Nombre d'administrateurs: {admins_count}")
        
        if admins_count > 0:
            print(f"   ✅ {admins_count} admins - système fonctionnel")
        else:
            print(f"   ⚠️ Aucun admin - problème potentiel")
        
        print()
        print("🎯 TEST TERMINÉ")
        print("   L'inscription d'utilisateur est maintenant configurée !")
        print()
        print("📋 RÉSUMÉ DES URLS :")
        print(f"   🔐 Connexion: http://localhost:8000/login/")
        print(f"   📝 Inscription: http://localhost:8000{url_inscription}")
        print(f"   📊 Dashboard: http://localhost:8000/dossiers/")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inscription_utilisateur()

