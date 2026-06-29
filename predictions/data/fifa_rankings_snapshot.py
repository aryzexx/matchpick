import re


SNAPSHOT_LABEL = "FIFA/Coca-Cola Men's World Ranking — 11 June 2026"
SOURCE_URL = "https://inside.fifa.com/fifa-world-ranking/men"

FIFA_RANKINGS_SNAPSHOT = {
    "Algeria": 29,
    "Argentina": 1,
    "Australia": 28,
    "Austria": 22,
    "Belgium": 10,
    "Bosnia & Herzegovina": 61,
    "Brazil": 5,
    "Canada": 30,
    "Cape Verde": 64,
    "Colombia": 11,
    "Croatia": 13,
    "Curaçao": 82,
    "Czech Republic": 48,
    "DR Congo": 41,
    "Ecuador": 25,
    "Egypt": 26,
    "England": 4,
    "France": 2,
    "Germany": 12,
    "Ghana": 65,
    "Haiti": 88,
    "Iran": 21,
    "Iraq": 63,
    "Ivory Coast": 31,
    "Japan": 17,
    "Jordan": 73,
    "Mexico": 9,
    "Morocco": 6,
    "Netherlands": 7,
    "New Zealand": 86,
    "Norway": 23,
    "Panama": 44,
    "Paraguay": 37,
    "Portugal": 8,
    "Qatar": 59,
    "Saudi Arabia": 58,
    "Scotland": 42,
    "Senegal": 18,
    "South Africa": 54,
    "South Korea": 32,
    "Spain": 3,
    "Sweden": 36,
    "Switzerland": 16,
    "Tunisia": 57,
    "Turkey": 27,
    "USA": 15,
    "Uruguay": 19,
    "Uzbekistan": 60,
}

TEAM_RANKING_ALIASES = {
    "Bosnia": "Bosnia & Herzegovina",
    "Bosnia and Herzegovina": "Bosnia & Herzegovina",
    "Curacao": "Curaçao",
    "Czechia": "Czech Republic",
    "Congo DR": "DR Congo",
    "DRC": "DR Congo",
    "IR Iran": "Iran",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Korea Republic": "South Korea",
    "United States": "USA",
    "United States of America": "USA",
    "Türkiye": "Turkey",
    "Turkiye": "Turkey",
}

PLACEHOLDER_TEAM_PATTERNS = [
    re.compile(r"^[123][A-H]$", re.IGNORECASE),
    re.compile(r"^[123][A-H](?:/[A-H])+$", re.IGNORECASE),
    re.compile(r"^[WL]\d+$", re.IGNORECASE),
]


def normalise_team_name(team_name):
    if not team_name:
        return ""

    return team_name.strip()


def is_placeholder_team_name(team_name):
    normalised_name = normalise_team_name(team_name)

    if not normalised_name:
        return False

    return any(
        pattern.match(normalised_name)
        for pattern in PLACEHOLDER_TEAM_PATTERNS
    )


def get_team_ranking(team_name):
    normalised_name = normalise_team_name(team_name)

    if not normalised_name:
        return None

    if is_placeholder_team_name(normalised_name):
        return None

    fifa_name = TEAM_RANKING_ALIASES.get(normalised_name, normalised_name)

    return FIFA_RANKINGS_SNAPSHOT.get(fifa_name)
