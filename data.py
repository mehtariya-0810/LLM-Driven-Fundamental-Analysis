def fetch_data(ticker):
    import os
    from dotenv import load_dotenv
    from sec_api import QueryApi, XbrlApi
    import requests
    import shutil
    import pandas as pd
    import numpy as np

    load_dotenv()
    sec_api_key = os.getenv("SEC_API_KEY")

    queryApi = QueryApi(api_key=sec_api_key)
    xbrlApi = XbrlApi(api_key=sec_api_key)

    def get_url_list(ticker, start="1995-01-01", end="2023-12-31"):
        url_list = []
        query = {
             "query": f"ticker:{ticker} " +
                     "AND formType:\"10-K\" " + 
                     "AND NOT formType:\"NT 10-K\" " + 
                     "AND NOT formType:\"10-K/A\" " +
                     f"AND filedAt:[{start} TO {end}]",
                "from": "0",
                "size": "50",
                "sort": [{ "filedAt": { "order": "asc" } }]
                }

        response = queryApi.get_filings(query)

        for filing in response['filings']:
            if "linkToHtml" in filing:
                url_list.append(filing["linkToHtml"])
    
        return url_list
    
    def get_xblr_json_list(url_list):
        xblr_json_list = []
        for url in url_list:
            try:
                xbrl_json = xbrlApi.xbrl_to_json(htm_url=url)
                xblr_json_list.append(xbrl_json)
                print("✅ " + url)
            except Exception as e:
                print("❌ " + url)
                continue
    
        return xblr_json_list
    
    # convert XBRL-JSON of income statement to pandas dataframe
    def get_income_statement(xblr_json):
        income_statement_store = {}

        # iterate over each US GAAP item in the income statement
        for usGaapItem in xblr_json['StatementsOfIncome']:
            values = []
            indicies = []

            for fact in xblr_json['StatementsOfIncome'][usGaapItem]:
                # only consider items without segment. not required for our analysis.
                if 'segment' not in fact and 'period' in fact:
                    index = fact['period']['startDate'] + ' to ' + fact['period']['endDate']
                    # ensure no index duplicates are created
                    if index not in indicies:
                        values.append(int(float(fact['value'])))
                        indicies.append(index)                    

                if 'unitRef' in fact:
                    income_statement_store[usGaapItem + '(in ' + fact['unitRef'] + ')'] = pd.Series(values, index=indicies)
                else:
                    income_statement_store[usGaapItem] = pd.Series(values, index=indicies) 

        income_statement = pd.DataFrame(income_statement_store)
        # switch columns and rows so that US GAAP items are rows and each column header represents a date range
        return income_statement.T 
    
    def concate_income_statement(xblr_json_list):
        flag = 0
        temp = 0

        for xblr_json in xblr_json_list:
            if 'StatementsOfIncome' in xblr_json:
                if flag == 0:
                    temp = get_income_statement(xblr_json)
                    flag = 1
                else:
                    temp1 = get_income_statement(xblr_json)
                    temp = pd.concat([temp, temp1], axis=1, join='outer')

        temp = temp.loc[:, ~temp.columns.duplicated()]

        return temp
    
    # convert XBRL-JSON of balance sheet to pandas dataframe
    def get_balance_sheet(xblr_json):
        balance_sheet_store = {}

        for usGaapItem in xblr_json['BalanceSheets']:
            values = []
            indicies = []

            for fact in xblr_json['BalanceSheets'][usGaapItem]:
                # only consider items without segment.
                if 'segment' not in fact and 'period' in fact:
                    index = fact['period']['instant']

                    # avoid duplicate indicies with same values
                    if index in indicies:
                        continue

                    # add 0 if value is nil
                    if "value" not in fact:
                        values.append(int(0))
                    else:
                        values.append(int(float(fact['value'])))

                    indicies.append(index)                    

                if 'unitRef' in fact:
                    balance_sheet_store[usGaapItem + '(in ' + fact['unitRef'] + ')'] = pd.Series(values, index=indicies)
                else:
                    balance_sheet_store[usGaapItem] = pd.Series(values, index=indicies) 

        balance_sheet = pd.DataFrame(balance_sheet_store)
        # switch columns and rows so that US GAAP items are rows and each column header represents a date instant
        return balance_sheet.T

    def concate_balance_sheet(xblr_json_list):
        flag = 0
        temp = 0

        for xblr_json in xblr_json_list:
            if 'BalanceSheets' in xblr_json:
                if flag == 0:
                    temp = get_balance_sheet(xblr_json)
                    flag = 1
                else:
                    temp1 = get_balance_sheet(xblr_json)
                    temp = pd.concat([temp, temp1], axis=1, join='outer')

        temp = temp.loc[:, ~temp.columns.duplicated()]

        return temp

    # convert XBRL-JSON of cash flow to pandas dataframe
    def get_cash_flow(xblr_json):
        cash_flow_store = {}

        for usGaapItem in xblr_json['StatementsOfCashFlows']:
            values = []
            indicies = []

            for fact in xblr_json['StatementsOfCashFlows'][usGaapItem]:
                # only consider items without segment.
                if 'segment' not in fact and 'period' in fact:
                    period = fact['period']
                    if 'startDate' in period and 'endDate' in period:
                        index = fact['period']['startDate'] + ' to ' + fact['period']['endDate']

                        # avoid duplicate indicies with same values
                        if index in indicies:
                            continue
                        
                        # add 0 if value is nil
                        if "value" not in fact:
                            values.append(np.nan)
                        else:
                            values.append(int(float(fact['value'])))

                        indicies.append(index)                    

                if 'unitRef' in fact:
                    cash_flow_store[usGaapItem + '(in ' + fact['unitRef'] + ')'] = pd.Series(values, index=indicies)
                else:
                    cash_flow_store[usGaapItem] = pd.Series(values, index=indicies) 

        cash_flow = pd.DataFrame(cash_flow_store)
        # switch columns and rows so that US GAAP items are rows and each column header represents a date instant
        return cash_flow.T

    def concate_cash_flow(xblr_json_list):
        flag = 0
        temp = 0

        for xblr_json in xblr_json_list:
            if 'StatementsOfCashFlows' in xblr_json:
                if flag == 0:
                    temp = get_cash_flow(xblr_json)
                    flag = 1
                else:
                    temp1 = get_cash_flow(xblr_json)
                    temp = pd.concat([temp, temp1], axis=1, join='outer')

        temp = temp.loc[:, ~temp.columns.duplicated()]

        return temp

    # convert XBRL-JSON of cash flow to pandas dataframe
    def get_equity(xblr_json):
        equity_store = {}

        for usGaapItem in xblr_json['StatementsOfShareholdersEquity']:
            values = []
            indicies = []

            try:
                for fact in xblr_json['StatementsOfShareholdersEquity'][usGaapItem]:
                    # only consider items without segment.
                    if 'segment' not in fact and 'period' in fact:
                        period = fact['period']
                        if 'startDate' in period and 'endDate' in period:
                            index = fact['period']['startDate'] + ' to ' + fact['period']['endDate']
                        elif 'instant' in period:
                            index = fact['period']['instant']

                        # avoid duplicate indicies with same values
                        if index in indicies:
                            continue
                        
                        # add 0 if value is nil
                        if "value" not in fact:
                            values.append(np.nan)
                        else:
                            values.append(int(float(fact['value'])))

                        indicies.append(index)                    

                    if 'unitRef' in fact:
                        equity_store[usGaapItem + '(in ' + fact['unitRef'] + ')'] = pd.Series(values, index=indicies)
                    else:
                        equity_store[usGaapItem] = pd.Series(values, index=indicies)  

            except Exception:
                continue

        cash_flow = pd.DataFrame(equity_store)
        # switch columns and rows so that US GAAP items are rows and each column header represents a date instant
        return cash_flow.T

    def concate_equity(xblr_json_list):
        flag = 0
        temp = 0

        for xblr_json in xblr_json_list:
            if 'StatementsOfShareholdersEquity' in xblr_json:
                if flag == 0:
                    temp = get_equity(xblr_json)
                    flag = 1
                else:
                    temp1 = get_equity(xblr_json)
                    temp = pd.concat([temp, temp1], axis=1, join='outer')

        temp = temp.loc[:, ~temp.columns.duplicated()]

        return temp

    url_list = get_url_list(ticker)
    xblr_json_list = get_xblr_json_list(url_list)

    data = {}

    data["income_statement"] = concate_income_statement(xblr_json_list)
    data["balance_sheet"] = concate_balance_sheet(xblr_json_list)
    data["cash_flow"] = concate_cash_flow(xblr_json_list)
    data["equity"] = concate_equity(xblr_json_list)

    folder_path = "data"

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for key in data:
        file_path = f"data/{key}.csv"
        data[key].to_csv(file_path)
