import csv
import time
import psycopg2
import argparse

from psycopg2 import extras
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

parser = argparse.ArgumentParser(description="My own. Personal. Parser...")
parser.add_argument("url", type=str, help="ссылочку сюда давай")
args = parser.parse_args()

def connect_to_db():
    conn = psycopg2.connect(
        dbname='guitars',
        user='',
        password='',
        host='localhost',
        port='5432'
    )
    return conn

def create_table_if_not_exists():
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS guitars (
                id SERIAL PRIMARY KEY,
                Ссылка TEXT NOT NULL,
                "Количество ладов (диапазон)" TEXT,
                "Количество струн" TEXT,
                "Конфигурация звукоснимателей" TEXT,
                "Крепление грифа" TEXT,
                "Материал грифа" TEXT,
                "Материал корпуса" TEXT,
                "Материал накладки грифа" TEXT,
                "Материал топа" TEXT,
                "Мензура, дюймы" TEXT,
                "Ориентация" TEXT,
                "Тип бриджа" TEXT,
                "Тип электроники" TEXT,
                "Форма корпуса" TEXT
            );
        """)
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблицы: {e}")
    finally:
        cur.close()
        conn.close()

def save_to_db(link, parameters):
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        columns = [
            "Ссылка",
            "Количество ладов (диапазон)",
            "Количество струн",
            "Конфигурация звукоснимателей",
            "Крепление грифа",
            "Материал грифа",
            "Материал корпуса",
            "Материал накладки грифа",
            "Материал топа",
            "Мензура, дюймы",
            "Ориентация",
            "Тип бриджа",
            "Тип электроники",
            "Форма корпуса"
        ]
        values = [link] + [parameters.get(col, None) for col in columns[1:]]
        query = f"""
            INSERT INTO guitars ({", ".join([f'"{col}"' for col in columns])})
            VALUES ({", ".join(["%s"] * len(values))})
        """
        cur.execute(query, values)
        conn.commit()
    except Exception as e:
        print(f"Ошибка при записи в базу данных: {e}")
    finally:
        cur.close()
        conn.close()

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

def collecting_data(link):
    driver.get(link)
    try:
        characteristics = {}
        item = driver.find_element(By.CLASS_NAME, "mt-product-info__list")
        no_data_message = "Мы обновляем информацию, характеристики товара скоро появятся."
        if no_data_message in item.text:
            return None
        lines = item.text.strip().split("\n")
        for line in lines:
            if ":" in line: 
                key, value = line.split(":", 1)
                characteristics[key.strip()] = value.strip()
        return {
            "Ссылка": link,
            **characteristics 
        }
    except Exception as e:
        print(f"Ошибка при сборе данных для ссылки {link}: {e}")
        return None

def write_to_csv(data, filename="guitars.csv"):
    columns = [
        "Ссылка",
        "Количество ладов (диапазон)",
        "Количество струн",
        "Конфигурация звукоснимателей",
        "Крепление грифа",
        "Материал грифа",
        "Материал корпуса",
        "Материал накладки грифа",
        "Материал топа",
        "Мензура, дюймы",
        "Ориентация",
        "Тип бриджа",
        "Тип электроники",
        "Форма корпуса"
    ]
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for item in data:
            if item:
                row = {col: item.get(col, "") for col in columns}
                writer.writerow(row)

create_table_if_not_exists()

start_url = args.url
links_to_guitars = []
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(start_url)
collecting_links(driver, links_to_guitars)
for i in range(1):
    click_next()
    collecting_links(driver, links_to_guitars)

guitars = []
for link_to_guitar in links_to_guitars:
    guitar = collecting_data(link_to_guitar)
    if guitar:
        guitars.append(guitar)
        save_to_db(guitar["Ссылка"], {k: v for k, v in guitar.items() if k != "Ссылка"})

write_to_csv(guitars)
driver.quit()