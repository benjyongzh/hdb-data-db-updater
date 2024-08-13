from rest_framework import serializers
from resaletransactions.models import ResaleTransaction
from postalcodes.models import PostalCodeAddress, BuildingGeometryPolygon
from timestamps.models import TablesLastUpdated

class ResaleTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResaleTransaction
        fields= '__all__'

class PostalCodeAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostalCodeAddress
        fields= '__all__'

class BuildingGeometryPolygonSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingGeometryPolygon
        fields= '__all__'

class TablesLastUpdatedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TablesLastUpdated
        fields= '__all__'