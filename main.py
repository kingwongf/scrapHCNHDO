from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import pandas as pd


def get_orderbook():
    url = "https://himalaya.exchange/trading"

    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    # print(soup.prettify())
    ask_table = soup.find("table",{"class":"table table-fixed order_book_table sell"}).prettify()
    bid_table = soup.find("table",{"class":"table table-fixed order_book_table buy"}).prettify()

    ask_table = pd.read_html(ask_table, flavor='bs4', attrs = {'id': 'sellTable'})[0]
    ask_table['side'] = 'ask'

    ask_table.rename(columns={'Price (  HDO  )':'price', 'Amount (  HCN  )':'quantity', 'Total (  HDO  )': 'usd_quantity', 'Trading.Sum': 'cum_usd_quantity'},
                     inplace=True)

    bid_table = pd.read_html(bid_table, flavor='bs4', attrs = {'id': 'buyTable'})[0]

    bid_table['side'] = 'bid'
    bid_table.rename(columns={'Price (  HDO  )':'price', 'HCN':'quantity', 'Total (  HDO  )': 'usd_quantity', 'Trading.Sum': 'cum_usd_quantity'},
                     inplace=True)



    orderbook = ask_table.append(bid_table)

    return orderbook.sort_values("price", ascending=False).reset_index(), 0.5*(ask_table[-1]['price'] + bid_table[0]['price'])


def track_own_order(orders: pd.DataFrame):
    '''

    if lowest bid < order price < highest ask
        if order price not in orderbook:
            filled
        if order quantity > orderbook[ob.price == order price]:
           most likely partial filled or filled
        if order quantity < orderbook[ob.price == order price]:
           most likely being not filled orr being filled


    :param orders:
    :return:
    '''
    curr_orderbook = get_orderbook()

    for order in orders.itertuples(index=False):
        if curr_orderbook.price.min() < order.price < curr_orderbook.price.max():
            if order.price not in curr_orderbook.price.tolist():
                orders['status'] = "fully filled"
            elif order.quantity > curr_orderbook[curr_orderbook.price == order.price]:
                orders['status'] = "partially filled/ fully filled"
            elif order.quantity <= curr_orderbook[curr_orderbook.price == order.price]:
                orders['status'] = "not filled/ partially filled"

