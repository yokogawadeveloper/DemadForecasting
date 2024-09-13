import os.path
import pandas as pd
import xlrd
from datetime import date
from datetime import datetime
from wsgiref.util import FileWrapper
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .bom_explosions import main_bom_explosion
from ..serializers import *


class inventoryGraphData(APIView):
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        TodayDate = date.today()
        queryset = InventoryGraph.objects.all().order_by('date')[:25]
        # queryset = InventoryGraph.objects.filter(date__year__gte = TodayDate.year,
        # 	date__month__gte = TodayDate.month)
        serializers = InventoryGraphSerializer(queryset, many=True).data
        context = {
            'date': [d['date'] for d in serializers],
            'CPA110Y': [d['CPA110Y'] for d in serializers],
            'CPA430Y': [d['CPA430Y'] for d in serializers],
            'CPA530Y': [d['CPA530Y'] for d in serializers],
            'CPA_total': [d['CPA_total'] for d in serializers],
            'CPA_Cost': [d['CPA_Cost'] for d in serializers],
            'KDP_Cost': [d['KDP_Cost'] for d in serializers],
            'Total_Inventory': [d['Total_Inventory'] for d in serializers],
        }

        return Response({'context': context, 'status': status.HTTP_201_CREATED})


class ChartData(APIView):
    permission_classes = (IsAuthenticated,)

    # permission_classes = (AllowAny,)

    def get(self, request, format=None):
        file = os.path.abspath('static/finalOutput/Consolidated Output.xlsx')
        dataset = pd.read_excel(file, skiprows=2)
        names = []

        def createList(modelName):
            names.append('Total')
            Models = dataset[dataset['PART NO.'].str.contains(modelName)]
            Models = Models.loc[:, 'Current': 'End']
            End = Models['End'].sum()
            Models.drop(['Current', 'End'], axis=1, inplace=True)
            namesList = Models.columns.tolist()
            names.append(str(namesList[0] + '-' + namesList[3]))
            names.append(str(namesList[4] + '-' + namesList[7]))
            currentMonth = Models.iloc[:, 0:3].sum(axis=1).sum()
            nextMonth = Models.iloc[:, 4:7].sum(axis=1).sum()
            names.append('End')
            total = int(currentMonth) + int(nextMonth) + int(End)
            return [total, currentMonth, nextMonth, End]

        context = {
            "CPA110": createList(str('CPA110')),
            "CPA430": createList(str('CPA430')),
            "CPA530": createList(str('CPA530')),
            "names": names[0:4],
        }
        if context:
            return Response({'context': context, 'status': status.HTTP_201_CREATED})
        return Response({'message': 'No data for chart', 'status': status.HTTP_400_BAD_REQUEST}, status=400)


