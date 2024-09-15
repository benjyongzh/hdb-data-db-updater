from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from resaletransactions.models import ResaleTransaction
from rest_framework.exceptions import NotFound
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from .serializers import ResaleTransactionSerializerBlock, ResaleTransactionSerializerUnit, ResaleTransactionSerializerFull, PostalCodeAddressSerializer, BuildingGeometryPolygonSerializer
from django.db.models import OuterRef, Subquery, Max, F
from django.core.exceptions import ObjectDoesNotExist

class get_all_resale_prices(ListAPIView):
    serializer_class = ResaleTransactionSerializerFull
    queryset = ResaleTransaction.objects.all().order_by("id")

    
class average_price_overview(APIView):
    def get(self, request, timeframe):
        print(timeframe)

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
        pass

    def get_queryset(self):
        pass
    
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
        
        # check for params
        town = self.request.query_params.get('town', None)
        if town:
            town = town.strip()
            queryset = queryset.filter(town__iexact=town)

        # TODO to be able to have a range of flat_types
        # flat_type = self.request.query_params.get('flat_type', None)
        # if flat_type:
        #     queryset = queryset.filter(flat_type=flat_type)

        # TODO implement range for storey_range
        # lowest_floor = self.request.query_params.get('lowest_floor', None)
        # if lowest_floor:
        #     queryset = queryset.filter(storey_range__gte=lowest_floor)

        # highest_floor = self.request.query_params.get('highest_floor', None)
        # if highest_floor:
        #     queryset = queryset.filter(storey_range__lte=highest_floor)

        min_price = self.request.query_params.get('min_price', None)
        if min_price:
            queryset = queryset.filter(resale_price__gte=min_price)

        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            queryset = queryset.filter(resale_price__lte=max_price)

        sort_by = self.request.query_params.get('sortby', None)
        if sort_by:
            queryset = queryset.order_by(sort_by)

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