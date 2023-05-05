import time, sys, sqlite3, random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

#start time
start_time = time.time()

#setting up chrome driver
sys.stdout.reconfigure(encoding='utf-8')
options = webdriver.ChromeOptions()
options.add_argument('--mute-audio')
options.add_argument('--disable-usb-devices')
options.add_argument('--disable-gpu')
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
username.send_keys('')
password.send_keys('')
login_button.click()

#finding elements to start session
browser.find_element(By.XPATH, '//*[@id="student_panel"]/p[1]/a').click()
try:
    browser.find_element(By.XPATH, '//*[@id="start_session_button"]').click()
except:
    browser.find_element(By.XPATH, '//*[@id="continue_session_button"]').click()

#some variables
time.sleep(2)
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
        time.sleep(1)
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
db.commit()
db.close()

#end time
end_time = time.time()
duration = end_time - start_time
print(f"It all took {duration:.2f} seconds")

time.sleep(4)
browser.close()