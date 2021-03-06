import time

from core.security_types import SecurityTypes
from stocks.stock import Stock
from threading import Thread

from core.logging import Logging

__author__ = 'kdedow'

class SecurityManager(object):
    """
    Class to create and run analysis on a target security
    """
    def __init__(self, database=None):
        """
        :type secTarget: String
        """
        self.stockDB = database

    def Get(self, secTarget, secType=SecurityTypes.stock):
        """
        Creates a security object (e.g. stock bond)

        :return:
        """
        if secType is SecurityTypes.stock:
            # Create a stock object to run analysis on
            return Stock(secTarget, self.stockDB)
        else:
            # This shouldn't happen but return None if we can't find an appropriate security
            return None

    def setupStockTable(self):
        """
        Setup stocks table in db with initial stocks

        :return:
        """
        # Get the date
        # NOTE: This is probably un
        date = datetime.date()
        dateStr = date.month() + "/" + date.day() + "/" + date.year()

        stocks = ("INTC", "AAPL", "GOOG", "YHOO", "SYK", "VZ")

        for stock in stocks:
            stockObj = self.securityFactory(stock)
            stockObj.queryAPI()

            self.stockDB.query("INSERT INTO basic_info (ticker, price, daily_change, company, year_high, year_low, \
             daily_percent, date, streak) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (stockObj.target, stockObj.curr, \
                                                                                stockObj.daily_change, stockObj.company,\
                                                                                stockObj.year_high, stockObj.year_low,\
                                                                                stockObj.daily_percent, dateStr, 0))

    def addStock(self, ticker=""):
        # Get the stock and analyze
        stockObj = self.Get(ticker)
        stockObj.queryAPI()

        # Store the stock in the db
        try:
            self.stockDB.query("INSERT INTO basic_info (ticker, price, daily_change, company, year_high, year_low, \
             daily_percent, date, streak) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (stockObj.target, stockObj.curr,
                                                                                stockObj.daily_change, stockObj.company,
                                                                                stockObj.year_high, stockObj.year_low,
                                                                                stockObj.daily_percent, stockObj.dateStr, 0))
        except:
            print("THIS MEANS WE ALREADY HAVE THE STOCK!")

    def removeStock(self, ticker=""):
        self.stockDB.query("DELETE FROM basic_info WHERE ticker=?", (ticker,))

    @Logging.SCOPE
    def updateStocks(self):
        """

        :return:
        """
        # Query the database for ticker symbols
        tickers = self.stockDB.query("SELECT ticker FROM basic_info")
        threads = []
        for stock in tickers:
            Logging.DEBUG("Updating " + str(stock[0]))
            stockObj = self.Get(stock[0])

            # TODO: Make sure this is safe (e.g no critical sections, appropriate thread completion)
            threads.append(Thread(target=stockObj.updateInfo()))

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()


    def getTrackedStocks(self):
        stocks = []

        tickers = self.stockDB.query("SELECT ticker FROM basic_info")

        for stock in tickers:
            stockObj = self.Get(stock[0])
            stocks.append(stockObj)

        return stocks

    def getHTMLTable(self):
        """
        Create a a table of the tracked stocks

        :return:
        """
        stocks = self.getTrackedStocks()

        html = " \
        <html> \
            <head></head> \
            <body> \
                <table> \
                    <tr> \
                        <th>Ticker</th> \
                        <th>Company</th> \
                        <th>Price</th> \
                        <th>Daily Change</th> \
                        <th>Daily Percent Change</th> \
                        <th>Year High</th> \
                        <th>Year Low</th> \
                    </tr>"

        for stock in stocks:
            html += "<tr>"

            html += "<td>"
            html += str(stock.target)
            html += "</td>"

            html += "<td>"
            html += str(stock.company)
            html += "</td>"

            html += "<td>"
            html += str(stock.curr)
            html += "</td>"

            html += "<td>"
            html += str(stock.daily_change)
            html += "</td>"

            html += "<td>"
            html += str(stock.daily_percent)
            html += "</td>"

            html += "<td>"
            html += str(stock.year_high)
            html += "</td>"

            html += "<td>"
            html += str(stock.year_low)
            html += "</td>"

            html += "</tr>"

        html += "</table></body></html>"

        return html

