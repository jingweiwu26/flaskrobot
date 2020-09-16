from datetime import datetime, timedelta
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
        content = xml.find('Content').text
        if msgType == 'text':
            content = xml.find('Content').text
            #if content != '宝宝':
            #    return reply_text(fromUser, toUser, "你是谁")
            #else:
            #    return reply_text(fromUser, toUser, "宝宝七夕节快乐")
            try:
                df = find_fund(content)
                df = basic_filter_fund(df)
                #df = quant_filter_fund(df)
                return reply_text(fromUser, to_user, df['reject'].iloc[0])
            except:
                return reply_text(fromUser, to_user, '无法查询，出bug了')


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


def get_max_drawdown(s):

    s_cummax = s.cummax()
    s_diff = s_cummax - s
    absolute_draw_down = max(s_diff)

    idx = s_diff.idxmax()
    max_level = s[:idx].max()
    ratio = (absolute_draw_down / max_level) * 100
    return ratio


def find_fund(ticker):
    df = pro.fund_basic(market='O')
    df['ts_code'] = df['ts_code'].str.split('.').str[0]
    fund = df[df['ts_code'] == ticker]
    return fund[['ts_code', 'name', 'fund_type', 'found_date', 'm_fee', 'c_fee', 'benchmark', 'invest_type']]


def basic_filter_fund(df):
    df['fee'] = df['m_fee'] + df['c_fee']
    df = df.drop(['m_fee', 'c_fee'], axis=1)
    df['reject'] = ''
    df.loc[df['fund_type'].isin(['股票型', '商品型', '另类投资型']), 'reject'] = df['reject'] + '投资类型风险高:' +df['fund_type'] + ';'
    df.loc[df['fee'] > 0.75, 'reject'] = df['reject'] + '总费率高:' + df['fee'].round(2).astype(str) + ';'
    df['found_date'] = pd.to_datetime(df['found_date'])
    date_filter = datetime.now() - timedelta(days=3 * 365)
    df.loc[df['found_date'] >= date_filter, 'reject'] = df['reject'] + '成立日期短:' + str(df['found_date'].dt.date.iloc[0]) + ';'

    return df

def quant_filter_fund(df):
    ticker = df['ts_code'].iloc[0] + '.OF'
    ddf = pro.fund_nav(ts_code=ticker)[::-1]
    ddf['pct'] = ddf['adj_nav'].pct_change()
    pos = len(ddf[ddf['pct'] > 0])
    neg = len(ddf[ddf['pct'] <= 0])
    df['reject'] = df['reject'] + '正收益天数:' + str(pos) + ';'
    df['reject'] = df['reject'] + '负收益天数:' + str(neg) + ';'
    df['reject'] = df['reject'] + '平均日涨幅:' + str(round(ddf['pct'].mean() * 100, 5)) + '%;'
    df['reject'] = df['reject'] + '波动率:' + str(ddf['pct'].std().round(5)) + ';'
    df['reject'] = df['reject'] + '风险调整后收益指数:' + str(round(ddf['pct'].mean() / ddf['pct'].std(), 5)) + ';'
    df['reject'] = df['reject'] + '最大回撤:' + str(round(get_max_drawdown(ddf['adj_nav']), 5)) + '%;'
    return df





def filter_fund_type(ticker):
    pro.fund_basic(market='E')


def get_return(df):
    df['return'] = df['adj_nav']


def get_benchmark():
    df = pro.index_daily(ts_code='399300.SZ')
    return df


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)
