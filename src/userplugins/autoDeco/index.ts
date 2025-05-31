import definePlugin from "../../utils/types";
import { addContextMenuPatch, removeContextMenuPatch } from "../../api/ContextMenu";
import { showNotification } from "../../api/Notifications";
import { SelectedChannelStore, UserStore } from "../../webpack/common/stores";
import { Menu, React } from "../../webpack/common";
import { findByPropsLazy } from "../../webpack/webpack";

let targetUserId: string | null = null;
let patchFn: any = null;
const VoiceActions = findByPropsLazy("leaveChannel");

export default definePlugin({
    name: "AutoDeco",
    description: "Se déconnecte automatiquement du canal vocal lorsqu'un utilisateur spécifique rejoint",
    authors: [{
        name: "Bash",
        id: 1327483363518582784n
    }],

    start() {
        // Patch du menu contextuel utilisateur
        patchFn = (children, ...args) => {
            // On récupère l'utilisateur depuis les arguments du menu contextuel
            const user = args[0]?.user || args[0];
            const currentUser = UserStore.getCurrentUser();
            if (!user || user.id === currentUser.id) return;

            // Cherche l'index du bouton 'Follow User'
            let followIdx = children.findIndex(child => {
                if (!child || !child.props) return false;
                return child.props.id === "user-context-follow" || child.props.label === "Follow User";
            });

            const isActive = targetUserId === user.id;
            const autoDecoBtn = React.createElement(Menu.MenuItem, {
                id: "autodeco-context",
                label: isActive ? "Désactiver AutoDeco" : "Activer AutoDeco",
                action: () => {
                    if (isActive) {
                        targetUserId = null;
                        showNotification({
                            title: "AutoDeco",
                            body: `AutoDeco désactivé pour ${user.username}`
                        });
                    } else {
                        targetUserId = user.id;
                        showNotification({
                            title: "AutoDeco",
                            body: `AutoDeco activé pour ${user.username}`
                        });
                    }
                },
                // Optionnel : coche si actif
                icon: isActive ? () => React.createElement("span", { style: { color: "#43b581", fontWeight: "bold" } }, "✔") : undefined
            });

            if (followIdx !== -1) {
                children.splice(followIdx + 1, 0, autoDecoBtn);
            } else {
                children.push(autoDecoBtn);
            }
        };
        addContextMenuPatch("user-context", patchFn);

        // Écoute les changements d'état vocal
        this.onVoiceStateUpdate = (oldState, newState) => {
            if (targetUserId && newState.userId === targetUserId && newState.channelId) {
                if (!oldState.channelId) {
                    const currentChannelId = SelectedChannelStore.getVoiceChannelId();
                    if (currentChannelId) {
                        if (VoiceActions && typeof VoiceActions.leaveChannel === "function") {
                            VoiceActions.leaveChannel();
                        }
                        showNotification({
                            title: "AutoDeco",
                            body: `Déconnexion automatique : ${newState.user?.username} a rejoint un canal vocal`
                        });
                    }
                }
            }
        };
    },

    stop() {
        targetUserId = null;
        if (patchFn) {
            removeContextMenuPatch("user-context", patchFn);
            patchFn = null;
        }
    }
});
