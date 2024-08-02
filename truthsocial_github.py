from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import time
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)

url = 'https://truthsocial.com/login'
driver.get(url)

time.sleep(2)
driver.save_screenshot('screenshot.png')
signin = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, ".//*[contains(text(), 'Sign In')]"))).click()
time.sleep(2)

username = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//input[contains(@placeholder, "Username")]')))
username.send_keys("StudentExperimental")
username.send_keys(Keys.ENTER)

password = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, '//input[contains(@placeholder, "Password")]')))
password.send_keys("#Student123")
password.send_keys(Keys.ENTER)

import pandas as pd

sheet = "posts_with_replies.xlsx"
data = pd.read_excel(sheet)

all_urls = data['url']
post_id = data['external_id']

all_urls_snippet = all_urls

a = 36176
wait_more = 10
while a < len(all_urls_snippet):
    if a % 30 == 0:
        print("Milestone: ", a)

    replies = []
    retruths = []
    like_buttons = []
    posts = []
    authors = []
    dates = []
    post_id_linked = []
    comment_ids = []

    last_last_height = 0
    last_height = 0
    now_height = 0

    breakPlease = False

    uniques = set()
    driver.get(all_urls_snippet[a])
    time.sleep(12)
    now_height = driver.execute_script("return document.body.scrollHeight")
    check_replies = driver.find_elements(By.CLASS_NAME, "normal-case.font-medium.font-sans.tracking-normal.text-sm")
    too_many = driver.find_elements(By.XPATH, ".//*[contains(text(), 'Too many requests')]")
    if len(too_many) > 0:
        time.sleep(wait_more)
        print(a)
        wait_more = wait_more * 2
        continue

    wait_more = 10
    if len(check_replies) == 0:
        a = a + 1
        continue
    else:
        if ".com" not in check_replies[0].text and ("reply" in check_replies[0].text or "replies" in check_replies[0].text):
            pass
        else:
            a = a + 1
            continue
    while True:
        if last_last_height == last_height == now_height:
            break
                    
        driver.execute_script("window.scrollBy(0, 400)")
        time.sleep(5)
        last_last_height = last_height
        last_height = now_height
        now_height = driver.execute_script("return document.body.scrollHeight")
        text = driver.find_elements("xpath", ".//div[contains(@class, 'status cursor-pointer focusable')]")
        try:
            for b in range(len(text)):
                comment_id = text[b].find_element("xpath", ".//div[contains(@class, 'status__wrapper space-y-4 status-public status-reply p-4')]")
                if comment_id.get_attribute("data-id") in uniques:
                    continue
                else:
                    uniques.add(comment_id.get_attribute("data-id"))
                    comment_ids.append(comment_id.get_attribute("data-id"))
                    split = text[b].text.split("\n")
                    try:
                        posts.append(split[5])
                    except: 
                        posts.append("")
                    authors.append(split[1][1:])
                    post_time = text[b].find_element("xpath", ".//time")
                    dates.append(post_time.get_attribute("title"))
                    post_id_linked.append(post_id[a])
                    reply = comment_id.find_elements("xpath", ".//button[contains(@title, 'Reply to thread')]")
                    for i in range(len(reply)):
                        if reply[i].text == "":
                            replies.append(0)
                        else:
                            replies.append(int(reply[i].text))
                    
                    retruth = comment_id.find_elements("xpath", ".//button[contains(@title, 'ReTruth')]")
                    for i in range(len(retruth)):
                        if retruth[i].text == "":
                            retruths.append(0)
                        else:
                            retruths.append(int(retruth[i].text))
                    
                    like_button = comment_id.find_elements("xpath", ".//button[contains(@title, 'Like')]")
                    for i in range(len(like_button)):
                        if like_button[i].text == "":
                            like_buttons.append(0)
                        elif "k" in like_button[i].text:
                            like_buttons.append(float(like_button[i].text.split("k")[0]) * 1000)
                        else:   
                            like_buttons.append(int(like_button[i].text))
        except:
            breakPlease = True
            a = a - 1
            break
    
    if breakPlease == True:
        print(a)
        continue

    a = a + 1

    columnsAll = [authors, comment_ids, dates, posts, post_id_linked, replies, retruths, like_buttons]
    df = pd.DataFrame(columnsAll)
    df = df.T
    df.to_csv('comments4.csv', mode='a', index=False, header=False)
