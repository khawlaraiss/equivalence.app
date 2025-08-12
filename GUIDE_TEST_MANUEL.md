# Guide de Test Manuel - Bouton de Suppression

## 🎯 Test du Bouton de Suppression

Maintenant que les migrations sont résolues, testons le bouton de suppression étape par étape.

### 📋 Prérequis

- ✅ Serveur Django démarré sur `http://localhost:8000`
- ✅ Migrations appliquées
- ✅ Compte administrateur disponible

### 🔧 Étapes de Test

#### 1. Démarrage du Serveur

```bash
cd C:\Users\HP\Desktop\equi22\equivalence
python manage.py runserver
```

#### 2. Accès à l'Interface

1. **Ouvrez votre navigateur**
2. **Allez sur** : `http://localhost:8000/dossiers/gestion/`
3. **Connectez-vous** en tant qu'administrateur

#### 3. Test du Bouton de Suppression

1. **Trouvez un dossier** dans la liste
2. **Cliquez sur le bouton rouge** (icône poubelle) à côté du dossier
3. **Confirmez la suppression** dans la boîte de dialogue
4. **Vérifiez que le dossier disparaît** de la liste

#### 4. Vérification des Logs

1. **Ouvrez les outils de développement** (F12)
2. **Allez dans l'onglet Console**
3. **Cliquez sur le bouton de suppression**
4. **Vérifiez les messages** qui apparaissent

**Messages attendus :**
```
Fonction supprimerDossier appelée avec ID: [numéro]
URL de suppression: /dossiers/dossier/[numéro]/supprimer/
Token CSRF trouvé: OUI
Formulaire créé et prêt à être soumis
```

### 🔍 Diagnostic des Problèmes

#### Si le bouton ne répond pas :

1. **Vérifiez la console** (F12) pour les erreurs JavaScript
2. **Vérifiez que vous êtes connecté** en tant qu'administrateur
3. **Videz le cache** du navigateur (Ctrl+F5)
4. **Essayez un autre navigateur**

#### Si vous voyez des erreurs :

- **Erreur 403** : Problème de permissions
- **Erreur 404** : Problème d'URL
- **Erreur JavaScript** : Problème de script

#### Si le dossier n'est pas supprimé :

1. **Vérifiez les logs du serveur** dans le terminal
2. **Vérifiez la console** du navigateur
3. **Rechargez la page** pour voir si le dossier a disparu

### 📊 Test de Validation

#### Test 1 : Création et Suppression

1. **Créez un nouveau dossier** via l'interface
2. **Notez son ID**
3. **Supprimez-le** avec le bouton
4. **Vérifiez qu'il a disparu**

#### Test 2 : Suppression Multiple

1. **Créez plusieurs dossiers de test**
2. **Supprimez-les un par un**
3. **Vérifiez qu'ils disparaissent tous**

#### Test 3 : Test des Permissions

1. **Connectez-vous** avec un compte non-admin
2. **Vérifiez que le bouton de suppression n'apparaît pas**
3. **Essayez d'accéder directement à l'URL de suppression**

### 🛠️ Solutions aux Problèmes Courants

#### Problème : Bouton ne répond pas

**Solution :**
1. Vérifiez que JavaScript est activé
2. Videz le cache du navigateur
3. Essayez un autre navigateur

#### Problème : Erreur "Token CSRF non trouvé"

**Solution :**
1. Rechargez la page (Ctrl+F5)
2. Vérifiez que vous êtes connecté
3. Videz le cache du navigateur

#### Problème : Erreur 403 (Forbidden)

**Solution :**
1. Vérifiez que vous êtes connecté en tant qu'administrateur
2. Déconnectez-vous et reconnectez-vous
3. Vérifiez votre rôle dans le profil utilisateur

#### Problème : Erreur 404 (Not Found)

**Solution :**
1. Vérifiez que le serveur Django fonctionne
2. Vérifiez l'URL dans la console
3. Redémarrez le serveur Django

### ✅ Checklist de Validation

- [ ] Serveur Django démarré
- [ ] Migrations appliquées
- [ ] Connecté en tant qu'administrateur
- [ ] Bouton de suppression visible
- [ ] Clic sur le bouton fonctionne
- [ ] Boîte de dialogue de confirmation apparaît
- [ ] Confirmation supprime le dossier
- [ ] Dossier disparaît de la liste
- [ ] Messages de débogage dans la console
- [ ] Aucune erreur dans la console

### 🎉 Succès !

Si tous les tests passent, le bouton de suppression fonctionne correctement !

### 📞 Support

Si vous rencontrez des problèmes :

1. **Collectez les informations :**
   - Messages d'erreur de la console
   - Logs du serveur Django
   - Étapes reproduites

2. **Consultez le guide de dépannage** : `GUIDE_DEPANNAGE_SUPPRESSION.md`

3. **Contactez le support technique** avec ces informations

---

**Le bouton de suppression devrait maintenant fonctionner parfaitement !** 🎯 