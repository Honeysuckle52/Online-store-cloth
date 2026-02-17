from django import template

register = template.Library()


@register.filter(name='get_list')
def get_list(value, arg):
    """
    Получает список значений из GET параметра
    Использование: {{ request.GET|get_list:'size' }}
    """
    if hasattr(value, 'getlist'):
        return value.getlist(arg)
    return []


@register.filter(name='in_list')
def in_list(value, arg):
    """
    Проверяет, находится ли значение в списке
    Использование: {% if value in list %}
    """
    return value in arg


@register.simple_tag
def query_transform(request, **kwargs):
    """
    Трансформирует GET параметры для пагинации и фильтров
    Использование: {% query_transform request page=num %}
    """
    updated = request.GET.copy()
    for key, value in kwargs.items():
        if value is not None:
            updated[key] = value
        else:
            updated.pop(key, 0)
    return updated.urlencode()