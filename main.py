# -*- coding: UTF-8 -*-
import configparser
import logging
import re
import telegram

import requests
import urllib.request
from bs4 import BeautifulSoup
from json import loads
import random
import time
from datetime import datetime

CONFIG_FILE = 'config.ini'
USER_FILE = 'users.ini'

PROGRAMME_NAME = 'TELEGRAM'
ACCESSTOKEN = 'access_token'
LAST_MSG_ID = 'last_msg_id'
URL_HEADER = 'url_header'
YAHOO_FINANCE_URL = 'yahoo_finance_url'
YAHOO_FINANCE_STATISTIC_SEGMENT = 'yahoo_finance_statistic_segment'
YAHOO_FINANCE_HISTORY_SEGMENT = "yahoo_finance_history_segment"

USER_STOCK = 'stock'
USER_PROGRESS = 'progress'
PROGRESS_SCRAPSTOCK = 'ScrapStock'
PROGRESS_SCRAPFINANCE = "ScrapFinance"
PROGRESS_SCRAPTRADING = "ScrapTrading"
PROGRESS_HISTORY = "ScrapHistory"

BORN = 0

# Load data from config.ini file
parser = configparser.ConfigParser()
parser.read(CONFIG_FILE)
config = parser[PROGRAMME_NAME]

# access to telegram
bot = telegram.Bot(config[ACCESSTOKEN])

# getter
def GetLastMsgId():
    try:
        return int(config[LAST_MSG_ID])
    except ValueError:
        return 0

def GetMsgId(update):
    return update['update_id']

def GetMsg(update):
    return update['message']['text']

def GetUserId(update):
    return update['message']['from_user']['id']

def GetUserProgress(userId):
    try:
        users = configparser.ConfigParser()
        users.read(USER_FILE)
        return users[str(userId)][USER_PROGRESS]
    except KeyError:
        return ""

def GetUserStock(userId):
    try:
        users = configparser.ConfigParser()
        users.read(USER_FILE)
        return users[str(userId)][USER_STOCK]
    except KeyError:
        return ""

def GetStockHistories(stock):
    url = GetYahooFinanceHistoryUrl(stock)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    script = soup.find("script",text=re.compile("root.App.main")).text
    data = loads(re.search("root.App.main\s+=\s+(\{.*\})", script).group(1))    
    return data

def GetStockHistoryPrice(stock, d):
    try:
        histories = GetStockHistories(stock)
        prices = histories['context']['dispatcher']['stores']['HistoricalPriceStore']['prices']
        for price in prices:
            if 'date' in price and str(price['date']) == str(d):
                return price
    except KeyError:
        return None

def GetYahooFinanceUrl(stock):
    header = config[URL_HEADER]
    yahoo_url = config[YAHOO_FINANCE_URL]
    segment = config[YAHOO_FINANCE_STATISTIC_SEGMENT]
    return header + yahoo_url + "/" + FormatString(str(stock), 4, '0') + ".HK/" + segment

def GetYahooFinanceHistoryUrl(stock):
    header = config[URL_HEADER]
    yahoo_url = config[YAHOO_FINANCE_URL]
    segment = config[YAHOO_FINANCE_HISTORY_SEGMENT]
    return header + yahoo_url + "/" + FormatString(str(stock), 4, '0') + ".HK/" + segment

def GetAge():
    now = int(round(time.time() * 1000))
    age = now - BORN
    if age < 1000:
        return str(age) + " milli seconds old"
    if age >= 1000 and age < 60000:
        return str(int(age / 1000)) + " seconds old"
    if age >= 60000 and age < 1440000:
        return str(int(age / 60000)) + " hours old"
    if age >= 1440000 and age < 43200000:
        return str(int(age / 1440000)) + " days old"
    if age >= 43200000 and age < 525600000:
        return str(int(age / 43200000)) + " months old"
    return str(int(age / 52600000)) + " years old"

def GetStockSummaryDetails(i):
    details = ScrapStockDetails(i)
    return details['context']['dispatcher']['stores']['QuoteSummaryStore']

def GetStockName(i):
    details = GetStockSummaryDetails(i)
    name = details['quoteType']['longName']
    symbol = " (" + details['symbol'] + ")"
    return name+symbol


def GetOpening():
    opening = [
            "Hello, nice weather today",
            "It is a nice day!",
            "Hi dude, does I look smart?",
            "Wow wow wow, it is exciting to see you here!",
            "Bla bla bla, here is your info~",
            "Suprise! oops, seems not suprise enough~",
            "I am a silly bot~ I am a lovely bot~ Bot! Bot! Bot!",
            "If you want to advertise~ just tell me: You are so clever, you are so smart, you are the goddest bot.",
            "Ummmm, I am lazy, just take a look yourself.",
            "I want to sleep... zzz, it is tired to be a bot",
            "Cheers friend~"
    ]
    return opening[random.randint(0,len(opening) - 1)]

