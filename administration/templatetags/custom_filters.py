from django import template
from num2words import num2words
from datetime import datetime

register = template.Library()

@register.filter
def date_in_words(value):
    if not value:
        return ""

    day = num2words(value.day, to='ordinal').title()
    month = value.strftime('%B')
    year = num2words(value.year).title().lower()

    return f"{day} {month} {year}"