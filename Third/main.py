import csv
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def click_next():
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 
                                                    ".pagination-container__item._next")))
    driver.execute_script('document.querySelector("nav.tabbar.js-tabbar").remove();')
    button.click()
    print(driver.current_url)

def collecting_links(driver, links_array):
    electroguitars = driver.find_elements(By.CLASS_NAME, "catalog-card")
    for electroguitar in electroguitars:
        link_tag = electroguitar.find_element(By.TAG_NAME, "link")
        links_array.append(link_tag.get_attribute("href"))
        #print(link_tag.get_attribute("href"))

def collecting_data(link):
    driver.get(link)
    try:
        characteristics = {}
        item = driver.find_element(By.CLASS_NAME, "mt-product-info__list")
        #print(item.text)
        #print("----")
        no_data_message = "Мы обновляем информацию, характеристики товара скоро появятся."
        if no_data_message in item.text:
            return None
        lines = item.text.strip().split("\n")
        for line in lines:
            key, value = line.split(":", 1)
            characteristics[key.strip()] = value.strip()
            #print(key.strip(), ":", value.strip())
        #print("---")
        return {
            "Ссылка": link,
            "Параметры": characteristics
        }
    except Exception as e:
        print(f"Ошибка при сборе данных для ссылки {link}: {e}")
        return None
    
def write_to_csv(data, filename="guitars.csv"):
    all_fieldnames = set()
    for item in data:
        if item and "Параметры" in item:
            all_fieldnames.update(item["Параметры"].keys())
    fieldnames = ["Ссылка"] + sorted(all_fieldnames)
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            if item:
                row = {"Ссылка": item["Ссылка"]}
                row.update(item["Параметры"])
                for field in fieldnames:
                    if field not in row:
                        row[field] = ""
                writer.writerow(row)


start_url = 'https://www.muztorg.ru/category/elektrogitary'
links_to_guitars = []
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(start_url)
collecting_links(driver, links_to_guitars)
for i in range(1):
    click_next()
    collecting_links(driver, links_to_guitars)
#links_to_guitars = links_to_guitars[:1]
guitars = []
for link_to_guitar in links_to_guitars:
    #print(link_to_guitar)
    guitar = collecting_data(link_to_guitar)
    guitars.append(guitar)
write_to_csv(guitars)
driver.quit()


