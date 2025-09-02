def get_FA(ticker):
    from data import fetch_data
    from injestion import injestion
    from qa_chain import get_qa_chain
    import markdown

    fetch_data(ticker=ticker)
    injestion()
    qa_chain = get_qa_chain()

    query = """
            You are given the following data for {ticker} from 1995 to 2023(if available):
            1. the balance sheet for the company(containing AccountsPayableCurrent, Assets, Liabilities, PropertyPlantAndEquipmentNet, CommonStockSharesIssued, etc.)
            2. the income statement(containing CostOfGoodsAndServicesSold, OperatingExpenses, GrossProfit, WeightedAverageNumberOfDilutedSharesOutstanding, Revenues, etc.)
            3. the cash flow statement(containing IncomeTaxesPaidNet, NetIncomeLoss, InterestPaid, PaymentsForRepurchaseOfCommonStock, PaymentsOfDividends, etc.)
            4. the shareholders' equity statement(containing ComprehensiveIncomeNetOfTax, StockholdersEquity, TreasuryStockSharesAcquired, Dividends, etc.)

            Go through it once.
            The trends of these informations over the years can be used to do a fundamental analysis of this company.
            Analyze these files, keep in mind the analysis and results you have taken out beforehand, and generate a fundamental analysis report  of the company in the following format:
            1. Company name
            2. About the company in 2 lines.
            3. Display the data and values
            4. Show financial ratios one by one, the value and its implications.
            5. According to the result, what's the sentiment of the stock, whether strong buy or strong sell.

            Use numbers wherever required and make sure to be 100 percent confident with your stance.
            Give me a complete analysis.
            """


    result = qa_chain(query.format(ticker=ticker))
    answer = result['result']

    return markdown.markdown(answer) # HTML formatting

def take_new_query(query):
    from qa_chain import get_qa_chain
    import markdown

    qa_chain = get_qa_chain()

    result = qa_chain(query)
    answer = result['result']

    return markdown.markdown(answer) #HTML formatting
