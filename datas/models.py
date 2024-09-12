from django.db import models
from datetime import date


class inputFromUi(models.Model):
	threshold = models.IntegerField()
	pipelineWeek = models.IntegerField(default=0)
	requiredWeek = models.IntegerField(default=0)
	inventoryTarget = models.IntegerField(default=0)


class SectorWise(models.Model):
	consumedQty = models.IntegerField()
	projectedQty = models.IntegerField()

	def __str__(self):
		return str(self.consumedQty)


class InventoryGraph(models.Model):
	date = models.DateField(default=date.today, unique=True)
	CPA110Y = models.IntegerField(blank=True, null=True, default=0)
	CPA430Y = models.IntegerField(blank=True, null=True, default=0)
	CPA530Y = models.IntegerField(blank=True, null=True, default=0)
	CPA_total = models.IntegerField(blank=True, null=True, default=0)
	CPA_Cost = models.FloatField(null=True, blank=True, default=0)
	KDP_Cost = models.FloatField(null=True, blank=True, default=0)
	Total_Inventory = models.FloatField(null=True, blank=True, default=0)
	CPA_Receipt = models.IntegerField(blank=True, null=True, default=0)

	def __str__(self):
		return str(self.date)


# CSV column names insert into below tables

class MfgDataCSV(models.Model):
	Mfg_Status = models.CharField(max_length=100, null=True)
	Cdd = models.CharField(max_length=100, null=True)
	Matl_Req_Date = models.CharField(max_length=100, null=True)
	Qty = models.CharField(max_length=100, null=True)
	Model_Code = models.CharField(max_length=100, null=True)
	Date = models.DateField(default=date.today)


class InventoryDataCSV(models.Model):
	Material_No = models.CharField(max_length=100, null=True)
	MS_Code = models.CharField(max_length=100, null=True)
	Stock_Qty = models.CharField(max_length=100, null=True)
	Stock_Amt = models.CharField(max_length=100, null=True)
	Date = models.DateField(default=date.today)


class CpaFobDataCSV(models.Model):
	PO_No = models.CharField(max_length=100, null=True)
	YHQ_Sales = models.CharField(max_length=100, null=True)
	Estimated_FOB = models.CharField(max_length=100, null=True)
	MS_Code = models.CharField(max_length=100, null=True)
	Qty = models.CharField(max_length=100, null=True)
	Date = models.DateField(default=date.today)


class GRListDataCSV(models.Model):
	PO = models.CharField(max_length=100, null=True)
	Item = models.CharField(max_length=100, null=True)
	Date = models.DateField(default=date.today)


class KdpartsDataCSV(models.Model):
	PO_No = models.CharField(max_length=100, null=True)
	SO_Item_No = models.CharField(max_length=100, null=True)
	Estimated_FOB = models.CharField(max_length=100, null=True)
	MS_Code = models.CharField(max_length=100, null=True)
	Qty = models.CharField(max_length=100, null=True)
	Date = models.DateField(default=date.today)
