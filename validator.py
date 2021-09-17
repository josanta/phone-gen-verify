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
        self.settings.clicked.connect(self.goto_settings)

    def goto_validator(self):
        validate_screen = validatorScreen()
        widget.addWidget(validate_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def goto_sms(self):
        sms_screen = smsScreen()
        widget.addWidget(sms_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def goto_settings(self):
        settings_screen = settingsScreen()
        widget.addWidget(settings_screen)
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
            if self.validate_check.isChecked():
                cred = self.load_conf_file('config.yml')
                self.updateStatus('validating...')
                for pnumber in pnumbers:
                    authid = random.randint(0, len(cred) - 1)
                    client = Client(cred[authid]['TWILIO_ACCOUNT_SID'], cred[authid]['TWILIO_AUTH_TOKEN'])
                    try:
                        caller_name = client.lookups.v1.phone_numbers('15108675310').fetch(type=['caller-name'])
                        c_name = caller_name.caller_name['caller_name']
                    except TypeError:
                        c_name = ''
                    try:
                        nums = client.lookups.phone_numbers(pnumber).fetch(type="carrier")
                        pattern = r'[/\<>"?:|*]'
                        carrier = re.sub(pattern, '', nums.carrier['name'])
                    except:
                        carrier = 'Unknown Carrier'
                    if carrier == 'AT&T Wireless':
                        p_nbr = f'{pnumber}@txt.att.net;{c_name}'
                    elif carrier == 'Verizon Wireless':
                        p_nbr = f'{pnumber}@vtext.com;{c_name}'
                    else:
                        p_nbr = f'{pnumber};{c_name}'
                    save_in = open(f'Carrier Verification/{carrier}.txt', 'a').writelines(str(p_nbr) + '\n')
                    print(thread_name)
                    print(f'Number: {pnumber} is valid and Carrier is: {carrier}')
                self.updateStatus(f'process completed successfully.')
            else:
                cred = self.load_conf_file('config.yml')
                self.updateStatus('validating...')
                for pnumber in pnumbers:
                    authid = random.randint(0, len(cred) - 1)
                    client = Client(cred[authid]['TWILIO_ACCOUNT_SID'], cred[authid]['TWILIO_AUTH_TOKEN'])
                    try:
                        nums = client.lookups.phone_numbers(pnumber).fetch(type="carrier")
                        pattern = r'[/\<>"?:|*]'
                        carrier = re.sub(pattern, '', nums.carrier['name'])
                    except:
                        carrier = 'Unknown Carrier'
                    if carrier == 'AT&T Wireless':
                        p_nbr = f'{pnumber}@txt.att.net;'
                    elif carrier == 'Verizon Wireless':
                        p_nbr = f'{pnumber}@vtext.com;'
                    else:
                        p_nbr = f'{pnumber};'
                    save_in = open(f'Carrier Verification/{carrier}.txt', 'a').writelines(str(p_nbr) + '\n')
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
        length = self.length.text()
        number_bx = self.number.text()
        if country_code == '' or service_code == '' or length == '' or number_bx == '':
            self.updateStatus('Check your input all fields are required!')
            self.status_label.setStyleSheet('color: red')
        else:
            self.updateStatus(f'Generating....')
            self.status_label.setStyleSheet('color: green')
            self.generate(country_code, service_code, int(length), int(number_bx))

    def splitter(self, a, n):
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

    def verify_thread(self):
        self.updateStatus('validating...')
        self.updateStatus('validating...')
        self.updateStatus('validating...')
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
        if len(phone_numbers_to_send) > 0:
            for single_phone in phone_numbers_to_send:
                time.sleep(2)
                try:
                    if self.sms_box.toPlainText() == '':
                        self.send_status.setText(f'Please type message to proceed!')
                        self.send_status.setStyleSheet('color: red')
                    else:
                        cred = self.load_conf_file('config.yml')
                        client = Client(cred[1]['TWILIO_ACCOUNT_SID'], cred[1]['TWILIO_AUTH_TOKEN'])
                        message = client.messages.create(
                            body=self.sms_box.toPlainText(),
                            from_='+18479840485',
                            to='+' + single_phone
                        )
                        self.send_status.setText(message.status)
                        time.sleep(3)
                        self.send_status.setText('Send successfully')
                except:
                    self.send_status.setText(f'Unable to send to +{single_phone} check your number')
                    self.send_status.setStyleSheet('color: red')
        else:
            self.send_status.setText('Please upload numbers to continue!')
            self.send_status.setStyleSheet('color: red')


class settingsScreen(QMainWindow):
    def __init__(self):
        super(settingsScreen, self).__init__()
        loadUi('settings.ui', self)
        self.back_settings.clicked.connect(self.goto_homepage)
        self.save_crd.clicked.connect(self.save_config)
        self.clear_crd.clicked.connect(self.delete_crd)

    def goto_homepage(self):
        homes = Home()
        widget.addWidget(homes)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def save_config(self):
        try:
            with open('config.yml', "r") as f:
                config = yaml.safe_load(f)
                API_DATA = [i["API_DATA"] for i in config]
                unique_sid = [n['TWILIO_ACCOUNT_SID'] for n in API_DATA]

            if self.twillio_sid.text() == '' or self.twillio_token.text() == '' or self.twillio_phone.text() == '':
                self.set_status.setText('Check your Credentials, all fields are required!')
                self.set_status.setStyleSheet('color: red')

            elif self.twillio_sid.text() not in unique_sid:
                p = {
                    'API_DATA': {
                        'TWILIO_ACCOUNT_SID': self.twillio_sid.text(),
                        'TWILIO_AUTH_TOKEN': self.twillio_token.text(),
                        'Sender_Phone': self.twillio_phone.text()
                    }
                }
                with open('config.yml', 'a') as f:
                    yaml.dump([p], f)
                self.set_status.setText('Credentials saved successfully!')
                self.set_status.setStyleSheet('color: green')
            else:
                self.set_status.setText('Twillio account sid already saved!')
                self.set_status.setStyleSheet('color: red')
        except FileNotFoundError:
            p = {
                'API_DATA': {
                    'TWILIO_ACCOUNT_SID': self.twillio_sid.text(),
                    'TWILIO_AUTH_TOKEN': self.twillio_token.text(),
                    'Sender_Phone': self.twillio_phone.text()
                }
            }
            with open('config.yml', 'w') as f:
                yaml.dump([p], f)
            self.set_status.setText('Credentials saved successfully!')
            self.set_status.setStyleSheet('color: green')
        self.twillio_sid.clear()
        self.twillio_token.clear()
        self.twillio_phone.clear()

    def delete_crd(self):
        os.remove('config.yml')
        self.set_status.setText('Configuration deleted successfully')
        self.set_status.setStyleSheet('color: green')


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
