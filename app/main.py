from flask import Flask, make_response
import hashlib
import pandas as pd
import tushare as ts

pro = ts.pro_api('8a23aa12fefee5feeddd696e1d41cdfd8cdf3f257ab79b9a6c2a1bf4')

app = Flask(__name__)



@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        token = 'Empire22'
        data = request.args
        signature = data.get('signature', '')
        timestamp = data.get('timestamp', '')
        nonce = data.get('nonce', '')
        echostr = data.get('echostr', '')
        s = sorted([token, timestamp, nonce])
        s = ''.join(s)
        if hashlib.sha1(s.encode('utf-8')).hexdigest() == signature:
            return echostr


@app.route('/wechat_api/', methods=['GET', 'POST'])
def wechat_api():
    if request.method == 'GET':
        token = 'Empire22'
        data = request.args
        signature = data.get('signature', '')
        timestamp = data.get('timestamp', '')
        nonce = data.get('nonce', '')
        echostr = data.get('echostr', '')
        s = sorted([token, timestamp, nonce])
        s = ''.join(s)
        if hashlib.sha1(s.encode('utf-8')).hexdigest() == signature:
            return echostr


def get_max_drawdown():
    return ts.get_fund_info(ticker)


def get_benchmark():
    df = pro.index_daily(ts_code='399300.SZ')
    return df


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
