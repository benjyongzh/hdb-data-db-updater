from rest_framework import serializers
from resaletransactions.models import ResaleTransaction
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from timestamps.models import TablesLastUpdated
from shapely.geometry import shape, mapping
from shapely.wkb import loads as load_wkb

class ResaleTransactionSerializerBlock(serializers.ModelSerializer):
    postal_code = serializers.CharField(source='postal_code_key.postal_code', read_only=True)
    class Meta:
        model = ResaleTransaction
        fields = ('id', 'block', 'street_name', 'resale_price', 'postal_code')

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

class TablesLastUpdatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablesLastUpdated
        fields= '__all__'