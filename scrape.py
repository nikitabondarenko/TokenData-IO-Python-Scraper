#!/usr/bin/env python
import sys
import os
import argparse
import time
from datetime import datetime
from random import random
import logging
import pandas as pd
import lxml.html #Faster than Beatuiful Soup
from lxml import etree

from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException


parser = argparse.ArgumentParser(description='Scraping Tokens and Coins')
parser.add_argument('min_USD_Raised', metavar='min_cap', type=int, nargs='?', default=0,
                   help='minimum market cap [usd] for currency to be scraped (default: scrape all)')
parser.add_argument('max_date', metavar='max_date', type=str, nargs='?', default="Dec 2015",
                   help='Get all coin founded after this data. Example: Dec 2015, (default: scrape all)')

args = parser.parse_args([])

# Configuration
timestamp_0 = 1367174841000
timestamp_1 = int(round(time.time() * 1000))
logging.basicConfig(
    filename="logging.log", 
    level=logging.INFO, 
    format='%(asctime)s:%(name)s:%(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')

BASE_URL = "https://www.tokendata.io"

countRequested = 0
interReqTime = 23
lastReqTime = None

def htmlRequest(targetURL):
    global countRequested
    global lastReqTime
    if lastReqTime is not None and time.time() - lastReqTime < interReqTime:
        timeToSleep = random()*(interReqTime-time.time()+lastReqTime)*2
        logging.info("Sleeping for {0} seconds before request.".format(timeToSleep))
        time.sleep(timeToSleep)

    option = webdriver.ChromeOptions()
    option.add_argument('--incognito')

    browser = webdriver.Chrome(executable_path='chromedriver', chrome_options=option)
    browser.get(targetURL)
    wait = WebDriverWait(browser, 10)
    rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='sample_1']/tbody/tr")))

    data = []
    for row in rows:
        datum = {}
        info = row.find_elements(By.TAG_NAME, "td")
        datum["name"] = info[1].text
        try:
            datum['usd_raised'] = float(info[2].text.strip().replace(",", "")[1:])
        except:
            datum['usd_raised'] = 0

        datum['month'] = info[3].text

        try:
            datum['token_sale_price'] = float(info[4].text.strip().replace(",", "")[1:])
        except:
            datum['token_sale_price'] = 0
        try:
            datum['current_token_price'] = float(info[5].text.strip().replace(",", "")[1:])
        except:
            datum['current_token_price'] = 0

        datum['token_return'] = info[6].text 
        datum['eth_return'] = info[7].text 
        datum['btc_return'] = info[8].text 
        datum['token/eth_return'] = info[9].text 
        datum['token/btc_return'] = info[10].text

        if args.min_USD_Raised < datum['usd_raised']:
            data.append(datum)

    #print(rows[0].find_elements(By.TAG_NAME, "td")[1].text)
    #print(rows[len(rows)-1].find_elements(By.TAG_NAME, "td")[1].text)

    count = 0
    while count < 10:
        previousFirst = rows[0].find_elements(By.TAG_NAME, "td")[1].text
        previousLast = rows[len(rows)-1].find_elements(By.TAG_NAME, "td")[1].text

        step = int(len(rows)-15) 
        browser.execute_script("return arguments[0].scrollIntoView(true);", rows[step])
        #wait for the browser to load after scroll
        time.sleep(1)

        rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='sample_1']/tbody/tr")))

        #print(len(rows))
        #print(rows[0].find_elements(By.TAG_NAME, "td")[1].text)
        #print(rows[len(rows)-1].find_elements(By.TAG_NAME, "td")[1].text)
        currentFirst = rows[0].find_elements(By.TAG_NAME, "td")[1].text
        currentLast = rows[len(rows)-1].find_elements(By.TAG_NAME, "td")[1].text
        if previousLast != currentLast:
            overlappingIndex = 0
            #find overlapping
            for index in range(0,len(rows)):
                currentName = rows[index].find_elements(By.TAG_NAME, "td")[1].text
                if previousLast == currentName:
                    overlappingIndex = index
                    break;

            for index in range(overlappingIndex+1, len(rows)):
                datum = {}
                info = rows[index].find_elements(By.TAG_NAME, "td")
                datum["name"] = info[1].text
                try:
                    datum['usd_raised'] = float(info[2].text.strip().replace(",", "")[1:])
                except:
                    datum['usd_raised'] = 0
                datum['month'] = info[3].text
                try:
                    datum['token_sale_price'] = float(info[4].text.strip().replace(",", "")[1:])
                except:
                    datum['token_sale_price'] = 0
                try:
                    datum['current_token_price'] = float(info[5].text.strip().replace(",", "")[1:])
                except:
                    datum['current_token_price'] = 0

                datum['token_return'] = info[6].text 
                datum['eth_return'] = info[7].text 
                datum['btc_return'] = info[8].text 
                datum['token/eth_return'] = info[9].text 
                datum['token/btc_return'] = info[10].text 
                # print(info[1].text)
                if args.min_USD_Raised < datum['usd_raised']:
                    data.append(datum)

        else:
            break
        count += 1

    return data