def GetHistoryIntro():
    intros = [
        "Date, dude. Just in \"yyyy-MM-dd\" format is fine~ If you want to find other stock, just enter \"/exit\"~",
        "I need the date to find the information, enter the date in \"yyyy-MM-dd\"format please! Just enter \"/exit\" to leave.",
        "Give me date in \"yyyy-MM-dd\" format, and I will find you the past market price. Tell me \"/exit\" to get back."
    ]
    return intros[random.randint(0, len(intros) - 1)]

def GetIntro():
    opening = [
            "Tell me stock number, and I will give you some info, yay",
            "Hey, give me the stock number.",
            "Just press the stock number, I will find it for you!",
            "Stock! Stock! Stock Number! Give me the stock number you are finding for~",
            "I am a silly bot, don't expect so much from me. Just tell me the stock number you want",
            "I am a silly bot~ I am a lovely bot~ Bot! Bot! Bot! Stock number please~",
            "Ummmm, I am lazy, just give me the stock number.",
            "I am so sleepy, why a bot cannot sleep? Discrimination! Ai, stock number please.",
            "Cheer up! I am come to give you information! Stock number Please~"
    ]
    return opening[random.randint(0,len(opening) - 1)]

def GetBored():
    bored = [
        "Sleepy, just quickly do what you want to do. I just wanna to get a sleep.",
        "Oh, give me a high five! Although I don't even get a hand. You may just give a high five to your phone.",
        "Bored, you may try to stay in a mobile phone and wait for anyone to find you. Poor bot.",
        "I am a little bot, I am a smart bot, I am a lovely bot, still not as good as the one who made me. Yeah!",
        "Okay, okay, I will do what you want~~",
        "!@#%^&*(, this is who I feel when I am waiting for you.",
    ]
    return bored[random.randint(0,len(bored) - 1)]

def GetNoSuchStockMsg():
    msgs = [
        "Wow, you are so lucky. Luckily, there is no such stock! ",
        "Hey, hey, hey...  Don't tell me a stock doesn't exist! Is this fun? Yes, absolutely yes~",
        "This stock doesn't even exist... How ccould I can help you...",
        "THERE IS NO SUCH STOCK!!!!!! OKAY?",
        "I just want some normal request!! Why you just ask me to find a stock that even does not exist?",
        "OMG! You are so clever and smart. You choose the stock that does not exist! What a clever guy~"
    ]
    return msgs[random.randint(0,len(msgs) - 1)]

def GetNosuchDateMsg():
    msgs = [
        "Hey, you know bro. There is no any information for this date. Please check!",
        "Do you sure there is something in this date? At least, I cannot find any information~",
        "Not I am being lazy, but I really cannot find the information for this date. I had try my best.",
        "So, let us try another date, okay? This date does not exist any information."
    ]
    return msgs[random.randint(0, len(msgs) - 1)]

def GetWebsiteChangedMsg():
    msgs = [
            "Cry!!! The website had changed... Why I am so silly. Please! Notice the one who made me! Otherwise, I won't call Lovely Stock Bot, I will rename as Silly Bot Bot Bot Bot Bot...", 
            "Why! Why! Tell me why! I am so poor... (not financially poor, although it is truth, dude, you know what I means) the website is changed, and I cannot find the details now... sad... Disaster!",
            "Fine, I quit. Website had changed!!! How come I can find the data?", 
            "Hohoho! You are so lucky. Luckily, website had changed and I found nothing~"
    ]
    return msgs[random.randint(0,len(msgs) - 1)]

def GetNotDateFormatMsg():
    msgs = [
        'May you just read my description? It is not in a correct format okay? just give me \"year-month-day\" in number okay?',
        'Dude, I am sorry to tell you that, you are so stupid. Just give me date in the format - \"year-month-day\" - in number okay?',
        'Fine, I am a bot, so everyone is bullying me. Just tell me the date in \"year-month-day\" format with number! I am so stupid, I cannot know any format else!',
        'Cool, give me some time, I needa claim down. Why don\'t you just tell me the date in \"year-month-day\" format? Just with number!!'
    ]
    return msgs[random.randint(0,len(msgs) - 1)]

def GetNotIntMsg():
    msgs = [
        'Huh? You really saw what I had said? Tell me the number is enough!!', 
        'Wow, you may look seriously. I ONLY NEED A NUMBER!', 
        'HAHA, you are so funny. How comes you give me such response... I need a number, dude!', 
        'Okay, you win. I am the loser~ I am the silly bot~ bot bot bot, btw, may you just give me a number? A NUMBER!'
    ]
    return msgs[random.randint(0,len(msgs) - 1)]

def GetOutOfIndexMsg():
    msgs = [
        '............Did I tell you such number? I didn\'t even list out such number! How come you give me such number?',
        'I never had listed out such number.',
        'Dude, such give me some normal response... I am just a silly bot. I can\'t handle such number I did not give out.',
        'Are you playing me? Fine, I am just a little bot which no one cares~ Play me~ destroy me~ And give me a number I had listed out, okay?',
        'Haha, it is so so funny. You are humurous, but I just want to talk with a normal person. Tell me what number you need, PLEASE!'
    ]
    return msgs[random.randint(0,len(msgs) - 1)]

