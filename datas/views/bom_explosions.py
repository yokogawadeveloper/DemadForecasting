import pandas as pd
import numpy as np
import itertools
import os
import re


def main_bom_explosion(code, qty, week=None):
    def eliminate(i, column_names, d1):
        # Individual characters in model code
        d1 = d1.loc[d1.loc[:, column_names[i]].str.contains(model_name[i], na=True)]
        return d1

    def and_eliminate(and_code, d1):
        d1 = d1.loc[d1['OPTION:AND'].isin(and_code)]
        return d1

    def or_eliminate(or_code, d1):
        pattern = '|'.join(or_code)
        if pattern:
            d1 = d1.loc[d1.loc[:, 'OPTION:OR'].str.contains(pattern, na=True)]
        else:
            d1 = d1[d1['OPTION:OR'].isnull()]
        return d1

    def not_eliminate(not_code, d1):
        pattern = '|'.join(not_code)
        d1 = d1.loc[~d1.loc[:, 'OPTION:NOT'].str.contains(pattern, na=False)]
        return d1

    # def cpa_code(st_code, option_code, model_name, app_option, cpa):
    #     if model_name[1] + model_name[2] in st_code:
    #         # If 'ML' should be treated as 'MS'
    #         if model_name[1] == 'M' and model_name[2] == 'L':
    #             cpa = cpa + 'MS' + "NN-NNNNN"
    #
    #         # If 'HL' should be treated as 'HS'
    #         elif model_name[1] == 'H' and model_name[2] == 'L':
    #             cpa = cpa + 'HS' + "NN-NNNNN"
    #
    #         # If 'VL' should be treated as 'VS'
    #         elif model_name[1] == 'V' and model_name[2] == 'L':
    #             cpa = cpa + 'VS' + "NN-NNNNN"
    #
    #         # If 'AL' should be treated as 'AS'
    #         elif model_name[1] == 'A' and model_name[2] == 'L':
    #             cpa = cpa + 'AS' + "NN-NNNNN"
    #
    #         # If 'BL' should be treated as 'BS'
    #         elif model_name[1] == 'B' and model_name[2] == 'L':
    #             cpa = cpa + 'BS' + "NN-NNNNN"
    #
    #         elif model_name[2] == 'L':
    #             cpa = cpa + model_name[1] + 'S' + "NN-NNNNN"
    #
    #         else:
    #             cpa = cpa + model_name[1] + model_name[2] + "NN-NNNNN"
    #
    #         # If third character is 'S', remove 'K1' and 'K5' from option_code
    #         if model_name[2] == 'S':
    #             option_code = [opt for opt in option_code if opt not in ['K1', 'K5']]
    #
    #         # Check if both 'MG1' and 'MH1' are present, only consider 'MG1'
    #         if 'MG1' in option_code and 'MH1' in option_code:
    #             option_code.remove('MH1')
    #
    #         # Option code handling
    #         if option_code:
    #             temp = ['K2', 'K3', 'K6']
    #             for i in option_code:
    #                 if i in temp:
    #                     cpa = cpa + '/K3'
    #                 if i == 'A1' or i == 'A2':
    #                     cpa = cpa + "/" + i
    #
    #
    #     else:
    #         cpa = cpa + model_name[1] + model_name[2]
    #         temp = ['0', '1', '2']
    #         if model_name[3] in temp:
    #             cpa = cpa + '0'
    #         else:
    #             cpa = cpa + '5'  # belongs to 3,4,5
    #         cpa = cpa + model_name[4] + '-' + model_name[5] + 'NNNN'
    #
    #         if option_code:
    #             # Check for the special case where the 3rd character is 'S' and 2nd character is 'F' or 'L'
    #             if model_name[2] == 'S' and model_name[1] in ['F', 'L']:
    #                 if 'MH1' in option_code:
    #                     option_code = [opt if opt != 'MH1' else 'MG1' for opt in option_code]
    #
    #             if 'HD' in option_code:
    #                 cpa = "CPA" + model_code[3:6] + "Y-N" + code[9:15] + "NNNN" + "/HD"
    #                 option_code.remove('HD')
    #             for i in option_code:
    #                 if i in app_option:
    #                     cpa = cpa + "/" + i
    #
    #     return cpa

    def cpa_code(st_code, option_code, model_name, app_option, cpa):
        if model_name[1] + model_name[2] in st_code:
            # Handle specific cases for 'ML', 'HL', 'VL', etc.
            if model_name[1] == 'M' and model_name[2] == 'L':
                cpa = cpa + 'MS' + "NN-NNNNN"
            elif model_name[1] == 'H' and model_name[2] == 'L':
                cpa = cpa + 'HS' + "NN-NNNNN"
            elif model_name[1] == 'V' and model_name[2] == 'L':
                cpa = cpa + 'VS' + "NN-NNNNN"
            elif model_name[1] == 'A' and model_name[2] == 'L':
                cpa = cpa + 'AS' + "NN-NNNNN"
            elif model_name[1] == 'B' and model_name[2] == 'L':
                cpa = cpa + 'BS' + "NN-NNNNN"
            elif model_name[2] == 'L':
                cpa = cpa + model_name[1] + 'S' + "NN-NNNNN"
            else:
                cpa = cpa + model_name[1] + model_name[2] + "NN-NNNNN"

            # Eliminate K1 and K5 - Remove all K-related codes if found
            if 'K1' in option_code or 'K5' in option_code:
                option_code = [opt for opt in option_code if not opt.startswith('K')]

            # Check for 'MG1' and 'MH1' condition
            if 'MG1' in option_code and 'MH1' in option_code:
                option_code.remove('MH1')

            # Option code handling
            if option_code:
                temp = ['K2', 'K3', 'K6']
                for i in option_code:
                    if i in temp:
                        cpa = cpa + '/K3'  # If any of K2, K3, K6 exists, add '/K3'
                    if i == 'A1' or i == 'A2':
                        cpa = cpa + "/" + i

        else:
            # Logic when model_name doesn't match st_code patterns
            cpa = cpa + model_name[1] + model_name[2]
            temp = ['0', '1', '2']
            if model_name[3] in temp:
                cpa = cpa + '0'
            else:
                cpa = cpa + '5'  # belongs to 3,4,5
            cpa = cpa + model_name[4] + '-' + model_name[5] + 'NNNN'

            # Further option code handling outside specific model patterns
            if option_code:
                if model_name[2] == 'S' and model_name[1] in ['F', 'L']:
                    if 'MH1' in option_code:
                        option_code = [opt if opt != 'MH1' else 'MG1' for opt in option_code]

                if 'HD' in option_code:
                    cpa = "CPA" + model_code[3:6] + "Y-N" + code[9:15] + "NNNN" + "/HD"
                    option_code.remove('HD')

                for i in option_code:
                    if i in app_option:
                        cpa = cpa + "/" + i

        return cpa

    # main logic is here.
    model_name = code
    model_code = model_name[0:7]

    if (model_code == 'EJA530E'):
        model_name = model_name[8:12] + model_name[15:19]
        dataset = pd.read_csv(os.path.abspath('static/final530e.csv'))
        options = pd.read_csv(os.path.abspath('static/option530.csv'))  # Upload separate options file

    else:
        model_name = model_name[8:13] + model_name[14:19]
        dataset = pd.read_csv(os.path.abspath('static/final110e430e.csv'))
        options = pd.read_csv(os.path.abspath('static/option110.csv'))

    dataset = dataset.loc[dataset['SC'] != 1.0]
    pattern = [model_code, 'EJA530?']
    pattern = '|'.join(pattern)
    d1 = dataset.loc[dataset.loc[:, 'MODEL CODE'].str.contains(pattern, na=True)]

    if model_code == 'EJA530E':
        column_names = ['OUTPUT', 'SPAN', 'MATERIAL', 'P-CONNECT', 'HOUSING', 'E-CONNECT', 'INDICATOR', 'BRACKET']
    else:
        column_names = ['OUTPUT', 'SPAN', 'MATERIAL', 'P-CONNECT', 'BOLT-NUT', 'INSTALL', 'HOUSING', 'E-CONNECT','INDICATOR', 'BRACKET']

    # Iterating through the list of columns
    for i in range(len(column_names)):
        d1 = eliminate(i, column_names, d1)
    option_code = code[20:]
    temp = option_code.split('/')
    for i in list(set(temp).intersection(list(options['S/W Options']))):
        temp.remove(i)

    # Eliminating
    orr = [i for i in (list(options['OR'])) if i == i]
    or_code = list(set(temp).intersection(orr))
    andd = [i for i in (list(options['AND'])) if i == i]
    and_code = list(set(temp).intersection(andd))

    # Checking permutations of AND codes
    comb = [','.join(i) for i in itertools.permutations(and_code, r=2)]
    comb = list(set(comb).intersection(andd))  # List of valid combinations (EX: N1,GS)
    temp = list()
    for i in and_code:
        for j in comb:
            if re.search(i, j):
                temp.append(i)  # Making a list of and codes
    and_code = list(set(and_code) - set(temp)) + comb  # EX: list = 'X2','PR' + 'N1,GS'

    d1 = or_eliminate(or_code, d1)
    and_code.append(np.nan)
    d1 = and_eliminate(and_code, d1)
    del and_code[-1]
    opt_code = or_code + and_code
    if opt_code:
        if 'N4' in opt_code:
            opt_code.remove('N4')
        d1 = not_eliminate(opt_code, d1)

    # CPA Login start.
    option_code = option_code.split('/')
    cpa = "CPA" + model_code[3:6] + "Y-N"

    if model_code[3:6] == '110':
        st_code = ['MS', 'HS', 'VS', 'ML', 'HL', 'VL']
        app_option = ['K3', 'HG', 'U1', 'HD', 'GS', 'N1', 'N2', 'N3', 'A1', 'A2', 'MG1', 'MH1']
        cpa = cpa_code(st_code, option_code, model_name, app_option, cpa)  # calling cpa_code

    elif model_code[3:6] == '430':
        st_code = ['AS', 'HS', 'BS', 'AL', 'HL', 'BL']
        app_option = ['K1', 'A1', 'A2', 'U1', 'GS', 'N1', 'N2', 'N3', 'MG1', 'MH1']
        cpa = cpa_code(st_code, option_code, model_name, app_option, cpa)  # calling cpa_code

    else:  # 530E
        cpa = cpa + code[9:15] + "NNNN"
        if option_code:
            app_option = ['K1', 'A1', 'A2', 'HG', 'MG1', 'MH1']
            # Check if K1, K2, and K6 are present; if so, only consider K3
            if any(k in option_code for k in ['K2', 'K3', 'K6']):
                cpa = cpa + "/K3"
                # Remove K1, K2, and K6 from option_code since we are considering K3
                option_code = [opt for opt in option_code if opt not in ['K2', 'K3', 'K6']]
            for i in option_code:
                if i in app_option:
                    cpa = cpa + "/" + i

    # CPA Login end.
    d1 = d1.loc[d1['QTY'] != 0]
    unwanted = pd.read_csv((os.path.abspath('static/unwanted.csv')))
    unwanted_list = unwanted["PART NO."].tolist()
    pattern = '|'.join(unwanted_list)
    d1 = d1.loc[~d1.loc[:, 'PART NO.'].str.contains(pattern)]
    d1 = d1[["PART NO.", "PART NAME", "QTY"]]
    d1['Week'] = week
    d1 = d1.append({'PART NO.': cpa, 'PART NAME': 'CPA', 'QTY': 1.0, 'Week': week}, ignore_index=True)
    d1['QTY'] = d1['QTY'] * int(qty)
    return d1
