# 🔄 Equicord Updater

Scripts pour vérifier et mettre à jour Equicord sans perdre vos plugins personnalisés.

## 📦 Fichiers inclus

- `install.py` - Script Python principal
- `equicord_updater.sh` - Script Shell pour Linux/macOS  
- `build_exe.py` - Générateur d'exécutable Windows
- `requirements.txt` - Dépendances Python

## 🚀 Utilisation

### Linux/macOS (Script Shell)

```bash
# Vérification simple
./equicord_updater.sh

# Simulation de mise à jour
./equicord_updater.sh --dry-run

# Mise à jour interactive
./equicord_updater.sh --update

# Spécifier un chemin personnalisé
./equicord_updater.sh --path /mon/chemin/equicord
```

### Linux/macOS/Windows (Python directement)

```bash
# Vérification simple
python3 install.py

# Simulation de mise à jour
python3 install.py --dry-run

# Mise à jour interactive
python3 install.py --update
```

### Windows (Exécutable)

1. **Générer l'exécutable** (sur Linux avec Wine ou sur Windows) :
```bash
python build_exe.py
```

2. **Utiliser l'exécutable** :
- Double-cliquez sur `equicord_updater.exe`
- Ou utilisez `equicord_updater.bat` pour un menu interactif

## 🛡️ Fonctionnalités de protection

### Plugins protégés automatiquement :
- `src/equicordplugins/` - Vos plugins Equicord modifiés
- `src/userplugins/` - Vos plugins personnels

### Processus de mise à jour sécurisée :
1. **Sauvegarde** des plugins dans un stash Git
2. **Mise à jour** depuis le dépôt upstream
3. **Restauration** automatique de vos plugins
4. **Gestion des conflits** si nécessaire

## 📋 Ce que le script affiche

```
🔍 Vérification des mises à jour d'Equicord...
============================================================
📦 Version actuelle: 1.12.2
📝 Commit actuel: db7447a9
🌐 Dernière version upstream: 1.12.3
📝 Dernier commit upstream: f8e9c2d1
🆕 ✅ Nouvelle version disponible!
📈 Vous êtes 5 commit(s) en retard

============================================================
🔒 Plugins protégés modifiés (2):
   - src/equicordplugins/followVoiceUser/index.tsx
   - src/userplugins/chatGpt/index.ts
⚠️  Autres fichiers modifiés (1):
   - package.json

📋 Notes de la dernière release:
----------------------------------------
- Corrections de bugs
- Nouveaux plugins
- Améliorations de performance
```

## ⚙️ Installation des dépendances

### Ubuntu/Debian :
```bash
sudo apt update
sudo apt install python3 git python3-requests python3-packaging
```

### Ou avec pip :
```bash
pip install requests packaging
```

## 🔧 Options disponibles

| Option | Description |
|--------|-------------|
| `--check` | Vérification seule (défaut) |
| `--update` | Mise à jour interactive avec confirmation |
| `--dry-run` | Simulation sans modifications |
| `--path PATH` | Chemin personnalisé du projet |
| `--help` | Afficher l'aide |

## 🚨 Gestion des conflits

Si des conflits surviennent lors de la restauration :

1. **Résolution manuelle** :
```bash
git status
git add .
git commit -m "Résolution conflits plugins"
```

2. **Restauration des plugins depuis stash** :
```bash
git stash list
git stash apply stash@{0}
```

3. **Annulation complète** :
```bash
git reset --hard HEAD~1
git stash pop
```

## 📝 Logs et dépannage

### Vérifier les remotes Git :
```bash
git remote -v
```
Doit afficher :
```
origin    https://github.com/VOTRE_USERNAME/Equicord.git
upstream  https://github.com/Equicord/Equicord.git
```

### Vérifier l'état Git :
```bash
git status
```

### Forcer la mise à jour des remotes :
```bash
git fetch --all
```

## ⚠️ Important

- **Toujours sauvegarder** avant une mise à jour importante
- **Tester avec --dry-run** avant une vraie mise à jour
- **Vérifier que vos plugins fonctionnent** après mise à jour
- **Ne pas oublier** de faire `pnpm install && pnpm build` après mise à jour

## 🤝 Contribution

Ce script est conçu pour votre fork Equicord personnel. Les plugins dans `src/equicordplugins/` et `src/userplugins/` sont automatiquement protégés.

Pour suggérer des améliorations, ouvrez une issue ou créez une pull request ! 