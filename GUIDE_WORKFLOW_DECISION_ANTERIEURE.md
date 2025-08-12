# Guide d'Utilisation du Workflow des Décisions Antérieures

## Vue d'ensemble

Ce guide explique comment utiliser le nouveau workflow pour gérer les dossiers ayant une décision antérieure dans le système d'équivalence de diplômes.

## Principe du Workflow

### 1. **Premier cycle (décision antérieure)**
- Le professeur traite un dossier et fait une évaluation
- Il fait **retour à l'admin** avec la décision antérieure
- L'admin examine le dossier **sur papier** (pas dans l'application)
- L'admin marque le dossier comme **"non traité"**

### 2. **Deuxième cycle (réévaluation)**
- L'admin utilise le bouton **"Renvoyer au professeur"**
- Le professeur reprend le dossier
- **La décision antérieure reste visible** dans "Voir évaluation"
- Le professeur peut **modifier** l'évaluation existante
- Quand il fait retour, même processus

### 3. **Cycle final**
- L'admin est notifié que le dossier est **"traité"**
- L'admin peut voir les **nouvelles notes** et la **nouvelle évaluation**
- **Pas de mélange** avec l'ancienne décision

## Utilisation par Rôle

### 👨‍🏫 **Professeur**

#### **Quand vous recevez un dossier avec décision antérieure :**

1. **Accédez à la vue d'évaluation** du dossier
2. **Vous verrez un avertissement** indiquant qu'il y a une décision antérieure
3. **La décision antérieure est affichée** avec :
   - Date de la décision
   - Détails de la décision
   - Pièces demandées
4. **Vous pouvez modifier** l'évaluation existante dans la consistance académique
5. **Quand vous avez terminé**, changez le statut du dossier à **"Traité"**

#### **Ce qui se passe :**
- ✅ La décision antérieure reste visible pour référence
- ✅ Vous pouvez modifier tous les critères d'évaluation
- ✅ L'admin sera notifié de votre nouvelle évaluation
- ✅ L'historique est conservé

### 👨‍💼 **Administrateur**

#### **Quand vous recevez un dossier avec décision antérieure :**

1. **Examinez le dossier sur papier** (pas dans l'application)
2. **Vérifiez** que le candidat a fourni les documents demandés
3. **Utilisez le bouton "Renvoyer au professeur"** dans le détail du dossier
4. **Rédigez un message** expliquant pourquoi vous renvoyez le dossier
5. **Confirmez** le renvoi

#### **Ce qui se passe :**
- ✅ Le statut du dossier redevient **"En cours"**
- ✅ Le professeur est notifié
- ✅ Un historique de l'action est créé
- ✅ Le dossier est prêt pour réévaluation

#### **Quand le professeur fait retour :**

1. **Vous recevez une notification** indiquant que le dossier a été retraité
2. **Accédez à la vue d'évaluation** pour voir les nouvelles notes
3. **Comparez** avec l'ancienne évaluation si nécessaire
4. **Prenez votre décision finale** basée sur la nouvelle évaluation

## Interface Utilisateur

### **Indicateurs visuels**

#### **Dans "Voir évaluation" :**
- 🟡 **Carte d'avertissement** avec fond jaune
- ⚠️ **Icône d'attention** 
- 📅 **Date de la décision antérieure**
- 📋 **Détails de la décision**
- 📝 **Processus de réévaluation** expliqué

#### **Dans le détail du dossier :**
- 🔵 **Bouton "Renvoyer au professeur"** (visible uniquement pour les admins)
- 📊 **Informations sur la décision antérieure**
- 📈 **Statut du dossier** mis à jour

### **Notifications**

#### **Types de notifications :**
- `renvoi` : Dossier renvoyé au professeur par l'admin
- `retour` : Dossier retraité par le professeur après décision antérieure
- `traitement` : Dossier traité normalement (nouveau)

#### **Contenu des notifications :**
- **Titre** explicite
- **Message** détaillé avec contexte
- **Lien** vers le dossier concerné

## Gestion des Erreurs

### **Problèmes courants et solutions :**

#### **1. Bouton "Renvoyer au professeur" non visible**
- ✅ Vérifiez que vous êtes connecté en tant qu'admin
- ✅ Vérifiez que le dossier a bien une décision antérieure
- ✅ Vérifiez que le candidat et l'état du dossier existent

#### **2. Décision antérieure non affichée**
- ✅ Vérifiez que `a_decision_anterieure = True` dans l'état du dossier
- ✅ Vérifiez que les champs de décision antérieure sont remplis
- ✅ Vérifiez les permissions d'accès

#### **3. Erreur lors du renvoi**
- ✅ Vérifiez que le message admin n'est pas trop long
- ✅ Vérifiez que le dossier n'est pas verrouillé
- ✅ Vérifiez les permissions d'écriture

## Tests et Validation

### **Script de test automatique :**
```bash
python test_workflow_decision_anterieure.py
```

### **Tests manuels recommandés :**
1. **Créer** un dossier avec décision antérieure
2. **Vérifier** l'affichage dans "Voir évaluation"
3. **Tester** le bouton "Renvoyer au professeur"
4. **Vérifier** les notifications
5. **Tester** la modification de l'évaluation
6. **Vérifier** le retour à l'admin

## Maintenance

### **Nettoyage des données :**
- Les décisions antérieures sont **conservées** pour l'historique
- Les anciennes évaluations sont **modifiées** (pas supprimées)
- L'historique des actions est **toujours disponible**

### **Surveillance :**
- **Vérifiez** régulièrement les notifications
- **Contrôlez** l'historique des actions
- **Validez** la cohérence des données

## Support

### **En cas de problème :**
1. **Consultez** ce guide
2. **Vérifiez** les logs de l'application
3. **Testez** avec le script de test
4. **Contactez** l'équipe technique

---

**Version :** 1.0  
**Date :** Janvier 2025  
**Auteur :** Équipe Technique Équivalence
