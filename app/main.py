from flask import Flask
import pandas as pd
import tushare as ts

pro = ts.pro_api('8a23aa12fefee5feeddd696e1d41cdfd8cdf3f257ab79b9a6c2a1bf4')

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello World!"


def get_max_drawdown():
    return ts.get_fund_info(ticker)


def get_benchmark():
    df = pro.index_daily(ts_code='399300.SZ')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