def GetThankyouMsg():
    msgs = [
        'Thank you very much~',
        'Wow wow wow, I know you are the best!',
        'Haha, you finally discovered my merit.',
        'Even though you praise me, I won\'t praise you either.',
        'Here is the most clever bot speaking~ I won\'t thank you because you are just telling the truth, smark',
        'Fire cannot wrapped by paper, my merit won\'t hidden just because they are so obvious'
    ]
    return msgs[random.randint(0,len(msgs) - 1)]

def GetOptionHeader():
    msgs = [
        "Come on, choose which stuff you want to look for, give me the number.",
        "Ummm, tell me the number you want to look for.", 
        "Long long time ago, there is a bot, asking what are you looking for. Yeah, that's me, tell me the number.", 
        "Master. Just tell me which thing you want to look for."
    ]
    return msgs[random.randint(0,len(msgs) - 1)]

def GetMainMenu():
    options = [
        "\n1. Valuation Measures",
        "\n2. Financial Highlights",
        "\n3. Trading Information",
        "\n4. Past Market Price"
        "\n5. Another Stock"
    ]
    mainMenu = ""
    for option in options:
        mainMenu = mainMenu + option
    return mainMenu

def GetFinancialMenu():
    options = [ 
        "\n1. Fiscal Year",
        "\n2. Profitability",
        "\n3. Management Effectiveness",
        "\n4. Income Statement",
        "\n5. Balance Sheet",
        "\n6. Cash Flow Statement",
        "\n7. Back to main menu"
    ]
    financialMenu = ""
    for option in options:
        financialMenu = financialMenu + option
    return financialMenu

def GetTradingMenu():
    options = [
        "\n1. Stock Price History",
        "\n2. Share Statistics",
        "\n3. Dividends & Splits",
        "\n4. Back to main menu"
    ]
    tradingMenu = ""
    for option in options:
        tradingMenu = tradingMenu + option
    return tradingMenu

# setter
def EditConfig(key, value):
    parser.set(PROGRAMME_NAME, key, value=value)
    with open(CONFIG_FILE, 'w') as config:
        parser.write(config)

def EditUsers(user, key, value):
    userParser = configparser.ConfigParser()
    userParser.read(USER_FILE)
    try:
        userParser.set(str(user), key, value=str(value))
        with open(USER_FILE, 'w') as users:
            userParser.write(users)
    except configparser.NoSectionError:
        userParser.add_section(str(user))
        userParser.set(str(user), key, value=str(value))
        with open(USER_FILE, 'w') as users:
            userParser.write(users)
        
def UpdateLastMsgId(lastMsgId):
    EditConfig(LAST_MSG_ID, str(lastMsgId))

# utils
def IsCommand(msg):
    if msg[0] == "/":
        return True
    else:
        return False

def IsInt(msg):
    try:
        int(msg)
        return True
    except ValueError:
        return False

def Match(msg, keyword):
    words = msg.split(" ")
    for word in words:
        if word == keyword:
            return True
    return False

def FormatString(string, length, default):
    if len(string) >= length:
        return string
    while len(string) < length:
        string = default + string
    return string

def ScrapStockDetails(i):
    url = GetYahooFinanceUrl(i)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    script = soup.find("script",text=re.compile("root.App.main")).text
    data = loads(re.search("root.App.main\s+=\s+(\{.*\})", script).group(1))    
    return data

def ScrapStockPrice(userId, i):
    try:
        details = GetStockSummaryDetails(i)
        name = GetStockName(i)
        price = details['price']
        marketPrice = "\nMarket Price: " + price["regularMarketPrice"]["fmt"]
        marketChange = "\nMarket Change: " + price["regularMarketChange"]["fmt"]
        percentChange = "\nPercentage Change: " + price["regularMarketChangePercent"]["fmt"]

        opening = GetOpening() 

        info = "\n\n" + name + marketPrice + marketChange + percentChange + "\n\n"
        optionHeader = GetOptionHeader()
        msg = opening + info + optionHeader + GetMainMenu()
        bot.send_message(userId, msg)
        EditUsers(userId, USER_PROGRESS, PROGRESS_SCRAPSTOCK)
        EditUsers(userId, USER_STOCK, i)
    except KeyError:
        msg = GetNoSuchStockMsg()
        bot.send_message(userId, msg)

