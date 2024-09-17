import pandas as pd
import os
from common.commonFunc import input_data
from rest_framework.response import Response
from datetime import datetime as dt
from .input_explosion import input_bom_explosion, missing_weeks
from ..models import InventoryGraph
from ..serializers import InventoryGraphSerializer


def manufacturing(file):
    mfg_list = pd.read_csv(file, low_memory=False, encoding='unicode_escape')
    mfg_list_col = list(mfg_list.columns)
    mfg_dataset = input_data(mfg_list_col, 'manufacture')

    if not isinstance(mfg_dataset, list):
        if mfg_dataset.status_code == 400:
            data = mfg_dataset.data
            return Response(data)

    mfg_list = mfg_list.loc[mfg_list[mfg_dataset[0]].isin(['MC Awtd', 'Forecast', 'MC Recd', 'MC awtd', 'Sch.'])]
    mfg_list[mfg_dataset[1]] = mfg_list[mfg_dataset[1]].astype('datetime64[ns]')
    mfg_list[mfg_dataset[2]] = mfg_list[mfg_dataset[2]].astype('datetime64[ns]')
    mfg_list['CDD_Year'] = mfg_list[mfg_dataset[1]].dt.year
    mfg_list['Matl_Req_Year'] = mfg_list[mfg_dataset[2]].dt.year
    current_year = dt.date(dt.now()).year
    mfg_list['CDD_Week_Number'] = mfg_list[mfg_dataset[1]].dt.week
    mfg_list['Matl_Req_Week_Number'] = mfg_list[mfg_dataset[2]].dt.week
    mfg_list.loc[mfg_list.CDD_Year < current_year, 'CDD_Week_Number'] = 1
    mfg_list.loc[mfg_list.CDD_Year == current_year + 1, 'CDD_Week_Number'] += 52
    mfg_list.loc[mfg_list.Matl_Req_Year < current_year, 'Matl_Req_Week_Number'] = 1
    mfg_list.loc[mfg_list.Matl_Req_Year == current_year + 1, 'Matl_Req_Week_Number'] += 52
    mfg_list['Final_Week'] = mfg_list['Matl_Req_Week_Number'].fillna(mfg_list['CDD_Week_Number'])
    mfg_list['Final_Week'] = mfg_list.Final_Week.fillna(0).astype(int)
    mfg_list[mfg_dataset[3]] = mfg_list.QTY.astype(int)
    mfg_list = mfg_list.sort_values(by=['Final_Week'])
    mfg_list['Final_Qty'] = mfg_list.groupby([mfg_dataset[4], 'Final_Week'])[mfg_dataset[3]].transform('sum')
    mfg_list = mfg_list.drop_duplicates(subset=[mfg_dataset[4], 'Final_Week'])
    model_df = mfg_list[[mfg_dataset[4], 'Final_Week', 'Final_Qty']]
    model_df = model_df.pivot_table("Final_Qty", [mfg_dataset[4]], "Final_Week")
    column_list = model_df.columns.tolist()
    model_df['Total'] = model_df[column_list].sum(axis=1)
    path = 'static/finalOutput'
    writer = pd.ExcelWriter(os.path.join(path, r'View_1.xlsx'), engine='xlsxwriter')
    model_df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    found = mfg_list[mfg_list[mfg_dataset[4]].str.contains('Z')]
    mfg_list = mfg_list[~mfg_list[mfg_dataset[4]].str.contains('Z')]
    writer = pd.ExcelWriter(os.path.join(path, r'Tokuchu.xlsx'), engine='xlsxwriter')
    found.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    code = list(mfg_list[mfg_dataset[4]])
    model_qty = list(mfg_list['Final_Qty'])
    week = list(mfg_list['Final_Week'])

    # calling input bom explosion start
    proc_list = pd.DataFrame()
    for i in range(len(model_qty)):
        d1 = input_bom_explosion(code[i], model_qty[i], week[i])
        proc_list = proc_list.append(d1, ignore_index=True)
    # end input bom explosion
    proc_list['Final_Qty'] = proc_list.groupby(['PART NO.', 'Week'])['QTY'].transform('sum')
    proc_list = proc_list.drop_duplicates(subset=['PART NO.', 'Week'])
    proc_list = proc_list.pivot_table("Final_Qty", ["PART NO.", "PART NAME"], "Week")
    proc_list = proc_list.reset_index()
    current_week = dt.today().isocalendar()[1]
    columns_list = proc_list.columns.tolist()[2:]
    column_begin = [columns_list[i] for i in range(len(columns_list)) if columns_list[i] <= current_week]
    proc_list['Current'] = proc_list[column_begin].sum(axis=1)
    individual_columns = list()
    for x in range(len(column_begin), len(columns_list)):
        individual_columns.append(columns_list[x])
        if len(individual_columns) >= 8:
            break
    # calling missing weeks from input explosion
    individual_columns = missing_weeks(individual_columns, columns_list, proc_list)
    column_end = [i for i in columns_list if i > individual_columns[len(individual_columns) - 1]]
    proc_list['End'] = proc_list[column_end].sum(axis=1)
    proc_list['Total Required'] = proc_list[columns_list].sum(axis=1)
    proc_list = proc_list[['PART NO.', 'PART NAME'] + ['Current'] + individual_columns + ['End', 'Total Required']]
    proc_list.columns = proc_list.columns.map(str)
    return proc_list


