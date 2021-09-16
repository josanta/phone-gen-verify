from PyQt5 import QtCore
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import sys
from PyQt5.uic import loadUi
import os
import re
import threading
import time
import yaml
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import random


class Home(QMainWindow):
    def __init__(self):
        super(Home, self).__init__()
        loadUi('welcome screen.ui', self)
        self.verify_btn1.clicked.connect(self.goto_validator)
        self.sms_btn.clicked.connect(self.goto_sms)

    def goto_validator(self):
        validate_screen = validatorScreen()
        widget.addWidget(validate_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def goto_sms(self):
        sms_screen = smsScreen()
        widget.addWidget(sms_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class validatorScreen(QMainWindow):
    def __init__(self):
        super(validatorScreen, self).__init__()
        loadUi('validator.ui', self)
        self.back_from_validator.clicked.connect(self.goto_homepage)
        self.generate_btn.clicked.connect(self.gen)
        self.validate_btn.clicked.connect(self.verify_thread)
        self.close_btn.clicked.connect(self.closePython)

    def load_conf_file(self, config_file):
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            API_DATA = [i["API_DATA"] for i in config]
        return API_DATA

    def is_valid_number(self, thread_name, pnumbers):
        try:
            cred = self.load_conf_file('config.yml')
            for pnumber in pnumbers:
                self.updateStatus('validating...')
                authid = random.randint(0, len(cred) - 1)
                client = Client(cred[authid]['TWILIO_ACCOUNT_SID'], cred[authid]['TWILIO_AUTH_TOKEN'])
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
            self.updateStatus(f'process completed successfully.')

        except TwilioRestException as e:
            if e.code == 20404:
                print(f'Number: {pnumber} is invalid')
            else:
                raise e
        except:
            self.updateStatus('Failed...')
            self.status_label.setStyleSheet('color: red')

    def goto_homepage(self):
        homes = Home()
        widget.addWidget(homes)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def updateStatus(self, text):
        self.status_label.setText(text)

    def generate(self, country_code, service_code, length, num):
        with open('generate.txt', 'a+') as file:
            file.truncate(0)
            for i in range(num):
                min_b = int('1' * length)
                max_b = int('9' * length)
                generated_number = str(country_code) + str(service_code) + str(random.randint(min_b, max_b))
                file.write(generated_number + '\n')
        self.updateStatus(f'Successfully generated {num} numbers!')

    def closePython(self):
        global stop_threads
        stop_threads = True
        self.updateStatus('Stopped all threads!')

    #
    def gen(self):
        self.updateStatus(f'Generating....')
        country_code = self.country_code.text()
        service_code = self.service_code.text()
        length = int(self.length.text())
        number_bx = int(self.number.text())
        self.generate(country_code, service_code, length, number_bx)

    def splitter(self, a, n):
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

    def verify_thread(self):
        f = open('generate.txt', 'r').read().splitlines()
        l = list(self.splitter(f, 5))
        t1 = threading.Thread(target=self.is_valid_number, args=("thread1", l[0]))
        t2 = threading.Thread(target=self.is_valid_number, args=("thread2", l[1]))
        t3 = threading.Thread(target=self.is_valid_number, args=("thread3", l[2]))
        t4 = threading.Thread(target=self.is_valid_number, args=("thread4", l[3]))
        t5 = threading.Thread(target=self.is_valid_number, args=("thread5", l[4]))
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


class smsScreen(QMainWindow):
    def __init__(self):
        super(smsScreen, self).__init__()
        loadUi('sms.ui', self)
        self.back_sms.clicked.connect(self.goto_homepage)
        self.upload_btn.clicked.connect(self.browse_files)
        self.send_sms.clicked.connect(self.sms_sender)

    def load_conf_file(self, config_file):
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
            API_DATA = [i["API_DATA"] for i in config]
        return API_DATA

    def goto_homepage(self):
        homes = Home()
        widget.addWidget(homes)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    nbrs = []

    def browse_files(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', QtCore.QDir.currentPath(), '*.txt')
        f = open(filename, 'r').read().splitlines()
        nb = [self.nbrs.append(nb) for nb in f]
        counter = len(f)
        self.number_count.setText(f'Uploaded {counter} Numbers')
        return f

    def sms_sender(self, phone_numbers_to_send):
        phone_numbers_to_send = self.nbrs
        for single_phone in phone_numbers_to_send:
            time.sleep(2)
            try:
                cred = self.load_conf_file('config.yml')
                client = Client(cred[1]['TWILIO_ACCOUNT_SID'], cred[1]['TWILIO_AUTH_TOKEN'])
                message = client.messages.create(
                    body=self.sms_box.toPlainText(),
                    from_='+18479840485',
                    to='+' + single_phone
                )
                status = self.send_status.setText(message.status)
                time.sleep(3)
                status = self.send_status.setText('Send successfully')

            except:
                status = self.send_status.setText(f'Unable to send to +{single_phone} check your number')
                self.send_status.setStyleSheet('color: red')


# main
app = QApplication(sys.argv)
home = Home()
widget = QtWidgets.QStackedWidget()
widget.addWidget(home)
widget.setWindowTitle('Phone Validator')
widget.setWindowIcon(QIcon('appp.ico'))
widget.setFixedWidth(851)
widget.setFixedHeight(618)
widget.show()

sys.exit(app.exec_())