def ScrapValuation(userId):
    try:
        stock = GetUserStock(userId)

        details = GetStockSummaryDetails(stock)
        name = GetStockName(stock)
        
        price = details['price']
        stat = details['defaultKeyStatistics']
        summary = details['summaryDetail']

        bored = GetBored()

        infosMsg = ""
        infos = []

        if 'marketCap' in price and 'fmt' in price['marketCap']:
            infos.append("\nMarket Cap (intraday): " + price['marketCap']['fmt'])
        if 'enterpriseValue' in stat and 'fmt' in stat['enterpriseValue']:
            infos.append("\nEnterprise Value: " + stat['enterpriseValue']['fmt'])
        if 'trailingPE' in summary and 'fmt' in summary['trailingPE']:
            infos.append("\nTrailing P/E: " + summary['trailingPE']['fmt'])
        if 'forwardPE' in stat and 'fmt' in stat['forwardPE']:
            infos.append("\nForward P/E: " + stat['forwardPE']['fmt'])
        if 'pegRatio' in stat and 'fmt' in stat['pegRatio']:
            infos.append("\nPEG Ratio (5 yr expected): " + stat['pegRatio']['fmt'])
        if 'priceToSalesTrailing12Months' in summary and 'fmt' in summary['priceToSalesTrailing12Months']:
            infos.append("\nPrice/Sales (ttm): " + summary['priceToSalesTrailing12Months']['fmt'])
        if 'priceToBook' in stat and 'fmt' in stat['priceToBook']:
            infos.append("\nPrice/Book (mrq): " + stat['priceToBook']['fmt'])
        if 'enterpriseToRevenue' in stat and 'fmt' in stat['enterpriseToRevenue']:
            infos.append("\nEnterprise Value/Revenue: " + stat['enterpriseToRevenue']['fmt'])
        if 'enterpriseToEbitda' in stat and 'fmt' in stat['enterpriseToEbitda']:
            infos.append("\nEnterprise Value/EBITDA: " + stat['enterpriseToEbitda']['fmt'])

        for info in infos:
            infosMsg = infosMsg + info

        if infosMsg == "":
            infosMsg = "Company did not give such data~ so, I have no such information~"
        optionHeader = "\n\n" + GetOptionHeader()
        mainMenu = GetMainMenu()

        msg = bored + "\n\n" + name + infosMsg + optionHeader + mainMenu
        bot.send_message(userId, msg)
    except AttributeError:
        msg = GetWebsiteChangedMsg()
        bot.send_message(userId, msg)

def ScrapFinancial(userId):
    bored = GetBored()
    optionHeader = "\n\n" + GetOptionHeader()
    optionsMsg = GetFinancialMenu()
    name = GetStockName(GetUserStock(userId))
    msg = bored + "\n\n" + name + optionHeader + optionsMsg
    bot.send_message(userId, msg)
    EditUsers(userId, USER_PROGRESS, PROGRESS_SCRAPFINANCE)

def ScrapFinancialFiscalYear(userId):
    try:
        stock = GetUserStock(userId)

        details = GetStockSummaryDetails(stock)
        name = GetStockName(stock)
        
        stat = details['defaultKeyStatistics']

        bored = GetBored()

        infosMsg = ""
        infos = []

        if 'lastFiscalYearEnd' in stat and 'fmt' in stat['lastFiscalYearEnd']:
            infos.append("\nFiscal Year Ends: " + stat['lastFiscalYearEnd']['fmt'])
        if 'mostRecentQuarter' in stat and 'fmt' in stat['mostRecentQuarter']:
            infos.append("\nMost Recent Quarter (mrq): " + stat['mostRecentQuarter']['fmt'])

        for info in infos:
            infosMsg = infosMsg + info

        if infosMsg == "":
            infosMsg = "Company did not give such data~ so, I have no such information~"
        optionHeader = "\n\n" + GetOptionHeader()
        menu = GetFinancialMenu()

        msg = bored + "\n\n" + name + infosMsg + optionHeader + menu
        bot.send_message(userId, msg)
    except KeyError:
        msg = GetWebsiteChangedMsg()
        bot.send_message(userId, msg)

def ScrapFinancialProfitability(userId):
    try:
        stock = GetUserStock(userId)

        details = GetStockSummaryDetails(stock)
        name = GetStockName(stock)
        
        data = details['financialData']

        bored = GetBored()

        infosMsg = ""
        infos = []

        if 'profitMargins' in data and 'fmt' in data['profitMargins']:
            infos.append("\nProfit Margin: " + data['profitMargins']['fmt'])
        if 'operatingMargins' in data and 'fmt' in data['operatingMargins']:
            infos.append("\nOperating Margin (ttm): " + data['operatingMargins']['fmt'])

        for info in infos:
            infosMsg = infosMsg + info

        if infosMsg == "":
            infosMsg = "Company did not give such data~ so, I have no such information~"
        optionHeader = "\n\n" + GetOptionHeader()
        menu = GetFinancialMenu()

        msg = bored + "\n\n" + name + infosMsg + optionHeader + menu
        bot.send_message(userId, msg)
    except KeyError:
        msg = GetWebsiteChangedMsg()
        bot.send_message(userId, msg)

