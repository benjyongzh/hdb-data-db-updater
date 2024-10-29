from rest_framework.generics import ListAPIView
from resaletransactions.models import ResaleTransaction
from rest_framework.exceptions import NotFound
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from .serializers import ResaleTransactionSerializerBlock, \
ResaleTransactionSerializerUnit, \
ResaleTransactionSerializerFull, \
ResaleTransactionSerializerBlockAverage, \
ResaleTransactionSerializerUnitAverage, \
ResaleTransactionSerializerBlockLatestAvg, \
PostalCodeAddressSerializer, \
BuildingGeometryPolygonSerializer, \
PolygonPriceSerializer
from django.db.models import OuterRef, Subquery, Max, F, Avg
from django.core.exceptions import ObjectDoesNotExist
from .utils import filter_queryset,filter_storey
from datetime import datetime, timedelta

class get_all_resale_prices(ListAPIView):
    serializer_class = ResaleTransactionSerializerFull

    def get_queryset(self):
        queryset = ResaleTransaction.objects.all()
        filter_fields = {
            'town': 'town__iexact',    # Case-insensitive category match
            'block': 'block__iexact',    # Case-insensitive category match
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
            # return ResaleTransactionSerializerFull

    def get_queryset(self):
        past_months = self.request.query_params.get('pastmonths', None)
        queryset = ResaleTransaction.objects.all()
        
        if past_months:         
            # Calculate the date that is `past_months` months ago from today
            current_date = datetime.now()
            min_year = current_date.year
            min_month = current_date.month
            month_count:int = 0
            while month_count < int(past_months):
                if min_month <= 1:
                    min_month = 12
                    min_year -=1
                else: min_month -=1
                month_count +=1

            # Convert `min_date` to the "YYYY-MM" format
            min_date_str = "{min_year}-{min_month}".format(min_year = min_year, min_month = min_month if min_month > 9 else "0"+str(min_month))
            queryset = queryset.filter(month__gte=min_date_str)

        group_by_block = self.request.query_params.get('groupbyblock', None)
        if group_by_block == "true":
            # get avg per block
            queryset = queryset.values("town",
                        "block",
                        "street_name") \
                .annotate(average_price=Avg('resale_price'))
        else:
            # get avg per unit
            queryset = queryset.values("town",
                        "flat_type",
                        "block",
                        "street_name",
                        "floor_area_sqm",
                        "flat_model",
                        "storey_range") \
                .annotate(average_price=Avg('resale_price'))
    
        filter_fields = {
            'town': 'town__iexact',    # Case-insensitive category match
            'max_price': 'average_price__lte',         # Price less than or equal to
            'min_price': 'average_price__gte',         # Price greater than or equal to
        }

        queryset = filter_queryset(queryset, self.request.query_params, filter_fields)
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
            'block': 'block__iexact',    # Case-insensitive category match
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
    def get_serializer_class(self):
        # check for params
        full_info = self.request.query_params.get('fullinfo', None)
        if full_info == "true":
            return ResaleTransactionSerializerFull
        return ResaleTransactionSerializerBlockLatestAvg
    
    def get_queryset(self):        
        # get all latest prices per unit
        queryset = ResaleTransaction.objects \
            .distinct(
                "town",
                "flat_type",
                "block",
                "street_name",
                "floor_area_sqm",
                "storey_range",) \
            .order_by(
                "town",
                "flat_type",
                "block",
                "street_name",
                "floor_area_sqm",
                "storey_range",
                "-id")
        
        # Now, group by townn, block and street_name and calculate the average of the latest resale prices
        queryset = ResaleTransaction.objects \
            .filter(id__in=Subquery(queryset.only("id"))) \
            .values('town','block','street_name') \
            .annotate(average_latest_price=Avg('resale_price'))
        
        # TODO add URL param for seeing only data from past few months?
        
        filter_fields = {
            'town': 'town__iexact',    # Case-insensitive category match
            'block': 'block__iexact',    # Case-insensitive category match
            'max_price': 'average_latest_price__lte',         # Price less than or equal to
            'min_price': 'average_latest_price__gte',         # Price greater than or equal to
        }

        queryset = filter_queryset(queryset, self.request.query_params, filter_fields)

        return queryset
    
class polygon_price_per_block(ListAPIView):
    serializer_class = PolygonPriceSerializer

    def get_serializer_context(self):
        # Pass the zoom level to the serializer context
        # zoom_level = int(self.request.query_params.get('zoom', 12))
        zoom_level = 1
        return {'zoom_level': zoom_level,
                **super().get_serializer_context()
        }
    
    # queryset = PostalCodeAddress.objects.all().with_geometry().with_latest_price().order_by("id")
    queryset = PostalCodeAddress.objects.all()