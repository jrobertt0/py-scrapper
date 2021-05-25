from time import sleep
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from datetime import datetime

from dotenv import load_dotenv
import os

import requests

load_dotenv()

class Afi:
    def __init__(self, data):
        self.organized_by = data[0].replace("\n", "")
        self.area = data[1].replace("\n", "")
        self.event = data[2].replace("\n", "")
        self.date_time_start = datetime.strptime(data[3] + ':00', '%d/%m/%Y %H:%M:%S')
        self.date_time_end = datetime.strptime(data[4] + ':00', '%d/%m/%Y %H:%M:%S')
        self.capacity = int(data[5])
        self.occupied = int(data[6])
        self.available = int(data[7])

    def obj_string(self):
        return f'{self.organized_by}, {self.area}, {self.event}, {self.date_time_start}, {self.date_time_end}'

    def __dict__(self):
        return {
            'organized_by': self.organized_by,
            'area': self.area,
            'event': self.event,
            'capacity': self.capacity,
            'occupied': self.occupied,
            'available': self.available,
            'date_time_start': str(self.date_time_start),
            'date_time_end': str(self.date_time_end),
        }

driver = webdriver.Chrome('C:/Users/robed/Documents/chromedriver/chromedriver.exe')

def frame_switch(css_selector):
  driver.switch_to.frame(driver.find_element_by_name(css_selector))
  
def calendar():
    driver.switch_to.parent_frame()
    frame_switch('left')

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Calendario de Eventos'))
        ).click()
    finally:
        print("Calendario")

    driver.switch_to.parent_frame()
    frame_switch('center')

    try:

        dirty_tr = driver.find_elements_by_tag_name('tr')
                
        afis = [[font.text for font in tr.find_elements_by_tag_name('font')[1:]] for tr in dirty_tr[6:]]
        afis = [Afi(afi) for afi in afis if len(afi) > 0]
        return afis
    finally:
        print("Afis")

def afi():
    frame_switch('top')

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'AFI'))
        ).click()
    finally:
        print("Afi")

    return calendar()


def clear_afis(dirty_afis):
    today = datetime.today()
    return [afi for afi in dirty_afis if int(afi.available) > 0 and afi.date_time_start > today]
    
def login():
    driver.get('https://www.uanl.mx/enlinea/')
    frame_switch('loginbox')
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "cuenta"))
        ).send_keys(os.getenv('MAT'))    
        driver.find_element_by_id('pass').send_keys(os.getenv('PASS'))
        driver.find_element_by_xpath('./html/body/div/form/fieldset/div[4]/button').click()
    finally:
        print("Servicios en Linea")
    
    try:
        careers = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, './/*[@id="contenido"]/form/a'))
        )
        careers[-1].click()
    finally:
        print("Seleccion de carrera")

def send_afis(afis):
    url = 'http://localhost:3000/api/afi/addAfis'
    data = {"afis" : [afi.__dict__() for afi in afis]}
    print("\n\n",data)
    x = requests.post(url, json=data)

    print(x.text)

def equal_list(l1, l2):
    l1 = [val.obj_string() for val in l1]
    l2 = [val.obj_string() for val in l2]

    flag = True
    for val in l1:
        if val not in l2:
            flag = False
            print(val)
            print(l2, "\n\n")
    flag2 = True
    for val in l2:
        if val not in l1:
            flag2 = False
            print(val)
            print(l1, "\n\n")
    return flag or flag2
                
        
if __name__ == "__main__" :
    login()
    dirty_afis = afi()
    prev_afis = clear_afis(dirty_afis)
    send_afis(prev_afis)

    while True:
        sleep(1500)
        dirty_afis = calendar()
        afis = clear_afis(dirty_afis)
        if not equal_list(afis, prev_afis):
            send_afis(afis)
            prev_afis = afis