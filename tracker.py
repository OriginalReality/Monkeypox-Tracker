import csv
import smtplib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime


# Input: A string taken from the CDC website containing the name of states and number of infections per state.
# Output: A dictionary mapping each state to their number of MonkeyPox infections.
def toDict(str):
    infections = []
    states = []
    lastInd = 0
    addNum = False
    i = 0
    while i < len(str):
        if str[i].isnumeric() and not addNum:
            states = states + [str[lastInd:i]]
            lastInd = i
            addNum = True
        elif str[i].isalpha() and addNum:
            infections = infections + [str[lastInd:i]]
            lastInd = i
            addNum = False
        if i == len(str) - 1:
            infections = infections + [str[lastInd:i + 1]]
        i = i + 1
    return {x: y for (x, y) in zip(states, infections)}


# A function that takes in a dictionary mapping states to a number of MonkeyPox infections and sends an email to a
# desired recipient
def email(tracker):
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.ehlo()
    server.login('someGmail@gmail.com', 'password')
    # If your gmail uses two-factor authentication, you will
    # have to set up an app specific password for gmail.

    server.sendmail('senderGmail', 'recipientGmail', "Infections in NY has rose to:",
                    tracker['New York'])
    server.close()


options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
url = "https://www.cdc.gov/poxvirus/monkeypox/response/2022/us-map.html"

driver.get(url)
sleep(1)
soup = BeautifulSoup(driver.page_source, features='html.parser')
finder = soup.find("tbody", {"role": "rowgroup"})
str = finder.get_text()

dictionary = toDict(str)
header = ['Date', 'New York Infections']
data = [datetime.today().strftime('%m/%d/%Y'), dictionary['New York']]

# Only include this in the beginning to create the csv file.
# Afterwards, it can be deleted or commented out to avoid rewriting the file with each run
with open('MonkeyPoxTracker.csv', 'w', newline='', encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerow([data[0], data[1]])


# A function that checks current number of infections and sends an email if it exceeds a given threshold
def update():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    url = "https://www.cdc.gov/poxvirus/monkeypox/response/2022/us-map.html"
    driver.get(url)
    sleep(1)
    soup = BeautifulSoup(driver.page_source, features='html.parser')
    table = soup.find("tbody", {"role": "rowgroup"})
    str = table.get_text()
    tracker = toDict(str)
    append = [datetime.today().strftime('%m/%d/%Y'), tracker['New York']]
    with open('MonkeyPoxTracker.csv', 'a+', newline='', encoding='UTF8') as f:
        write = csv.writer(f)
        write.writerow([append[0], append[1]])
    if tracker['New York'] == 5000:
        email(tracker)
    elif tracker['New York'] == 10000:
        email(tracker)
    elif tracker['New York'] == 20000:
        email(tracker)


# The while loop automates the entire process to check once every 24 hours, however it is unnecessary and only for
# convenience.
while True:
    update()
    sleep(86400)
