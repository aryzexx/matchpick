from django import template
from django.utils.html import format_html

from predictions.models import get_team_flag_url


register = template.Library()


@register.simple_tag
def team_flag_img(team_name, class_name="team-flag-img"):
    """
    Renders a real flag image for a country/team name.

    This avoids relying on emoji flags because some Windows/browser setups show
    country codes instead of proper flag emojis.
    """
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
    """
    Renders a team/country name with a real flag image.

    Use this anywhere on the site where a country name is shown.
    """
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
        '</span>',
        class_name,
        flag_url,
        team_name,
        team_name,
    )