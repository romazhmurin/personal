from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs

import lxml
import time
import os

import pandas as pd
import numpy as np
import datetime



def loadALLInfo(driver, requestKeys, keyName):
    keyErrors = np.asarray([])
    url = 'https://api.vin.transdekra.com/?login=sogaz&pass=******&output=PreviewXML&'+keyName+'=' + requestKeys[0]
    driver.get(url)
    elem = driver.find_element(By.TAG_NAME, 'pre')
    page_source = elem.text
    bs_content = bs(page_source, "lxml")

    cols = bs_content.find_all('fieldrus')
    cols = np.concatenate((keyName, np.array(cols).flatten()), axis=None)
    res = bs_content.find_all('fieldvalue')
    res = np.insert(np.array(res, dtype=object).flatten(), 0, requestKeys[0])
    res = np.char.replace(
                    np.char.replace(np.array(list(map(str, np.array(res, dtype=object)))), 
                                                                                    '<fieldvalue>', ''),
                                                                                            '</fieldvalue>', '')
    df = pd.DataFrame([res], columns = cols)
    for keys in requestKeys:
        url = 'https://api.vin.transdekra.com/?login=sogaz&pass=******&output=PreviewXML&'+keyName+'=' + keys
        driver.get(url)
        elem = driver.find_element(By.TAG_NAME, 'pre')
        page_source = elem.text
        bs_content = bs(page_source, "lxml")

        cols = bs_content.find_all('fieldrus')
        cols = np.concatenate((keyName, np.array(cols).flatten()), axis=None)
        res = bs_content.find_all('fieldvalue')
        res = np.array(res, dtype=object).flatten()
        if len(res) != 0:
            res = np.insert(res, 0, keys)
            res = np.char.replace(
                            np.char.replace(np.array(list(map(str, np.array(res, dtype=object)))), 
                                                                                            '<fieldvalue>', ''),
                                                                                                    '</fieldvalue>', '')

            df = df.append(pd.DataFrame([res], columns=cols), ignore_index=True)
        else:
            keyErrors = np.append(keyErrors, keys)
    return keyErrors, df


def extractDataKeys(mask):
    requestKeys = []
    path = os.getcwd()
    with open(path + '\\ '.strip() + mask + '.txt', encoding='utf-8') as file:
        for line in file:
            if line != '':
                requestKeys.append(line.rstrip())
    requestKeys = list(filter(None, requestKeys))
    return requestKeys


requestKeysVIN = extractDataKeys('VIN')
requestKeysBODY = extractDataKeys('BODY')

s = Service(r'C:\Users\Zhmurin.Roman\Anaconda3\Scripts\geckodriver.exe')
driver = webdriver.Firefox(service=s)

keyName = 'CODE_VIN'
keyErrorsVINRes, dataResVIN = loadALLInfo(driver, requestKeysVIN, keyName)
dataToSaveVIN = dataResVIN[[keyName, 'Тип транспортного средства', 'Мощность двигателя (л.с.)',
                             'Область', 'Проиводитель', 'Страна', 'Дата первичной регистрации',
                             'Дата последней регистрации', 'Год производства',
                             'Тип кузова ТС', 'Количество владельцев']]
conv_to_string = [str(x) for x in dataToSaveVIN['Год производства']]
dataToSaveVIN['Год производства'] = conv_to_string
dataToSaveVIN['Год производства'] = pd.to_datetime(dataToSaveVIN['Год производства']).dt.year

dataToSaveVIN.to_excel(keyName + '.xlsx', index=False)

keyName = 'BODY_NUM'
keyErrorsBODYRes, dataResBODY = loadALLInfo(driver, requestKeysBODY, keyName)
#driver.close()
dataToSaveBODY = dataResBODY[[keyName, 'Тип транспортного средства', 'Мощность двигателя (л.с.)',
                             'Область', 'Проиводитель', 'Страна', 'Дата первичной регистрации',
                             'Дата последней регистрации', 'Год производства',
                             'Тип кузова ТС', 'Количество владельцев']]
conv_to_string = [str(x) for x in dataToSaveBODY['Год производства']]
dataToSaveBODY['Год производства'] = conv_to_string
dataToSaveBODY['Год производства'] = pd.to_datetime(dataToSaveBODY['Год производства']).dt.year

dataToSaveBODY.to_excel(keyName + '.xlsx', index=False)

driver.close()
