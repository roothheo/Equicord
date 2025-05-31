#!/bin/bash

# Script Shell pour vérifier les mises à jour d'Equicord
# Wrapper pour install.py

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    echo -e "${BLUE}🔧 Equicord Updater${NC}"
    echo -e "${BLUE}=====================${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --check       Vérifier les mises à jour (défaut)"
    echo "  --update      Effectuer la mise à jour"
    echo "  --dry-run     Simulation de mise à jour"
    echo "  --path PATH   Chemin du projet Equicord"
    echo "  --help        Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0                    # Vérification simple"
    echo "  $0 --update         # Mise à jour interactive"
    echo "  $0 --dry-run        # Simulation"
    echo ""
}

# Fonction pour vérifier les prérequis
check_requirements() {
    local missing_deps=()
    
    # Vérifier Python3
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    # Vérifier Git
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    # Vérifier les modules Python
    if ! python3 -c "import requests" &> /dev/null; then
        missing_deps+=("python3-requests")
    fi
    
    if ! python3 -c "import packaging" &> /dev/null; then
        missing_deps+=("python3-packaging")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}❌ Dépendances manquantes:${NC}"
        for dep in "${missing_deps[@]}"; do
            echo -e "   - ${dep}"
        done
        echo ""
        echo -e "${YELLOW}💡 Pour installer sur Ubuntu/Debian:${NC}"
        echo "   sudo apt update"
        echo "   sudo apt install python3 git python3-requests python3-packaging"
        echo ""
        echo -e "${YELLOW}💡 Ou avec pip:${NC}"
        echo "   pip install requests packaging"
        return 1
    fi
    
    return 0
}

# Fonction principale
main() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local python_script="$script_dir/install.py"
    local project_path=""
    local args=()
    
    # Détecter automatiquement le chemin du projet
    if [[ -f "$script_dir/package.json" ]]; then
        project_path="$script_dir"
    elif [[ -f "/home/bash/Desktop/dev/bashcord/package.json" ]]; then
        project_path="/home/bash/Desktop/dev/bashcord"
    fi
    
    # Parser les arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --check|--update|--dry-run)
                args+=("$1")
                shift
                ;;
            --path)
                if [[ -n "$2" ]]; then
                    project_path="$2"
                    args+=("--path" "$2")
                    shift 2
                else
                    echo -e "${RED}❌ L'option --path nécessite un argument${NC}"
                    exit 1
                fi
                ;;
            *)
                echo -e "${RED}❌ Option inconnue: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Vérifier si le script Python existe
    if [[ ! -f "$python_script" ]]; then
        echo -e "${RED}❌ Script Python non trouvé: $python_script${NC}"
        echo -e "${YELLOW}💡 Assurez-vous que install.py est dans le même dossier${NC}"
        exit 1
    fi
    
    # Vérifier les prérequis
    echo -e "${BLUE}🔍 Vérification des prérequis...${NC}"
    if ! check_requirements; then
        exit 1
    fi
    
    # Vérifier le projet Equicord
    if [[ -n "$project_path" ]]; then
        if [[ ! -f "$project_path/package.json" ]]; then
            echo -e "${RED}❌ Projet Equicord non trouvé dans: $project_path${NC}"
            echo -e "${YELLOW}💡 Utilisez --path pour spécifier le bon chemin${NC}"
            exit 1
        fi
    fi
    
    # Ajouter le chemin du projet si détecté automatiquement
    if [[ -n "$project_path" && ${#args[@]} -eq 0 ]]; then
        args+=("--path" "$project_path")
    elif [[ -n "$project_path" ]]; then
        # Vérifier si --path n'est pas déjà dans les args
        local has_path=false
        for arg in "${args[@]}"; do
            if [[ "$arg" == "--path" ]]; then
                has_path=true
                break
            fi
        done
        if [[ "$has_path" == false ]]; then
            args+=("--path" "$project_path")
        fi
    fi
    
    # Afficher les informations
    echo -e "${GREEN}✅ Prérequis vérifiés${NC}"
    if [[ -n "$project_path" ]]; then
        echo -e "${BLUE}📁 Projet détecté: $project_path${NC}"
    fi
    echo ""
    
    # Exécuter le script Python
    echo -e "${BLUE}🚀 Lancement d'Equicord Updater...${NC}"
    echo ""
    
    if [[ ${#args[@]} -eq 0 ]]; then
        python3 "$python_script"
    else
        python3 "$python_script" "${args[@]}"
    fi
    
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        echo ""
        echo -e "${GREEN}✅ Terminé avec succès${NC}"
    else
        echo ""
        echo -e "${RED}❌ Erreur (code: $exit_code)${NC}"
    fi
    
    return $exit_code
}

# Gestion des signaux
trap 'echo -e "\n${YELLOW}⚠️  Interruption détectée. Arrêt...${NC}"; exit 130' INT TERM

# Point d'entrée
main "$@" 