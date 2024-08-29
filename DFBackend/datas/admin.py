from django.contrib import admin
from .models import *


@admin.register(inputFromUi)
class inputFromUiAdmin(admin.ModelAdmin):
    list_display = ('id', 'threshold','pipelineWeek','requiredWeek','inventoryTarget')

@admin.register(SectorWise)
class SectorWisedAdmin(admin.ModelAdmin):
    list_display = ('id', 'consumedQty', 'projectedQty')

@admin.register(InventoryGraph)
class InventoryGraphdAdmin(admin.ModelAdmin):
    list_display = ('date', 'CPA110Y', 'CPA430Y','CPA530Y', 'CPA_total', 'CPA_Cost','KDP_Cost','Total_Inventory', 'CPA_Receipt')


admin.site.register(KdpartsDataCSV)
admin.site.register(GRListDataCSV)
admin.site.register(CpaFobDataCSV)
admin.site.register(InventoryDataCSV)