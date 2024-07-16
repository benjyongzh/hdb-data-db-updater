from rest_framework import serializers
from datacollector.models import ResaleTransaction

class ResaleTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResaleTransaction
        fields= '__all__'