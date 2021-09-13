import requests
import threading
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QFormLayout, QPushButton, QLabel
import time
import sys
import random
import os
import re
import yaml

conf = ''


def load_conf_file(config_file):
    global conf
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        API_DATA = [i["API_DATA"] for i in config]
        # conf = str(list(API_DATA.values()))[1:-1]
    return API_DATA


cred = load_conf_file('config.yml')
def is_valid_number(thread_name, pnumbers):
    for pnumber in pnumbers:
        authid = random.randint(0, len(cred)-1)
        client = Client(cred[authid]['TWILIO_ACCOUNT_SID'], cred[authid]['TWILIO_AUTH_TOKEN'])
        try:
            response = client.lookups.phone_numbers(pnumber).fetch(type="carrier")
            try:
                nums = client.lookups.phone_numbers(pnumber).fetch(type="carrier")
                pattern = r'[/\<>"?:|*]'
                carrier = re.sub(pattern, '', nums.carrier['name'])
            except:
                carrier = 'Unknown Carrier'
            save_in = open(f'Carrier Verification/{carrier}.txt', 'a').writelines(str(pnumber) + '\n')
            print(thread_name)
            print(f'Number: {pnumber} is valid and Carrier is: {carrier}')

        except TwilioRestException as e:
            if e.code == 20404:
                print(f'Number: {pnumber} is invalid')
            else:
                raise e


def generate(country_code, service_code, length, num):
    with open('generate.txt', 'a+') as file:
        file.truncate(0)
        for i in range(num):
            min_b = int('1' * length)
            max_b = int('9' * length)
            generated_number = str(country_code) + str(service_code) + str(random.randint(min_b, max_b))
            file.write(generated_number + '\n')
    updateStatus(f'Successfully generated {num} numbers!')


app = QApplication(sys.argv)
window = QWidget()
window.resize(550, 210)
window.setWindowTitle("Number Validator")
formLayout = QFormLayout(parent=window)
country_code, service_code, length, number = QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit()
filePath, generateButton, verifyButton, cancel = QPushButton('Find'), QPushButton('Generate'), QPushButton(
    'Validate'), QPushButton('Cancel')
formLayout.addRow(QLabel(''), QLabel(''))
formLayout.addRow(QLabel(''), QLabel(''))

status_label = QLabel('Ready to start', parent=window)
status_label.move(10, 10)
status_label.resize(530, 30)
status_label.setStyleSheet("font-weight: bold")


def updateStatus(text):
    status_label.setText(text)


formLayout.addRow(QLabel('Enter Country Code:'), country_code)
formLayout.addRow(QLabel('Enter the area code:'), service_code)
formLayout.addRow(QLabel('Enter the length of Remaining Digits:'), length)
formLayout.addRow(QLabel('How many numbers to generate?'), number)
formLayout.addRow(QLabel(''), generateButton)
formLayout.addRow(cancel, verifyButton)


def gen():
    updateStatus(f'Generating....')
    generate(country_code.text(), service_code.text(), int(length.text()), int(number.text()))


def closePython():
    global stop_threads
    stop_threads = True
    updateStatus('Stopped all threads!')


def splitter(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def verify_thread():
    f = open('generate.txt', 'r').read().splitlines()
    l = list(splitter(f, 5))
    t1 = threading.Thread(target=is_valid_number, args=("thread1", l[0]))
    t2 = threading.Thread(target=is_valid_number, args=("thread2", l[1]))
    t3 = threading.Thread(target=is_valid_number, args=("thread3", l[2]))
    t4 = threading.Thread(target=is_valid_number, args=("thread4", l[3]))
    t5 = threading.Thread(target=is_valid_number, args=("thread5", l[4]))
    start = time.time()
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()

    # join threads
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    end = time.time()


generateButton.clicked.connect(gen)
verifyButton.clicked.connect(verify_thread)
cancel.clicked.connect(closePython)

window.show()
app.exec()
