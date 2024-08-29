from rest_framework import serializers
from .models import *


class ThresholdSerializer (serializers.ModelSerializer):
    class Meta:
        model = inputFromUi
        fields = '__all__'


class SectorWiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectorWise
        fields = '__all__'


class InventoryGraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryGraph
        fields = '__all__'