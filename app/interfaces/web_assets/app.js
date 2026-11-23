"use strict";

const token = document.querySelector('meta[name="session-token"]').content;
const engine = document.getElementById("engine");
const conversation = document.getElementById("conversation");
const composer = document.getElementById("composer");
const message = document.getElementById("message");
const status = document.getElementById("status");
const buttons = document.querySelectorAll("button");
let busy = false;

function setBusy(value) {
  busy = value;
  for (const button of buttons) button.disabled = value;
}

function addMessage(role, text) {
  const entry = document.createElement("article");
  const author = document.createElement("strong");
  const content = document.createElement("p");
  entry.className = `message ${role}`;
  author.textContent = { user: "Vous", assistant: "M.A.L.I.E.C.A.", error: "Erreur" }[role];
  content.textContent = text;
  entry.append(author, content);
  conversation.append(entry);
  conversation.scrollTop = conversation.scrollHeight;
}

async function request(path, input) {
  const headers = { Authorization: `Bearer ${token}` };
  const options = { headers };
  if (input !== undefined) {
    headers["Content-Type"] = "application/json";
    options.method = "POST";
    options.body = JSON.stringify({ message: input });
  }
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error);
  return data;
}

async function send(input) {
  if (busy || !input) return;
  setBusy(true);
  addMessage("user", input);
  status.textContent = "Demande en cours…";
  try {
    const data = await request("/api/input", input);
    if (input === "/historique effacer") conversation.replaceChildren();
    addMessage("assistant", data.reply);
  } catch (error) {
    addMessage("error", error.message);
  } finally {
    status.textContent = "";
    setBusy(false);
    message.focus();
  }
}

composer.addEventListener("submit", (event) => {
  event.preventDefault();
  const input = message.value.trim();
  if (!input || busy) return;
  message.value = "";
  void send(input);
});

for (const button of document.querySelectorAll("nav button")) {
  button.addEventListener("click", () => void send(button.dataset.command));
}

async function loadHistory() {
  setBusy(true);
  try {
    const data = await request("/api/history");
    engine.textContent = data.engine;
    for (const item of data.messages) addMessage(item.role, item.text);
  } catch (error) {
    engine.textContent = "Connexion indisponible";
    addMessage("error", error.message);
  } finally {
    setBusy(false);
  }
}

void loadHistory();
