from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl import load_workbook
import re
import time
import sys
import os
# https://github.com/birlurnou

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

start_time = time.time()

try:
    with open('user.txt', 'r') as f:
        content = f.readlines()
    user_login = content[0].strip()
    user_password = content[1].strip()
    if user_login == '' or user_password == '':
        exit()
except:
    exit()

def open_driver():

    options = Options()
    options.add_argument(f'--user-agent={custom_user_agent}')
    #options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    return driver

def get_cookie():
    try:
        driver.get(url)
        time.sleep(1)
        driver.implicitly_wait(10)
        username = driver.find_element(By.ID, 'loginform-username').send_keys(user_login)
        password = driver.find_element(By.ID, 'loginform-password').send_keys(user_password)
        time.sleep(20)
        login_button = driver.find_element(By.XPATH, '//*[@id="login-form"]/button').click()
        time.sleep(1)
        cookies = driver.get_cookies()
        return cookies

    except Exception as e:
        print(e)

def add_cookie(cookies):

    for cookie in cookies:
        driver.add_cookie(cookie)
    # print('Куки добавлены')
    driver.refresh()
    url_client = f'https://encoreiset.fitbase.io/clients'
    driver.get(url_client)

    try:
        driver.implicitly_wait(3)
        last_client = driver.find_element(By.XPATH, '''//*[@id="example"]/table/tbody/tr[1]/td[1]/input''').get_attribute('value')
        print(f"Количество клиентов: {last_client}")
    except:
        exit()
    finally:
        driver.quit()

    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    return last_client

def request(client_id):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Referer': f'https://encoreiset.fitbase.io/clients/?clientModal={client_id}',
            'x-requested-with': 'XMLHttpRequest'
        }
        response = s.get(f'''https://encoreiset.fitbase.io/clients/view?id={client_id}''', headers=headers)
        bs = BeautifulSoup(response.text,"lxml")

        name = bs.find('h1', 'client_name').text.split('\n')[1].strip()

        contracts = []
        contracts_code = []

        contract_id = bs.find_all('div', id=lambda x: x and x.startswith('contract_item-'))
        for j in contract_id:
            contract = j['id'].split('-')[1]
            contract_code = j['id'].split('-')[2]
            contracts.append(contract)
            contracts_code.append(contract_code)

        for i, j in zip(contracts, contracts_code):
            card_data = bs.find('div', id=f'contract_item-{i}-{j}')
            card_name_set = card_data.find('div', 'contract_item-name')
            card_name_data = card_name_set.text.strip().split('\n')[0]
            card_name = ' '.join(card_name_data.split())
            card_id_set = card_data.find('span', 'contract_item-id')
            # card_id = card_id_set.text.strip()
            card_id = card_id_set.text.replace('#', '').strip()

            table = card_data.find('table', 'table table-bordered table-striped table-hover')
            td_elements = table.find_all('td')
            abonement_list = []
            for k in range(0, len(td_elements), 2):
                label = td_elements[k].get_text(strip=True)
                value = td_elements[k + 1].get_text(strip=True)
                abonement_list.append((label, value))
            # card_id = abonement_list[0][1]
            date_payment = abonement_list[5][1]
            date_start = abonement_list[6][1]
            date_end = abonement_list[7][1]

            pattern = r"\d\d.\d\d.\d\d\d\d"
            if re.match(pattern, date_end):
                # print(date_end)
                # print(int(date_end.split('.')[2]))
                # print(int(date_end.split('.')[1]))
                # if (int(date_end.split('.')[2]) == 2025 and int(date_end.split('.')[1]) > 8) or (int(date_end.split('.')[2]) == 2025 and int(date_end.split('.')[1]) == 8 and int(date_end.split('.')[0]) >= 12) or int(date_end.split('.')[2]) > 2025:

                # if (int(date_end.split('.')[2]) == 2025 and int(date_end.split('.')[1]) > 8) or (
                #         int(date_end.split('.')[2]) == 2025 and int(date_end.split('.')[1]) == 8 and int(
                #         date_end.split('.')[0]) >= 12) or int(date_end.split('.')[2]) > 2025:
                a = 1
                b = 1
                # if int(date_end.split('.')[2]) >= 2025 or not int(date_end.split('.')[2]):
                # if a == b:
                if (int(date_end.split('.')[2]) == 2025 and int(date_end.split('.')[1]) >= 8) or int(date_end.split('.')[2]) > 2025 or not date_end:
                    # print(date_end)
                    # continue
            # abonement_price = abonement_list[9][1].split('из ')[1].split(',00')[0].strip().replace(' ','')

            # response2 = s.get(f'''https://encoreiset.fitbase.io/clients/freeze-stat?contract_id={i}&client_id={client_id}''')
            # bs2 = BeautifulSoup(response2.text, "lxml")
            # page_freeze = bs2.find_all('li', style='border-bottom: 0')

            # for f in page_freeze:
            #     if f.find('h2', 'title').text.strip().split(' ')[2] == 'на':
            #         days = f.find('h2', 'title').text.strip().split(' ')[3]
            #     else:
            #         days = f.find('h2', 'title').text.strip().split(' ')[2].split('+')[1]
            #     contract_end_1 = f.find('p', 'excerpt').text.strip().split('\n')[1].strip().split(' ')[0]
            #     contract_end_2 = f.find('p', 'excerpt').text.strip().split('\n')[1].strip().split(' ')[2]
            #     freeze_start = f.find('p', 'excerpt').text.strip().split('\n')[3].strip().split(' ')[3]
            #     freeze_end = f.find('p', 'excerpt').text.strip().split('\n')[5].strip().split(' ')[3]
            #     if freeze_end == 'заморозки:':
            #         freeze_end = f.find('p', 'excerpt').text.strip().split('\n')[5].strip().split(' ')[4]
            #     usage_date = f.find('div', 'byline').text.strip().split(' ')[2]

                    obj = [
                        name,               # имя
                        client_id,          # id клиента
                        # card_id,            # id абонемента
                        card_name,          # название абонемента
                        card_id,
                        date_payment,       # дата оплаты
                        date_start,         # дата активации
                        date_end,           # дата окончания
                        # contact,            # контакты
                        # days,               # добавленные дни
                        # freeze_start,       # дата начала заморозки
                        # freeze_end,         # дата конца заморозки
                        # contract_end_1,     # конец контракта 1
                        # contract_end_2,     # конец контракта 2
                        # usage_date,         # дата использования
                        # abonement_price
                    ]

                    data.append(obj)
                    print(obj)

    except Exception as e:
        #print(f'Клиент {client_id} не обработан')
        print(e)
    finally:
        #print(f'Клиент {client_id} обработан')
        ...

