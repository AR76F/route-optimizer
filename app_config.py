from pathlib import Path
from typing import Any, Dict
import tomllib


BRANCH_CONFIG_DIR = Path(__file__).resolve().parent / "config" / "branches"


# Links surfaced by the Service Assistant quick-links menu.
# Keep labels and categories bilingual so the UI can render the active language.
QUICK_LINKS = [
    {
        "label": "BMS",
        "label_fr": "BMS",
        "category": "Core tools",
        "category_fr": "Outils principaux",
        "url": "https://onebmscan.cummins.com/forms/frmservlet?config=12c_canada_eng",
        "icon": ":material/assignment:",
    },
    {
        "label": "FieldAware",
        "label_fr": "FieldAware",
        "category": "Core tools",
        "category_fr": "Outils principaux",
        "url": "https://app.fieldaware.com/account/jobs_and_quotes/scheduler",
        "icon": ":material/calendar_month:",
    },
    {
        "label": "Power BI",
        "label_fr": "Power BI",
        "category": "Core tools",
        "category_fr": "Outils principaux",
        "url": "https://app.powerbi.com/groups/me/apps/ed3dd510-050a-47ed-9455-477e60121d5d/reports/f18265a3-a16f-4eaa-ac0e-1ff1630c4117/ReportSection37e3466f482fcfc46c49?experience=power-bi",
        "icon": ":material/insights:",
    },
    {
        "label": "Clover",
        "label_fr": "Clover",
        "category": "Core tools",
        "category_fr": "Outils principaux",
        "url": "https://www.clover.com/login",
        "icon": ":material/payments:",
    },
    {
        "label": "PGBU Warranty System",
        "label_fr": "Système de garantie PGBU",
        "category": "Cummins resources",
        "category_fr": "Ressources Cummins",
        "url": "https://mylogin.cummins.com/clw/s/login/?ec=302&inst=Uz&startURL=%2Fclw%2FIAM_Authorize%3Fappid%3Da1a4N00000Hd6gr",
        "icon": ":material/verified_user:",
    },
    {
        "label": "QuickServe Online (QSOL)",
        "label_fr": "QuickServe Online (QSOL)",
        "category": "Cummins resources",
        "category_fr": "Ressources Cummins",
        "url": "https://mylogin.cummins.com/clw/s/login/?ec=302&inst=Uz&startURL=%2Fclw%2FIAM_Authorize%3Fappid%3Da1a4N00000DEdub",
        "icon": ":material/menu_book:",
    },
    {
        "label": "Seismic Learning",
        "label_fr": "Formation Seismic",
        "category": "Cummins resources",
        "category_fr": "Ressources Cummins",
        "url": "https://cummins.seismic.com/apps/learning/learn",
        "icon": ":material/school:",
    },
    {
        "label": "Geotab",
        "label_fr": "Geotab",
        "category": "Cummins resources",
        "category_fr": "Ressources Cummins",
        "url": "https://ari.geotab.com/cummins_inc/",
        "icon": ":material/location_on:",
    },
    {
        "label": "WWIMS Next Gen",
        "label_fr": "WWIMS Next Gen",
        "category": "Cummins resources",
        "category_fr": "Ressources Cummins",
        "url": "https://wwimsngn.cummins.com",
        "icon": ":material/manage_accounts:",
    },
    {
        "label": "Route Optimizer",
        "label_fr": "Route Optimizer",
        "category": "Internal tools",
        "category_fr": "Outils internes",
        "url": "https://route-optimizer-6hqpt2tqchkcfycp8ovgee.streamlit.app/",
        "icon": ":material/route:",
    },
]


def load_branch_profiles() -> Dict[str, Dict[str, Any]]:
    profiles: Dict[str, Dict[str, Any]] = {}

    for config_path in sorted(BRANCH_CONFIG_DIR.glob("*.toml")):
        with config_path.open("rb") as config_file:
            profile = tomllib.load(config_file)

        branch = profile.get("branch", {})
        label = branch.get("label")
        if not label:
            raise ValueError(f"Branch config is missing branch.label: {config_path}")

        profiles[label] = branch

    if not profiles:
        raise RuntimeError(f"No branch profiles found in {BRANCH_CONFIG_DIR}")

    return profiles


BRANCH_PROFILES = load_branch_profiles()

SUPPORTED_BRANCHES = [
    label
    for label, _profile in sorted(
        BRANCH_PROFILES.items(),
        key = lambda item: item[1].get("display_order", 999),
    )
]

BRANCH_DEFAULT_LANGUAGES = {
    label: profile.get("default_language", "en")
    for label, profile in BRANCH_PROFILES.items()
}
