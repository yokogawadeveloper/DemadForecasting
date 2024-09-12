from rest_framework.response import Response
from rest_framework import status
from datas.models import MfgDataCSV, InventoryDataCSV, CpaFobDataCSV, GRListDataCSV, KdpartsDataCSV


def comparing_data(dataset, data_list, file_name, query_set):

    compared_list = []

    data_len = len(data_list)

    for i in range(data_len):
        for index, value in enumerate(dataset):
            if data_list[i] == value:
                compared_list.append(value)

    comp_list = set(compared_list)
    static_value = set(data_list)
    value = list(static_value - comp_list)

    if value:
        return Response({"value": "false",
                         "message": "{filename}.csv column header '{val}' Renamed or Column position has been changed".format(filename=file_name, val=value[0]),
                         "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
    else:
        checking_queryset(compared_list, file_name, query_set)
        return compared_list


def checking_queryset(compared_list, file_name, query_set):
    if file_name == 'manufacture':
        if query_set.exists():
            MfgDataCSV.objects.filter().update(Mfg_Status=compared_list[0], Cdd=compared_list[1],
                                               Matl_Req_Date=compared_list[2], Qty=compared_list[3],
                                               Model_Code=compared_list[4])
        else:
            MfgDataCSV.objects.filter().create(Mfg_Status=compared_list[0], Cdd=compared_list[1],
                                               Matl_Req_Date=compared_list[2], Qty=compared_list[3],
                                               Model_Code=compared_list[4])
    elif file_name == 'inventory':
        if query_set.exists():
            InventoryDataCSV.objects.filter().update(Material_No=compared_list[0], MS_Code=compared_list[1],
                                                     Stock_Qty=compared_list[2], Stock_Amt=compared_list[3])
        else:
            InventoryDataCSV.objects.filter().create(Material_No=compared_list[0], MS_Code=compared_list[1],
                                                     Stock_Qty=compared_list[2], Stock_Amt=compared_list[3])
    elif file_name == 'cpaFob':
        if query_set.exists():
            CpaFobDataCSV.objects.filter().update(PO_No=compared_list[0], YHQ_Sales=compared_list[1],
                                                  Estimated_FOB=compared_list[2], MS_Code=compared_list[3],
                                                  Qty=compared_list[4])
        else:
            CpaFobDataCSV.objects.filter().create(PO_No=compared_list[0], YHQ_Sales=compared_list[1],
                                                  Estimated_FOB=compared_list[2], MS_Code=compared_list[3],
                                                  Qty=compared_list[4])
    elif file_name == 'grList':
        if query_set.exists():
            GRListDataCSV.objects.filter().update(PO=compared_list[0], Item=compared_list[1])
        else:
            GRListDataCSV.objects.filter().create(PO=compared_list[0], Item=compared_list[1])

    elif file_name == 'kdparts':
        if query_set.exists():
            KdpartsDataCSV.objects.filter().update(PO_No=compared_list[0], SO_Item_No=compared_list[1],
                                                   Estimated_FOB=compared_list[2], MS_Code=compared_list[3],
                                                   Qty=compared_list[4])
        else:
            KdpartsDataCSV.objects.filter().create(PO_No=compared_list[0], SO_Item_No=compared_list[1],
                                                   Estimated_FOB=compared_list[2], MS_Code=compared_list[3],
                                                   Qty=compared_list[4])
    return True


def input_data(dataset, csv_filename):

    global col_data, queryset

    if csv_filename == 'manufacture':

        queryset = MfgDataCSV.objects.all()
        if queryset.exists():
            col_data = queryset.values_list('Mfg_Status', 'Cdd', 'Matl_Req_Date', 'Qty', 'Model_Code').last()
        else:
            col_data = ['MFG Status', 'CDD (mm/dd/yyyy)', 'Matl Req DATE (mm/dd/yyyy)', 'QTY', 'MODEL CODE']

    elif csv_filename == 'inventory':

        queryset = InventoryDataCSV.objects.all()
        if queryset.exists():
            col_data = queryset.values_list('Material_No', 'MS_Code', 'Stock_Qty', 'Stock_Amt').last()
        else:
            col_data = ['Material Number', 'MS Code', 'Stock Quantity', 'Stock Amount']

    elif csv_filename == 'cpaFob':

        queryset = CpaFobDataCSV.objects.all()
        if queryset.exists():
            col_data = queryset.values_list('PO_No', 'YHQ_Sales', 'Estimated_FOB', 'MS_Code', 'Qty').last()
        else:
            col_data = ['P/O  No.', 'yhq Sales Order No', 'Estimated\nFOB', 'MS Code', 'Qty']

    elif csv_filename == 'grList':

        queryset = GRListDataCSV.objects.all()
        if queryset.exists():
            col_data = queryset.values_list('PO', 'Item').last()
        else:
            col_data = ['Purchase Order', 'Item']

    elif csv_filename == 'kdparts':

        queryset = KdpartsDataCSV.objects.all()
        if queryset.exists():
            # col_data = queryset.values_list('PO_No', 'SO_Item_No', 'Estimated_FOB', 'MS_Code', 'Qty').last()
            col_data = ['P/O  No.', 'YHQ Sales Order Item No', 'Estimated\nFOB', 'MS Code', 'Qty']
        else:
            col_data = ['P/O  No.', 'YHQ Sales Order Item No', 'Estimated\nFOB', 'MS Code', 'Qty']

    csv_column_name = comparing_data(dataset, col_data, csv_filename, queryset)

    return csv_column_name




