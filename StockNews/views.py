from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
#import nltk then in console type nltk.download() and download vader_lexicon from the gui
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import matplotlib.pyplot as plt

#return home page
def greetings(request):
    res = render(request,'StockNews/home.html')
    return res

def test(request):
    return render(request, 'StockNews/test.html')
# return home page with visualization
def search(request):
    if request.method == 'POST':
        company_name = request.POST['search_text']
        company_ticker_data = pd.read_excel("companies.xlsx")
        company_ticker = company_ticker_data.loc[company_ticker_data['company'] == company_name, 'ticker'].iloc[0]
        finviz_url = 'https://finviz.com/quote.ashx?t='
        tickers = []
        tickers.append(company_ticker)

        news_tables = {}
        for ticker in tickers:
            url = finviz_url + ticker

            req = Request(url=url, headers={'user-agent': 'my-app'})
            response = urlopen(req)

            html = BeautifulSoup(response, features='html.parser')
            news_table = html.find(id='news-table')
            news_tables[ticker] = news_table

        parsed_data = []

        for ticker, news_table in news_tables.items():

            for row in news_table.findAll('tr'):

                title = row.a.text
                date_data = row.td.text.split(' ')

                if len(date_data) == 1:
                    time = date_data[0]
                else:
                    date = date_data[0]
                    time = date_data[1]

                parsed_data.append([ticker, date, time, title])
        
        df = pd.DataFrame(parsed_data, columns=['ticker', 'date', 'time', 'title'])

        vader = SentimentIntensityAnalyzer()

        f = lambda title: vader.polarity_scores(title)['compound']
        df['compound'] = df['title'].apply(f)
        df['date'] = pd.to_datetime(df.date).dt.date

        # plt.figure(figsize=(10,8))
        mean_df = df.groupby(['ticker', 'date']).mean().unstack()
        mean_df = mean_df.xs('compound', axis="columns")
        plot = mean_df.plot(figsize=(10,8),kind='bar')
        # plt.show()
        fig = plot.get_figure()
        fig.savefig("static/images/output.png")
        
        # res = render(request,'StockNews/home.html')
        res = render(request,'StockNews/home.html',{"img_name":"output.png"})
        return res