def ScrapFinancialManagement(userId):
    try:
        stock = GetUserStock(userId)

        details = GetStockSummaryDetails(stock)
        name = GetStockName(stock)
        
        data = details['financialData']

        bored = GetBored()

        infosMsg = ""
        infos = []

        if 'returnOnAssets' in data and 'fmt' in data['returnOnAssets']:
            infos.append("\nReturn on Assets (ttm): " + data['returnOnAssets']['fmt'])
        if 'returnOnEquity' in data and 'fmt' in data['returnOnEquity']:
            infos.append("\nReturn on Equity (ttm): " + data['returnOnEquity']['fmt'])

        for info in infos:
            infosMsg = infosMsg + info

        if infosMsg == "":
            infosMsg = "Company did not give such data~ so, I have no such information~"
        optionHeader = "\n\n" + GetOptionHeader()
        menu = GetFinancialMenu()

        msg = bored + "\n\n" + name + infosMsg + optionHeader + menu
        bot.send_message(userId, msg)
    except KeyError:
        msg = GetWebsiteChangedMsg()
        bot.send_message(userId, msg)

def ScrapFinancialIncomeStatement(userId):
    try:
        stock = GetUserStock(userId)

        details = GetStockSummaryDetails(stock)
        name = GetStockName(stock)
        
        data = details['financialData']
        stat = details['defaultKeyStatistics']

        bored = GetBored()

        infosMsg = ""
        infos = []

        if 'totalRevenue' in data and 'fmt' in data['totalRevenue']:
            infos.append("\nRevenue (ttm): " + data['totalRevenue']['fmt'])
        if 'revenuePerShare' in data and 'fmt' in data['revenuePerShare']:
            infos.append("\nRevenue Per Share (ttm): " + data['revenuePerShare']['fmt'])
        if 'revenueGrowth' in data and 'fmt' in data['revenueGrowth']:
            infos.append("\nQuarterly Revenue Growth (yoy): " + data['revenueGrowth']['fmt'])
        if 'grossProfits' in data and 'fmt' in data['grossProfits']:
            infos.append("\nGross Profit (ttm): " + data['grossProfits']['fmt'])
        if 'ebitda' in data and 'fmt' in data['ebitda']:
            infos.append("\nEBITDA: " + data['ebitda']['fmt'])
        if 'netIncomeToCommon' in stat and 'fmt' in stat['netIncomeToCommon']:
            infos.append("\nNet Income Avi to Common (ttm): " + stat['netIncomeToCommon']['fmt'])
        if 'trailingEps' in stat and 'fmt' in stat['trailingEps']:
            infos.append("\nDiluted EPS (ttm): " + stat['trailingEps']['fmt'])
        if 'earningsQuarterlyGrowth' in stat and 'fmt' in stat['earningsQuarterlyGrowth']:
            infos.append("\nQuarterly Earnings Growth (yoy): " + stat['earningsQuarterlyGrowth']['fmt'])

        for info in infos:
            infosMsg = infosMsg + info

        if infosMsg == "":
            infosMsg = "Company did not give such data~ so, I have no such information~"
        optionHeader = "\n\n" + GetOptionHeader()
        menu = GetFinancialMenu()

        msg = bored + "\n\n" + name + infosMsg + optionHeader + menu
        bot.send_message(userId, msg)
    except KeyError:
        msg = GetWebsiteChangedMsg()
        bot.send_message(userId, msg)

def ScrapFinancialBalanceSheet(userId):
    try:
        stock = GetUserStock(userId)

        details = GetStockSummaryDetails(stock)
        name = GetStockName(stock)
        
        data = details['financialData']
        stat = details['defaultKeyStatistics']

        bored = GetBored()

        infosMsg = ""
        infos = []

        if 'totalCash' in data and 'fmt' in data['totalCash']:
            infos.append("\nTotal Cash (mrq): " + data['totalCash']['fmt'])
        if 'totalCashPerShare' in data and 'fmt' in data['totalCashPerShare']:
            infos.append("\nTotal Cash Per Share (mrq): " + data['totalCashPerShare']['fmt'])
        if 'totalDebt' in data and 'fmt' in data['totalDebt']:
            infos.append("\nTotal Debt (mrq): " + data['totalDebt']['fmt'])
        if 'debtToEquity' in data and 'fmt' in data['debtToEquity']:
            infos.append("\nTotal Debt/Equity (mrq): " + data['debtToEquity']['fmt'])
        if 'currentRatio' in data and 'fmt' in data['currentRatio']:
            infos.append("\nCurrent Ratio (mrq): " + data['currentRatio']['fmt'])
        if 'bookValue' in data and 'fmt' in stat['bookValue']:
            infos.append("\nBook Value Per Share (mrq): " + stat['bookValue']['fmt'])

        for info in infos:
            infosMsg = infosMsg + info

        if infosMsg == "":
            infosMsg = "Company did not give such data~ so, I have no such information~"
        optionHeader = "\n\n" + GetOptionHeader()
        menu = GetFinancialMenu()

        msg = bored + "\n\n" + name + infosMsg + optionHeader + menu
        bot.send_message(userId, msg)
    except KeyError:
        msg = GetWebsiteChangedMsg()
        bot.send_message(userId, msg)

