import time, sys, sqlite3, random, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

#start time
start_time = time.time()

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

#finding elements to start session
time.sleep(1)
browserfind_click('//*[@id="student_panel"]/p[1]/a')
try:
    browserfind_click('//*[@id="start_session_button"]')
except:
    browserfind_click('//*[@id="continue_session_button"]')

#some variables
time.sleep(3)
nr = 0

#connecting to database
db = sqlite3.connect("data.db")
cur = db.cursor()

#main loop of program (I hope it's working)
while True:
    #more variables
    random_sec1 = random.randint(2, 4) #wait time before writing answer
    random_sec2 = random.randint(4, 8) #wait time before clicking check
    random_sec3 = random.randint(1, 3) #wait time before clicking next word
    random_chance = random.randint(0, 100) #leave it unchanged
    know_new = browser.find_element(By.XPATH, '//*[@id="know_new"]')
    skip = browser.find_element(By.XPATH, '//*[@id="skip"]')
    word = browser.find_element(By.XPATH, '//*[@id="question"]/div[2]/div[2]')
    check = browser.find_element(By.XPATH, '//*[@id="check"]/h4')
    next_word = browser.find_element(By.XPATH, '//*[@id="next_word"]')
    answer = browser.find_element(By.XPATH, '//*[@id="answer"]')
    try:
        know_new.click()
        skip.click()
        time.sleep(2)
    except:
        try:
            word_str = word.text
        except:
            break
        cur.execute("SELECT niemiecki FROM slowka WHERE polski = ?", (word_str,))
        result = cur.fetchone()
        if result is None:
            print(f'the word {word_str} was not found in the database')
            break
        else:
            time.sleep(random_sec1)
            if random_chance >= 4: #that means the field will be empty
                if random_chance >= 7: #that means it will leave typo
                    answer.send_keys(result)
                else:
                    answer.send_keys(result)
                    answer.send_keys(Keys.BACKSPACE)
            time.sleep(random_sec2)
            check.click()
            time.sleep(random_sec3)
            next_word.click()
            nr += 1
            print(f"Completed {nr} words")

cur.close()
db.close()

#end time
end_time = time.time()
duration = end_time - start_time
print(f"It all took {duration:.2f} seconds")

time.sleep(4)
browser.close()