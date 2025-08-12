# Guide de Test - Ordre des Critères Personnalisés

## 🎯 Objectif
Vérifier que quand l'admin ajoute un nouveau critère personnalisé, il est bien ajouté à la **dernière ligne** du tableau, pas au milieu.

## ✅ Modifications Apportées

### 1. Vue `controle_fiche_evaluation`
- **Fichier**: `dossiers/views.py` (lignes ~3040-3070)
- **Modification**: Calcul d'ID unique pour chaque nouveau critère
- **Code ajouté**:
```python
# Calculer le prochain ID en s'assurant qu'il est unique
next_id = 1
if structure.criteres_personnalises_globaux:
    existing_ids = [c.get('id', 0) for c in structure.criteres_personnalises_globaux]
    next_id = max(existing_ids) + 1 if existing_ids else 1
```

### 2. Tri des Critères
- **Fichier**: `dossiers/views.py` (lignes ~3180-3190)
- **Modification**: Tri automatique des critères par ID avant affichage
- **Code ajouté**:
```python
# Trier les critères personnalisés par ordre d'ajout (par ID) pour garantir l'ordre d'affichage
if structure.criteres_personnalises_globaux:
    structure.criteres_personnalises_globaux.sort(key=lambda x: x.get('id', 0))
```

### 3. Vue `consistance_academique`
- **Fichier**: `dossiers/views.py` (lignes ~750-760)
- **Modification**: Tri des critères personnalisés dans la vue principale
- **Code ajouté**: Même logique de tri

## 🧪 Tests Effectués

### Test 1: Vérification de l'Ordre
```bash
cd equivalence
python test_criteres_ordre.py
```
**Résultat**: ✅ Les critères sont bien triés par ID

### Test 2: Simulation Interface Web
```bash
cd equivalence
python test_interface_web.py
```
**Résultat**: ✅ Les nouveaux critères sont ajoutés à la fin

## 🌐 Test Manuel Interface Web

### Étapes de Test
1. **Démarrer le serveur**:
   ```bash
   cd equivalence
   python manage.py runserver
   ```

2. **Se connecter en tant qu'admin**:
   - Aller sur `http://localhost:8000/admin/`
   - Se connecter avec un compte admin

3. **Accéder à la page de consistance académique**:
   - Aller sur `http://localhost:8000/consistance-academique/`

4. **Ajouter un nouveau critère**:
   - Cliquer sur "Ajouter un critère personnalisé"
   - Remplir le formulaire avec un nom unique
   - Cliquer sur "Ajouter"

5. **Vérifier l'ordre**:
   - Le nouveau critère doit apparaître à la **dernière ligne** du tableau
   - La numérotation doit être séquentielle (8, 9, 10, etc.)

### Vérifications
- [ ] Le nouveau critère apparaît à la dernière ligne
- [ ] La numérotation est séquentielle
- [ ] L'ordre des critères existants est préservé
- [ ] Le critère "Gouvernance" reste à sa position (ID 2)

## 🔍 Points de Contrôle

### Dans le Template `consistance_academique.html`
- Les critères personnalisés utilisent `{{ forloop.counter|add:7 }}`
- L'ordre d'affichage respecte l'ordre de la liste Python

### Dans la Vue `controle_fiche_evaluation`
- Les critères fixes utilisent des numéros calculés dynamiquement
- Les critères personnalisés sont triés par ID avant affichage

## 📊 État Actuel des Critères
```
1. inform (ID: 1)
2. Gouvernance (ID: 2) 
3. Test Critère 16:41:26 (ID: 3)
4. Interface Web Test 16:42:34 (ID: 4)
```

## ✅ Résultat Attendu
Quand l'admin ajoute un nouveau critère "Nouveau Critère", il doit apparaître comme :
```
5. Nouveau Critère (ID: 5)
```

**ET NON PAS** au milieu comme avant :
```
2. Gouvernance (ID: 2)
3. Nouveau Critère (ID: 3) ← ❌ INCORRECT
4. Test Critère... (ID: 4)
```

## 🚀 Déploiement
Les modifications sont déjà en place et testées. L'interface web respecte maintenant l'ordre d'ajout des critères personnalisés.