custom_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
s = requests.Session()
s.headers.update({'user-agent': custom_user_agent})

url = 'https://encoreiset.fitbase.io'

driver = open_driver()
cookies = get_cookie()
last_client = add_cookie(cookies)

data = []

for i in range(1, int(last_client)+1):
    request(i)

# for i in range(4510, 4550):
#     request(i)

# for i in range(4800, 4900):
#     request(i)

# for i in range(44, 45):
#     request(i)

# columns = ['ФИО', 'ID клиента', 'ID карты', 'Имя карты', 'Дата активации', 'Дата окончания', 'Контакт', 'Добавленные дни', 'Начало заморозки', 'Конец заморозки', 'Конец контракта 1', 'Конец контракта 2', 'Дата использования', 'Стоимость абонемента']
columns = ['ФИО', 'ID клиента', 'Имя абонемента', 'ID абонемента', 'Дата оплаты', 'Дата активации', 'Дата окончания']
if data != []:
    df = pd.DataFrame(data, columns=columns)
    # df['Добавленные дни'] = df['Добавленные дни'].astype(int)
    # df['Стоимость абонемента'] = df['Стоимость абонемента'].astype(int)
    while True:
        final = 0
        try:
            with pd.ExcelWriter(f'abonements (1-{last_client}).xlsx', engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            final = 1
        except:
            print('Ошибка записи в файл')
            time.sleep(1)
        if final == 1:
            print('Данные записаны')

            workbook = load_workbook(f'abonements (1-{last_client}).xlsx')
            sheet = workbook.active
            for column in sheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                sheet.column_dimensions[column_letter].width = adjusted_width

            workbook.save(f'abonements (1-{last_client}).xlsx')
            break

end_time = time.time()
# print(f'{(end_time - start_time)}')
print(f'Время выполнения: {round((end_time - start_time)/3600, 1)} часов')