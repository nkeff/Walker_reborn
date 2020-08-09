from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import logging
import os
import datetime
import random 

from Page import Page
from HandleStorage import HandleStorage
import utils

import time

class Bypass(object):
    """Class for bypass webshell"""

    def __init__(self, url, data_path, max_nesting_lvl):
        # path for service data
        self.data_path = os.path.abspath(data_path)

        assert self.create_path()
        logging.info('Paths created')

        self.base_url = url

        # Current nesting level and max nesting level
        self.max_nesting_lvl = 2

        # Тут хранятся пользовательские пароли
        self.user_passwords = ['pwd', '123456', 'password', 'qwerty']

        # Показатель запаролен шелл или нет (по умолчанию считаем что нет)
        self.is_secret_shell = False

        # уникальные внешние ссылки
        self.external_urls = []

        # webdriver
        self.driver = webdriver.Firefox(executable_path=r'./geckodriver')
        logging.info("Driver started")

        self.storage = HandleStorage(self.base_url, self.max_nesting_lvl)

        # Code for highlighting xpath
        with open('./service_js/ext.js') as ext_source:
            self.ext_script = ext_source.read()

        # Code for get absolute xpath
        with open('./service_js/absoluteXPath.js') as js_source:
            self.xpath_script = js_source.read()
        
        logging.info('Javascript loaded')

    def create_path(self):
        """Create dirs for service data...

        Returns:
            True for success..

        """

        # Which subdirs should be in test dir?
        # shots - dir for screenshots
        # ... - dir for ...
        data_subdirs = ['shots']

        # If not dir...
        if not os.path.exists(self.data_path):

            # ... create it!
            os.makedirs(self.data_path)
            logging.debug(f'Create {self.data_path}')

        # Same for subdirs
        for sbdr in data_subdirs:
            full_path = os.path.abspath(os.path.join(self.data_path, sbdr))

            if not os.path.exists(full_path):
                os.makedirs(full_path)
                logging.debug(f'Create {full_path}')

        return True

    def process_service(self):
        self.start_bypass()
        self.end_bypass()

    def start_bypass(self):

        # Save info for controller
        self.save_source(os.path.join(self.data_path, 'start.html'))
        logging.info('Start page saved!')

        self.crawl_page()

    def end_bypass(self):
        # TODO: quit or exit?

        print('На новом уровне вложенности еще {0} путей'.format(self.storage.get_future_ways()))
        self.driver.quit()
        logging.info('Finished!')

    def make_screenshot(self):
        self.driver.execute_script(self.ext_script)

        # Create path for screenshot like .../shots/dd-mm-yyyy_hh:mm.png
        time = datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y_%H:%M')
        full_path = os.path.join(self.data_path, 'shots', f"{time}.png")
        
        # If you make a screenshot of the element, it hits the whole picture
        body = self.driver.find_element_by_tag_name('body')
        body.screenshot(full_path)

        logging.info(f'Screenshot {full_path} saved!')

    def save_source(self, target_name):
        with open(target_name, 'w') as target_file:
            target_file.write(self.driver.page_source)

    def get_xpath(self, element):
        return self.driver.execute_script(self.xpath_script, element)

    def highlight_element(self, xpath):
        self.driver.execute_script(self.ext_script, xpath)
        
    def crawl_page(self):
        while self.storage.is_okey():

            link = self.storage.get_link()
            if link == False:
                return

            # получаем ссылку для обхода
            try:
                self.driver.get(link)
            except:
                print('URL не валиден')
            
            # парсим страничку (в классе будут необходимые поля)
            page = Page(self.driver.page_source, self.base_url)
            
            # добавляем найденные ссылки в хранилище
            self.storage.add_links(page.links)

            # сохраняем внешние ссылки 
            for ex_url in page.external_url:
                self.external_urls.append(ex_url)

            # обходим страничку
            self.crawl_it(page, link)

            #logging.warning('|---> обошли {0} из {1} |  уровень вложенности = {2} ({3})'.format(self.storage.get_passed_ways(), self.storage.get_all_ways(), self.storage.get_nesting_level(), self.storage.link_number))
        
            print('=========================================================================')
            print('|---> обошли {0} из {1} |  уровень вложенности = {2} ({3})'.format(self.storage.get_passed_ways(), self.storage.get_all_ways(), self.storage.get_nesting_level(), self.storage.link_number))
            print('| {0} '.format(link))
            print('=========================================================================')


    def crawl_it(self, page, current_link):
        """
        Обход страницы
        Для каждой формы:
            -заполняем текстовые поля
            -нажимаем чекбоксы
            -выбираем радиокнопку
            -нажимаем button or submit

            Если есть поле PASSWD то делаем сигнал пользователю
        """
        for form in page.forms.keys():

            text_inputs = page.forms[form]['text']
            checkbox_inputs = page.forms[form]['checkbox']
            radio_inputs = page.forms[form]['radio']
            submit_inputs = page.forms[form]['submit']
            password_inputs = page.forms[form]['password']
            button_inputs = page.forms[form]['button']

            ######################################################################
            # Тут разбираемся что делать с паролем

            # Проверяем формы на наличие поля пароля и пробуем пароли из известных            
            for pwd_input in password_inputs:
                self.is_secret_shell = True
                for pwd in self.user_passwords:
                    try:
                        self.driver.find_element_by_xpath(pwd_input).clear()
                        self.driver.find_element_by_xpath(pwd_input).send_keys(pwd)
                    except:
                        print('Не получилось ввести пароль')
                    try:
                        self.driver.find_element_by_xpath(submit_inputs[0]).click()
                    except:
                        print('Не получилось нажать на кнопку отправки пароля')

                    if self.driver.current_url != current_link:
                        self.is_secret_shell = False
                        print('Пароль взломан')
                        break

            # Случай если поле с паролем лежит вне формы 
            # Пока считаем что такого не бывает


            # Если шелл запаролен то маякнем пользователю
            if self.is_secret_shell:
                logging.warning('я не знаю пароля, ПОМОГИ')

            ######################################################################

            # Заполняем форму
            self.fill_form(text_inputs, checkbox_inputs, radio_inputs)
            
            # Жмем отправку формы если есть такая кнопка 
            if len(submit_inputs):
                try:
                    self.driver.find_element_by_xpath(submit_inputs[0]).click()
                except:
                    print('Не могу нажать submit')

                # Если попали на новую ссылку сохраним ее и вернемся на тестируемую страницу 
                if self.driver.current_url != current_link:
                    self.return_to_current_page(current_link)

                    # Заполняем форму
                    self.fill_form(text_inputs, checkbox_inputs, radio_inputs)

            # Нажимаем на все кнопки 
            for button in button_inputs:
                try:
                    self.driver.find_element_by_xpath(button).click()
                except:
                    print('Не могу нажать button')

                # Если попали на новую ссылку сохраним ее и вернемся на тестируемую страницу 
                if self.driver.current_url != current_link:
                    self.return_to_current_page(current_link)

                    # Заполняем форму
                    self.fill_form(text_inputs, checkbox_inputs, radio_inputs)



    def fill_form(self, text_inputs, checkbox_inputs, radio_inputs):
        # Заполняем текстовые поля
            for text_input in text_inputs:
                try: 
                    self.driver.find_element_by_xpath(text_input).send_keys('SOME TEXT')
                except:
                    print('Текстовое поле не заполнено')

            # Выбираем чекбоксы
            for chbox_input in checkbox_inputs:
                try:
                    self.driver.find_element_by_xpath(chbox_input).click()
                except:
                    print('Не могу нажать на чекбокс')

            # Выбираем случайную радиокнопку
            if len(radio_inputs):
                try:
                    self.driver.find_element_by_xpath(radio_inputs[random.randint(0, len(radio_inputs))]).click()
                except:
                    print('Не могу выбрать радиокнопку')

    def return_to_current_page(self, current_link):
        # сохряняет текущую ссылку и вернется на указанную
        self.storage.add_links(self.driver.current_url)
        self.driver.get(current_link)