def inventory(file):
    inv_list = pd.read_csv(file, low_memory=False, encoding='unicode_escape')
    inventory_col = list(inv_list.columns)
    inventory_dataset = input_data(inventory_col, 'inventory')

    if not isinstance(inventory_dataset, list):
        if inventory_dataset.status_code == 400:
            data = inventory_dataset.data
            return Response(data)

    inv_list['Final Parts'] = inv_list[inventory_dataset[1]].fillna(inv_list[inventory_dataset[0]])
    inv_list["Total"] = inv_list[inventory_dataset[2]].str.replace(",", "").astype(int)
    inv_list = inv_list[['Final Parts', 'Total']]
    inv_list['Stock Qty'] = inv_list.groupby(['Final Parts'])['Total'].transform('sum')
    inv_list = inv_list.drop_duplicates(subset=['Final Parts'])
    inv_list = inv_list.rename(index=str, columns={"Final Parts": "PART NO."})
    inv_list.drop('Total', axis=1, inplace=True)

    inventory = pd.read_csv(os.path.abspath('static/inputFiles/inventory.csv'), low_memory=False,
                            encoding='unicode_escape')
    inventory[inventory_dataset[3]] = inventory[inventory_dataset[3]].str.split(',').str.join('').astype(
        'float64')
    inventory[inventory_dataset[2]] = inventory[inventory_dataset[2]].str.split(',').str.join('').astype(
        'float64')
    inventory["Total stock value"] = inventory[inventory_dataset[2]] * inventory[inventory_dataset[3]]
    CPA110Y = inventory[inventory[inventory_dataset[1]].str.contains(r'CPA110Y', na=False)][
        inventory_dataset[2]].sum()
    CPA430Y = inventory[inventory[inventory_dataset[1]].str.contains(r'CPA430Y', na=False)][
        inventory_dataset[2]].sum()
    CPA530Y = inventory[inventory[inventory_dataset[1]].str.contains(r'CPA530Y', na=False)][
        inventory_dataset[2]].sum()
    CPA_Tot = CPA110Y + CPA430Y + CPA530Y
    Total_inventory = inventory["Total stock value"].sum()
    KDP_cost = inventory[~inventory[inventory_dataset[1]].str.contains('CPA', na=False)][
        "Total stock value"].sum()
    CPA_cost = Total_inventory - KDP_cost
    dataSet = {
        'CPA110Y': CPA110Y,
        'CPA430Y': CPA430Y,
        'CPA530Y': CPA530Y,
        'CPA_total': CPA_Tot,
        'CPA_Cost': round(CPA_cost, 2),
        'KDP_Cost': round(KDP_cost, 2),
        'Total_Inventory': round(Total_inventory, 2),
        # 'CPA_Receipt':
    }
    global todayData
    date_val = InventoryGraph.objects.values_list('date', flat=True).last()
    if str(date_val) != dt.today().strftime('%Y-%m-%d'):
        todayData = InventoryGraph.objects.filter(date=dt.today().strftime('%Y-%m-%d'))
    else:
        todayData = InventoryGraph.objects.get(date=dt.today().strftime('%Y-%m-%d'))

    if todayData:
        serializer = InventoryGraphSerializer(todayData, data=dataSet)
    else:
        serializer = InventoryGraphSerializer(data=dataSet)
    if serializer.is_valid():
        serializer.save()
    return inv_list


def cpa_fob(file):
    cpa_list = pd.read_csv(file, engine='python')
    cpa_col = list(cpa_list.columns)
    cpa_dataset = input_data(cpa_col, 'cpaFob')

    if not isinstance(cpa_dataset, list):
        if cpa_dataset.status_code == 400:
            data = cpa_dataset.data
            return Response(data)

    cpa_list = cpa_list[[cpa_dataset[0], cpa_dataset[1], cpa_dataset[2], cpa_dataset[3], cpa_dataset[4]]]
    cpa_list[cpa_dataset[2]] = cpa_list[cpa_dataset[2]].astype('datetime64[ns]')
    cpa_list = cpa_list.rename(index=str, columns={cpa_dataset[0]: "Purchase_Order", cpa_dataset[1]: "Item"})
    cpa_list['Purchase_Order'] = cpa_list['Purchase_Order'].astype(str)
    cpa_list = cpa_list[cpa_list['Purchase_Order'].str.startswith('4')]
    return cpa_list


def gr_list(file, cpa_list):
    gr_list = pd.read_csv(file, low_memory=False,encoding='unicode_escape')
    gr_list_col = list(gr_list.columns)
    gr_dataset = input_data(gr_list_col, 'grList')

    if not isinstance(gr_dataset, list):
        if gr_dataset.status_code == 400:
            data = gr_dataset.data
            return Response(data)

    gr_list = gr_list[[gr_dataset[0], gr_dataset[1]]]
    gr_list = gr_list.rename(index=str, columns={gr_dataset[0]: "Purchase_Order"})
    gr_list.Purchase_Order = gr_list.Purchase_Order.map(lambda x: '{:.0f}'.format(x))
    gr_list['Purchase_Order'] = gr_list['Purchase_Order'].astype(str)
    final_cpa = cpa_list.merge(gr_list, on=['Purchase_Order', gr_dataset[1]], how='left', indicator=True)
    final_cpa = final_cpa[final_cpa['_merge'] == 'left_only']
    return final_cpa