class DownloadStaticFiles(APIView):
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        excelFiles = ['thresholdQty', 'customerWiseData', 'growthRate', 'industryWiseData']
        if request.GET.get('name') in excelFiles:
            name = request.GET.get('name') + '.xlsx'
        else:
            name = request.GET.get('name') + '.csv'
        zip_file = open('static/' + name, 'rb')
        response = HttpResponse(FileWrapper(zip_file), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % name
        return response


class Alert(APIView):
    permission_classes = (IsAuthenticated,)

    # permission_classes = (AllowAny,)

    def get(self, request, format=None):
        wb = xlrd.open_workbook('static/finalOutput/alert.xlsx')
        sheet = wb.sheet_by_index(0)
        sheet.cell_value(1, 0)
        data = []
        for val in range(1, sheet.nrows):
            '''
			Remove the zeros from alert table
			'''
            if sheet.cell_value(val, 2) == 0:
                continue
            else:
                dictVal = {'partNo': sheet.cell_value(val, 1), 'alert': sheet.cell_value(val, 2)}
                data.append(dictVal)
        if data:
            return Response(data, status=200)
        return Response({'message': 'No data available for alert', 'status': status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST)


class DatesOfInputfiles(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        file = os.path.abspath('static/inputFiles/')
        context = {}
        context['manufacture'] = datetime.fromtimestamp(os.path.getmtime(file + '/manufacture.csv')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        context['cpaFob'] = datetime.fromtimestamp(os.path.getmtime(file + '/cpaFob.csv')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        context['grList'] = datetime.fromtimestamp(os.path.getmtime(file + '/grList.csv')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        context['inventory'] = datetime.fromtimestamp(os.path.getmtime(file + '/inventory.csv')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        context['kdParts'] = datetime.fromtimestamp(os.path.getmtime(file + '/kdParts.csv')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        if context:
            return Response(context, status=200)
        return Response({'message': 'Files may be missing', 'status': status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST)


class DatesOfStaticfiles(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        file = os.path.abspath('static/')
        context = {}
        context['LeadTimeCategoryPrice'] = datetime.fromtimestamp(
            os.path.getmtime(file + '/LeadTimeCategoryPrice.csv')).strftime("%m/%d/%Y, %H:%M:%S")
        context['final110e430e'] = datetime.fromtimestamp(os.path.getmtime(file + '/final110e430e.csv')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        context['final530e'] = datetime.fromtimestamp(os.path.getmtime(file + '/final530e.csv')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        context['finalPrediction'] = datetime.fromtimestamp(os.path.getmtime(file + '/finalPrediction.csv')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        context['option110'] = datetime.fromtimestamp(os.path.getmtime(file + '/option110.csv')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        context['option530'] = datetime.fromtimestamp(os.path.getmtime(file + '/option530.csv')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        context['thresholdQty'] = datetime.fromtimestamp(os.path.getmtime(file + '/thresholdQty.xlsx')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        context['unwanted'] = datetime.fromtimestamp(os.path.getmtime(file + '/unwanted.csv')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        context['growthRate'] = datetime.fromtimestamp(os.path.getmtime(file + '/growthRate.xlsx')).strftime(
            "%m/%d/%Y, %H:%M:%S")
        context['customerWiseData'] = datetime.fromtimestamp(
            os.path.getmtime(file + '/customerWiseData.xlsx')).strftime("%m/%d/%Y, %H:%M:%S")
        if context:
            return Response(context, status=200)
        return Response({'message': 'Files may be missing', 'status': status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST)


class KanbanData(APIView):
    permission_classes = (IsAuthenticated,)

    # permission_classes = (AllowAny,)

    def get(self, request):
        file = os.path.abspath('static/finalOutput/kanban.xlsx')
        dataset = pd.read_excel(file)[['PART NO.', 'No. of kanbans', 'Dropped', 'Ordered']]
        dataset[['No. of kanbans', 'Dropped', 'Ordered']].astype(int)
        context = {}
        for i, row in dataset.iterrows():
            ''' 
			If the stock gets negative value, then the dropped value will be added to ordered
			'''
            stock = row[1] - row[2]
            if stock < 0:
                context[row[0]] = [0, row[2], abs(row[3] + stock)]
            else:
                context[row[0]] = [abs(stock), abs(row[2]), abs(row[3])]
        return Response(context, status=200)


class CPAStokeChartData(APIView):
    permission_classes = (IsAuthenticated,)

    # permission_classes = (AllowAny,)

    def get(self, request, format=None):
        file = os.path.abspath('static/finalOutput/Consolidated Output.xlsx')
        dataset = pd.read_excel(file, skiprows=2)
        context = {}

        def createListPending(modelName):
            Models = dataset[dataset['PART NO.'].str.contains(modelName)]
            Models = Models.loc[:, 'Current': 'End']
            End = Models['End'].sum()
            Models.drop(['Current', 'End'], axis=1, inplace=True)
            namesList = Models.columns.tolist()
            currentMonth = Models.iloc[:, 0:3].sum(axis=1).sum()
            nextMonth = Models.iloc[:, 4:7].sum(axis=1).sum()
            total = int(currentMonth) + int(nextMonth) + int(End)
            return [0, total, 0, currentMonth, 0, nextMonth, 0, End]

        context['EJA110'] = createListPending(str('CPA110'))
        context['EJA430'] = createListPending(str('CPA430'))
        context['EJA530'] = createListPending(str('CPA530'))
        columns = ['PART NO.', 'Current', 'Stock Qty'] + dataset.columns.tolist()[16:26]
        names = ['Total', str(columns[4]) + '-' + str(columns[7]), str(columns[8]) + '-' + str(columns[11]), 'End']
        dataset = dataset[columns]

        def createList(modelName):
            Models = dataset[dataset['PART NO.'].str.contains(modelName)]
            totalStockQTy = Models['Stock Qty'].sum()
            totalPipelineQTy = Models['Pipeline Total'].sum()
            currentStockQty = Models['Current'].sum()
            Models = Models.loc[:, 'Pipeline Total': 'Pipeline Onwards']
            currentPipeline = Models.iloc[:, 1:5].sum(axis=1).sum()
            nextPipeline = Models.iloc[:, 5:8].sum(axis=1).sum()
            endPipeline = Models['Pipeline Onwards'].sum()
            context['EJA' + modelName[3:]][4] = nextPipeline
            context['EJA' + modelName[3:]][-2] = endPipeline
            context['EJA' + modelName[3:] + 'STOCK'] = [totalStockQTy, 0, currentStockQty]
            context['EJA' + modelName[3:] + 'PIPE'] = [totalPipelineQTy, 0, currentPipeline]
            return context

        createList(str('CPA110'))
        createList(str('CPA430'))
        createList(str('CPA530'))
        if context:
            return Response({'context': context, 'status': status.HTTP_201_CREATED})
        return Response({'message': 'No data for chart', 'status': status.HTTP_400_BAD_REQUEST}, status=400)


# Code Break API
class BomExplosion(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        dataset = pd.read_excel(request.FILES['modelFile'])
        try:
            code = list(dataset['MSCODE'])
            model_qty = list(dataset['QTY'])
            final = pd.DataFrame()
            for i in range(len(code)):
                d1 = main_bom_explosion(code[i], model_qty[i])   # calling main bom explosion
                final = final.append(d1, ignore_index=True)
            # sum of part no and qty in Final QTY
            final['Final_Qty'] = final.groupby(['PART NO.'])['QTY'].transform('sum')
            final = final.drop_duplicates(subset=['PART NO.'])
            final = final[["PART NO.", "PART NAME", "Final_Qty"]]
            final.to_excel('static/finalOutput/listOfQty.xlsx')
            return Response({'message': 'Successful', 'status': status.HTTP_200_OK}, status=200)
        except Exception as e:
            return Response({'message': repr(e), 'status': status.HTTP_400_BAD_REQUEST})
