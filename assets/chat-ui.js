/**
 * Chat UI — wires the logic (chat.js) to the DOM.
 * Owns: FAB toggle, bubbles, typing indicator, suggestion chips.
 * Does NOT own: transport or history — that's chat.js's job.
 */

import { sendMessage } from "./chat.js";

const fab = document.getElementById("chat-fab");
const badge = document.getElementById("chat-fab-badge");
const panel = document.getElementById("chat-panel");
const messagesEl = document.getElementById("chat-messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const sendBtn = document.getElementById("chat-send");

let welcomed = false;  // first open -> bot greets + suggestion chips
let streaming = false; // one response at a time

// Defensive: re-render lucide icons in case this module loads after their init
window.lucide?.createIcons();

// --- helpers -----------------------------------------------------------

function scrollBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addBubble(sender, text = "") {
    const bubble = document.createElement("div");
    bubble.className = `chat-msg ${sender}`;
    bubble.textContent = text;
    messagesEl.appendChild(bubble);
    scrollBottom();
    return bubble;
}

// --- FAB / panel ---------------------------------------------------------

fab.addEventListener("click", () => {
    const open = panel.classList.toggle("open");
    fab.classList.toggle("open", open);
    panel.setAttribute("aria-hidden", String(!open));
    badge.remove();
    if (open && !welcomed) welcome();
});

// --- welcome + suggestions -------------------------------------------------

const SUGGESTIONS = [
    "Quelles sont tes compétences ?",
    "Parle-moi de tes projets",
    "Quelle est ta formation ?",
];

function welcome() {
    welcomed = true;
    addBubble("bot", "👋 Bonjour ! Posez vos questions sur mon parcours, mes compétences ou mes projets.");

    const chips = document.createElement("div");
    chips.className = "chat-chips";
    for (const text of SUGGESTIONS) {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "chat-chip";
        chip.textContent = text;
        chip.addEventListener("click", () => { chips.remove(); ask(text); });
        chips.appendChild(chip);
    }
    messagesEl.appendChild(chips);
    scrollBottom();
}

// --- sending -----------------------------------------------------------------

form.addEventListener("submit", (e) => {
    e.preventDefault();
    ask(input.value.trim());
});

function ask(question) {
    if (!question || streaming) return;
    streaming = true;
    input.value = "";
    input.disabled = true;
    sendBtn.disabled = true;

    addBubble("user", question);

    // Typing indicator, shown until the first token arrives
    const typing = document.createElement("div");
    typing.className = "chat-msg bot";
    const dots = document.createElement("span");
    dots.className = "typing-dots";
    for (let i = 0; i < 3; i++) dots.appendChild(document.createElement("span"));
    typing.appendChild(dots);
    messagesEl.appendChild(typing);
    scrollBottom();

    let bubble = null;

    sendMessage(question, {
        onToken(t) {
            if (typing.isConnected) typing.remove();
            if (!bubble) {
                bubble = addBubble("bot");
                bubble.classList.add("streaming");
            }
            bubble.textContent += t;
            scrollBottom();
        },
        onError(msg) {
            if (typing.isConnected) typing.remove();
            if (bubble) bubble.classList.remove("streaming");
            addBubble("bot", `⚠️ ${msg}`);
        },
        onDone() {
            if (typing.isConnected) typing.remove();
            if (bubble) bubble.classList.remove("streaming");
            streaming = false;
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
            scrollBottom();
        },
    });
}
