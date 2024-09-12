from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.core.files.storage import default_storage
from django.http import HttpResponse
from ..models import *
from ..serializers import *
import itertools, os.path, re, xlsxwriter, numpy as np, pandas as pd
import time


class Sectorwise(APIView):
	# permission_classes = (IsAuthenticated,)
	permission_classes = (AllowAny,)

	def get(self, request):
		queryset = SectorWise.objects.filter(pk=1)
		if queryset:
			serializer = SectorWiseSerializer(queryset, many=True).data
			return Response(serializer, status=200)
		else:
			return Response({"value": "false", "message": "No data available, Please upload Industry Wise Data",
							'status': status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

		# return Response({'message':'Bad request', 'status' : status.HTTP_400_BAD_REQUEST},
	# status=status.HTTP_400_BAD_REQUEST)

	def post(self, request, format=None):
		if 1:
			for file in request.FILES:
				file_name = default_storage.delete(os.path.abspath('static/{}.xlsx'.format(file)))					
				file_name = default_storage.save(os.path.abspath('static/{}.xlsx'.format(file)), request.FILES[file])
			if request.data.get('consumedQty') and request.data.get('projectedQty'):
				SectorWise.objects.filter().update(consumedQty=request.data['consumedQty']\
				,projectedQty=request.data['projectedQty'])

			start_time = time.time()
			queryset = SectorWise.objects.latest('id')
			serializer = SectorWiseSerializer(queryset).data
			Consumed_qty = serializer['consumedQty']
			Projected_qty = serializer['projectedQty']
			THIS_FOLDER = 'static/'
			dfall = pd.read_excel(os.path.join(THIS_FOLDER, 'customerWiseData.xlsx'))
			list_of_sectors = dfall.Sector.unique()
			# list_of_sectors = dfall.Sector.unique()
			no_of_sectors = dfall.Sector.nunique(dropna = True)
			cleanedLi = [x for x in list_of_sectors if x == x]

			df_growth_rate = pd.read_excel(os.path.join(THIS_FOLDER, 'growthRate.xlsx'))
			df_sectors = pd.DataFrame(cleanedLi, columns=['Sector'])
			df_sectors = pd.merge(df_sectors, df_growth_rate, how = 'left', on=['Sector']).fillna(0.0)
			growth_rate = df_sectors['% Growth'].round(2).tolist()

			def BOM(code, qty):
				model_name=code
				model_code=model_name[0:7]

				if (model_code == 'EJA530E'):
					model_name=model_name[8:12]+model_name[15:19]
					dataset = pd.read_csv(os.path.abspath('static/final530e.csv'))    
					options = pd.read_csv(os.path.abspath('static/option530.csv'))    #Upload separate options file
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
					app_option=['K1','K2','K3','K5','K6','T12','T13','HG','U1','HD','GS','N1','N2','N3']
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
				d1 = d1.append({'PART NO.': cpa, 'PART NAME':'CPA','QTY':1.0},ignore_index=True)
				d1['QTY']=d1['QTY']*int(qty)
				return d1

			dfall = dfall[['MSCODE','Sum of QTY','Sector']]
			code = list(dfall['MSCODE'])
			model_qty = list(dfall['Sum of QTY'])
			finalparts = pd.DataFrame()
			for i in range(len(code)):
				d1 = BOM(code[i],model_qty[i])
				finalparts = finalparts.append(d1, ignore_index = True)

			finalparts['Final_Qty'] = finalparts.groupby(['PART NO.'])['QTY'].transform('sum')
			finalparts = finalparts.drop_duplicates(subset=['PART NO.'])
			finalparts = finalparts.sort_values(by=['PART NO.'], axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last')
			finalparts = finalparts.drop(columns=['Final_Qty','QTY'])

			total_cpa = []
			for j in range(0, no_of_sectors):
				df_parts = dfall.loc[(dfall['Sector']) == (cleanedLi[j])]
				df_parts = df_parts[['MSCODE','Sum of QTY']]
				code = list(df_parts['MSCODE'])
				model_qty = list(df_parts['Sum of QTY'])
				intermediate = pd.DataFrame()
				for i in range(len(code)):
					d1in = BOM(code[i], model_qty[i])
					intermediate = intermediate.append(d1in, ignore_index = True)
				
				intermediate['Final_Qty'] = intermediate.groupby(['PART NO.'])['QTY'].transform('sum')
				intermediate = intermediate.drop_duplicates(subset=['PART NO.'])

				intermediate = intermediate[["PART NO.","Final_Qty"]]
				
				total_intermediate = pd.DataFrame()
				total_intermediate = intermediate.loc[intermediate["PART NO."].str.startswith('CPA', na=False)]
				total_cpa.append(total_intermediate['Final_Qty'].sum())
				
				intermediate['% w.r.t Consumed_qty Qty.'] = ((intermediate['Final_Qty']/Consumed_qty) * 100).round(2)
				intermediate['% w.r.t Chemical Qty.'] = ((intermediate['Final_Qty']/total_cpa[j]) * 100).round(2)
				intermediate['Nos. w.r.t Chemical Qty.'] = ((total_cpa[j] * intermediate['% w.r.t Chemical Qty.'])/100).astype(int)
				intermediate['Prediction Qty. w.r.t CAGR %'] = ((intermediate['% w.r.t Chemical Qty.'] * (Consumed_qty * growth_rate[j])) / 100).astype(int)
				intermediate['Prediction Qty. w.r.t CAGR % + FY2019 Projection'] = ((intermediate['% w.r.t Chemical Qty.'] * (Projected_qty * growth_rate[j])) / 100).astype(int)
				finalparts = pd.merge(finalparts, intermediate, how = 'left', on=["PART NO."]).fillna(0.0)

			dfallmodel = dfall[dfall['Sector'].isin(cleanedLi)]
			dfallmodel = dfallmodel.groupby(['MSCODE','Sector'],as_index = False)['Sum of QTY'].sum()
			finalmodel = dfallmodel[['MSCODE','Sum of QTY']]
			finalmodel = finalmodel.sort_values(by=['MSCODE'], axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last')

			for row in range(0, no_of_sectors):
				dfmodel = dfallmodel.loc[(dfallmodel['Sector']) == (cleanedLi[j])]
				dfmodel = dfmodel[['MSCODE','Sum of QTY']]

				dfmodel['% w.r.t Total Qty.'] = ((dfmodel['Sum of QTY']/Consumed_qty) * 100).round(2)
				dfmodel['% w.r.t Chemical Qty.'] = ((dfmodel['Sum of QTY']/total_cpa[row]) * 100).round(2)
				dfmodel['Nos. w.r.t Chemical Qty.'] = ((total_cpa[row] * dfmodel['% w.r.t Chemical Qty.'])/100).astype(int)
				dfmodel['Prediction Qty. w.r.t CAGR %'] = ((dfmodel['% w.r.t Chemical Qty.'] * (Consumed_qty * growth_rate[row])) / 100).astype(int)
				dfmodel['Prediction Qty. w.r.t CAGR % + FY2019 Projection'] = ((dfmodel['% w.r.t Chemical Qty.'] * (Projected_qty * growth_rate[row])) / 100).astype(int)
				finalmodel = pd.merge(finalmodel, dfmodel, how = 'left', on=['MSCODE']).fillna(0.0)

			writer_object = pd.ExcelWriter(os.path.join(THIS_FOLDER,r'industryWiseData.xlsx'), engine ='xlsxwriter')

			perc_wrt_total = []
			pred_qty = []
			projection = []
			for i in range(0, no_of_sectors):
				perc_wrt_total.append(((total_cpa[i]/Consumed_qty)* 100).round(2))
				pred_qty.append((growth_rate[i]/100)*Consumed_qty)
				projection.append((growth_rate[i]*Projected_qty)/100)

			finalparts.to_excel(writer_object, sheet_name ='Sheet1', startrow = 6, header = False) #final replace with any other dataframe
			finalmodel.to_excel(writer_object, sheet_name ='Sheet2', startrow = 6, header = False)
			Sheets = ['Sheet1', 'Sheet2']
			workbook_object = writer_object.book
			merge_format = workbook_object.add_format({
			'bold': 2,
			'border': 5,
			'font_size': 10,
			'align': 'center',
			'valign': 'vcenter',
			'text_wrap': True})

			for sheet in Sheets:
				worksheet_object = writer_object.sheets[sheet]
				worksheet_object.activate()

				for i in range(3,((no_of_sectors*6)+3),6):
					worksheet_object.write(3, i, 'Qty.', merge_format)
					worksheet_object.write(3, i+1, '% w.r.t Total Qty.', merge_format)
					worksheet_object.write(3, i+2, '% w.r.t Chemical Qty.', merge_format)
					worksheet_object.write(3, i+3, 'Nos. w.r.t Chemical Qty.', merge_format)
					worksheet_object.write(3, i+4, 'Prediction Qty. w.r.t CAGR %', merge_format)
					worksheet_object.write(3, i+5, 'Prediction Qty. w.r.t CAGR % + FY2019 Projection', merge_format)

				for i in range(0,4):
					if (i==2):
						worksheet_object.set_row(2, 30)
					else:
						worksheet_object.set_row(i, 50)

				worksheet_object.set_column(1,1, 40)

				worksheet_object.merge_range( 2, 1, 3, 1, 'Part No.', merge_format)
				worksheet_object.merge_range( 2, 2, 3, 2, 'Part Name', merge_format)
				i=0
				for col in range(2, ((no_of_sectors*6)+1), 6):
					worksheet_object.merge_range( 2, col+1, 2, col+6 , cleanedLi[i], merge_format)
					i=i+1

				worksheet_object.merge_range( 0, 5, 0, 6, 'Consumed Qty. FY 2018', merge_format)
				worksheet_object.merge_range( 0, 7, 0, 8, 'Projected Qty. FY2019', merge_format)
				worksheet_object.merge_range(1, 5, 1, 6, Consumed_qty, merge_format)
				worksheet_object.merge_range(1, 7, 1, 8, Projected_qty, merge_format)
				worksheet_object.merge_range(1, 3, 1, 4 , 'Total Manufactured :', merge_format)
				i=0
				for coltot in range(3, ((no_of_sectors*6)+1), 6):
					worksheet_object.write(4, coltot, total_cpa[i])
					worksheet_object.write(4, coltot+1, perc_wrt_total[i])
					worksheet_object.write(4, coltot+4, growth_rate[i])
					worksheet_object.write(5, coltot+4, pred_qty[i])
					worksheet_object.write(5, coltot+5, projection[i])
					i=i+1

			writer_object.save()
			workbook_object.close()
			print("--- %s seconds ---" % (time.time() - start_time))
			return Response({'message': 'Data updated'}, status=200)
		return Response({'message':'Bad request', 'status' : status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)