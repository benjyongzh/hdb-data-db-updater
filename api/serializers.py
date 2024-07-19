from rest_framework import serializers
from datacollector.models import ResaleTransaction
from postalcodedata.models import PostalCodeAddress

class ResaleTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResaleTransaction
        fields= '__all__'

class PostalCodeAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostalCodeAddress
        fields= '__all__'