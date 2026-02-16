import requests
from config import Config

class TwelveDataManager():
    def __init__(self):
        self.config = Config()
        self.twelvedata_api_key = self.config.TWELVEDATA_API_KEY

    def get_prices(self, symbol:str):
        #symbol = "BTC/USD"
        interval = "1day"
        output_size = 10
        requestURL = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize={output_size}&apikey={self.twelvedata_api_key}"
        r = requests.get(requestURL)
        result = r.json()

        if "status" in result and result["status"] == "error":  # run out api credits : result["code"] == 429
            #flash(result["message"])
            #flash(f"You have run out of API credits for the current minute.")
            return None
        return result
        
    
    def get_current_price(self, symbol:str):
        requestURL = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={self.twelvedata_api_key}"
        r = requests.get(requestURL)
        current_price = r.json()
        
        if "status" in current_price and current_price["status"] == "error":  # run out api credits : result["code"] == 429
            #flash(result["message"])
            #flash(f"You have run out of API credits for the current minute.")
            return None
        return current_price


