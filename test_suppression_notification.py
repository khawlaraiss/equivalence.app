#!/usr/bin/env python3
"""
Test de la fonctionnalité de suppression des notifications
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'equivalence.settings')
django.setup()

from dossiers.models import Notification, Dossier
from users.models import CustomUser
from django.urls import reverse
from django.test import Client
from django.contrib.auth import authenticate

def test_suppression_notification():
    print("=== 🧪 TEST SUPPRESSION NOTIFICATION ===")
    
    # Vérifier les utilisateurs
    try:
        admin = CustomUser.objects.get(username='admin')
        prof = CustomUser.objects.get(username='prof')
        print(f"✅ Utilisateurs trouvés: Admin={admin.username}, Prof={prof.username}")
    except CustomUser.DoesNotExist as e:
        print(f"❌ Erreur utilisateur: {e}")
        return
    
    # Vérifier les notifications existantes
    notifications_admin = admin.notifications.all()
    notifications_prof = prof.notifications.all()
    
    print(f"\n📊 Notifications existantes:")
    print(f"   Admin: {notifications_admin.count()}")
    print(f"   Prof: {notifications_prof.count()}")
    
    if notifications_admin.count() == 0 and notifications_prof.count() == 0:
        print("⚠️  Aucune notification à tester")
        return
    
    # Tester l'accès à la page des notifications
    client = Client()
    
    print(f"\n🔗 Test accès page notifications:")
    
    # Test admin
    client.force_login(admin)
    response = client.get(reverse('dossiers:notifications'))
    print(f"   Admin: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    # Test prof
    client.force_login(prof)
    response = client.get(reverse('dossiers:notifications'))
    print(f"   Prof: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
    
    # Tester l'URL de suppression
    print(f"\n🔗 Test URL suppression notification:")
    
    # Prendre la première notification disponible
    notification_test = None
    if notifications_admin.count() > 0:
        notification_test = notifications_admin.first()
        user_test = admin
    elif notifications_prof.count() > 0:
        notification_test = notifications_prof.first()
        user_test = prof
    
    if notification_test:
        print(f"   Notification de test: ID={notification_test.id}, Titre='{notification_test.titre}'")
        
        # Test accès URL suppression
        client.force_login(user_test)
        url_suppression = reverse('dossiers:supprimer_notification', args=[notification_test.id])
        print(f"   URL suppression: {url_suppression}")
        
        # Test GET (devrait rediriger)
        response = client.get(url_suppression)
        print(f"   GET suppression: {response.status_code} {'✅' if response.status_code == 302 else '❌'}")
        
        # Test POST (devrait supprimer)
        response = client.post(url_suppression)
        print(f"   POST suppression: {response.status_code} {'✅' if response.status_code == 302 else '❌'}")
        
        # Vérifier que la notification a été supprimée
        try:
            notification_test.refresh_from_db()
            print(f"   ❌ Notification toujours présente après suppression")
        except Notification.DoesNotExist:
            print(f"   ✅ Notification supprimée avec succès")
    else:
        print("   ⚠️  Aucune notification disponible pour le test")
    
    print(f"\n🎯 TEST TERMINÉ")

if __name__ == '__main__':
    test_suppression_notification()
