from typing import Any


SUPPORTED_LANGUAGES = {
    "English": "en",
    "Français": "fr",
}


UI_TEXT = {
    "en": {
        "assistant_title": "Hi, I’m Bob. How can I help?",
        "assistant_caption": "Ask about dispatch, technician selection, booking, troubleshooting, and invoicing.",
        "upload_label": "Temporary files (images, PDFs, text)",
        "upload_help": "These files are only used during this conversation.",
        "priority_button": "Dispatch prioritization system",
        "feedback_button": "Submit feedback",
        "feedback_help": "Open the feedback form in SharePoint.",
        "clear_button": "Clear conversation",
        "attached": "Attached in this conversation: {count} file(s)",
        "temporary_notes": "Optional temporary notes",
        "temporary_notes_placeholder": "Feel free to take notes here.",
        "chat_placeholder": "Ask a service question...",
        "analyzing": "Analyzing request...",
        "greeting": "Hi — Ask a question.",
    },
    "fr": {
        "assistant_title": "Allo, je suis Bob. Comment puis-je vous aider?",
        "assistant_caption": "Posez vos questions sur la répartition, la sélection des techniciens, les rendez-vous, le dépannage et la facturation.",
        "upload_label": "Fichiers temporaires (images, PDF, texte)",
        "upload_help": "Ces fichiers sont utilisés seulement dans cette conversation.",
        "priority_button": "Système de priorisation du dispatch",
        "feedback_button": "Soumettre un commentaire",
        "feedback_help": "Ouvrir le formulaire de commentaires dans SharePoint.",
        "clear_button": "Effacer la conversation",
        "attached": "Fichier(s) joint(s) dans cette conversation : {count}",
        "temporary_notes": "Notes temporaires optionnelles",
        "temporary_notes_placeholder": "Libre à vous de prendre des notes ici.",
        "chat_placeholder": "Posez une question sur le service...",
        "analyzing": "Analyse de la demande...",
        "greeting": "Bonjour — Posez une question.",
    },
}


def get_ui_text(language: str, key: str, **kwargs: Any) -> str:
    return UI_TEXT[language][key].format(**kwargs)
