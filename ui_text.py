from typing import Any


SUPPORTED_LANGUAGES = {
    "English": "en",
    "Français": "fr",
}


UI_TEXT = {
    "en": {
        "assistant_title": "Hi, I’m Bob. How can I help?",
        "assistant_caption": "Ask about procedures, technician selection, booking, warranties, invoicing, and more.",
        "upload_label": "Temporary files (images, PDFs, text)",
        "upload_help": "These files are only used during this conversation.",
        "priority_button": "Dispatch prioritization system",
        "quick_links_button": "Quick links",
        "quick_links_title": "Useful service links",
        "feedback_button": "Submit feedback",
        "feedback_help": "Open the feedback form in SharePoint.",
        "clear_button": "Clear conversation",
        "clear_help": "Delete and reset the current conversation.",
        "attached": "Attached in this conversation: {count} file(s)",
        "temporary_notes": "Optional temporary notes",
        "temporary_notes_placeholder": "Feel free to take notes here.",
        "chat_placeholder": "Ask a service question...",
        "analyzing": "Analyzing request...",
        "greeting": "Hi — Ask a question.",
        "suggestions_intro": "Quick questions to get started:",
        "suggested_questions": [
            "How do I create a work order?",
            "How do I process a warranty claim?",
            "How do I invoice a work order?",
            "How do I handle a cash customer?",
        ],
    },
    "fr": {
        "assistant_title": "Allo, je suis Bob. Comment puis-je vous aider?",
        "assistant_caption": "Posez vos questions sur les procédures, la sélection des techniciens, les rendez-vous, les garanties, la facturation et bien plus.",
        "upload_label": "Fichiers temporaires (images, PDF, texte)",
        "upload_help": "Ces fichiers sont utilisés seulement dans cette conversation.",
        "priority_button": "Système de priorisation du dispatch",
        "quick_links_button": "Liens rapides",
        "quick_links_title": "Liens de service utiles",
        "feedback_button": "Soumettre un commentaire",
        "feedback_help": "Ouvrir le formulaire de commentaires dans SharePoint.",
        "clear_button": "Effacer la conversation",
        "clear_help": "Supprimer et réinitialiser la conversation actuelle.",
        "attached": "Fichier(s) joint(s) dans cette conversation : {count}",
        "temporary_notes": "Notes temporaires optionnelles",
        "temporary_notes_placeholder": "Libre à vous de prendre des notes ici.",
        "chat_placeholder": "Posez une question sur le service...",
        "analyzing": "Analyse de la demande...",
        "greeting": "Bonjour — Posez une question.",
        "suggestions_intro": "Questions rapides pour commencer :",
        "suggested_questions": [
            "Comment créer un bon de travail?",
            "Comment traiter une réclamation de garantie?",
            "Comment facturer un bon de travail?",
            "Comment prendre en charge un client cash?",
        ],
    },
}


def get_ui_text(language: str, key: str, **kwargs: Any) -> Any:
    value = UI_TEXT[language][key]
    return value.format(**kwargs) if isinstance(value, str) else value
