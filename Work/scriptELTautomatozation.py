import pyodbc
import os
import shutil
import time
import win32com.client
import win32con, win32gui
from pathlib import Path

from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def clearOldFiles(pathToData, pathToLogs, pathBulk, pyLogs):
    pyLogs.write('Очистка папок запущена ' + str(datetime.now()) + '\n')
    # pathToData = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\1_Внешняя обработка\Данные\1_Без Модели'
    # pathToLogs = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\1_Внешняя обработка\Логи\1_Без Модели'
    # pathBulk = r'\\s00-0000-vsq9\BulkFiles\Zhmurin\Пролонгация'
    for root, dirs, files in os.walk(pathToData): # Данные С
        for file in files:
            print(pathToData + '\ '.strip() + file)
            os.remove(pathToData + '\ '.strip() + file)

    for root, dirs, files in os.walk(pathToLogs): # Логи С
        for file in files:
            print(pathToLogs + '\ '.strip() + file)
            os.remove(pathToLogs + '\ '.strip() + file)

    for root, dirs, files in os.walk(pathBulk): # Данные Bulk
        for file in files:
            print(pathBulk + '\ '.strip() + file)
            os.remove(pathBulk + '\ '.strip() + file)
    pyLogs.write('Очистка папок выполнена ' + str(datetime.now()) + '\n')


def download1C(date_today, pathAndFile, pathToDir, pathToLogs, pyLogs):
    pyLogs.write('Выгрузка 1С запущена ' + str(datetime.now()) + '\n')
    # date_today = datetime.today().date()
    date_start = (date_today - relativedelta(months=2)).month
    # pathAndFile = r'"C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\Отчет по пролонгации\1_Внешняя обработка\Скрипт\1_Без Модели\Процент Пролонгации_ОСАГО_2022.'
    # pathToDir = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\Отчет по пролонгации\1_Внешняя обработка\Скрипт\1_Без Модели'
    os.chdir(pathToDir)
    logsArray = []
    for importDate in range(date_start, date_start + 5):  # date_start, date_start + 5
        if importDate <= 12:
            importMonth = '{:02d}'.format(importDate)
            pyLogs.write('importMonth: ' + str(importMonth) + '\n')
            logsArray.append('Пролонгация_2022_' + importMonth + '_LOG_End.txt')
            os.system('cmd /c ' + pathAndFile + importMonth + '.vbs"')
        else:#
            importMonth = '{:02d}'.format(importDate % 12)
            pyLogs.write('importMonth:' + str(importMonth) + '\n')
            logsArray.append('Пролонгация_2022_' + importMonth + '_LOG_End.txt')
            os.system('cmd /c ' + pathAndFile + importMonth + '.vbs"')

    pyLogs.write(str(logsArray) + '\n')
    pyLogs.flush()
    os.fsync(pyLogs.fileno())
    flag = True
    # pathToLogs = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\1_Внешняя обработка\Логи\1_Без Модели'
    while flag:
        for root, dirs, files in os.walk(pathToLogs):
            if set(logsArray).issubset(set(files)):
                flag = False
            else:
                continue
        pyLogs.write('Ожидание. Сон 5 минут.' + '\n')
        pyLogs.flush()
        os.fsync(pyLogs.fileno())
        time.sleep(360)
    pyLogs.write('Выгрузка 1С выполнена ' + str(datetime.now()) + '\n')


def fromCToBulk(pathToData, pathBulk, pyLogs):
    pyLogs.write('Перенос с С на Bulk запущен ' + str(datetime.now()) + '\n')
    pyLogs.flush()
    os.fsync(pyLogs.fileno())
    # pathToData = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\1_Внешняя обработка\Данные\1_Без Модели'
    # pathBulk = r'\\s00-0000-vsq9\BulkFiles\Zhmurin\Пролонгация'
    for root, dirs, files in os.walk(pathToData):
        for file in files:
            # print(pathToData + '\ '.strip() + file)
            print('Перенесен: ', file)
            shutil.copy(pathToData + '\ '.strip() + file, pathBulk)
    pyLogs.write('Перенос с С на Bulk выполнен ' + str(datetime.now()) + '\n')


def sqlStartScript(sql, pyLogs):
    pyLogs.write('SQL запущен ' + str(datetime.now()) + '\n')
    pyLogs.flush()
    os.fsync(pyLogs.fileno())
    with pyodbc.connect(Driver='{ODBC Driver 17 for SQL Server}',Server='S00-0000-VSQ9\VSQ9',database='Auto',Trusted_connection='yes') as conn:
        with conn.cursor() as cursor:
            #sql = """EXEC [dbo].[OSAGO_Пролонгация_0_step_autoscript]"""
            cursor.execute(sql)
            conn.commit()
    pyLogs.write('SQL выполнен ' + str(datetime.now()) + '\n')


