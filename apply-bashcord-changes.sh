#!/bin/bash

# Script pour appliquer automatiquement les changements Bashcord après un pull

echo "🔄 Application des changements Bashcord..."

# Remplacer Equicord par Bashcord dans settings.tsx
sed -i 's/label: "Equicord"/label: "Bashcord"/g' src/plugins/_core/settings.tsx
sed -i 's/"Equicord", "Settings", "Equicord Settings"/"Bashcord", "Settings", "Bashcord Settings"/g' src/plugins/_core/settings.tsx
sed -i 's/Where to put the Equicord settings section/Where to put the Bashcord settings section/g' src/plugins/_core/settings.tsx
sed -i 's/\`Equicord \${gitHash}/\`Bashcord \${gitHash}/g' src/plugins/_core/settings.tsx

echo "✅ Changements Bashcord appliqués avec succès!" 