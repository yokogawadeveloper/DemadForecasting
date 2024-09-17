import numpy as np
import os.path
import pandas as pd
import smtplib
from datetime import datetime as dt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from wsgiref.util import FileWrapper

from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.commonFunc import input_data
from kd.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, TO_RECEIVER, CC_RECEIVER
from ..serializers import *
from .input_explosion import missing_weeks
from .reference import manufacturing, inventory, cpa_fob, gr_list


class DownloadData(APIView):
    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        name = request.GET.get('name') + '.xlsx'
        zip_file = open('static/finalOutput/' + name, 'rb')
        response = HttpResponse(FileWrapper(zip_file), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % name
        return response


class StaticFileUpload(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        dictval = request.FILES
        if dictval:
            for file in dictval:
                if file == 'thresholdQty':
                    file_name = default_storage.delete(os.path.abspath('static/{}.xlsx'.format(file)))
                    file_name = default_storage.save(os.path.abspath('static/{}.xlsx'.format(file)), dictval[file])
                else:
                    file_name = default_storage.delete(os.path.abspath('static/{}.csv'.format(file)))
                    file_name = default_storage.save(os.path.abspath('static/{}.csv'.format(file)), dictval[file])
            return Response({'message': 'File stored', 'status': status.HTTP_201_CREATED},
                            status=status.HTTP_201_CREATED)
        return Response({'message': 'Check the files', 'status': status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST)


class DataCrud(APIView):
    permission_classes = (IsAuthenticated,)

    def alertMail(data, request):
        email = [TO_RECEIVER, ]
        cc = [CC_RECEIVER]
        html_data = data.to_html()
        message = render_to_string('alertMail.html', {
            'alertData': html_data,
        })

        msg = MIMEMultipart()
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = ', '.join(email)
        msg['Cc'] = ', '.join(cc)
        msg['Subject'] = "Alert for CPA parts."
        msg.attach(MIMEText(message, 'html'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        toEmail = email
        server.ehlo()
        server.sendmail(msg['From'], toEmail, msg.as_string())
        server.quit()

    def get(self, request, format=None):
        data = inputFromUi.objects.all()
        if not data.exists():
            return Response({'value': 'false', 'message': 'No data available'})
        else:
            queryset = inputFromUi.objects.latest('id')
            serializer = ThresholdSerializer(queryset).data
            return Response(serializer, status=200)
        return Response({'message': 'Bad request', 'status': status.HTTP_400_BAD_REQUEST},
                        status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        path = os.path.abspath('static/outputFiles')
        if True:
            for file in request.FILES:
                file_name = default_storage.delete(os.path.abspath('static/inputFiles/{}.csv'.format(file)))
                file_name = default_storage.save(os.path.abspath('static/inputFiles/{}.csv'.format(file)),request.FILES[file])

            thresholdValue = int(request.data['threshold'])
            pipeline_week_user = int(request.data['pipelineWeek'])
            required_week_user = int(request.data['requiredWeek'])
            queryset = inputFromUi.objects.all()
            if not queryset.exists():
                inputFromUi.objects.filter().create(threshold=thresholdValue, pipelineWeek=pipeline_week_user,requiredWeek=required_week_user)
            else:
                inputFromUi.objects.filter().update(threshold=thresholdValue, pipelineWeek=pipeline_week_user,requiredWeek=required_week_user)

            pd.options.mode.chained_assignment = None  # default='warn'
            #--------------------------------- Files with path ------------------------------------------#
            manufacturing_file = os.path.abspath('static/inputFiles/manufacture.csv')
            inventory_file = os.path.abspath('static/inputFiles/inventory.csv')
            cpa_fob_file = os.path.abspath('static/inputFiles/cpaFob.csv')
            gr_list_file = os.path.abspath('static/inputFiles/grList.csv')

            # ------------------------------- Start Manufacturing ---------------------------------------#
            try:
                proc_list = manufacturing(file=manufacturing_file)
            except Exception as e:
                return Response({'message': f'Error processing manufacturing file: {str(e)}'}, status=500)

            #------------------------------- Start Inventory ---------------------------------------#
            try:
                inv_list = inventory(inventory_file)
            except Exception as e:
                return Response({'message': f'Error processing inventory file: {str(e)}'}, status=500)
            #-------------------------------- Start CPA FOB -----------------------------#
            try:
                cpa_list = cpa_fob(cpa_fob_file)
            except Exception as e:
                return Response({'message': f'Error processing CAP FOB file: {str(e)}'}, status=500)
            # -------------------------------- Start GR List -----------------------------#
            try:
                final_cpa = gr_list(gr_list_file, cpa_list)
            except Exception as e:
                return Response({'message': f'Error processing CAP FOB file: {str(e)}'}, status=500)
            # -------------------------------- Start KD Parts -----------------------------#
            kdparts_list = pd.read_csv(os.path.abspath('static/inputFiles/kdParts.csv'), low_memory=False,encoding='unicode_escape')
            kdparts_col = list(kdparts_list.columns)
            kdparts_dataset = input_data(kdparts_col, 'kdparts')

            if not isinstance(kdparts_dataset, list):
                if kdparts_dataset.status_code == 400:
                    data = kdparts_dataset.data
                    return Response(data)

            kdparts_list = kdparts_list[
                [kdparts_dataset[0], kdparts_dataset[1], kdparts_dataset[2], kdparts_dataset[3], kdparts_dataset[4]]]
            kdparts_list = kdparts_list.rename(index=str, columns={kdparts_dataset[0]: "Purchase_Order",
                                                                   kdparts_dataset[1]: "Item"})
            kdparts_list['Purchase_Order'] = kdparts_list['Purchase_Order'].astype(str)
            kdparts_list = kdparts_list[kdparts_list['Purchase_Order'].str.startswith('4')]
            kdparts_list[kdparts_dataset[2]] = kdparts_list[kdparts_dataset[2]].astype('datetime64[ns]')
            final_kdparts = kdparts_list.merge(gr_list, on=['Purchase_Order', 'Item'], how='left', indicator=True)
            final_kdparts = final_kdparts[final_kdparts['_merge'] == 'left_only']
            pipeline_list = final_cpa.append(final_kdparts, ignore_index=True)
            pipeline_list[kdparts_dataset[2]] = pipeline_list[kdparts_dataset[2]].astype('datetime64[ns]')
            pipeline_list['Final_Date'] = pipeline_list[kdparts_dataset[2]] + pd.DateOffset(days=12)
            pipeline_list['Week_Number'] = pipeline_list['Final_Date'].dt.week
            pipeline_list['Final_Year'] = pipeline_list['Final_Date'].dt.year
            current_year = dt.date(dt.now()).year
            pipeline_list.loc[pipeline_list.Final_Year < current_year, 'Week_Number'] = 1
            pipeline_list.loc[pipeline_list.Final_Year == current_year + 1, 'Week_Number'] += 52
            pipeline_list.loc[pipeline_list.Final_Year == current_year + 2, 'Week_Number'] += 104
            pipeline_list = pipeline_list.sort_values(by=['Week_Number'])
            pipeline_list = pipeline_list.rename(index=str, columns={"MS Code": "PART NO.", "Qty": "QTY"})
            pipeline_list = pipeline_list[["PART NO.", "QTY", "Week_Number"]]
            pipeline_list['Discrepancy'] = 0
            pipeline_list['QTY'] = pipeline_list.groupby(['PART NO.', 'Week_Number'])['QTY'].transform('sum')
            pipeline_list.drop_duplicates(subset=['PART NO.', 'Week_Number'])
            pipeline_list.loc[pipeline_list['Week_Number'] <= dt.today().isocalendar()[1], 'Discrepancy'] = 1
            pipeline_list = pipeline_list.pivot_table("QTY", ["PART NO.", "Discrepancy"], "Week_Number")
            pipeline_list = pipeline_list.reset_index()
            current_week = dt.today().isocalendar()[1]
            columns_list = pipeline_list.columns.tolist()[2:]
            column_begin = [x for x in columns_list if x < current_week]
            individual_columns = list()
            for x in range(len(column_begin), len(columns_list)):
                individual_columns.append(columns_list[x])
                if (len(individual_columns) >= 8): break;

            individual_columns = missing_weeks(individual_columns)
            # individual_columns = sorted(individual_columns)[:8]
            column_end = [i for i in columns_list if i > individual_columns[len(individual_columns) - 1]]
            pipeline_list['Pipeline Total'] = pipeline_list[columns_list].sum(axis=1)
            pipeline_list['Pipeline Onwards'] = pipeline_list[column_end].sum(axis=1)

            try:
                pipe_list = pipeline_list[
                    ['PART NO.', 'Discrepancy', 'Pipeline Total'] + individual_columns + ['Pipeline Onwards']]
            except KeyError as e:
                for x in individual_columns:
                    if x not in pipeline_list.columns:
                        pipeline_list[x] = 0
                pipe_list = pipeline_list[
                    ['PART NO.', 'Discrepancy', 'Pipeline Total'] + individual_columns + ['Pipeline Onwards']]

            lead_time_price = pd.read_csv(os.path.abspath('static/LeadTimeCategoryPrice.csv'))
            # lead_time = pd.read_csv(os.path.abspath('static/leadTime.csv'))
            # lead_time = lead_time.rename(index=str, columns={"Part No.": "PART NO."})
            lead_time_price["MOQ"] = 1
            final = pd.merge(proc_list, inv_list[['PART NO.', 'Stock Qty']], on=['PART NO.'], how='left')
            final = pd.merge(final, pipe_list, on=['PART NO.'], how='left')
            final = pd.merge(final, lead_time_price[['PART NO.', 'Lead Time', 'MOQ']], on=['PART NO.'], how='left')

            cols = final.columns.tolist()
            cols = cols[0:2] + cols[len(cols) - 2:len(cols)] + cols[2:len(cols) - 2]
            cols = [val for val in cols if not str(val).endswith("_x") if not str(val).endswith("_y")]
            final = final[cols]

            final['Pipeline Total'] = final['Pipeline Total'].fillna(0)
            final['Stock Qty'] = final['Stock Qty'].fillna(0)

            final['Total Available'] = final['Stock Qty'] + final['Pipeline Total']

            final['Difference'] = final['Total Available'] - final['Total Required']
            cpa_leadtime = lead_time_price
            final = pd.merge(final, cpa_leadtime[['PART NO.', 'Lead Time']], on=['PART NO.'], how='left')
            final['Lead Time_x'] = final['Lead Time_y'].fillna(final['Lead Time_x'])
            final.drop('Lead Time_y', axis=1, inplace=True)
            final = final.rename(index=str, columns={"Lead Time_x": "Lead Time"})
            final['Lead Time'].fillna(50, inplace=True)
            final['Estimated Delivery Week'] = final['Lead Time'] / 7 + current_week
            final = final.astype({"Estimated Delivery Week": int})

            # price_category = pd.read_csv((os.path.abspath('static/categoryPrice.csv')))
            price_category = lead_time_price

            final = pd.merge(final, price_category[['PART NO.', 'Std. Price', 'Category']], on=['PART NO.'], how='left')

            final["Std. Price"] = final["Std. Price"].astype(float)
            final["Total Cost"] = final['Difference'] * final['Std. Price']

            cols = list(final.columns)

            pipeline_columns = cols[cols.index('Pipeline Total') + 1:cols.index('Pipeline Onwards')]

            pipeline_columns = [int(i) for i in pipeline_columns]

            discrepancy = final[final['Discrepancy'] == 1]

            discrepancy = discrepancy.drop(['Discrepancy'], axis=1)

            writer = pd.ExcelWriter(os.path.join(path, r'Discrepancy.xlsx'), engine='xlsxwriter')
            discrepancy.to_excel(writer, sheet_name='Sheet1')
            writer.save()
            final['sum'] = discrepancy.iloc[:, 5:13].sum(axis=1)
            final[final.columns[18]] = final[[final.columns[18], 'sum']].sum(axis=1)
            final = final.drop(['sum'], axis=1)

            discrepancy = discrepancy[['PART NO.', 'PART NAME', 'Pipeline Total']]
            Category = final[['Category', 'PART NO.']]
            final = final.drop_duplicates(subset=['PART NO.', 'Current', 'Lead Time', 'Total Required'], keep='first',
                                          inplace=False)

            final = final.groupby(['PART NO.', 'PART NAME'], sort=False).sum().reset_index()
            final = final.merge(Category, on='PART NO.')

            # Delete the pielin columns
            # final.drop(delete_columns, axis=1, inplace=True)

            predict = pd.read_csv(os.path.abspath('static/finalPrediction.csv'))
            predict = predict[["PART NO.", "PART NAME", "Final_Qty", "Year"]]
            part_no = list(final['PART NO.'])
            # Regression Testing
            from sklearn.model_selection import train_test_split
            from sklearn.linear_model import LinearRegression
            predicted_values = list()
            for i in part_no:
                is_value = predict['PART NO.'] == i
                sub = predict[is_value]
                if not sub.empty and len(sub) > 2:
                    X = sub.iloc[:, 3:4].values
                    y = sub.iloc[:, 2].values
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)
                    regressor = LinearRegression()
                    regressor.fit(X_train, y_train)
                    predicted_values.append(int(regressor.predict([[current_year]])))
                else:
                    predicted_values.append(0)

            predict_pivot = predict.pivot_table("Final_Qty", ["PART NO.", "PART NAME"], "Year")
            predict_pivot = predict_pivot.reset_index()

            columns_list = predict_pivot.columns.tolist()
            columns_list.pop(0)
            columns_list.pop(0)

            column_begin = list()
            for i in columns_list:
                if i <= current_year - 4:
                    column_begin.append(i)
            predict_pivot.drop(column_begin, axis=1, inplace=True)
            predict_pivot.drop('PART NAME', axis=1, inplace=True)

            final = pd.merge(final, predict_pivot, on=['PART NO.'], how='left')

            final['Prediction for current year'] = predicted_values
            final['Prediction for current year'][final['Prediction for current year'] < 0] = 0
            final['Monthly Prediction'] = final['Prediction for current year'] / 12
            final = final.astype({"Monthly Prediction": int})
            Threshold_qty = pd.read_excel(os.path.abspath('static/thresholdQty.xlsx'))
            Threshold_qty = Threshold_qty[["PART NO.", "Consumption Percentage(%)"]].dropna(subset=['PART NO.'])
            Threshold_qty['Threshold'] = Threshold_qty["Consumption Percentage(%)"] * thresholdValue
            Threshold_qty = Threshold_qty.drop('Consumption Percentage(%)', axis=1)
            final = pd.merge(final, Threshold_qty, how='left', on=['PART NO.'])
            #test for alert
            indexNum_pipeline = final.columns.tolist().index('Pipeline Total')
            indexNum_required = final.columns.tolist().index('Current')
            datalist_pipeline = final.iloc[:, indexNum_pipeline + 1:int(pipeline_week_user + 1)].fillna(0).sum(axis=1)
            pending_requirements = final.iloc[:, indexNum_required + 1:int(required_week_user + 1)].fillna(0).sum(
                axis=1)
            stock_status = final['Stock Qty'] + datalist_pipeline

            def createAlert(pending_requirements, stock_status, threshold):
                final['alert'] = False
                final['value'] = False

                df = pd.DataFrame(
                    {'requirements': pending_requirements, 'stock_status': stock_status, 'threshold': threshold,
                     'alert': False, 'value': False}).fillna(0)
                final['alert'][
                    (df['stock_status'] >= df['threshold']) & (df['stock_status'] >= df['requirements'])] = False
                final['alert'][(df['stock_status'] < df['threshold']) & (df['stock_status'] < df['requirements']) & (
                        df['threshold'] < df['requirements'])] = 'ORANGE'
                final['alert'][
                    (df['stock_status'] <= df['threshold']) & (df['stock_status'] >= df['requirements'])] = 'BLUE'
                final['alert'][
                    (df['stock_status'] >= df['threshold']) & (df['stock_status'] <= df['requirements'])] = 'RED'

                final['value'][
                    (df['stock_status'] >= df['threshold']) & (df['stock_status'] >= df['requirements'])] = False
                final['value'][(df['stock_status'] < df['threshold']) & (df['stock_status'] < df['requirements']) & (
                        df['threshold'] < df['requirements'])] = df['threshold'] - df['stock_status']  #orange
                final['value'][(df['stock_status'] <= df['threshold']) & (df['stock_status'] >= df['requirements'])] = \
                    df['threshold'] - df['stock_status']  #blue
                final['value'][(df['stock_status'] >= df['threshold']) & (df['stock_status'] <= df['requirements'])] = \
                    df['requirements'] - df['stock_status']  #red
                del df

            createAlert(pending_requirements, stock_status, final['Threshold'])

            alert = final[final['alert'] != False]
            alert = alert[['PART NO.', 'value', 'alert']]
            alert['value'] = alert['value'].abs().apply(np.ceil)
            alert = alert.drop_duplicates(keep='first', inplace=False)
            writer = pd.ExcelWriter(os.path.join(path, r'alert.xlsx'), engine='xlsxwriter')
            number_rows = len(alert.index) + 1
            alert.to_excel(writer, sheet_name='Sheet1')
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            worksheet.conditional_format("$A$1:$D$%d" % (number_rows),
                                         {"type": "formula",
                                          "criteria": '=INDIRECT("D"&ROW())="BLUE"',
                                          "format": workbook.add_format({'bg_color': '#00CCFF', 'border': 1})
                                          })
            worksheet.conditional_format("$A$1:$D$%d" % (number_rows),
                                         {"type": "formula",
                                          "criteria": '=INDIRECT("D"&ROW())="ORANGE"',
                                          "format": workbook.add_format({'bg_color': '#FF9900', 'border': 1})
                                          })
            worksheet.conditional_format("$A$1:$D$%d" % (number_rows),
                                         {"type": "formula",
                                          "criteria": '=INDIRECT("D"&ROW())="RED"',
                                          "format": workbook.add_format({'bg_color': '#993300', 'border': 1})
                                          })
            worksheet.set_column('D:D', None, None, {'hidden': 1})
            workbook.close()
            alert = alert.drop(['alert'], axis=1)
            alert = alert[alert['value'] != 0]
            if not alert.empty:
                DataCrud.alertMail(alert, request)

            kanban = final
            cols = final.columns.tolist()
            cols.insert(-1, cols.pop(cols.index('Discrepancy')))
            final = final.reindex(columns=cols)
            final = final.drop(['alert', 'value', 'MOQ'], axis=1)
            final = final.replace(np.nan, 0)
            final = final.drop_duplicates(keep='first', inplace=False)
            # final['pipelinePlusconsolidatedWeek'] = final['PART NO.'].map(discrepancy.set_index('PART NO.')['Pipeline Total']).fillna(0)
            final['pipelinePlusconsolidatedWeek'] = final['PART NO.'].map(discrepancy['Pipeline Total']).fillna(0)
            pieLineTotalNextWeek = final.columns.tolist().index('Pipeline Total')
            final[final.columns[pieLineTotalNextWeek + 1]] = final['pipelinePlusconsolidatedWeek'] + final[
                final.columns[pieLineTotalNextWeek + 1]]
            writer_object = pd.ExcelWriter(os.path.join(path, r'Consolidated Output.xlsx'), engine='xlsxwriter')
            headerList = list(final)
            for x in range(len(headerList)):
                if headerList[x] == "Current":
                    i = x + 1
                if headerList[x] == "Total Required":
                    j = x + 1
                if headerList[x] == "Pipeline Total":
                    k = x + 1
                if headerList[x] == "Pipeline Onwards":
                    l = x + 1
                if headerList[x] == "Total Available":
                    m = x + 1
                if headerList[x] == "Difference":
                    n = x + 1
                if headerList[x] == "Total Cost":
                    o = x + 2
                if headerList[x] == "Prediction for current year":
                    p = x
                    q = x + 1
                if headerList[x] == "Monthly Prediction":
                    r = x + 1
                else:
                    continue;

            final.to_excel(writer_object, sheet_name='Sheet1', startrow=2,
                           header=True)  #final replace with any other dataframe

            workbook_object = writer_object.book
            worksheet_object = writer_object.sheets['Sheet1']
            worksheet_object.activate()

            worksheet_object.set_row(1, 50)
            worksheet_object.set_row(0, 50)
            worksheet_object.set_row(2, 30)
            worksheet_object.set_column('AL:AL', None, None, {'hidden': 1})
            merge_format = workbook_object.add_format(
                {'bold': 2, 'border': 1, 'font_size': 20, 'align': 'center', 'valign': 'vcenter'})
            worksheet_object.merge_range(0, 0, 0, r + 1, 'Ordering Status', merge_format)
            worksheet_object.merge_range(1, 0, 1, i - 2, '  ', merge_format)
            worksheet_object.merge_range(1, i, 1, j, 'Pending Requirement', merge_format)
            worksheet_object.merge_range(1, k + 1, 1, l, 'Pipeline Status', merge_format)
            worksheet_object.merge_range(1, m + 1, 1, n + 1, 'Parts Status', merge_format)
            worksheet_object.merge_range(1, o + 1, 1, p, 'History', merge_format)
            worksheet_object.merge_range(1, q, 1, r, 'Prediction', merge_format)

            week = workbook_object.add_format({
                'bg_color': '#FFFFFF',
                'border': 1
            })
            pipeline = workbook_object.add_format({
                'bg_color': '#FFFFFF',
                'border': 1
            })
            partstatus = workbook_object.add_format({
                'bg_color': '#FFFFFF',
                'border': 1
            })
            history = workbook_object.add_format({
                'bg_color': '#FFFFFF',
                'border': 1
            })
            prediction = workbook_object.add_format({
                'bg_color': '#FFFFFF',
                'border': 1
            })

            format_green = workbook_object.add_format({'bg_color': '#FFFFFF', 'border': 1})

            worksheet_object.set_column(i, j, 10, week)
            worksheet_object.set_column(k + 1, l, 10, pipeline)
            worksheet_object.set_column(m + 1, n + 1, 10, partstatus)
            worksheet_object.set_column(o + 1, p, 10, history)
            worksheet_object.set_column(q, r, 10, prediction)

            worksheet_object.conditional_format('A4:AK1000', {'type': 'formula',
                                                              'criteria': '=$AL4>0.0',
                                                              'format': format_green})

            worksheet_object.conditional_format('A4:AK1000', {'type': 'no_blanks', 'format': format_green})

            writer_object.save()
            final = kanban
            final = final[['PART NO.', 'Stock Qty', 'Pipeline Total']]
            Threshold_qty = pd.read_excel(os.path.abspath('static/thresholdQty.xlsx'))
            Threshold_qty = Threshold_qty[
                ['Kanban Qty', 'No. of kanbans', "Kanban Qty * No' of Kanbans", 'PART NO.']].dropna()
            final = pd.merge(final, Threshold_qty, how='left', on=["PART NO."]).dropna()
            del Threshold_qty
            final['Stock Total at present'] = final['Stock Qty'] + final['Pipeline Total']
            final['Dropped'] = (
                    (final["Kanban Qty * No' of Kanbans"] - final['Stock Qty']) / final['Kanban Qty']).apply(
                np.ceil).apply(abs)
            final['Ordered'] = (final["Pipeline Total"] / final['Kanban Qty']).apply(np.ceil).apply(abs)

            lessQty = final.loc[final['Stock Total at present'] < final["Kanban Qty * No' of Kanbans"]]
            moreQty = final.loc[final['Stock Total at present'] > final["Kanban Qty * No' of Kanbans"]]

            final = lessQty.append(moreQty, ignore_index=True)
            final = final.drop_duplicates(subset=['PART NO.']).fillna(0)
            final = final.replace([np.inf, -np.inf], np.nan).dropna(how='any')
            final = final.loc[final['Dropped'] != final["Ordered"]]
            final.to_excel(os.path.abspath('static/finalOutput/kanban.xlsx'))
            if not final.empty:
                DataCrud.alertMail(final, request)
            writer.save()
            return Response("file Upload successful", status=status.HTTP_201_CREATED)