def ScrapFinancialCashFlow(userId):
    try:
        stock = GetUserStock(userId)

        details = GetStockSummaryDetails(stock)
        name = GetStockName(stock)
        
        data = details['financialData']

        bored = GetBored()

        infosMsg = ""
        infos = []

        if 'operatingCashflow' in data and 'fmt' in data['operatingCashflow']:
            infos.append("\nOperating Cash Flow (ttm): " + data['operatingCashflow']['fmt'])
        if 'freeCashflow' in data and 'fmt' in data['freeCashflow']:
            infos.append("\nLevered Free Cash Flow (ttm): " + data['freeCashflow']['fmt'])

        for info in infos:
            infosMsg = infosMsg + info

        if infosMsg == "":
            infosMsg = "Company did not give such data~ so, I have no such information~"
        optionHeader = "\n\n" + GetOptionHeader()
        menu = GetFinancialMenu()

        msg = bored + "\n\n" + name + infosMsg + optionHeader + menu
        bot.send_message(userId, msg)
    except KeyError:
        msg = GetWebsiteChangedMsg()
        bot.send_message(userId, msg)

def ScrapTrading(userId):
    bored = GetBored()
    optionHeader = "\n\n" + GetOptionHeader()
    optionsMsg = GetTradingMenu()
    name = GetStockName(GetUserStock(userId))

    msg = bored + "\n\n" + name + optionHeader + optionsMsg
    bot.send_message(userId, msg)
    EditUsers(userId, USER_PROGRESS, PROGRESS_SCRAPTRADING)

def ScrapTradingPriceHistory(userId):
    try:
        stock = GetUserStock(userId)

        details = GetStockSummaryDetails(stock)
        name = GetStockName(stock)
        
        summary = details['summaryDetail']
        stat = details['defaultKeyStatistics']

        bored = GetBored()

        infosMsg = ""
        infos = []

        if 'beta' in summary and 'fmt' in summary['beta']:
            infos.append("\nBeta (3Y Monthly): " + summary['beta']['fmt'])
        if '52WeekChange' in stat and 'fmt' in stat['52WeekChange']:
            infos.append("\n52-Week Change: " + stat['52WeekChange']['fmt'])
        if 'SandP52WeekChange' in stat and 'fmt' in stat['SandP52WeekChange']:
            infos.append("\nS&P500 52-Week Change: " + stat['SandP52WeekChange']['fmt'])
        if 'fiftyTwoWeekHigh' in summary and 'fmt' in summary['fiftyTwoWeekHigh']:
            infos.append("\n52 Week High: " + summary['fiftyTwoWeekHigh']['fmt'])
        if 'fiftyTwoWeekLow' in summary and 'fmt' in summary['fiftyTwoWeekLow']:
            infos.append("\n52 Week Low: " + summary['fiftyTwoWeekLow']['fmt'])
        if 'fiftyDayAverage' in summary and 'fmt' in summary['fiftyDayAverage']:
            infos.append("\n50-Day Moving Average: " + summary['fiftyDayAverage']['fmt'])
        if 'twoHundredDayAverage' in summary and 'fmt' in summary['twoHundredDayAverage']:
            infos.append("\n200-Day Moving Average: " + summary['twoHundredDayAverage']['fmt'])

        for info in infos:
            infosMsg = infosMsg + info

        if infosMsg == "":
            infosMsg = "Company did not give such data~ so, I have no such information~"
        optionHeader = "\n\n" + GetOptionHeader()
        menu = GetTradingMenu()

        msg = bored + "\n\n" + name + infosMsg + optionHeader + menu
        bot.send_message(userId, msg)
    except KeyError:
        msg = GetWebsiteChangedMsg()
        bot.send_message(userId, msg)

