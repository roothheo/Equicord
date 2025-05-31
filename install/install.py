#!/usr/bin/env python3
"""
Script pour vérifier les mises à jour d'Equicord sans toucher aux plugins modifiés
Utilise l'API GitHub pour comparer les versions et commits
"""

import json
import requests
import subprocess
import sys
import os
from datetime import datetime
from packaging import version
import argparse
import shutil

class EquicordUpdater:
    def __init__(self, project_path="/home/bash/Desktop/dev/bashcord"):
        self.project_path = project_path
        self.upstream_repo = "Equicord/Equicord"
        self.protected_dirs = [
            "src/equicordplugins",
            "src/userplugins"
        ]
        
    def get_current_version(self):
        """Récupère la version actuelle depuis package.json"""
        try:
            with open(os.path.join(self.project_path, "package.json"), 'r') as f:
                package_data = json.load(f)
                return package_data.get("version", "unknown")
        except Exception as e:
            print(f"❌ Erreur lors de la lecture du package.json: {e}")
            return None
    
    def get_current_commit(self):
        """Récupère le commit actuel"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur Git: {e}")
            return None
    
    def get_upstream_info(self):
        """Récupère les infos de la dernière release du dépôt upstream"""
        try:
            # API GitHub pour la dernière release
            url = f"https://api.github.com/repos/{self.upstream_repo}/releases/latest"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            
            # API pour obtenir le commit principal
            commits_url = f"https://api.github.com/repos/{self.upstream_repo}/commits/main"
            commits_response = requests.get(commits_url, timeout=10)
            commits_response.raise_for_status()
            
            latest_commit = commits_response.json()
            
            return {
                "version": release_data.get("tag_name", "").lstrip('v'),
                "commit": latest_commit["sha"],
                "commit_date": latest_commit["commit"]["committer"]["date"],
                "commit_message": latest_commit["commit"]["message"],
                "release_url": release_data.get("html_url", ""),
                "release_notes": release_data.get("body", "")
            }
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des infos upstream: {e}")
            return None
    
    def check_git_status(self):
        """Vérifie l'état des fichiers modifiés localement"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            modified_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            protected_files = []
            other_files = []
            
            for file_line in modified_files:
                if len(file_line) < 3:
                    continue
                    
                file_path = file_line[3:]  # Enlever les 3 premiers caractères (status + espace)
                
                # Vérifier si le fichier est dans un dossier protégé
                is_protected = any(file_path.startswith(protected_dir) for protected_dir in self.protected_dirs)
                
                if is_protected:
                    protected_files.append(file_path)
                else:
                    other_files.append(file_path)
            
            return {
                "protected_files": protected_files,
                "other_files": other_files,
                "total_modified": len(modified_files)
            }
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de la vérification du statut Git: {e}")
            return None
    
    def get_commits_behind(self):
        """Vérifie combien de commits on est en retard sur upstream"""
        try:
            # Récupérer les infos d'upstream
            subprocess.run(
                ["git", "fetch", "upstream"],
                cwd=self.project_path,
                capture_output=True,
                check=True
            )
            
            # Compter les commits en retard
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD..upstream/main"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return int(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de la vérification des commits: {e}")
            return None
    
    def show_update_summary(self):
        """Affiche un résumé des mises à jour disponibles"""
        print("🔍 Vérification des mises à jour d'Equicord...")
        print("=" * 60)
        
        # Version actuelle
        current_version = self.get_current_version()
        current_commit = self.get_current_commit()
        
        print(f"📦 Version actuelle: {current_version}")
        print(f"📝 Commit actuel: {current_commit[:8] if current_commit else 'unknown'}")
        
        # Infos upstream
        upstream_info = self.get_upstream_info()
        if not upstream_info:
            return False
        
        print(f"🌐 Dernière version upstream: {upstream_info['version']}")
        print(f"📝 Dernier commit upstream: {upstream_info['commit'][:8]}")
        
        # Comparaison des versions
        try:
            if version.parse(current_version) < version.parse(upstream_info['version']):
                print("🆕 ✅ Nouvelle version disponible!")
            elif version.parse(current_version) == version.parse(upstream_info['version']):
                print("✅ Vous êtes à jour (version)")
            else:
                print("🔄 Votre version est plus récente que la release officielle")
        except Exception:
            print("⚠️  Impossible de comparer les versions")
        
        # Vérifier les commits
        commits_behind = self.get_commits_behind()
        if commits_behind is not None:
            if commits_behind > 0:
                print(f"📈 Vous êtes {commits_behind} commit(s) en retard")
            else:
                print("✅ Vous êtes à jour (commits)")
        
        print("\n" + "=" * 60)
        
        # Vérifier les fichiers modifiés
        git_status = self.check_git_status()
        if git_status:
            if git_status["protected_files"]:
                print(f"🔒 Plugins protégés modifiés ({len(git_status['protected_files'])}):")
                for file in git_status["protected_files"][:5]:  # Afficher max 5
                    print(f"   - {file}")
                if len(git_status["protected_files"]) > 5:
                    print(f"   ... et {len(git_status['protected_files']) - 5} autres")
            
            if git_status["other_files"]:
                print(f"⚠️  Autres fichiers modifiés ({len(git_status['other_files'])}):")
                for file in git_status["other_files"][:5]:  # Afficher max 5
                    print(f"   - {file}")
                if len(git_status["other_files"]) > 5:
                    print(f"   ... et {len(git_status['other_files']) - 5} autres")
        
        # Afficher les notes de release si disponibles
        if upstream_info.get("release_notes") and len(upstream_info["release_notes"]) > 10:
            print(f"\n📋 Notes de la dernière release:")
            print("-" * 40)
            # Limiter les notes à 500 caractères
            notes = upstream_info["release_notes"]
            if len(notes) > 500:
                notes = notes[:500] + "..."
            print(notes)
            print(f"\n🔗 Lien: {upstream_info['release_url']}")
        
        return True
    
    def safe_update(self, dry_run=True):
        """Effectue une mise à jour sécurisée sans toucher aux plugins"""
        if dry_run:
            print("\n🧪 SIMULATION - Aucune modification ne sera effectuée")
        
        print("\n🔄 Préparation de la mise à jour sécurisée...")
        
        # Vérifier l'état
        git_status = self.check_git_status()
        if not git_status:
            return False
        
        # Sauvegarder les plugins modifiés
        if git_status["protected_files"]:
            print("💾 Sauvegarde des plugins modifiés...")
            if not dry_run:
                # Créer un stash avec seulement les fichiers protégés
                for file in git_status["protected_files"]:
                    try:
                        subprocess.run(
                            ["git", "add", file],
                            cwd=self.project_path,
                            check=True
                        )
                    except subprocess.CalledProcessError:
                        pass
                
                subprocess.run(
                    ["git", "stash", "push", "-m", f"Plugins sauvegardés - {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
                    cwd=self.project_path,
                    check=True
                )
        
        # Merger depuis upstream
        print("🔄 Mise à jour depuis upstream...")
        if not dry_run:
            try:
                subprocess.run(
                    ["git", "fetch", "upstream"],
                    cwd=self.project_path,
                    check=True
                )
                
                subprocess.run(
                    ["git", "merge", "upstream/main"],
                    cwd=self.project_path,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur lors du merge: {e}")
                return False
        
        # Restaurer les plugins
        if git_status["protected_files"] and not dry_run:
            print("♻️  Restauration des plugins...")
            try:
                subprocess.run(
                    ["git", "stash", "pop"],
                    cwd=self.project_path,
                    check=True
                )
            except subprocess.CalledProcessError:
                print("⚠️  Conflit lors de la restauration - résolution manuelle nécessaire")
        
        if dry_run:
            print("✅ Simulation terminée - la mise à jour semble sûre")
        else:
            print("✅ Mise à jour terminée!")
            print("💡 N'oubliez pas de faire: pnpm install && pnpm build")
        
        return True

def check_and_install_dependencies(project_path):
    """
    Vérifie et installe git, node.js et pnpm si besoin, puis exécute pnpm install, build et inject.
    """
    import platform
    import time
    
    def is_installed(cmd):
        return shutil.which(cmd) is not None

    # Vérification de git
    if not is_installed("git"):
        print("❌ git n'est pas installé !")
        if platform.system() == "Linux":
            print("➡️  Installation de git (sudo requis)...")
            subprocess.run(["sudo", "apt", "update"])  # Pour Debian/Ubuntu
            subprocess.run(["sudo", "apt", "install", "-y", "git"])
        elif platform.system() == "Darwin":
            print("➡️  Installation de git via Homebrew...")
            subprocess.run(["brew", "install", "git"])
        else:
            print("Veuillez installer git manuellement : https://git-scm.com/download/win")
            return False
    else:
        print("✅ git est installé")

    # Vérification de node
    if not is_installed("node"):
        print("❌ node.js n'est pas installé !")
        if platform.system() == "Linux":
            print("➡️  Installation de node.js (sudo requis)...")
            subprocess.run(["sudo", "apt", "update"])
            subprocess.run(["sudo", "apt", "install", "-y", "nodejs", "npm"])
        elif platform.system() == "Darwin":
            print("➡️  Installation de node via Homebrew...")
            subprocess.run(["brew", "install", "node"])
        else:
            print("Veuillez installer Node.js manuellement : https://nodejs.org/en/download/")
            return False
    else:
        print("✅ node.js est installé")

    # Vérification de pnpm
    if not is_installed("pnpm"):
        print("➡️  Installation de pnpm...")
        subprocess.run(["npm", "install", "-g", "pnpm"])
    else:
        print("✅ pnpm est installé")

    # Installation des dépendances Node.js
    print("\n📦 Installation des dépendances Node.js (pnpm install)...")
    subprocess.run(["pnpm", "install", "--no-frozen-lockfile"], cwd=project_path, check=True)

    # Build
    print("\n🔨 Build d'Equicord (pnpm build)...")
    subprocess.run(["pnpm", "build"], cwd=project_path, check=True)

    # Injection
    print("\n🚀 Injection d'Equicord dans Discord (pnpm inject)...")
    subprocess.run(["pnpm", "inject"], cwd=project_path, check=True)

    print("\n✅ Installation complète !")
    return True

def main():
    # Chemin du projet (dossier parent du script install)
    project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print(f"📁 Dossier du projet : {project_path}")

    # 1. Vérifier et installer les dépendances + build + inject
    check_and_install_dependencies(project_path)

    # 2. Mettre à jour le dépôt (pull depuis upstream si possible)
    updater = EquicordUpdater(project_path)
    print("\n🔄 Mise à jour du dépôt depuis upstream (si possible)...")
    try:
        subprocess.run(["git", "fetch", "upstream"], cwd=project_path, check=True)
        subprocess.run(["git", "merge", "upstream/main"], cwd=project_path, check=True)
    except Exception as e:
        print(f"⚠️  Impossible de merger upstream automatiquement : {e}")

    # 3. Afficher un résumé de l'état
    updater.show_update_summary()

if __name__ == "__main__":
    main() 