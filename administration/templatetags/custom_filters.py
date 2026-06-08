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

    year = value.year
    if 1000 <= year <= 2099:
        first_part = num2words(year // 100).title()
        second_part = num2words(year % 100).title()

        if year % 100 == 0:
            year_words = f"{first_part} Hundred"
        else:
            year_words = f"{first_part} {second_part}"
    else:
        year_words = num2words(year).title()

    return f"{day} {month} {year_words}"