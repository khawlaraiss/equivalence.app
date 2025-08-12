# Guide de Dépannage - Bouton de Suppression des Dossiers

## 🔍 Diagnostic du Problème

Si le bouton de suppression ne fonctionne toujours pas, suivez ce guide étape par étape :

### 1. Vérification de la Console du Navigateur

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

**Si vous voyez des erreurs :**
- `Token CSRF non trouvé dans le DOM` → Problème avec le template
- `Erreur lors de la suppression` → Problème JavaScript
- Erreurs 403/404 → Problème de permissions ou d'URL

### 2. Vérification des Permissions

**Assurez-vous que :**
- Vous êtes connecté en tant qu'administrateur
- Votre compte a le rôle `admin`
- Vous n'êtes pas en mode déconnecté

**Pour vérifier :**
1. Allez dans votre profil utilisateur
2. Vérifiez que le rôle est "Administrateur"
3. Si ce n'est pas le cas, contactez un autre administrateur

### 3. Vérification de l'URL

**Testez l'URL directement :**
1. Remplacez `[ID]` par l'ID d'un dossier dans cette URL :
   ```
   http://localhost:8000/dossiers/dossier/[ID]/supprimer/
   ```
2. Si vous obtenez une erreur 404, le problème vient des URLs
3. Si vous obtenez une erreur 403, le problème vient des permissions

### 4. Vérification du Serveur

**Vérifiez que le serveur Django fonctionne :**
1. Ouvrez un terminal
2. Naviguez vers le dossier `equivalence`
3. Lancez : `python manage.py runserver`
4. Vérifiez qu'il n'y a pas d'erreurs

### 5. Test Manuel de la Suppression

**Créez un test manuel :**
1. Créez un nouveau dossier de test
2. Notez son ID
3. Essayez de le supprimer
4. Vérifiez qu'il a bien été supprimé

## 🛠️ Solutions aux Problèmes Courants

### Problème 1 : Token CSRF manquant

**Symptômes :** Message "Token CSRF non trouvé dans le DOM"

**Solution :**
1. Vérifiez que le template contient :
   ```html
   <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">
   ```
2. Rechargez la page (Ctrl+F5)
3. Videz le cache du navigateur

### Problème 2 : Erreur JavaScript

**Symptômes :** Erreurs dans la console du navigateur

**Solution :**
1. Vérifiez que JavaScript est activé
2. Désactivez les extensions qui bloquent JavaScript
3. Essayez un autre navigateur

### Problème 3 : Erreur 403 (Forbidden)

**Symptômes :** Message "Accès non autorisé"

**Solution :**
1. Vérifiez que vous êtes connecté
2. Vérifiez que votre compte a le rôle admin
3. Déconnectez-vous et reconnectez-vous

### Problème 4 : Erreur 404 (Not Found)

**Symptômes :** Page non trouvée

**Solution :**
1. Vérifiez que le serveur Django fonctionne
2. Vérifiez que l'URL est correcte
3. Redémarrez le serveur Django

### Problème 5 : Le dossier n'est pas supprimé

**Symptômes :** Le dossier reste visible après suppression

**Solution :**
1. Vérifiez les logs du serveur Django
2. Vérifiez qu'il n'y a pas d'erreurs de base de données
3. Essayez de supprimer manuellement en base de données

## 🔧 Tests de Validation

### Test 1 : Vérification du Template

```bash
cd equivalence
python test_bouton_final.py
```

### Test 2 : Test de Suppression en Base

```bash
cd equivalence
python test_suppression.py
```

### Test 3 : Test Simple

```bash
cd equivalence
python test_simple_suppression.py
```

## 📞 Support

Si aucun de ces tests ne résout le problème :

1. **Collectez les informations :**
   - Messages d'erreur de la console
   - Logs du serveur Django
   - Version de Django et Python
   - Navigateur utilisé

2. **Contactez le support technique** avec ces informations

## ✅ Checklist de Vérification

- [ ] Vous êtes connecté en tant qu'administrateur
- [ ] Le serveur Django fonctionne
- [ ] JavaScript est activé
- [ ] Aucune erreur dans la console du navigateur
- [ ] Le token CSRF est présent dans le DOM
- [ ] L'URL de suppression est correcte
- [ ] Les permissions sont correctes
- [ ] La base de données est accessible

## 🎯 Résolution Rapide

Si vous voulez une solution rapide :

1. **Redémarrez le serveur Django**
2. **Videz le cache du navigateur**
3. **Reconnectez-vous**
4. **Testez avec un dossier de test**

Le bouton de suppression devrait maintenant fonctionner correctement ! 