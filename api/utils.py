from django.db.models import QuerySet

def filter_queryset(queryset: QuerySet, params: dict, filter_fields: dict) -> QuerySet:
    """
    Apply filters to a queryset based on dynamic filter fields and query parameters.
    :param queryset: The queryset to filter
    :param params: Query parameters (request.query_params)
    :param filter_fields: Dictionary mapping query param names to model field lookups (e.g. 'category': 'category__iexact')
    :return: Filtered queryset
    """
    for param, field_lookup in filter_fields.items():
        value = params.get(param)
        if value:
            if isinstance(value, str):
                value = value.strip()  # Remove any leading/trailing spaces
            queryset = queryset.filter(**{field_lookup: value})
    
    return queryset