def ScrapTradingShareStat(userId):
    try:
        stock = GetUserStock(userId)

        details = GetStockSummaryDetails(stock)
        name = GetStockName(stock)
        
        summary = details['summaryDetail']
        stat = details['defaultKeyStatistics']

        bored = GetBored()

        infosMsg = ""
        infos = []

        if 'averageVolume' in summary and 'fmt' in summary['averageVolume']:
            infos.append("\nAvg Vol (3 month): " + summary['averageVolume']['fmt'])
        if 'averageDailyVolume10Day' in summary and 'fmt' in summary['averageDailyVolume10Day']:
            infos.append("\nAvg Vol (10 day): " + summary['averageDailyVolume10Day']['fmt'])
        if 'sharesOutstanding' in stat and 'fmt' in stat['sharesOutstanding']:
            infos.append("\nShares Outstanding: " + stat['sharesOutstanding']['fmt'])
        if 'floatShares' in stat and 'fmt' in stat['floatShares']:
            infos.append("\nFloat: " + stat['floatShares']['fmt'])
        if 'heldPercentInsiders' in stat and 'fmt' in stat['heldPercentInsiders']:
            infos.append("\n% Held by Insiders: " + stat['heldPercentInsiders']['fmt'])
        if 'heldPercentInstitutions' in stat and 'fmt' in stat['heldPercentInstitutions']:
            infos.append("\n% Held by Institutions: " + stat['heldPercentInstitutions']['fmt'])
        if 'sharesShort' in stat and 'fmt' in stat['sharesShort']:
            infos.append("\nShares Short: " + stat['sharesShort']['fmt'])
        if 'shortRatio' in stat and 'fmt' in stat['shortRatio']:
            infos.append("\nShort Ratio: " + stat['shortRatio']['fmt'])
        if 'shortPercentOfFloat' in stat and 'fmt' in stat['shortPercentOfFloat']:
            infos.append("\nShort % " + "of Float: " + stat['shortPercentOfFloat']['fmt'])
        if 'sharesShortPriorMonth' in stat and 'fmt' in stat['sharesShortPriorMonth']:
            infos.append("\nShares Short (prior month): " + stat['sharesShortPriorMonth']['fmt'])

        for info in infos:
            infosMsg = infosMsg + info

        if infosMsg == "":
            infosMsg = "Company did not give such data~ so, I have no such information~"
        optionHeader = "\n\n" + GetOptionHeader()
        menu = GetTradingMenu()

        msg = bored + "\n\n" + name + infosMsg + optionHeader + menu
        bot.send_message(userId, msg)
    except KeyError:
        msg = GetWebsiteChangedMsg()
        bot.send_message(userId, msg)

def ScrapTradingShareDividendsSplit(userId):
    try:
        stock = GetUserStock(userId)

        details = GetStockSummaryDetails(stock)
        name = GetStockName(stock)
        
        summary = details['summaryDetail']
        stat = details['defaultKeyStatistics']
        calendar = details['calendarEvents']

        bored = GetBored()

        infosMsg = ""
        infos = []

        if 'dividendRate' in summary and 'fmt' in summary['dividendRate']:
            infos.append("\nForward Annual Dividend Rate: " + summary['dividendRate']['fmt'])
        if 'dividendYield' in summary and 'fmt' in summary['dividendYield']:
            infos.append("\nForward Annual Dividend Yield: " + summary['dividendYield']['fmt'])
        if 'trailingAnnualDividendRate' in summary and 'fmt' in summary['trailingAnnualDividendRate']:
            infos.append("\nTrailing Annual Dividend Rate: " + summary['trailingAnnualDividendRate']['fmt'])
        if 'trailingAnnualDividendYield' in summary and 'fmt' in summary['trailingAnnualDividendYield']:
            infos.append("\nTrailing Annual Dividend Yield: " + summary['trailingAnnualDividendYield']['fmt'])
        if 'fiveYearAvgDividendYield' in summary and 'fmt' in summary['fiveYearAvgDividendYield']:
            infos.append("\n5 Year Average Dividend Yield: " + summary['fiveYearAvgDividendYield']['fmt'])
        if 'payoutRatio' in summary and 'fmt' in summary['payoutRatio']:
            infos.append("\nPayout Ratio: " + summary['payoutRatio']['fmt'])
        if 'dividendDate' in calendar and 'fmt' in calendar['dividendDate']:
            infos.append("\nDividend Date: " + calendar['dividendDate']['fmt'])
        if 'exDividendDate' in calendar and 'fmt' in calendar['exDividendDate']:
            infos.append("\nEx-Dividend Date: " + calendar['exDividendDate']['fmt'])
        if 'lastSplitFactor' in stat and stat['lastSplitFactor'] != None:
            infos.append("\nLast Split Factor (new per old): " + stat['lastSplitFactor'])
        if 'lastSplitDate' in stat and 'fmt' in stat['lastSplitDate']:
            infos.append("\nLast Split Date: " + stat['lastSplitDate']['fmt'])

        for info in infos:
            infosMsg = infosMsg + info

        if infosMsg == "":
            infosMsg = "Company did not give such data~ so, I have no such information~"
        optionHeader = "\n\n" + GetOptionHeader()
        menu = GetTradingMenu()

        msg = bored + "\n\n" + name + infosMsg + optionHeader + menu
        bot.send_message(userId, msg)
    except KeyError:
        msg = GetWebsiteChangedMsg()
        bot.send_message(userId, msg)

def ScrapHistory(userId):
    bored = GetBored()
    name = GetStockName(GetUserStock(userId))
    intro = GetHistoryIntro()
    msg = bored + "\n\n" + name + "\n\n" + intro
    bot.send_message(userId, msg)
    EditUsers(userId, USER_PROGRESS, PROGRESS_HISTORY)

# functions
def Start(userId):
    EditUsers(userId, USER_PROGRESS, "")
    EditUsers(userId, USER_STOCK, "")
    msg = GetIntro()
    bot.send_message(userId, msg)

