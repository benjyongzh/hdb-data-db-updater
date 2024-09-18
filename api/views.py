from rest_framework.generics import ListAPIView
from resaletransactions.models import ResaleTransaction
from rest_framework.exceptions import NotFound
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from .serializers import ResaleTransactionSerializerBlock, \
ResaleTransactionSerializerBlockLatestAvg, \
ResaleTransactionSerializerUnit, \
ResaleTransactionSerializerFull, \
ResaleTransactionSerializerBlockAverage, \
ResaleTransactionSerializerUnitAverage, \
PostalCodeAddressSerializer, \
BuildingGeometryPolygonSerializer
from django.db.models import OuterRef, Subquery, Max, F, Avg
from django.core.exceptions import ObjectDoesNotExist
from .utils import filter_queryset,filter_storey

class get_all_resale_prices(ListAPIView):
    serializer_class = ResaleTransactionSerializerFull

    def get_queryset(self):
        queryset = ResaleTransaction.objects.all()
        filter_fields = {
            'town': 'town__iexact',    # Case-insensitive category match
            'max_price': 'resale_price__lte',         # Price less than or equal to
            'min_price': 'resale_price__gte',         # Price greater than or equal to
            'flat_type': 'flat_type__iexact'
        }

        queryset = filter_queryset(queryset, self.request.query_params, filter_fields).order_by("id")
        queryset = filter_storey(queryset, self.request.query_params)
        
        return queryset

class get_resale_price_detail(ListAPIView):
    serializer_class = ResaleTransactionSerializerFull
    def get_queryset(self):
        transaction_id = self.kwargs.get('id')
        try:
            transaction = ResaleTransaction.objects.get(id=transaction_id)
            return ResaleTransaction.objects.filter(id=transaction.id)
        except ObjectDoesNotExist:
            raise NotFound(detail=f"Transaction with ID '{transaction_id}' does not exist.")


class get_all_postal_codes(ListAPIView):
    queryset = PostalCodeAddress.objects.all().order_by("id")
    serializer_class = PostalCodeAddressSerializer


class get_all_building_polygons(ListAPIView):
    queryset = BuildingGeometryPolygon.objects.all().order_by("id")
    serializer_class = BuildingGeometryPolygonSerializer

    def get_serializer_context(self):
        # Pass the zoom level to the serializer context
        # zoom_level = int(self.request.query_params.get('zoom', 12))
        zoom_level = 1
        return {'zoom_level': zoom_level}

# return the average price of a block within a past given timeframe
class average_prices(ListAPIView):
    def get_serializer_class(self):
        # check for params
        group_by_block = self.request.query_params.get('groupbyblock', None)
        if group_by_block == "true":
            return ResaleTransactionSerializerBlockAverage
        else:
            return ResaleTransactionSerializerUnitAverage

    def get_queryset(self):
        # check for params
        group_by_block = self.request.query_params.get('groupbyblock', None)
        past_months = self.request.query_params.get('pastmonths', None)

        if group_by_block == "true":
            # get avg per block
            queryset = ResaleTransaction.objects \
                .values("town",
                        "flat_type",
                        "block",
                        "street_name") \
                .annotate(average_price=Avg('resale_price'))
        else:
            # get avg per unit
            queryset = ResaleTransaction.objects \
                .values("town",
                        "flat_type",
                        "block",
                        "street_name",
                        "floor_area_sqm",
                        "flat_model",
                        "storey_range") \
                .annotate(average_price=Avg('resale_price'))

        # if past_months:
        #     pass
    
        # filter_fields = {
        #     'town': 'town__iexact',    # Case-insensitive category match
        #     'max_price': 'resale_price__lte',         # Price less than or equal to
        #     'min_price': 'resale_price__gte',         # Price greater than or equal to
        #     'flat_type': 'flat_type__iexact'
        # }

        # queryset = filter_queryset(queryset, self.request.query_params, filter_fields)

        # sort_by = self.request.query_params.get('sortby', 'id')
        # queryset = queryset.order_by(sort_by)
        # print(queryset)
        return queryset

class latest_prices(ListAPIView):
    
    def get_serializer_class(self):
        # check for params
        full_info = self.request.query_params.get('fullinfo', None)
        if full_info == "true":
            return ResaleTransactionSerializerFull
        else:
            group_by_block = self.request.query_params.get('groupbyblock', None)
            if group_by_block == "true":
                return ResaleTransactionSerializerBlock
            else:
                return ResaleTransactionSerializerUnit

    def get_queryset(self):
        # check for params
        group_by_block = self.request.query_params.get('groupbyblock', None)

        if group_by_block == "true":
            # get all latest prices per block
            queryset = ResaleTransaction.objects \
                .distinct(
                    "town",
                    "flat_type",
                    "block",
                    "street_name") \
                .order_by(
                    "town",
                    "flat_type",
                    "block",
                    "street_name",
                    "-id")
        else:
            # get all latest prices per unit
            queryset = ResaleTransaction.objects \
                .distinct(
                    "town",
                    "flat_type",
                    "block",
                    "street_name",
                    "floor_area_sqm",
                    "flat_model",
                    "storey_range",) \
                .order_by(
                    "town",
                    "flat_type",
                    "block",
                    "street_name",
                    "floor_area_sqm",
                    "flat_model",
                    "storey_range",
                    "-id")
        
        queryset = ResaleTransaction.objects.filter(id__in=Subquery(queryset.only("id")))

        filter_fields = {
            'town': 'town__iexact',    # Case-insensitive category match
            'max_price': 'resale_price__lte',         # Price less than or equal to
            'min_price': 'resale_price__gte',         # Price greater than or equal to
            'flat_type': 'flat_type__iexact'
        }

        queryset = filter_queryset(queryset, self.request.query_params, filter_fields)

        sort_by = self.request.query_params.get('sortby', 'id')
        queryset = queryset.order_by(sort_by)

        queryset = filter_storey(queryset, self.request.query_params)

        return queryset


class latest_avg_per_block(ListAPIView):
    serializer_class = PostalCodeAddressSerializer

    latest_transaction_per_unit = ResaleTransaction.objects \
        .distinct(
            "town",
            "flat_type",
            "block",
            "street_name",
            "floor_area_sqm",
            "flat_model",
            "storey_range",) \
        .order_by(
            "town",
            "flat_type",
            "block",
            "street_name",
            "floor_area_sqm",
            "flat_model",
            "storey_range",
            "-id")
    
    # use aggregate
    # queryset = PostalCodeAddress.objects.annotate(latest_transaction = Subquery(latest_transaction))