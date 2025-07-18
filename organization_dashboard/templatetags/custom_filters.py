# organization_dashboard/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """
    Replaces all occurrences of a substring with another.
    Usage: {{ value|replace:"old_substring,new_substring" }}
    Example: {{ "hello world"|replace:" ," }}  -> "helloworld"
    """
    if not isinstance(value, str):
        return value
        
    try:
        old_sub, new_sub = arg.split(',', 1)
    except ValueError:
        return value # Return original value if arg is not in "old,new" format
    
    return value.replace(old_sub, new_sub)