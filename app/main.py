from flask import Flask, make_response, request
import hashlib
import pandas as pd
import tushare as ts
import time
import xml.etree.ElementTree as ET

pro = ts.pro_api('8a23aa12fefee5feeddd696e1d41cdfd8cdf3f257ab79b9a6c2a1bf4')

app = Flask(__name__)



@app.route("/")
def index():
    return "hello world"


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
    else:
        xml = ET.fromstring(request.data)
        toUser = xml.find('ToUserName').text
        fromUser = xml.find('FromUserName').text
        msgType = xml.find("MsgType").text

        if msgType == 'text':
            content = xml.find('Content').text
            return reply_text(
                fromUser, toUser, get_response(
                    fromUser, content))
        else:
            return reply_text(fromUser, toUser, "宝宝七夕节快乐")



def reply_text(to_user, from_user, content):
    reply = """
    <xml><ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    <FuncFlag>0</FuncFlag></xml>
    """
    response = make_response(reply % (to_user, from_user,
                                      str(int(time.time())), content))
    response.content_type = 'application/xml'
    return response


def get_max_drawdown():
    return ts.get_fund_info(ticker)


def get_benchmark():
    df = pro.index_daily(ts_code='399300.SZ')
    return df


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
