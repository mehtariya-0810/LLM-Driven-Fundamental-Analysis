def fetch_data(ticker):

    import os
    from dotenv import load_dotenv
    from sec_api import QueryApi
    import requests
    import shutil

    load_dotenv()
    sec_api_key = os.getenv("SEC_API_KEY")

    queryApi = QueryApi(api_key=sec_api_key)
    PDF_GENERATOR_API = 'https://api.sec-api.io/filing-reader'

    def standardize_url(url):
      return url.replace('ix?doc=/', '')

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
            if "linkToFilingDetails" in filing:
                url_list.append(standardize_url(filing["linkToFilingDetails"]))
    
        return url_list

    def download_pdf(ticker, url_list):
        folder = "data"

        if os.path.exists(folder):
            shutil.rmtree(folder)
            
        if not os.path.isdir(folder):
            os.makedirs(folder)
    
        i = 0
        for url in url_list:
            try:
                file_path = os.path.join(folder, f"{ticker}_{i}.pdf")
                api_url = f"{PDF_GENERATOR_API}?token={sec_api_key}&type=pdf&url={url}"
                response = requests.get(api_url, stream=True)
                response.raise_for_status()

                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            
                i += 1
            except:
                continue

    print(f"=> Downloading {ticker} 10-K fillings from 1995 to 2023...")
    url_list = get_url_list(ticker)
    download_pdf(ticker, url_list)
    print("Successfully downloaded!")
