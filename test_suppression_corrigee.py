#!/usr/bin/env python
"""
Test de la suppression corrigée
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import DossierTraite
from django.test import Client
from django.urls import reverse

def test_suppression_corrigee():
    """Tester la suppression corrigée"""
    print("=== 🧪 TEST SUPPRESSION CORRIGÉE ===")
    print("Vérification que la suppression fonctionne maintenant !")
    print()
    
    try:
        # 1. Vérifier qu'on a bien des dossiers traités
        dossiers_traites = DossierTraite.objects.all()
        total = dossiers_traites.count()
        print(f"📊 Total dossiers traités: {total}")
        
        if total == 0:
            print("❌ Aucun dossier traité à tester")
            return
        
        # 2. Prendre le premier dossier pour le test
        dossier_test = dossiers_traites.first()
        print(f"🔍 Dossier de test: ID {dossier_test.id}, Numéro: {dossier_test.numero}")
        
        # 3. Tester l'accès à la page de suppression
        print("\n--- Test 1: Accès à la page de suppression ---")
        client = Client()
        
        # Créer un utilisateur admin temporaire (simulation)
        from users.models import CustomUser
        admin_user = CustomUser.objects.create_user(
            username='admin_test_suppression',
            email='admin_test@example.com',
            password='adminpass123',
            role='admin'
        )
        
        # Se connecter
        login_success = client.login(username='admin_test_suppression', password='adminpass123')
        print(f"✅ Connexion admin: {login_success}")
        
        # Accéder à la page de suppression
        url_suppression = reverse('dossiers:supprimer_dossier_traite', args=[dossier_test.id])
        print(f"🔗 URL de suppression: {url_suppression}")
        
        response = client.get(url_suppression)
        print(f"✅ Code réponse: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Page de suppression accessible !")
            content = response.content.decode()
            
            if "Confirmer la suppression" in content:
                print("✅ Formulaire de confirmation affiché")
            else:
                print("❌ Formulaire de confirmation non trouvé")
                
            if str(dossier_test.numero) in content:
                print(f"✅ Numéro du dossier affiché: {dossier_test.numero}")
            else:
                print("❌ Numéro du dossier non affiché")
        else:
            print("❌ Erreur d'accès à la page de suppression")
        
        # 4. Nettoyer
        admin_user.delete()
        print("\n🧹 Utilisateur de test supprimé")
        
        print("\n🎯 CONCLUSION:")
        print("   Si la page de suppression s'affiche correctement,")
        print("   alors la correction a fonctionné !")
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_suppression_corrigee()
