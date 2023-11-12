import time, sys, sqlite3, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

#config
with open('config.json') as f:
    config = json.load(f)

#setting up chrome driver
service = webdriver.chrome.service.Service(executable_path='./chromedriver.exe')
sys.stdout.reconfigure(encoding='utf-8')
options = webdriver.ChromeOptions()
options.add_argument('--mute-audio')
options.add_argument('--disable-usb-devices')
options.add_argument('--disable-gpu')
options.add_argument("--headless")
browser = webdriver.Chrome(service=service, options=options)

#def check if element exists
def browserfind_click(xpath):
    for i in range(5):
        try:
            browser.find_element(By.XPATH, xpath).click()
            break
        except NoSuchElementException:
            print(f"Element not found retrying {i+1}/5")
            time.sleep(5)

def browserfind_sendkeys(xpath, keys):
    for i in range(5):
        try:
            browser.find_element(By.XPATH, xpath).send_keys(keys)
            break
        except NoSuchElementException:
            print(f"Element not found retrying {i+1}/5")
            time.sleep(5)

#opening website
url = ('https://instaling.pl/teacher.php?page=login')
browser.get(url)

#finding elements to login
time.sleep(3)
browserfind_sendkeys('//*[@id="log_email"]', config["username"])
browserfind_sendkeys('//*[@id="log_password"]', config["password"])
browserfind_click('//*[@id="main-container"]/div[3]/form/div/div[3]/button')

#finding elements to start data scraping
browserfind_click('//*[@id="student_panel"]/p[5]/a')
browserfind_click('//*[@id="account_page"]/div/a[1]/h4')
browserfind_click('//*[@id="show_words"]')

tr = 0

time.sleep(3)
#connecting to database
db = sqlite3.connect("data.db")
cur = db.cursor()

#main loop of program (I hope it's working)
while True:
    tr += 1
    try:
        slowko1 = browser.find_element(By.XPATH, f'//*[@id="assigned_words"]/tr[{tr}]/td[1]').text
        slowko2 = browser.find_element(By.XPATH, f'//*[@id="assigned_words"]/tr[{tr}]/td[2]').text
        cur.execute("CREATE TABLE IF NOT EXISTS slowka(polski, niemiecki)")
        cur.execute(f"SELECT polski FROM slowka WHERE niemiecki = '{slowko1}'")
        cur.execute(f"SELECT niemiecki FROM slowka WHERE polski = '{slowko2}'")
        wynik = cur.fetchone()
        if wynik is None:
            cur.execute('''INSERT OR IGNORE INTO slowka (polski, niemiecki) VALUES (?, ?)''', (slowko2, slowko1))
            print(f'Added {slowko2}, {slowko1}')
    except NoSuchElementException:
        break

cur.close()
db.commit()
db.close()

browser.close()