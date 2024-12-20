from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from resaletransactions.models import ResaleTransaction
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from timestamps.models import TablesLastUpdated
from shapely.geometry import mapping
from shapely.wkb import loads as load_wkb
from mrtstations.models import MrtStation, Line
from .utils import format_decimal

class ResaleTransactionSerializerBlock(serializers.ModelSerializer):
    postal_code = serializers.CharField(source='postal_code_key.postal_code', read_only=True)
    class Meta:
        model = ResaleTransaction
        fields = ('id', 'block', 'street_name', 'resale_price', 'postal_code',)

class ResaleTransactionSerializerUnit(serializers.ModelSerializer):
    postal_code = serializers.CharField(source='postal_code_key.postal_code', read_only=True)
    class Meta:
        model = ResaleTransaction
        fields = ('id', 'flat_type', 'block', 'street_name', 'storey_range', 'floor_area_sqm', 'flat_model', 'resale_price', 'postal_code')

class ResaleTransactionSerializerBlockAverage(serializers.ModelSerializer):
    postal_code = serializers.CharField(source='postal_code_key.postal_code', read_only=True)
    average_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model = ResaleTransaction
        fields = ("town", "block", "street_name", 'postal_code', 'average_price')
        
class ResaleTransactionSerializerUnitAverage(serializers.ModelSerializer):
    postal_code = serializers.CharField(source='postal_code_key.postal_code', read_only=True)
    average_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model = ResaleTransaction
        fields = ("town", "flat_type", "block", "street_name", "floor_area_sqm", "flat_model", "storey_range", 'postal_code', 'average_price')

class ResaleTransactionSerializerBlockLatestAvg(serializers.ModelSerializer):
    postal_code = serializers.CharField(source='postal_code_key.postal_code', read_only=True)
    average_latest_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    class Meta:
        model = ResaleTransaction
        fields = ("town", "block", "street_name", 'postal_code', 'average_latest_price')

class ResaleTransactionSerializerFull(serializers.ModelSerializer):
    postal_code = serializers.CharField(source='postal_code_key.postal_code', read_only=True)
    class Meta:
        model = ResaleTransaction
        fields= '__all__'

class PostalCodeAddressSerializer(serializers.ModelSerializer):
    resale_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = PostalCodeAddress
        fields= '__all__'

class BuildingGeometryPolygonSerializer(serializers.ModelSerializer):
    building_polygon = serializers.SerializerMethodField()
    class Meta:
        model = BuildingGeometryPolygon
        fields= '__all__'

    def get_building_polygon(self, obj):
        # Get the zoom level from the context (default to 12 if not provided)
        zoom_level = self.context.get('zoom_level', 12)
        simplify_factor = max(0.001, 0.01 * (15 - zoom_level))

        # Extract the geometry from the object and convert it to a Shapely shape
        geom = obj.building_polygon  # This is a GEOSGeometry object
        polygon = load_wkb(bytes(geom.wkb))  # Convert GEOSGeometry to Shapely using WKB
        
        # Simplify the geometry using the calculated simplify factor
        simplified_polygon = polygon.simplify(simplify_factor, preserve_topology=True)

        return mapping(simplified_polygon)
    
class BlockLatestPriceSerializer(GeoFeatureModelSerializer):
    price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    simplified_geometry = serializers.SerializerMethodField()

    class Meta:
        model = PostalCodeAddress
        geo_field = 'simplified_geometry'  # The GeoJSON geometry field
        fields = ('id', 'block', 'street_name', 'postal_code', 'simplified_geometry', 'price')  # Include the latest price dynamically

    def get_simplified_geometry(self, obj):
        # Get the zoom level from the context (default to 12 if not provided)
        zoom_level = self.context.get('zoom_level', 12)
        simplify_factor = max(0.001, 0.01 * (15 - zoom_level))

        # Extract the geometry from the object and convert it to a Shapely shape
        geom = obj.geometry  # This is a GEOSGeometry object
        if geom:
            polygon = load_wkb(bytes(geom.wkb))  # Convert GEOSGeometry to Shapely using WKB
            
            # Simplify the geometry using the calculated simplify factor
            simplified_polygon = polygon.simplify(simplify_factor, preserve_topology=True)

            return mapping(simplified_polygon)
        return None
    
class BlockSerializer(GeoFeatureModelSerializer):
    # price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    price = serializers.SerializerMethodField()
    simplified_geometry = serializers.SerializerMethodField()

    class Meta:
        model = PostalCodeAddress
        geo_field = 'simplified_geometry'  # The GeoJSON geometry field
        fields = ('id', 'block', 'street_name', 'postal_code', 'simplified_geometry', 'price')  # Include the latest price dynamically

    def get_simplified_geometry(self, obj):
        get_geometry = self.context.get('get_geometry', None)
        if get_geometry != "true":
            return None
        
        # Get the zoom level from the context (default to 12 if not provided)
        zoom_level = self.context.get('zoom_level', 12)
        simplify_factor = max(0.001, 0.01 * (15 - zoom_level))

        # Extract the geometry from the object and convert it to a Shapely shape
        geom = obj.geometry  # This is a GEOSGeometry object
        if geom:
            polygon = load_wkb(bytes(geom.wkb))  # Convert GEOSGeometry to Shapely using WKB
            
            # Simplify the geometry using the calculated simplify factor
            simplified_polygon = polygon.simplify(simplify_factor, preserve_topology=True)

            return mapping(simplified_polygon)
        return None
    
    def get_price(self,obj):
        price = self.context.get('price', None)
        if price == None:
            return None
        else:
            return format_decimal(str(obj.price), 2)

class TablesLastUpdatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablesLastUpdated
        fields= '__all__'

class FlatTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResaleTransaction
        fields= ['flat_type']

class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields= '__all__'

class MrtStationSerializer(serializers.ModelSerializer):    
    type = serializers.SerializerMethodField()
    geometry = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()
    class Meta:
        model = MrtStation
        fields = ("id", "type", 'geometry', "properties")

    def get_type(self, obj):
        return "Feature"

    def get_geometry(self, obj):
        # Get the zoom level from the context (default to 12 if not provided)
        # zoom_level = self.context.get('zoom_level', 12)
        # simplify_factor = max(0.001, 0.01 * (15 - zoom_level))

        # Extract the geometry from the object and convert it to a Shapely shape
        geom = obj.building_polygon  # This is a GEOSGeometry object
        polygon = load_wkb(bytes(geom.wkb))  # Convert GEOSGeometry to Shapely using WKB
        
        # Simplify the geometry using the calculated simplify factor
        # simplified_polygon = polygon.simplify(simplify_factor, preserve_topology=True)

        return mapping(polygon)

    def get_properties(self, obj):
        # Use the nested serializer for lines
        lines = LineSerializer(obj.lines.all(), many=True).data
        return {"name": obj.name, 'lines': lines}
