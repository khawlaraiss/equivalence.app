# 🔍 GUIDE DE TEST : DÉSACTIVATION D'UTILISATEUR

## 📋 **SITUATION ACTUELLE**
- ✅ **Vue** : `desactiver_utilisateur` existe et est correctement configurée
- ✅ **URL** : `/users/utilisateur/{id}/desactiver/` fonctionne
- ✅ **Modèle** : `CustomUser.is_active` peut être modifié en base
- ❌ **Interface** : Le bouton de désactivation ne fonctionne pas

## 🔍 **DIAGNOSTIC ÉTAPE PAR ÉTAPE**

### **Étape 1: Vérifier que le serveur Django fonctionne**
```bash
# Dans un terminal
cd C:\Users\HP\Desktop\equi22
python manage.py runserver
```

**Résultat attendu** : Le serveur démarre sur `http://localhost:8000/`

### **Étape 2: Accéder à l'interface de gestion**
1. Ouvrir le navigateur
2. Aller sur `http://localhost:8000/users/login/`
3. Se connecter avec un compte **administrateur**
4. Aller sur "Gestion des Utilisateurs"

**Vérifications** :
- ✅ La page se charge sans erreur
- ✅ La liste des utilisateurs s'affiche
- ✅ Les boutons "Désactiver" sont visibles (icône ban jaune)

### **Étape 3: Tester le bouton de désactivation**
1. **Cliquer** sur un bouton "Désactiver" (icône ban)
2. **Observer** ce qui se passe :
   - ❌ Rien ne se passe ?
   - ❌ Erreur JavaScript dans la console ?
   - ❌ Page qui se recharge sans changement ?
   - ✅ Boîte de confirmation qui s'affiche ?

### **Étape 4: Vérifier la console JavaScript**
1. **Ouvrir** les outils de développement (F12)
2. **Aller** dans l'onglet "Console"
3. **Cliquer** sur le bouton de désactivation
4. **Observer** les erreurs éventuelles

**Erreurs possibles** :
- `desactiverUtilisateur is not defined`
- `csrfmiddlewaretoken not found`
- `Cannot read property of undefined`

### **Étape 5: Vérifier le code source de la page**
1. **Clic droit** sur la page → "Afficher le code source"
2. **Rechercher** (Ctrl+F) : `desactiverUtilisateur`
3. **Vérifier** que la fonction JavaScript est bien présente

## 🐛 **PROBLÈMES IDENTIFIÉS ET SOLUTIONS**

### **Problème 1: Fonction JavaScript manquante**
**Symptôme** : `desactiverUtilisateur is not defined`
**Solution** : Vérifier que le template charge bien le JavaScript

### **Problème 2: Token CSRF manquant**
**Symptôme** : `csrfmiddlewaretoken not found`
**Solution** : Vérifier que `{% csrf_token %}` est dans le template

### **Problème 3: URL incorrecte**
**Symptôme** : Erreur 404 lors de la soumission
**Solution** : Vérifier que l'URL est correctement générée

### **Problème 4: Permissions insuffisantes**
**Symptôme** : Message "Accès non autorisé"
**Solution** : S'assurer d'être connecté avec un compte admin

## 🧪 **TESTS DE VALIDATION**

### **Test 1: Vérification du JavaScript**
```javascript
// Dans la console du navigateur
console.log(typeof desactiverUtilisateur);
// Doit retourner "function"
```

### **Test 2: Vérification du token CSRF**
```javascript
// Dans la console du navigateur
const token = document.querySelector('[name=csrfmiddlewaretoken]');
console.log(token ? token.value : 'Token non trouvé');
// Doit afficher une valeur
```

### **Test 3: Test de la fonction**
```javascript
// Dans la console du navigateur
desactiverUtilisateur(1);
// Doit afficher une boîte de confirmation
```

## 🔧 **SOLUTIONS DE DÉPANNAGE**

### **Solution 1: Recharger la page**
- **Problème** : JavaScript non chargé
- **Solution** : F5 ou Ctrl+R pour recharger

### **Solution 2: Vider le cache**
- **Problème** : Ancienne version du JavaScript
- **Solution** : Ctrl+Shift+R (rechargement forcé)

### **Solution 3: Vérifier les erreurs de serveur**
- **Problème** : Erreur côté serveur
- **Solution** : Vérifier le terminal Django pour les erreurs

### **Solution 4: Vérifier la base de données**
- **Problème** : Utilisateur non trouvé
- **Solution** : Vérifier que l'utilisateur existe toujours

## 📱 **INTERFACE ATTENDUE**

### **Bouton Désactiver (utilisateur actif)**
- **Couleur** : Jaune (`btn-outline-warning`)
- **Icône** : Ban (`fas fa-ban`)
- **Action** : Désactiver l'utilisateur

### **Bouton Activer (utilisateur inactif)**
- **Couleur** : Vert (`btn-outline-success`)
- **Icône** : Check (`fas fa-check`)
- **Action** : Réactiver l'utilisateur

### **Comportement attendu**
1. **Clic** → Boîte de confirmation
2. **Confirmation** → Envoi de la requête POST
3. **Succès** → Message de confirmation + changement de statut
4. **Erreur** → Message d'erreur

## 🎯 **RÉSULTAT FINAL ATTENDU**

Après avoir cliqué sur "Désactiver" et confirmé :
- ✅ L'utilisateur passe de "Actif" à "Inactif"
- ✅ Le bouton change de "Désactiver" à "Activer"
- ✅ Un message de succès s'affiche
- ✅ L'utilisateur ne peut plus se connecter

---

**🔍 Suivez ce guide étape par étape pour identifier le problème exact !**
