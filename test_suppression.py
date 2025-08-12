#!/usr/bin/env python
"""
Script de test pour vérifier la fonction de suppression des dossiers
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Dossier
from users.models import CustomUser

def test_suppression_dossier():
    """Test de la suppression d'un dossier"""
    print("=== Test de suppression de dossier ===")
    
    # Vérifier qu'il y a des dossiers
    dossiers = Dossier.objects.all()
    print(f"Nombre de dossiers existants : {dossiers.count()}")
    
    if dossiers.count() == 0:
        print("❌ Aucun dossier trouvé pour le test")
        return False
    
    # Prendre le premier dossier
    dossier = dossiers.first()
    dossier_id = dossier.id
    dossier_titre = dossier.titre
    
    print(f"📁 Dossier à supprimer : {dossier_titre} (ID: {dossier_id})")
    
    # Vérifier les pièces jointes associées
    pieces_jointes = dossier.pieces_jointes.all()
    print(f"📎 Pièces jointes associées : {pieces_jointes.count()}")
    
    # Vérifier les historiques associés
    historiques = dossier.historiques.all()
    print(f"📝 Historiques associés : {historiques.count()}")
    
    # Supprimer le dossier
    try:
        # Supprimer les pièces jointes d'abord
        pieces_jointes.delete()
        print("✅ Pièces jointes supprimées")
        
        # Supprimer le dossier
        dossier.delete()
        print("✅ Dossier supprimé avec succès")
        
        # Vérifier que le dossier n'existe plus
        try:
            Dossier.objects.get(id=dossier_id)
            print("❌ Erreur : Le dossier existe encore après suppression")
            return False
        except Dossier.DoesNotExist:
            print("✅ Confirmation : Le dossier a bien été supprimé")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la suppression : {str(e)}")
        return False

def test_creation_dossier_test():
    """Créer un dossier de test pour les tests"""
    print("\n=== Création d'un dossier de test ===")
    
    try:
        # Créer un utilisateur admin si nécessaire
        admin, created = CustomUser.objects.get_or_create(
            username='admin_test',
            defaults={
                'email': 'admin@test.com',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # Créer un dossier de test
        dossier = Dossier.objects.create(
            titre="Dossier de test pour suppression",
            description="Ce dossier est créé pour tester la fonction de suppression",
            statut='non_traite'
        )
        
        print(f"✅ Dossier de test créé : {dossier.titre} (ID: {dossier.id})")
        return dossier
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du dossier de test : {str(e)}")
        return None

if __name__ == "__main__":
    print("🔧 Test de la fonctionnalité de suppression des dossiers")
    print("=" * 50)
    
    # Créer un dossier de test
    dossier_test = test_creation_dossier_test()
    
    if dossier_test:
        # Tester la suppression
        success = test_suppression_dossier()
        
        if success:
            print("\n🎉 Tous les tests de suppression sont passés avec succès !")
        else:
            print("\n❌ Les tests de suppression ont échoué")
    else:
        print("\n❌ Impossible de créer un dossier de test")
    
    print("\n" + "=" * 50) 