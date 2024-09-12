from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.http import HttpResponse
from django.core.files.storage import default_storage
from wsgiref.util import FileWrapper
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from datetime import datetime as dt

from common.commonFunc import input_data
from datas.models import inputFromUi
from ..serializers import *
import itertools, os.path, re, smtplib, numpy as np, pandas as pd
from smtplib import SMTP_SSL
from kd.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, TO_RECEIVER, CC_RECEIVER
from email.mime.application import MIMEApplication
from rest_framework.decorators import action

from django.core.mail import EmailMessage


class DownloadData(APIView):
	# permission_classes = (IsAuthenticated,)
	permission_classes = (AllowAny,)

	def get(self, request, format=None):
		name = request.GET.get('name')+'.xlsx'
		zip_file = open('static/finalOutput/'+name, 'rb')
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
			return Response({'message' : 'File stored', 'status' : status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
		return Response({'message':'Check the files', 'status' : status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)


class DataCrud(APIView):
	permission_classes = (IsAuthenticated,)

	def alertMail(data,request):
		email = [TO_RECEIVER,]
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
		return Response({'message': 'Bad request', 'status': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

	def post(self, request, format=None):

		# try:
		if True:
			for file in request.FILES:
				file_name = default_storage.delete(os.path.abspath('static/inputFiles/{}.csv'.format(file)))
				file_name = default_storage.save(os.path.abspath('static/inputFiles/{}.csv'.format(file)), request.FILES[file])
			thresholdValue = int(request.data['threshold'])
			pipeline_week_user = int(request.data['pipelineWeek'])
			required_week_user = int(request.data['requiredWeek'])
			queryset = inputFromUi.objects.all()
			if not queryset.exists():
				inputFromUi.objects.filter().create(threshold=thresholdValue, pipelineWeek=pipeline_week_user,
													requiredWeek=required_week_user)
			else:
				inputFromUi.objects.filter().update(threshold=thresholdValue, pipelineWeek=pipeline_week_user,
													requiredWeek=required_week_user)

			pd.options.mode.chained_assignment = None  # default='warn'
			# mfg_list = pd.read_csv(request.FILES['manufacture'], low_memory=False, encoding = 'unicode_escape')
			mfg_list = pd.read_csv(os.path.abspath('static/inputFiles/manufacture.csv'), low_memory=False, encoding = 'unicode_escape')
			# mfg_list=mfg_list[['MODEL CODE','QTY','MFG Status','CDD (mm/dd/yyyy)','Matl Req DATE (mm/dd/yyyy)']]

			mfg_list_col = list(mfg_list.columns)
			mfg_dataset = input_data(mfg_list_col, 'manufacture')

			if not isinstance(mfg_dataset, list):
				if mfg_dataset.status_code == 400:
					data = mfg_dataset.data
					return Response(data)

			mfg_list=mfg_list.loc[mfg_list[mfg_dataset[0]].isin(['MC Awtd','Forecast','MC Recd','MC awtd', 'Sch.'])]
			mfg_list[mfg_dataset[1]] = mfg_list[mfg_dataset[1]].astype('datetime64[ns]')
			mfg_list[mfg_dataset[2]] = mfg_list[mfg_dataset[2]].astype('datetime64[ns]')
			mfg_list['CDD_Year'] = mfg_list[mfg_dataset[1]].dt.year
			mfg_list['Matl_Req_Year'] = mfg_list[mfg_dataset[2]].dt.year
			current_year = dt.date(dt.now()).year
			mfg_list['CDD_Week_Number'] = mfg_list[mfg_dataset[1]].dt.week
			mfg_list['Matl_Req_Week_Number'] = mfg_list[mfg_dataset[2]].dt.week
			mfg_list.loc[mfg_list.CDD_Year < current_year, 'CDD_Week_Number'] = 1
			mfg_list.loc[mfg_list.CDD_Year == current_year+1, 'CDD_Week_Number'] += 52
			mfg_list.loc[mfg_list.Matl_Req_Year < current_year, 'Matl_Req_Week_Number'] = 1
			mfg_list.loc[mfg_list.Matl_Req_Year == current_year+1, 'Matl_Req_Week_Number'] += 52
			mfg_list['Final_Week'] = mfg_list['Matl_Req_Week_Number'].fillna(mfg_list['CDD_Week_Number'])
			mfg_list['Final_Week'] = mfg_list.Final_Week.fillna(0).astype(int)
			mfg_list[mfg_dataset[3]] = mfg_list.QTY.astype(int)
			mfg_list=mfg_list.sort_values(by=['Final_Week'])
			mfg_list['Final_Qty'] = mfg_list.groupby([mfg_dataset[4], 'Final_Week'])[mfg_dataset[3]].transform('sum')
			mfg_list = mfg_list.drop_duplicates(subset=[mfg_dataset[4],'Final_Week'])
			model_df = mfg_list[[mfg_dataset[4],'Final_Week','Final_Qty']]
			model_df = model_df.pivot_table("Final_Qty",[mfg_dataset[4]],"Final_Week")
			column_list= model_df.columns.tolist()
			model_df['Total'] = model_df[column_list].sum(axis=1)
			path = 'static/finalOutput'
			writer = pd.ExcelWriter(os.path.join(path,r'View_1.xlsx'), engine='xlsxwriter')
			model_df.to_excel(writer, sheet_name='Sheet1')
			writer.save()
			found = mfg_list[mfg_list[mfg_dataset[4]].str.contains('Z')]
			mfg_list = mfg_list[~mfg_list[mfg_dataset[4]].str.contains('Z')]
			# found.to_csv(os.path.join(path,r'Tokuchu.xlsx'))
			writer = pd.ExcelWriter(os.path.join(path,r'Tokuchu.xlsx'), engine='xlsxwriter')
			found.to_excel(writer, sheet_name='Sheet1')
			writer.save()
			code = list(mfg_list[mfg_dataset[4]])
			model_qty = list(mfg_list['Final_Qty'])
			week = list(mfg_list['Final_Week'])
			def BOM_Explosion(code, qty, week):
				model_name=code
				model_code=model_name[0:7]

				if (model_code == 'EJA530E'):
					model_name=model_name[8:12]+model_name[15:19]
					dataset = pd.read_csv(os.path.abspath('static/final530e.csv'))
					options = pd.read_csv(os.path.abspath('static/option530.csv'))     #Upload separate options file
				else:
					model_name=model_name[8:13]+model_name[14:19]
					dataset=pd.read_csv(os.path.abspath('static/final110e430e.csv'))
					options = pd.read_csv(os.path.abspath('static/option110.csv'))

				dataset = dataset.loc[dataset['SC'] != 1.0]
				pattern = [model_code,'EJA530?']
				pattern = '|'.join(pattern)
				d1=dataset.loc[dataset.loc[:,'MODEL CODE'].str.contains(pattern,na=True)]

				def eliminate(i,column_names,d1):
				#Individual characters in model code
					d1 = d1.loc[d1.loc[:,column_names[i]].str.contains(model_name[i],na=True)]
					return d1

				if model_code == 'EJA530E':
					column_names = ['OUTPUT','SPAN','MATERIAL','P-CONNECT','HOUSING','E-CONNECT','INDICATOR','BRACKET']
				else:
					column_names = ['OUTPUT','SPAN','MATERIAL','P-CONNECT','BOLT-NUT','INSTALL','HOUSING','E-CONNECT','INDICATOR','BRACKET']
			#Iterating through the list of columns
				for i in range(len(column_names)):
					d1 = eliminate(i,column_names,d1)

				option_code = code[20:]

				temp=option_code.split('/')
				for i in list(set(temp).intersection(list(options['S/W Options']))):
					temp.remove(i)
				orr = [i for i in (list(options['OR'])) if i==i]
				or_code=list(set(temp).intersection(orr))
				andd = [i for i in (list(options['AND'])) if i==i]
				and_code=list(set(temp).intersection(andd))

			#Checking permutations of AND codes
				comb=[','.join(i) for i in itertools.permutations(and_code,r=2)]
				comb=list(set(comb).intersection(andd))    #List of valid combinations (EX: N1,GS)
				temp=list()
				for i in and_code:
					for j in comb:
						if re.search(i,j):
							temp.append(i)           # Making a list of and codes
				and_code = list(set(and_code) - set(temp)) + comb      #EX: list = 'X2','PR' + 'N1,GS'

				def and_eliminate(and_code,d1):
					d1=d1.loc[d1['OPTION:AND'].isin(and_code)]
					return d1

				def or_eliminate(or_code,d1):
					pattern = '|'.join(or_code)
					if pattern:
						d1=d1.loc[d1.loc[:,'OPTION:OR'].str.contains(pattern,na=True)]
					else:
						d1=d1[d1['OPTION:OR'].isnull()]
					return d1

				def not_eliminate(not_code,d1):
					pattern = '|'.join(not_code)
					d1=d1.loc[~d1.loc[:,'OPTION:NOT'].str.contains(pattern,na=False)]
					return d1

				d1=or_eliminate(or_code,d1)
				and_code.append(np.nan)
				d1=and_eliminate(and_code,d1)
				del and_code[-1]
				opt_code=or_code+and_code
				if opt_code:
					if 'N4' in opt_code:
						opt_code.remove('N4')
					d1=not_eliminate(opt_code,d1)

				def cpacode(st_code,option_code,model_name,app_option,cpa):
					if model_name[1]+model_name[2] in st_code:
						if model_name[2] == 'L':
							cpa=cpa+model_name[1]+'S'+"NN-NNNNN"
						else:
							cpa=cpa+model_name[1]+model_name[2]+"NN-NNNNN"
						if option_code:
							temp=['K2','K3','K6']
							for i in option_code:
								if i in temp:
									cpa=cpa+'/K3'
								if i == 'A1' or i=='A2':
									cpa=cpa+"/"+i

					else:
						cpa=cpa+model_name[1]+model_name[2]
						temp=['0','1','2']
						if model_name[3] in temp:
							cpa=cpa+'0'
						else:
							cpa=cpa+'5' #belongs to 3,4,5
						cpa=cpa+model_name[4]+'-'+model_name[5]+'NNNN'
						if option_code:
							if 'HD' in option_code:
								cpa="CPA"+model_code[3:6]+"Y-N"+code[9:15]+"NNNN"+"/HD"
								option_code.remove('HD')
							for i in option_code:
								if i in app_option:
									cpa=cpa+"/"+i
					return cpa

				option_code=option_code.split('/')
				cpa="CPA"+model_code[3:6]+"Y-N"
				if model_code[3:6]=='110':
					st_code=['MS','HS','VS','ML','HL','VL']
					app_option=['K1','K2','K3','K5','K6','T12','T13','HG','U1','HD','GS','N1','N2','N3','A1','A2']
					cpa=cpacode(st_code,option_code,model_name,app_option,cpa)

				elif model_code[3:6]=='430':
					st_code=['AS','HS','BS','AL','HL','BL']
					app_option=['K1','K2','K3','K5','K6','A1','A2','T11','T01','T12','U1','GS','N1','N2','N3']
					cpa=cpacode(st_code,option_code,model_name,app_option,cpa)

				else: #530E
					cpa=cpa + code[9:15] + "NNNN"
					if option_code:
						app_option=['K1','K2','K3','A1','T05','T06','T07','T08','T15','HG']
						for i in option_code:
							if i in app_option:
								cpa=cpa+"/"+i

				d1=d1.loc[d1['QTY'] != 0]   #Eliminating all quantites equal to 0

				unwanted=pd.read_csv((os.path.abspath('static/unwanted.csv')))
				unwanted_list = unwanted["PART NO."].tolist()
				pattern = '|'.join(unwanted_list)
				d1=d1.loc[~d1.loc[:,'PART NO.'].str.contains(pattern)]

				d1=d1[["PART NO.","PART NAME","QTY"]]
				d1['Week'] = week
				d1 = d1.append({'PART NO.': cpa, 'PART NAME':'CPA','QTY':1.0,'Week': week},ignore_index=True)
				d1['QTY']=d1['QTY']*int(qty)
				return d1

			proc_list = pd.DataFrame()
			for i in range(len(model_qty)):
				d1 = BOM_Explosion(code[i],model_qty[i],week[i])
				proc_list = proc_list.append(d1, ignore_index = True)

			proc_list['Final_Qty'] = proc_list.groupby(['PART NO.', 'Week'])['QTY'].transform('sum')
			proc_list = proc_list.drop_duplicates(subset=['PART NO.','Week'])

			proc_list = proc_list.pivot_table("Final_Qty",["PART NO.","PART NAME"],"Week")
			proc_list = proc_list.reset_index()

			current_week = dt.today().isocalendar()[1]
			columns_list = proc_list.columns.tolist()[2:]
			column_begin = [columns_list[i] for i in range(len(columns_list)) if columns_list[i] <=current_week]
			proc_list['Current'] = proc_list[column_begin].sum(axis=1)
			individual_columns = list()
			for x in range(len(column_begin), len(columns_list)):
				individual_columns.append(columns_list[x])
				if (len(individual_columns) >= 8):break;

			def missing_weeks(lst):
				[lst.append(x) for x in range(lst[0], lst[-1] + 1) if x not in lst]
				lst.sort()
				if len(lst)<8:
					[lst.append(x) for x in range(lst[-1], lst[-1]+len(lst)) if x not in lst]
				lst = lst[0:8]
				for x in range(len(lst)):
					if lst[x] >52:
						lst[x] = lst[x]-52
					if lst[x] not in columns_list:
						proc_list[lst[x]]=0
				return lst
			individual_columns = missing_weeks(individual_columns)
			column_end = [i for i in columns_list if i>individual_columns[len(individual_columns)-1]]

			proc_list['End'] = proc_list[column_end].sum(axis=1)
			proc_list['Total Required'] = proc_list[columns_list].sum(axis=1)

			proc_list = proc_list[['PART NO.', 'PART NAME']+['Current']+individual_columns+['End','Total Required']]
			proc_list.columns = proc_list.columns.map(str)

			# inv_list = pd.read_csv(value_list[1], engine='python')
			inv_list = pd.read_csv(os.path.abspath('static/inputFiles/inventory.csv'), low_memory=False, encoding = 'unicode_escape')

			inventory_col = list(inv_list.columns)
			inventory_dataset = input_data(inventory_col, 'inventory')

			if not isinstance(inventory_dataset, list):
				if inventory_dataset.status_code == 400:
					data = inventory_dataset.data
					return Response(data)

			inv_list['Final Parts'] = inv_list[inventory_dataset[1]].fillna(inv_list[inventory_dataset[0]])
			inv_list["Total"] = inv_list[inventory_dataset[2]].str.replace(",","").astype(int)
			inv_list=inv_list[['Final Parts', 'Total']]
			inv_list['Stock Qty'] = inv_list.groupby(['Final Parts'])['Total'].transform('sum')
			inv_list = inv_list.drop_duplicates(subset=['Final Parts'])
			inv_list = inv_list.rename(index=str, columns={"Final Parts": "PART NO."})
			inv_list.drop('Total', axis=1, inplace=True)

			# ----------------InventryGraph data -----------------

			inventory = pd.read_csv(os.path.abspath('static/inputFiles/inventory.csv'), low_memory=False, encoding = 'unicode_escape')

			inventory[inventory_dataset[3]] = inventory[inventory_dataset[3]].str.split(',').str.join('').astype('float64')
			inventory[inventory_dataset[2]] = inventory[inventory_dataset[2]].str.split(',').str.join('').astype('float64')
			inventory["Total stock value"] = inventory[inventory_dataset[2]] * inventory[inventory_dataset[3]]
			CPA110Y = inventory[inventory[inventory_dataset[1]].str.contains(r'CPA110Y', na=False)][inventory_dataset[2]].sum()
			CPA430Y = inventory[inventory[inventory_dataset[1]].str.contains(r'CPA430Y', na=False)][inventory_dataset[2]].sum()
			CPA530Y = inventory[inventory[inventory_dataset[1]].str.contains(r'CPA530Y', na=False)][inventory_dataset[2]].sum()
			CPA_Tot = CPA110Y + CPA430Y + CPA530Y
			Total_inventory = inventory["Total stock value"].sum()
			KDP_cost = inventory[~inventory[inventory_dataset[1]].str.contains('CPA', na=False)]["Total stock value"].sum()
			CPA_cost = Total_inventory - KDP_cost
			dataSet = {
			'CPA110Y':CPA110Y,
			'CPA430Y':CPA430Y,
			'CPA530Y':CPA530Y,
			'CPA_total': CPA_Tot,
			'CPA_Cost': round(CPA_cost,2),
			'KDP_Cost':round(KDP_cost,2),
			'Total_Inventory':round(Total_inventory,2),
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
			# ----------------InventryGraph data ----------------- End

			cpa_list = pd.read_csv(os.path.abspath('static/inputFiles/cpaFob.csv'), engine='python')

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
			# print(cpa_list)
			gr_list = pd.read_csv(os.path.abspath('static/inputFiles/grList.csv'), low_memory=False, encoding = 'unicode_escape')

			gr_list_col = list(gr_list.columns)
			gr_dataset = input_data(gr_list_col, 'grList')

			if not isinstance(gr_dataset, list):
				if gr_dataset.status_code == 400:
					data = gr_dataset.data
					return Response(data)

			gr_list=gr_list[[gr_dataset[0], gr_dataset[1]]]
			gr_list=gr_list.rename(index=str,columns={gr_dataset[0]: "Purchase_Order"})
			gr_list.Purchase_Order = gr_list.Purchase_Order.map(lambda x: '{:.0f}'.format(x))
			gr_list['Purchase_Order'] = gr_list['Purchase_Order'].astype(str)
			final_cpa = cpa_list.merge(gr_list, on=['Purchase_Order', gr_dataset[1]], how='left', indicator=True)
			final_cpa=final_cpa[final_cpa['_merge'] == 'left_only']

			# kdparts_list = pd.read_csv(value_list[3], engine='python')
			kdparts_list = pd.read_csv(os.path.abspath('static/inputFiles/kdParts.csv'), low_memory=False, encoding = 'unicode_escape')

			kdparts_col = list(kdparts_list.columns)
			kdparts_dataset = input_data(kdparts_col, 'kdparts')

			if not isinstance(kdparts_dataset, list):
				if kdparts_dataset.status_code == 400:
					data = kdparts_dataset.data
					return Response(data)

			kdparts_list=kdparts_list[[kdparts_dataset[0], kdparts_dataset[1], kdparts_dataset[2], kdparts_dataset[3], kdparts_dataset[4]]]
			kdparts_list=kdparts_list.rename(index=str, columns={kdparts_dataset[0]: "Purchase_Order", kdparts_dataset[1]:"Item"})
			kdparts_list['Purchase_Order']=kdparts_list['Purchase_Order'].astype(str)

			kdparts_list = kdparts_list[kdparts_list['Purchase_Order'].str.startswith('4')]

			kdparts_list[kdparts_dataset[2]] = kdparts_list[kdparts_dataset[2]].astype('datetime64[ns]')
			final_kdparts = kdparts_list.merge(gr_list, on=['Purchase_Order','Item'], how='left', indicator=True)
			final_kdparts=final_kdparts[final_kdparts['_merge'] == 'left_only']
			pipeline_list = final_cpa.append(final_kdparts, ignore_index = True)
			pipeline_list[kdparts_dataset[2]] = pipeline_list[kdparts_dataset[2]].astype('datetime64[ns]')
			pipeline_list['Final_Date'] = pipeline_list[kdparts_dataset[2]] + pd.DateOffset(days=12)
			pipeline_list['Week_Number'] = pipeline_list['Final_Date'].dt.week
			pipeline_list['Final_Year'] = pipeline_list['Final_Date'].dt.year
			# print('@@@@@@@@@@@@@@@@@',pipeline_list.head(20))
			current_year = dt.date(dt.now()).year
			pipeline_list.loc[pipeline_list.Final_Year < current_year, 'Week_Number'] = 1
			pipeline_list.loc[pipeline_list.Final_Year == current_year+1, 'Week_Number'] += 52
			pipeline_list.loc[pipeline_list.Final_Year == current_year+2, 'Week_Number'] += 104
			pipeline_list=pipeline_list.sort_values(by=['Week_Number'])
			pipeline_list = pipeline_list.rename(index=str, columns={"MS Code": "PART NO.", "Qty": "QTY"})
			pipeline_list = pipeline_list[["PART NO.", "QTY", "Week_Number"]]
			pipeline_list['Discrepancy'] = 0
			pipeline_list['QTY'] = pipeline_list.groupby(['PART NO.','Week_Number'])['QTY'].transform('sum')
			pipeline_list.drop_duplicates(subset=['PART NO.','Week_Number'])
			pipeline_list.loc[pipeline_list['Week_Number'] <= dt.today().isocalendar()[1], 'Discrepancy'] = 1
			pipeline_list = pipeline_list.pivot_table("QTY",["PART NO.","Discrepancy"],"Week_Number")
			pipeline_list = pipeline_list.reset_index()
			current_week = dt.today().isocalendar()[1]
			columns_list = pipeline_list.columns.tolist()[2:]
			column_begin = [x for x in columns_list if x < current_week]
			individual_columns = list()
			for x in range(len(column_begin), len(columns_list)):
				individual_columns.append(columns_list[x])
				if (len(individual_columns) >= 8):break;

			individual_columns = missing_weeks(individual_columns)
			# individual_columns = sorted(individual_columns)[:8]
			column_end = [i for i in columns_list if i>individual_columns[len(individual_columns)-1]]
			pipeline_list['Pipeline Total'] = pipeline_list[columns_list].sum(axis=1)
			pipeline_list['Pipeline Onwards'] = pipeline_list[column_end].sum(axis=1)

			try:
				pipe_list = pipeline_list[['PART NO.', 'Discrepancy','Pipeline Total']+individual_columns+['Pipeline Onwards']]
			except KeyError as e:
				for x in individual_columns:
					if x not in pipeline_list.columns:
						pipeline_list[x]=0
				pipe_list = pipeline_list[['PART NO.', 'Discrepancy','Pipeline Total']+individual_columns+['Pipeline Onwards']]


			lead_time_price = pd.read_csv(os.path.abspath('static/LeadTimeCategoryPrice.csv'))
			# lead_time = pd.read_csv(os.path.abspath('static/leadTime.csv'))
			# lead_time = lead_time.rename(index=str, columns={"Part No.": "PART NO."})
			lead_time_price["MOQ"] = 1
			final = pd.merge(proc_list,inv_list[['PART NO.','Stock Qty']], on=['PART NO.'], how='left')
			final = pd.merge(final, pipe_list, on=['PART NO.'], how='left')
			final = pd.merge(final, lead_time_price[['PART NO.','Lead Time', 'MOQ']], on=['PART NO.'], how='left')

			cols = final.columns.tolist()
			cols = cols[0:2] + cols[len(cols)-2:len(cols)] + cols[2:len(cols)-2]
			cols = [val for val in cols if not str(val).endswith("_x") if not str(val).endswith("_y")]

			final = final[cols]

			final['Pipeline Total'] = final['Pipeline Total'].fillna(0)
			final['Stock Qty'] = final['Stock Qty'].fillna(0)

			final['Total Available'] = final['Stock Qty'] + final['Pipeline Total']

			final['Difference'] = final['Total Available'] - final['Total Required']

			# cpa_leadtime = pd.read_csv((os.path.abspath('static/cpaLeadTime.csv')))
			cpa_leadtime = lead_time_price
			# cpa_leadtime = cpa_leadtime.rename(index=str, columns={"MS code": "PART NO."})

			final = pd.merge(final, cpa_leadtime[['PART NO.', 'Lead Time']], on=['PART NO.'], how='left')

			final['Lead Time_x'] = final['Lead Time_y'].fillna(final['Lead Time_x'])

			final.drop('Lead Time_y', axis=1, inplace=True)
			final = final.rename(index=str, columns={"Lead Time_x": "Lead Time"})

			# final['MOQ'].fillna(1, inplace=True)
			final['Lead Time'].fillna(50, inplace=True)

			final['Estimated Delivery Week'] = final['Lead Time'] / 7 + current_week
			final = final.astype({"Estimated Delivery Week": int})

			# price_category = pd.read_csv((os.path.abspath('static/categoryPrice.csv')))
			price_category = lead_time_price

			final = pd.merge(final, price_category[['PART NO.','Std. Price','Category']], on=['PART NO.'], how='left')

			final["Std. Price"] = final["Std. Price"].astype(float)
			final["Total Cost"] = final['Difference'] * final['Std. Price']

			cols = list(final.columns)

			pipeline_columns = cols[cols.index('Pipeline Total')+1:cols.index('Pipeline Onwards')]

			pipeline_columns = [int(i) for i in pipeline_columns]

			discrepancy = final[final['Discrepancy']==1]

			discrepancy = discrepancy.drop(['Discrepancy'], axis=1)

			writer = pd.ExcelWriter(os.path.join(path,r'Discrepancy.xlsx'), engine='xlsxwriter')
			discrepancy.to_excel(writer, sheet_name='Sheet1')
			writer.save()
			final['sum'] = discrepancy.iloc[ : ,5:13].sum(axis=1)
			final[final.columns[18]] = final[[final.columns[18],'sum']].sum(axis=1)
			final = final.drop(['sum'], axis=1)

			# final = final[final['Discrepancy']!=1]

			# Create deletion list from pieline columns
			# delete_columns = list()
			# for i in range(len(pipeline_columns)):
			# 	if pipeline_columns[i] < current_week:
			# 		delete_columns.append(pipeline_columns[i])

			discrepancy = discrepancy[['PART NO.', 'PART NAME', 'Pipeline Total']]
			Category = final[['Category', 'PART NO.']]
			# final = final.append(discrepancy, sort=False)
			final = final.drop_duplicates(subset=['PART NO.', 'Current', 'Lead Time', 'Total Required'], keep='first', inplace=False)

			final = final.groupby(['PART NO.', 'PART NAME'], sort=False).sum().reset_index()
			final = final.merge(Category, on='PART NO.')

			# Delete the pielin columns
			# final.drop(delete_columns, axis=1, inplace=True)

			predict = pd.read_csv(os.path.abspath('static/finalPrediction.csv'))
			predict = predict[["PART NO.","PART NAME","Final_Qty","Year"]]
			part_no = list(final['PART NO.'])
			from sklearn.model_selection import train_test_split
			from sklearn.linear_model import LinearRegression
			predicted_values=list()
			for i in part_no:
				is_value =predict['PART NO.'] == i
				sub = predict[is_value]
				if not sub.empty and len(sub)>2:
					X = sub.iloc[:, 3:4].values
					y = sub.iloc[:, 2].values
					X_train, X_test, y_train, y_test = train_test_split(X, y,test_size = 0.1,random_state = 0)
					regressor=LinearRegression()
					regressor.fit(X_train,y_train)
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
				if i <= current_year-4:
					column_begin.append(i)
			predict_pivot.drop(column_begin, axis=1, inplace=True)
			predict_pivot.drop('PART NAME', axis=1, inplace=True)

			final = pd.merge(final, predict_pivot, on=['PART NO.'], how='left')

			final['Prediction for current year'] = predicted_values
			final['Prediction for current year'][final['Prediction for current year']<0] = 0
			final['Monthly Prediction'] = final['Prediction for current year']/12
			final = final.astype({"Monthly Prediction": int})
			Threshold_qty = pd.read_excel(os.path.abspath('static/thresholdQty.xlsx'))
			Threshold_qty = Threshold_qty[["PART NO.", "Consumption Percentage(%)"]].dropna(subset=['PART NO.'])
			Threshold_qty['Threshold'] = Threshold_qty["Consumption Percentage(%)"] * thresholdValue
			Threshold_qty = Threshold_qty.drop('Consumption Percentage(%)', axis=1)
			final = pd.merge(final, Threshold_qty, how='left', on=['PART NO.'])
			#test for alert
			indexNum_pipeline = final.columns.tolist().index('Pipeline Total')
			indexNum_required = final.columns.tolist().index('Current')
			datalist_pipeline = final.iloc[:,indexNum_pipeline+1:int(pipeline_week_user+1)].fillna(0).sum(axis=1)
			pending_requirements = final.iloc[:,indexNum_required+1:int(required_week_user+1)].fillna(0).sum(axis=1)
			stock_status = final['Stock Qty'] + datalist_pipeline

			def createAlert(pending_requirements, stock_status, threshold):
				final['alert'] = False
				final['value'] = False

				df = pd.DataFrame({'requirements': pending_requirements, 'stock_status': stock_status, 'threshold': threshold,'alert':False, 'value':False}).fillna(0)
				final['alert'][(df['stock_status'] >= df['threshold']) & (df['stock_status'] >= df['requirements'])] = False
				final['alert'][(df['stock_status'] < df['threshold']) & (df['stock_status'] < df['requirements']) & (df['threshold'] < df['requirements'])] = 'ORANGE'
				final['alert'][(df['stock_status'] <= df['threshold']) & (df['stock_status'] >= df['requirements'])] = 'BLUE'
				final['alert'][(df['stock_status'] >= df['threshold']) & (df['stock_status'] <= df['requirements'])] = 'RED'

				final['value'][(df['stock_status'] >= df['threshold']) & (df['stock_status'] >= df['requirements'])] = False
				final['value'][(df['stock_status'] < df['threshold']) & (df['stock_status'] < df['requirements']) & (df['threshold'] < df['requirements'])] = df['threshold'] - df['stock_status'] #orange
				final['value'][(df['stock_status'] <= df['threshold']) & (df['stock_status'] >= df['requirements'])] = df['threshold'] - df['stock_status'] #blue
				final['value'][(df['stock_status'] >= df['threshold']) & (df['stock_status'] <= df['requirements'])] = df['requirements'] - df['stock_status'] #red
				del df

			createAlert(pending_requirements, stock_status, final['Threshold'])

			alert = final[final['alert'] !=False]
			alert = alert[['PART NO.', 'value', 'alert']]
			alert['value'] = alert['value'].abs().apply(np.ceil)
			alert = alert.drop_duplicates(keep='first', inplace=False)
			writer = pd.ExcelWriter(os.path.join(path,r'alert.xlsx'), engine='xlsxwriter')
			number_rows = len(alert.index) + 1
			alert.to_excel(writer, sheet_name='Sheet1')
			workbook = writer.book
			worksheet = writer.sheets['Sheet1']
			worksheet.conditional_format("$A$1:$D$%d" % (number_rows),
										 {"type": "formula",
										  "criteria": '=INDIRECT("D"&ROW())="BLUE"',
										  "format": workbook.add_format({'bg_color': '#00CCFF', 'border':1})
										 })
			worksheet.conditional_format("$A$1:$D$%d" % (number_rows),
										 {"type": "formula",
										  "criteria": '=INDIRECT("D"&ROW())="ORANGE"',
										  "format": workbook.add_format({'bg_color': '#FF9900', 'border':1})
										 })
			worksheet.conditional_format("$A$1:$D$%d" % (number_rows),
										 {"type": "formula",
										  "criteria": '=INDIRECT("D"&ROW())="RED"',
										  "format": workbook.add_format({'bg_color': '#993300', 'border':1})
										 })
			worksheet.set_column('D:D', None, None, {'hidden': 1})
			workbook.close()
			alert = alert.drop(['alert'], axis=1)
			alert = alert[alert['value'] != 0]
			if not alert.empty:
				DataCrud.alertMail(alert,request)

			kanban = final
			cols = final.columns.tolist()
			cols.insert(-1, cols.pop(cols.index('Discrepancy')))
			final = final.reindex(columns= cols)
			final = final.drop(['alert','value', 'MOQ'], axis=1)
			final = final.replace(np.nan, 0)
			final = final.drop_duplicates(keep='first', inplace=False)
			# final['pipelinePlusconsolidatedWeek'] = final['PART NO.'].map(discrepancy.set_index('PART NO.')['Pipeline Total']).fillna(0)
			final['pipelinePlusconsolidatedWeek'] = final['PART NO.'].map(discrepancy['Pipeline Total']).fillna(0)
			pieLineTotalNextWeek = final.columns.tolist().index('Pipeline Total')
			final[final.columns[pieLineTotalNextWeek + 1]] = final['pipelinePlusconsolidatedWeek'] + final[final.columns[pieLineTotalNextWeek + 1]]
			writer_object = pd.ExcelWriter(os.path.join(path,r'Consolidated Output.xlsx'), engine='xlsxwriter')
			headerList = list(final)
			for x in range(len(headerList)):
				if headerList[x]=="Current":
					i=x+1
				if headerList[x]=="Total Required":
					j=x+1
				if headerList[x]=="Pipeline Total":
					k=x+1
				if headerList[x]=="Pipeline Onwards":
					l=x+1
				if headerList[x]=="Total Available":
					m=x+1
				if headerList[x]=="Difference":
					n=x+1
				if headerList[x]=="Total Cost":
					o=x+2
				if headerList[x]=="Prediction for current year":
					p=x
					q=x+1
				if headerList[x]=="Monthly Prediction":
					r=x+1
				else:
					continue;

			final.to_excel(writer_object, sheet_name='Sheet1', startrow=2, header=True) #final replace with any other dataframe

			workbook_object = writer_object.book
			worksheet_object = writer_object.sheets['Sheet1']
			worksheet_object.activate()

			worksheet_object.set_row(1, 50)
			worksheet_object.set_row(0, 50)
			worksheet_object.set_row(2, 30)
			worksheet_object.set_column('AL:AL', None, None, {'hidden': 1})
			merge_format = workbook_object.add_format({'bold': 2,'border': 1,'font_size': 20,'align': 'center','valign': 'vcenter'})
			worksheet_object.merge_range( 0, 0, 0, r+1, 'Ordering Status', merge_format)
			worksheet_object.merge_range( 1, 0, 1, i-2, '  ', merge_format)
			worksheet_object.merge_range( 1, i, 1, j, 'Pending Requirement', merge_format)
			worksheet_object.merge_range( 1, k+1, 1, l, 'Pipeline Status', merge_format)
			worksheet_object.merge_range( 1, m+1, 1, n+1, 'Parts Status', merge_format)
			worksheet_object.merge_range( 1, o+1, 1, p, 'History', merge_format)
			worksheet_object.merge_range( 1, q, 1, r, 'Prediction', merge_format)

			week = workbook_object.add_format({
											'bg_color':'#FFFFFF',
											'border':1
												})
			pipeline = workbook_object.add_format({
											'bg_color':'#FFFFFF',
											'border':1
												})
			partstatus = workbook_object.add_format({
											'bg_color':'#FFFFFF',
											'border':1
												})
			history = workbook_object.add_format({
											'bg_color':'#FFFFFF',
											'border':1
												})
			prediction = workbook_object.add_format({
											'bg_color':'#FFFFFF',
											'border':1
												})

			format_green = workbook_object.add_format({'bg_color': '#FFFFFF', 'border':1})

			worksheet_object.set_column(i, j, 10, week)
			worksheet_object.set_column(k+1, l, 10, pipeline)
			worksheet_object.set_column(m+1, n+1, 10, partstatus)
			worksheet_object.set_column(o+1, p, 10, history)
			worksheet_object.set_column(q, r, 10, prediction)

			worksheet_object.conditional_format('A4:AK1000', {'type': 'formula',
										'criteria': '=$AL4>0.0',
										'format': format_green})

			worksheet_object.conditional_format('A4:AK1000', {'type': 'no_blanks', 'format': format_green})

			writer_object.save()
			final = kanban
			final = final[['PART NO.','Stock Qty','Pipeline Total']]
			Threshold_qty = pd.read_excel(os.path.abspath('static/thresholdQty.xlsx'))
			Threshold_qty = Threshold_qty[['Kanban Qty','No. of kanbans',"Kanban Qty * No' of Kanbans",'PART NO.']].dropna()
			final = pd.merge(final, Threshold_qty, how = 'left', on=["PART NO."]).dropna()
			del Threshold_qty
			final['Stock Total at present'] = final['Stock Qty'] + final['Pipeline Total']
			final['Dropped'] = ((final["Kanban Qty * No' of Kanbans"] - final['Stock Qty'])/ final['Kanban Qty']).apply(np.ceil).apply(abs)
			final['Ordered'] = (final["Pipeline Total"] / final['Kanban Qty']).apply(np.ceil).apply(abs)

			lessQty = final.loc[final['Stock Total at present'] < final["Kanban Qty * No' of Kanbans"]]
			moreQty = final.loc[final['Stock Total at present'] > final["Kanban Qty * No' of Kanbans"]]

			final = lessQty.append(moreQty, ignore_index=True)
			final = final.drop_duplicates(subset=['PART NO.']).fillna(0)
			final = final.replace([np.inf, -np.inf], np.nan).dropna(how='any')
			final = final.loc[final['Dropped'] != final["Ordered"]]
			final.to_excel(os.path.abspath('static/finalOutput/kanban.xlsx'))
			if not final.empty:
				DataCrud.alertMail(final,request)
			writer.save()
			return Response("file Upload successful", status=status.HTTP_201_CREATED)
		# 		# except Exception as e:
		# 	return Response({'message':repr(e),'status' : status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
		return Response({'message':'Bad request', 'status' : status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