def scrapeAdvanceDataList():
    URL = "{0}/{1}".format(BASE_URL, 'advanced')
    data = htmlRequest(URL)
    return data

def filterTimeFrom(df):
    dataString = args.max_date
    print(dataString)
    number = args.max_date[:len(args.max_date)-1]
    suffix = args.max_date[-1].upper()
    if number.isdigit(): 
        number = int(num)
    else:
        logging.info("invalid max_date")
        sys.exit()
    if suffix.isdigit():
        logging.info("invalid max_date")
        sys.exit()

    if suffix == "D":
        d = datetime.timedelta(day=number)
    else:
        logging.info("invalid string. Please retry with Y,M,D only.")
        sys.exit()

    threeMonth = df['time'].iloc[-1] - d
    df = df[df['time']>threeMonth]

    print(df.describe())
    
def main():
    data = scrapeAdvanceDataList()
    df = pd.DataFrame(data)
    df.to_csv("{0}.csv".format("dataTokenAdvance"), sep=',', index=False)

def testing():
    #Custom Testing

    # html_source = browser.page_source
    # root = etree.Element(html_source)
    # print(etree.tostring(root, pretty_print=True))

    # html = lxml.html.fromstring(html_source)
    # rows = html.cssselect("table > tbody > tr")

    # for row in rows:
    #     fields = row.cssselect('td')
    #     try:
    #         name = fields[1].cssselect("span")[0].text_content().strip()
    #     except:
    #         name = fields[1].text_content().strip()
        #print(name)

    # data = []
    # count = 0
    # while count<= 5:
        # if(data != [] and data[-1] == last):
        #     count += 1
        # else:
        #     count = 0
        #     table = browser.find_elements_by_xpath("//*[@id='sample_1']/tbody")[0]
        #     total_rows = table.find_elements(By.TAG_NAME, "tr")
        #     for row in total_rows:
        #         col = row.find_elements(By.TAG_NAME, "td")[1]
        #         print(col.text)
        #     last = total_rows[-1].find_elements(By.TAG_NAME, "td")[1]

        # table = browser.find_element_by_xpath("//*[@id='sample_1']/tbody")
        # total_rows = table.find_elements(By.TAG_NAME, "tr")

        # print(total_rows[0].find_elements(By.TAG_NAME, "td")[1].text)
        # print(total_rows[len(total_rows)-1].find_elements(By.TAG_NAME, "td")[1].text)

        # for row in total_rows:
        #     col = row.find_elements(By.TAG_NAME, "td")[1]
        #     print(col.text)


        # break

        # past = total_rows[-1].find_elements(By.TAG_NAME, "td")[1].text
        # current = total_rows[-1].find_elements(By.TAG_NAME, "td")[1].text
        # index = 1
        # while current == past:
        #     browser.execute_script("return arguments[0].scrollIntoView(true);", total_rows[index])
        #     time.sleep(0.2)
        #     table = browser.find_element_by_xpath("//*[@id='sample_1']/tbody")
        #     total_rows = table.find_elements(By.TAG_NAME, "tr")
        #     current = total_rows[-1].find_elements(By.TAG_NAME, "td")[1].text
        #     index += 1

        # print("_________________________________________ENDING")
        # print(total_rows[0].find_elements(By.TAG_NAME, "td")[1].text)
        # print(total_rows[-1].find_elements(By.TAG_NAME, "td")[1].text)


    # lastReqTime = time.time()
    # countRequested += 1
    # if r.status_code == requests.codes.ok:
    #     return r.text
    # else:
    #     raise Exception("Could not process request. \
    #         Received status code {0}.".format(r.status_code))
    return 

if __name__=='__main__':
    main()
    #testing()