from django.db.models import QuerySet,Q
from django.http import JsonResponse
from rest_framework import status

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


def filter_storey(queryset: QuerySet, params: dict):
    lowest_floor = params.get('lowest_floor', None)
    highest_floor = params.get('highest_floor', None)
    if lowest_floor is None and highest_floor is None:
        return queryset
    
    filtered_transactions = []
    for transaction in queryset:
        lower, upper = transaction.get_storey_range()
        if lower is not None and upper is not None:
            try:
                if lowest_floor and highest_floor:
                    if int(lowest_floor) <= upper and int(highest_floor) >= lower:
                        filtered_transactions.append(transaction)

                elif lowest_floor:
                    if int(lowest_floor) <= upper:
                        filtered_transactions.append(transaction)

                elif int(highest_floor) >= lower:
                        filtered_transactions.append(transaction)

            except ValueError:
                return JsonResponse({"error": "Invalid lower storey limit provided."}, status=status.HTTP_400_BAD_REQUEST)
    return filtered_transactions

def format_decimal(value:str, decimal_places:int):
    decimal:str = "."
    parts = value.split(decimal)
    return parts[0] +decimal + parts[1][:decimal_places]