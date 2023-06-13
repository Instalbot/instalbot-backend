import time, sys, sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

#setting up chrome driver
sys.stdout.reconfigure(encoding='utf-8')
options = webdriver.ChromeOptions()
options.add_argument('--mute-audio')
options.add_argument('--disable-usb-devices')
options.add_argument('--disable-gpu')
options.add_argument("--headless")
browser = webdriver.Chrome('./chromedriver.exe', options=options)

#opening website
url = ('https://instaling.pl/teacher.php?page=login')
browser.get(url)

#finding elements to login
time.sleep(2)
username = browser.find_element(By.XPATH, '//*[@id="log_email"]')
password = browser.find_element(By.XPATH, '//*[@id="log_password"]')
login_button = browser.find_element(By.XPATH, '//*[@id="main-container"]/div[3]/form/div/div[3]/button')

#login
time.sleep(2)
username.send_keys(config["username"])
password.send_keys(config["password"])
login_button.click()

#finding elements to data scraping
browser.find_element(By.XPATH, '//*[@id="student_panel"]/p[5]/a').click()
browser.find_element(By.XPATH, '//*[@id="account_page"]/div/a[1]/h4').click()
browser.find_element(By.XPATH, '//*[@id="show_words"]').click()

tr = 0

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
            print(f'Dodano {slowko2}, {slowko1}')
    except NoSuchElementException:
        break

cur.close()
db.commit()
db.close()

browser.close()