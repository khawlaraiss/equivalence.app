# Test Manuel - Interface Web Critères Personnalisés

## 🎯 Objectif
Vérifier que l'interface web respecte maintenant l'ordre des critères personnalisés.

## ✅ Modifications Appliquées
- **Calcul d'ID unique** pour chaque nouveau critère
- **Tri automatique** des critères par ID avant affichage
- **Ordre préservé** lors de l'ajout de nouveaux critères

## 🌐 Test de l'Interface Web

### 1. Démarrer le Serveur
```bash
cd C:\Users\HP\Desktop\equi22\equivalence
python manage.py runserver
```
**URL**: http://127.0.0.1:8000/

### 2. Se Connecter en Tant qu'Admin
- Aller sur: http://127.0.0.1:8000/admin/
- Se connecter avec un compte admin
- Vérifier que vous avez les droits d'administration

### 3. Accéder à la Page de Contrôle
- Aller sur: http://127.0.0.1:8000/controle-fiche-evaluation/
- Cette page permet de gérer les critères personnalisés

### 4. Vérifier l'État Actuel
**Critères fixes (1-7):**
1. Sciences géodésiques
2. Topographie
3. Photogrammétrie
4. Cartographie
5. Droit foncier
6. SIG
7. Télédétection

**Critères personnalisés actuels (8+):**
8. inform
9. Gouvernance
10. Test Critère 16:41:26
11. Gouvernance
12. Test Final 16:44:39

### 5. Ajouter un Nouveau Critère
1. **Remplir le formulaire:**
   - Nom: "Test Interface Web"
   - Note maximale: 15
   
2. **Cliquer sur "Ajouter"**

3. **Vérifier le résultat:**
   - Le nouveau critère doit apparaître à la **dernière ligne**
   - Il doit avoir le numéro **13** (après les 7 critères fixes + 5 critères personnalisés)
   - L'ordre des critères existants doit être préservé

### 6. Vérifications Attendues
- [ ] Le nouveau critère apparaît à la dernière ligne
- [ ] La numérotation est séquentielle (13)
- [ ] L'ordre des critères existants est préservé
- [ ] Le critère "Gouvernance" reste à sa position (ID 2)

## 🔍 Points de Contrôle

### Dans la Vue `controle_fiche_evaluation`
- Les nouveaux critères reçoivent un ID unique
- Les critères sont triés par ID avant affichage
- L'ordre est maintenu lors de la sauvegarde

### Dans le Template
- Les critères personnalisés utilisent `{{ forloop.counter|add:7 }}`
- L'ordre d'affichage respecte l'ordre de la liste Python triée

## 📊 Résultat Attendu

**Avant l'ajout:**
```
8. inform
9. Gouvernance
10. Test Critère 16:41:26
11. Gouvernance
12. Test Final 16:44:39
```

**Après l'ajout de "Test Interface Web":**
```
8. inform
9. Gouvernance
10. Test Critère 16:41:26
11. Gouvernance
12. Test Final 16:44:39
13. Test Interface Web  ← NOUVEAU CRITÈRE À LA FIN
```

## ❌ Problème Résolu
**Avant**: Les nouveaux critères étaient ajoutés au milieu
**Maintenant**: Les nouveaux critères sont ajoutés à la fin

## 🧪 Test Automatique
Si vous voulez vérifier programmatiquement:
```bash
cd C:\Users\HP\Desktop\equi22\equivalence
python test_ordre_final.py
```

## 🚀 Déploiement
Les modifications sont en place et testées. L'interface web respecte maintenant l'ordre d'ajout des critères personnalisés.


