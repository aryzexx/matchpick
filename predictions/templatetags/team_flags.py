from django import template
from django.utils.html import format_html

from predictions.models import get_team_flag_url

register = template.Library()


TEAM_ABBREVIATION_MAP = {
    "mexico": "MEX",
    "south africa": "RSA",
    "south korea": "KOR",
    "korea republic": "KOR",
    "czechia": "CZE",
    "czech republic": "CZE",
    "canada": "CAN",
    "bosnia and herzegovina": "BIH",
    "bosnia & herzegovina": "BIH",
    "qatar": "QAT",
    "switzerland": "SUI",
    "brazil": "BRA",
    "morocco": "MAR",
    "haiti": "HAI",
    "scotland": "SCO",
    "united states": "USA",
    "usa": "USA",
    "paraguay": "PAR",
    "australia": "AUS",
    "turkey": "TUR",
    "türkiye": "TUR",
    "turkiye": "TUR",
    "germany": "GER",
    "curacao": "CUW",
    "curaçao": "CUW",
    "ivory coast": "CIV",
    "côte d'ivoire": "CIV",
    "cote d'ivoire": "CIV",
    "ecuador": "ECU",
    "netherlands": "NED",
    "japan": "JPN",
    "sweden": "SWE",
    "tunisia": "TUN",
    "spain": "ESP",
    "cape verde": "CPV",
    "saudi arabia": "KSA",
    "uruguay": "URU",
    "belgium": "BEL",
    "egypt": "EGY",
    "iran": "IRN",
    "new zealand": "NZL",
    "france": "FRA",
    "senegal": "SEN",
    "iraq": "IRQ",
    "norway": "NOR",
    "argentina": "ARG",
    "algeria": "ALG",
    "austria": "AUT",
    "jordan": "JOR",
    "portugal": "POR",
    "dr congo": "COD",
    "d.r. congo": "COD",
    "democratic republic of the congo": "COD",
    "uzbekistan": "UZB",
    "colombia": "COL",
    "england": "ENG",
    "croatia": "CRO",
    "ghana": "GHA",
    "panama": "PAN",
}


def normalise_team_key(team_name):
    return str(team_name or "").strip().lower()


def get_team_abbreviation(team_name):
    team_key = normalise_team_key(team_name)

    if team_key in TEAM_ABBREVIATION_MAP:
        return TEAM_ABBREVIATION_MAP[team_key]

    compact_name = str(team_name or "").strip().upper()

    if not compact_name:
        return "—"

    return compact_name[:3]


@register.simple_tag
def team_flag_img(team_name, class_name="team-flag-img"):
    flag_url = get_team_flag_url(team_name)

    if not flag_url:
        return ""

    return format_html(
        '<img class="{}" src="{}" alt="{} flag" loading="lazy">',
        class_name,
        flag_url,
        team_name,
    )


@register.simple_tag
def team_with_flag(team_name, class_name="team-flag-img"):
    flag_url = get_team_flag_url(team_name)

    if not flag_url:
        return format_html(
            '<span class="team-inline"><span>{}</span></span>',
            team_name,
        )

    return format_html(
        '<span class="team-inline">'
        '<img class="{}" src="{}" alt="{} flag" loading="lazy">'
        '<span>{}</span>'
        "</span>",
        class_name,
        flag_url,
        team_name,
        team_name,
    )


@register.simple_tag
def team_code(team_name):
    return get_team_abbreviation(team_name)


@register.simple_tag
def team_code_with_flag(team_name, class_name="team-flag-img"):
    flag_url = get_team_flag_url(team_name)
    team_abbreviation = get_team_abbreviation(team_name)

    if not flag_url:
        return format_html(
            '<span class="team-code-inline" title="{}">'
            '<span>{}</span>'
            '<span class="visually-hidden">{}</span>'
            "</span>",
            team_name,
            team_abbreviation,
            team_name,
        )

    return format_html(
        '<span class="team-code-inline" title="{}">'
        '<img class="{}" src="{}" alt="{} flag" loading="lazy">'
        '<span>{}</span>'
        '<span class="visually-hidden">{}</span>'
        "</span>",
        team_name,
        class_name,
        flag_url,
        team_name,
        team_abbreviation,
        team_name,
    )