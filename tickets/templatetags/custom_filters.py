from django import template
from datetime import datetime

register = template.Library()

@register.filter
def dynamic_zfill(value, store_code):
    """
    Format the value with leading zeros, including the dynamic year, store code, and the dynamic portion.
    """
    value_str = str(value)
    zeros_count = max(6 - len(value_str), 0)
    
    # Get the last two digits of the current year
    current_year = datetime.now().year % 100
    next_year = (current_year + 1) % 100
    
    return f'{store_code}{current_year:02}{next_year:02}{value_str.zfill(zeros_count + len(value_str))}'


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

