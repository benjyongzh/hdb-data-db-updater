from django.db.models import QuerySet,Q

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
        if value and isinstance(value, str):
            # value = value.strip()  # Remove any leading/trailing spaces
            value = [item.strip() for item in value.split(',')]
            if len(value) > 1:
                # Build a Q object for case-insensitive filtering on multiple categories
                q_object = Q()
                for item in value:
                    q_object |= Q(**{field_lookup: item})
                
                # Filter the products based on the Q object
                queryset = queryset.filter(q_object)
                # queryset = queryset.filter(**{lookup_string: value})
            else:
                queryset = queryset.filter(**{field_lookup: value[0]})
    return queryset


def filter_storey(queryset: QuerySet, param_value:str|None, limit:str):
    if param_value:
        # try:
            param_value = int(param_value)
            # Filter products based on age range in the associated category
            filtered_transactions = []
            for transaction in queryset:
                lower, upper = transaction.get_storey_range()
                if lower is not None and upper is not None:
                    if limit == "lower":
                        if param_value >= lower:
                            filtered_transactions.append(transaction)
                    elif limit == "upper":
                        if param_value <= upper:
                            filtered_transactions.append(transaction)
                    
            return filtered_transactions
        # except ValueError:
        #     return Response({"error": "Invalid age range provided."}, status=400)
    return queryset