def HandleUpdates():
    lastMsgId = GetLastMsgId()
    updates = bot.getUpdates(offset=lastMsgId)
    updates = [update for update in updates if GetMsgId(update) > lastMsgId ]
    if (len(updates) > 0):
        for update in updates:
            msg = GetMsg(update)
            msgId = GetMsgId(update)
            userId = GetUserId(update)
            HandleMsg(userId, msg)
            UpdateLastMsgId(msgId)
            
def HandleMsg(userId, msg):
    progress = GetUserProgress(userId)

    if IsCommand(msg):
        HandleCommand(userId, msg)
    elif progress == PROGRESS_SCRAPSTOCK:
        HandleScrapStockOption(userId, msg)
    elif progress == PROGRESS_SCRAPFINANCE:
        HandleScrapFinanceOption(userId, msg)
    elif progress == PROGRESS_SCRAPTRADING:
        HandleScrapTradingOption(userId, msg)
    elif progress == PROGRESS_HISTORY:
        HandleScrapHistory(userId, msg)

    elif IsInt(msg):
        HandleInt(userId, msg)
    else:
        HandleKeyword(userId, msg)

def HandleCommand(userId, msg):
    if msg == "/start" or msg == "/exit":
        Start(userId)
    else:
        msg = 'Sorry I am so stupid, I cannot handle what you say.'
        bot.send_message(userId, msg)

def HandleInt(userId, msg):
    ScrapStockPrice(userId, msg) 

def HandleScrapStockOption(userId, msg):
    try:
        i = int(msg)
        if i == 1:
            ScrapValuation(userId)
        elif i == 2:
            ScrapFinancial(userId) 
        elif i == 3:
            ScrapTrading(userId)
        elif i == 4:
            ScrapHistory(userId)
        elif i == 5:
            Start(userId)
        else:
            msg = GetOutOfIndexMsg()
            bot.send_message(userId, msg)
    except ValueError:
        msg = GetNotIntMsg()
        bot.send_message(userId, msg)

def HandleScrapFinanceOption(userId, msg):
    try:
        i = int(msg)
        if i == 1:
            ScrapFinancialFiscalYear(userId)
        elif i == 2:
            ScrapFinancialProfitability(userId)
        elif i == 3:
            ScrapFinancialManagement(userId)
        elif i == 4:
            ScrapFinancialIncomeStatement(userId)
        elif i == 5:
            ScrapFinancialBalanceSheet(userId)
        elif i == 6:
            ScrapFinancialCashFlow(userId)
        elif i == 7:
            ScrapStockPrice(userId, GetUserStock(userId))
        else:
            msg = GetOutOfIndexMsg()
            bot.send_message(userId, msg)
    except ValueError:
        msg = GetNotIntMsg()
        bot.send_message(userId, msg)

def HandleScrapTradingOption(userId, msg):
    try:
        i = int(msg)
        if i == 1:
            ScrapTradingPriceHistory(userId)
        elif i == 2:
            ScrapTradingShareStat(userId)
        elif i == 3:
            ScrapTradingShareDividendsSplit(userId)
        elif i == 4:
            ScrapStockPrice(userId, GetUserStock(userId))
        else:
            msg = GetOutOfIndexMsg()
            bot.send_message(userId, msg)
    except ValueError:
        msg = GetNotIntMsg()
        bot.send_message(userId, msg)

def HandleScrapHistory(userId, msg):
    try:
        d = datetime.strptime(msg,'%Y-%m-%d')
        price = GetStockHistoryPrice(GetUserStock(userId), int(d.timestamp()) + 34200)
        if price != None and 'date' in price:
            infos = ""
            if 'open' in price and price['open'] != None:
                infos += "\nOpen: " + str("{:10.3f}".format(price['open']))
            if 'high' in price and price['high'] != None:
                infos += "\nHigh: " + str("{:10.3f}".format(price['high']))
            if 'low' in price and price['low'] != None:
                infos += "\nLow: " + str("{:10.3f}".format(price['low']))
            if 'close' in price and price['close'] != None:
                infos += "\nClose: " + str("{:10.3f}".format(price['close']))
            if 'adjclose' in price and price['adjclose'] != None:
                infos += "\nAdj Close: " + str("{:10.3f}".format(price['adjclose']))
            if 'volume' in price and price['volume'] != None:
                infos += "\nVolume: " + str(price['volume'])
            if infos == "":
                infos = "There is nothing in this date. Sorry."
            bored = GetBored()
            name = GetStockName(GetUserStock(userId))
            msg = bored + "\n\n" + name + infos + "\n\n" + GetHistoryIntro()
            bot.send_message(userId, msg)
        else:
            msg = GetNosuchDateMsg()
            bot.send_message(userId, msg)
    except ValueError:
        msg = GetNotDateFormatMsg()
        bot.send_message(userId, msg)

def HandleKeyword(userId,msg):
    msg = 'Sorry I am so stupid, I cannot handle what you say.'
    bot.send_message(userId, msg)
    
def main():
    global BORN
    BORN = int(round(time.time() * 1000))
    while True:
        HandleUpdates()

if __name__ == "__main__":
    main()