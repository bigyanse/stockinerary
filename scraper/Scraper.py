import re
import csv
from . import write_file as wf
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

class Scraper:
    driver: WebDriver
    stack_exchage: str
    url: str
    wait: int
    company_links: list
    compnay_profiles: list
    profile_fieldnames: list
    link_fieldnames: list
    last_failed_count: int

    def __init__(self, stack_exchange, url, wait):
        self.stack_exchange = stack_exchange
        self.url = url
        self.wait = 2 * wait
        self.company_links = []
        self.company_profiles = []
        self.profile_fieldnames = ["company_name", "company_code", "market_capitalization", "current_price", "volume_traded", "high_price", "low_price", "open_price", "previous_close_price", "date"]
        self.link_fieldnames = ["name", "code", "link"]
        self.initialize()

    def initialize(self):
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options)

    def write_links_into_csv(self):
        with open(f"{self.stack_exchange}_links.csv", "w") as file:
            writer = csv.DictWriter(file, delimiter=",", fieldnames=self.link_fieldnames)
            for company in self.company_links:
                writer.writerow(company)

    def write_profiles_into_csv(self):
        with open(f"{self.stack_exchange}_profiles.csv", "w") as file:
            writer = csv.DictWriter(file, delimiter=",", fieldnames=self.profile_fieldnames)
            for company in self.company_profiles:
                writer.writerow(company)

    def append_profile_into_csv(self, company):
        with open(f"{self.stack_exchange}_profiles.csv", "a") as file:
            writer = csv.DictWriter(file, delimiter=",", fieldnames=self.profile_fieldnames)
            writer.writerow(company)

    def write_data_into_db(self):
        try:
            with open(f"{self.stack_exchange}_profiles.csv") as file:
                reader = csv.DictReader(file, delimiter=",", fieldnames=self.profile_fieldnames)
                print(reader)
        except Exception as e:
            print(e)
            print("First run write_links_to_csv() and write_profiles to csv()")

class NYSE(Scraper):
    stack_exchange: str = "nyse"
    url: str = "https://www.nyse.com/listings_directory/stock"

    def __init__(self, wait):
        self.wait = wait
        super().__init__(self.stack_exchange, self.url, self.wait)

    def get_company_links_pagination(self):
        table = WebDriverWait(self.driver, self.wait).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.table-data > tbody")))
        html = table.get_attribute("innerHTML")
        if html is not None:
            soup = BeautifulSoup(html, "lxml")

            for row in soup.find_all("tr"):
                cols = row.find_all("td")
                for link in cols[0].find_all("a"):
                    self.company_links.append({ "name": cols[1].text, "code": link.text, "link": link["href"] })
            print(self.company_links)
        else:
            print("Could not locate stocks table to fetch data")

    def scrape_company_links(self):
        self.driver.get(self.url)
        while True:
            try:
                self.get_company_links_pagination()
                next_btn = WebDriverWait(self.driver, self.wait).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[rel='next']")))
                next_btn.click()
            except Exception as e:
                print(e)
                print("Next button not found")
                break
        self.write_links_into_csv()

    def read_company_links(self):
        with open(f"{self.stack_exchange}_links.csv") as file:
            fieldnames = ["name", "code", "link"]
            reader = csv.DictReader(file, delimiter=",", fieldnames=fieldnames)
            for link in reader:
                self.company_links.append(link)
                print(link)

    def read_company_profiles(self):
        with open(f"{self.stack_exchange}_profiles.csv") as file:
            fieldnames = ["company_name", "company_code", "market_capitalization", "current_price", "volume_traded", "high_price", "low_price", "open_price", "previous_close_price", "date"]
            reader = csv.DictReader(file, delimiter=",", fieldnames=fieldnames)
            for profile in reader:
                self.company_profiles.append(profile)
                print(profile)

    def get_company_profiles(self, scrape_links=True):
        if scrape_links:
            self.scrape_company_links()
        else:
            self.read_company_links()
        count = 0
        try:
            file = open("resume.txt")
            count = int(file.read().strip()) + 1
            file.close()
        except:
            count = 0
        while count < len(self.company_links):
            company = self.company_links[count]
            self.driver.get(company.get("link"))
            try:
                content = WebDriverWait(self.driver, self.wait).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.contentContainer")))
                html = content.get_attribute("innerHTML")
                if html is not None:
                    soup = BeautifulSoup(html, "lxml")
                    table_row = soup.select(".flex_tr")
                    table_data = []
                    for row in table_row:
                        table_col = row.select(".flex_td")
                        row_data = {
                            "date": table_col[0].text,
                            "open_price": table_col[1].text,
                            "high_price": table_col[2].text,
                            "low_price": table_col[3].text,
                            "close_price": table_col[4].text,
                            "volume": table_col[5].text,
                        }
                        table_data.append(row_data)
                    total_vol = 0
                    for data in table_data:
                        vol = round(int(re.sub(r"[^0-9]", "", data["volume"])), 2)
                        total_vol += vol
                    market_cap = round(total_vol * float(table_data[0]["close_price"]), 2)
                    data = {
                        "company_name": company["name"],
                        "company_code": company["code"],
                        "market_capitalization": market_cap,
                        "current_price": table_data[0]["close_price"],
                        "volume_traded": table_data[0]["volume"],
                        "high_price": table_data[0]["high_price"],
                        "low_price": table_data[0]["low_price"],
                        "open_price": table_data[0]["open_price"],
                        "previous_close_price": table_data[1]["close_price"],
                        "date": table_data[0]["date"]
                    }
                    self.company_profiles.append(data)
                    count += 1
                    self.append_profile_into_csv(data)
                    wf.write_into_file("resume.txt", count)
                    print(data)
                else:
                    print("Could not locate company data")
            except Exception as e:
                print(e)
                last_failed_count = count
                if last_failed_count != count:
                    count = count - 1
                wf.write_into_file("resume.txt", count)
