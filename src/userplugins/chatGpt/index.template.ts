import definePlugin from "@utils/types";
import { OpenAI } from "openai";
import { ApplicationCommandInputType, ApplicationCommandOptionType, sendBotMessage } from "@api/Commands";

// 🔑 IMPORTANT: Remplacez "VOTRE_CLE_API_ICI" par votre vraie clé API OpenAI
// ⚠️  NE COMMITEZ JAMAIS ce fichier avec une vraie clé API !
const OPENAI_API_KEY = "VOTRE_CLE_API_ICI";

let isInitialized = false;

export default definePlugin({
    name: "ChatGPT",
    description: "Permet d'utiliser ChatGPT directement dans Discord",
    authors: [{
        name: "Bash",
        id: 1327483363518582784n
    }],
    dependencies: ["CommandsAPI"],
    commands: [
        {
            inputType: ApplicationCommandInputType.BUILT_IN,
            name: "chatgpt",
            description: "Posez une question à ChatGPT",
            options: [
                {
                    name: "question",
                    description: "Votre question pour ChatGPT",
                    type: ApplicationCommandOptionType.STRING,
                    required: true
                }
            ],
            execute: async (opts, ctx) => {
                try {
                    const client = new OpenAI({ apiKey: OPENAI_API_KEY, dangerouslyAllowBrowser: true });
                    const question = opts.find(opt => opt.name === "question")?.value;

                    if (!question) throw "Aucune question fournie !";

                    const response = await client.chat.completions.create({
                        model: "gpt-3.5-turbo",
                        messages: [
                            {
                                role: "user",
                                content: question
                            }
                        ]
                    });

                    const answer = response.choices[0].message.content ?? "";

                    sendBotMessage(ctx.channel.id, {
                        embeds: [{
                            author: { name: "Réponse de ChatGPT", iconURL: "", url: "", iconProxyURL: "" },
                            rawDescription: answer,
                            color: "65280"
                        } as any]
                    });
                } catch (error) {
                    console.error("[ChatGPT] Erreur lors de l'exécution de la commande:", error);
                    sendBotMessage(ctx.channel.id, {
                        content: "Une erreur s'est produite lors de la communication avec ChatGPT."
                    });
                }
            }
        }
    ],
    start() {
        if (isInitialized) {
            console.log("[ChatGPT] Le plugin est déjà initialisé");
            return;
        }

        try {
            console.log("[ChatGPT] Initialisation du plugin...");

            if (!OPENAI_API_KEY || OPENAI_API_KEY === "VOTRE_CLE_API_ICI") {
                throw new Error("La clé API OpenAI n'est pas configurée. Veuillez modifier le fichier et remplacer VOTRE_CLE_API_ICI par votre vraie clé API.");
            }

            isInitialized = true;
            console.log("[ChatGPT] Plugin initialisé avec succès");
        } catch (error) {
            console.error("[ChatGPT] Erreur lors de l'initialisation du plugin:", error);
            isInitialized = false;
            throw error;
        }
    },
    stop() {
        console.log("[ChatGPT] Arrêt du plugin...");
        isInitialized = false;
        // Nettoyage si nécessaire
    }
}); 