def OLAPCubeUpdate(connection_string, query, pyLogs):
    pyLogs.write('OLAP старт ' + str(datetime.now()) + '\n')
    pyLogs.flush()
    os.fsync(pyLogs.fileno())
    conn = win32com.client.Dispatch('ADODB.Connection')
    conn.CommandTimeout = 0
    conn.Open(connection_string)

    rs = win32com.client.Dispatch('ADODB.RecordSet')
    rs.Open(query, conn)
    pyLogs.write('OLAP конец ' + str(datetime.now()) + '\n')


def excelRefresh(fileLink, pyLogs):
    excel = win32com.client.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = True

    # fileLink = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\Отчет по пролонгации\4_Файл\Отчет_Пролонгация_Olap - Копия Test.xlsx'
    wb = excel.Workbooks.Open(fileLink)
    for sheet in wb.Sheets:
        print(sheet.Name)
        for i in range(1, 10):
            try:
                pyLogs.write("Найдено: %s" % sheet.PivotTables(i).Name + '\n')
                if sheet.PivotTables(i).RefreshTable() == True:
                    pyLogs.write("\t++Обновлено: %s" % sheet.PivotTables(i).Name + '\n')
                else:
                    pyLogs.write("Ошибка обновления: %s" % sheet.PivotTables(i).Name + '\n')
            except:
                # print("No pivot table #%s found on sheet %s" % (i,sheet.Name))
                break


#######################################################################################################################
pyLogsFile = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\Отчет по пролонгации\5_Автоматизация'
pyLogs = open(pyLogsFile + '\ '.strip() + 'logs.txt', "a")
pyLogs.write('************************** Логи выгрузка от ' + str(datetime.now()) + '**************************\n')
pyLogs.flush()
os.fsync(pyLogs.fileno())

# Очистка Диска С
pathToData = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\1_Внешняя обработка\Данные\1_Без Модели'
pathToLogs = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\1_Внешняя обработка\Логи\1_Без Модели'
pathBulk = r'\\s00-0000-vsq9\BulkFiles\Zhmurin\Пролонгация'

clearOldFiles(pathToData, pathToLogs, pathBulk, pyLogs)

pyLogs.flush()
os.fsync(pyLogs.fileno())

# 1C Выгрузка
date_today = datetime.today().date()
pathAndFile = r'"C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\Отчет по пролонгации\1_Внешняя обработка\Скрипт\1_Без Модели\Процент Пролонгации_ОСАГО_2022.'
pathToDir = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\Отчет по пролонгации\1_Внешняя обработка\Скрипт\1_Без Модели'
pathToLogs = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\1_Внешняя обработка\Логи\1_Без Модели'

download1C(date_today, pathAndFile, pathToDir, pathToLogs, pyLogs)

pyLogs.flush()
os.fsync(pyLogs.fileno())

# Перенос из Диска С на сервер bulkfiles
pathToData = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\1_Внешняя обработка\Данные\1_Без Модели'
pathBulk = r'\\s00-0000-vsq9\BulkFiles\Zhmurin\Пролонгация'

fromCToBulk(pathToData, pathBulk, pyLogs)
pyLogs.flush()
os.fsync(pyLogs.fileno())


# SQL обработка
sql = """EXEC [dbo].[OSAGO_Пролонгация_0_step_autoscript]"""

sqlStartScript(sql, pyLogs)
pyLogs.flush()
os.fsync(pyLogs.fileno())


# Запуск обновления куба в MVS
connection_string = """Provider=MSOLAP.6;
                        Integrated Security=SSPI;
                        Persist Security Info=True;
                        Initial Catalog=********;
                        Data Source=*********;
                        MDX Compatibility=1;
                        Safety Options=2;
                        MDX Missing Member Mode=Error"""

query = """*******"""

OLAPCubeUpdate(connection_string, query, pyLogs)

# Обновление Excel
fileLink = r'C:\Users\Zhmurin.Roman\Работа\Диск С\2022\Отчет по пролонгации\Отчет по пролонгации\4_Файл\Отчет_Пролонгация_Olap - Копия Test.xlsx'

excelRefresh(fileLink, pyLogs)
pyLogs.flush()
os.fsync(pyLogs.fileno())
