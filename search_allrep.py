from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import random

# optional first step, define the driver, ie chrome or Brave
driver = webdriver.Chrome('./chromedriver 2')

# define dataset
df = pd.read_csv('taxdlq_subset.csv',index_col=0)

#df = df[0:500]

df['2020_Status'] = ''
df['2020_TtlTaxDue'] = ''
df['Mkt_Value'] = ''
df['Yrs_Unpaid'] = 0
df['Type'] = ''
df['Use'] = ''
df['Yr_Bought'] = ''
df['Owner_Code'] = ''

#i = 25

for i in df.index:
    time.sleep(random.randint(1,3))

    print(i)

    #open web page
    driver.get('http://www2.alleghenycounty.us/RealEstate/search.aspx')

    # identify the button to choose "search by parcel ID"
    parcel_button = driver.find_element_by_id('radio1_1')

    # click that button
    parcel_button.click()

    time.sleep(2)

    # identify the parcel ID search box
    search_parcel = driver.find_element_by_name('txtParcelIDFull')

    # give it an input
    search_parcel.send_keys(df.loc[i,'ID']) #  <<-- later change this to an iterative process

    # identify the search button
    search_button = driver.find_element_by_name('btnSearch')

    # click the search button //*[@id="lblTaxInfo"]/table/tbody/tr[2]/td[2]
    search_button.click()

    time.sleep(1)

    #   ~~~~~ RECORD CLASS, USE_CODE AND SALE_DATE

    # DONT ENTER INTO DATAFRAME UNTIL LATER
    url = driver.current_url
    #print(url)

    if url == 'http://www2.alleghenycounty.us/RealEstate/search.aspx':
        print(f'Parcel ID does not match entry {i}')
        df.loc[i, '2020_Status'] = 'ParcelIDNotValid'

        continue

    try:
        driver.find_element_by_id('lblState')

    except NoSuchElementException:
        print('Parcel does not exist')
        df.loc[i, '2020_Status'] = 'ParcelNoLongerExists'

        continue

    # record class type for later addition to dataframe
    class_type = driver.find_element_by_id('lblState')
    class_type_text = class_type.text

    # record use_code type for later addition to dataframe
    use_type = driver.find_element_by_id('lblUse')
    use_type_text = use_type.text

    # record sale date for later addition to dataframe
    sale_date = driver.find_element_by_id('lblSaleDate')
    sale_date_text = sale_date.text

    # record owner_code for later addition to dataframe
    owner_code = driver.find_element_by_id('lblOwnerCode')
    owner_code_text = owner_code.text

    # identify the tax info header
    tax_info_box = driver.find_element_by_name('Header1$lnkTax')

    # click it
    tax_info_box.click()

    # pause to let the page load
    time.sleep(2)

    # -- identify tax data -- 

    # find just the most recent paid/unpaid status -- //*[@id="lblTaxInfo"]/table/tbody/tr[2]/td[2]
    paid_data1 = driver.find_element_by_xpath('//*[@id="lblTaxInfo"]/table/tbody/tr[2]/td[2]')
    paid_text1 = paid_data1.text

    # need to count the amount of values that do not equal 'PAID', then record that number
    unpaid_years = 0

    if paid_text1 != 'PAID':
        # find the second most recent year(2019) paid status
        # try except necessary because it will error out if the element does not exist
        try:
            driver.find_element_by_xpath('//*[@id="lblTaxInfo"]/table/tbody/tr[3]/td[2]')

        except NoSuchElementException:
            df.loc[i, 'Yrs_Unpaid'] = 1
            print('No 2nd year')
            continue

        paid_data2 = driver.find_element_by_xpath('//*[@id="lblTaxInfo"]/table/tbody/tr[3]/td[2]')
        paid_text2 = paid_data2.text

        # check year two
        if paid_text2 != 'PAID':
            # count the amount of unpaid years
            unpaid_years = 2

            # add the most recent tax status to the dataset
            df.loc[i, '2020_Status'] = paid_text1

            # find the amount of taxes due in 2020
            amt_taxes_data = driver.find_element_by_xpath('//*[@id="lblTaxInfo"]/table/tbody/tr[2]/td[3]/font')
            amt_taxes_text = amt_taxes_data.text        
            df.loc[i, '2020_TtlTaxDue'] = amt_taxes_text

            # Find the market value of the property
            mkt_value = driver.find_element_by_id('lblTaxValue')
            mkt_value_text = mkt_value.text
            df.loc[i, 'Mkt_Value'] =  mkt_value_text

            df.loc[i,'Type'] = class_type_text
            df.loc[i, 'Use'] = use_type_text
            df.loc[i, 'Yr_Bought'] = sale_date_text
            df.loc[i, 'Owner_Code']= owner_code_text

            
            print(df.loc[i,'Type'])
            print(df.loc[i,'Use'])
            print(df.loc[i,'Yr_Bought'])
            print(df.loc[i,'Mkt_Value'])
            

            try:
                driver.find_element_by_xpath('//*[@id="lblTaxInfo"]/table/tbody/tr[4]/td[2]')

            except NoSuchElementException:
                df.loc[i, 'Yrs_Unpaid'] = unpaid_years
                print('No 3rd year')
                continue

            paid_data3 = driver.find_element_by_xpath('//*[@id="lblTaxInfo"]/table/tbody/tr[4]/td[2]')
            paid_text3 = paid_data3.text

            if paid_text3 != 'PAID':
                unpaid_years += 1

            try:
                driver.find_element_by_xpath('//*[@id="lblTaxInfo"]/table/tbody/tr[5]/td[2]')

            except NoSuchElementException: 
                df.loc[i, 'Yrs_Unpaid'] = unpaid_years
                print('No 4th year')
                continue

            paid_data4 = driver.find_element_by_xpath('//*[@id="lblTaxInfo"]/table/tbody/tr[5]/td[2]')
            paid_text4 = paid_data4.text

            if paid_text4 != 'PAID':
                unpaid_years += 1

            df.loc[i, 'Yrs_Unpaid'] = unpaid_years
            print(df.loc[i,'Yrs_Unpaid'])
            

df.to_csv('search_allegheny_1500to2000.csv')

# close the driver
driver.quit()