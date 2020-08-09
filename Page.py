from bs4 import BeautifulSoup
import logging
import validators

import utils

class Page:
    """
    Класс реализующий анализ HTML-страницы на предмет активных элементов (форм, ссылок и хуйни)
    """
    def __init__(self, source, bs_url):

        self.base_url = bs_url

        self.stop_words = ['delete', 'remove', 'dl', 'download', 'kill', 'sleep', 'upload']

        # Какую инфу нужно доставать из страницы?
        # Сейчас это формы и ссылки
        self.forms = dict()
        self.links = []
        self.password = []

        # Внешние ссылки могут дать информацию о создателе шелла
        self.external_url = []

        # Текст страницы
        self.source = source
        # Создаем и запускаем парсер
        self.soup = BeautifulSoup(self.source, 'html.parser')
        self.process()

    def process(self):
        # Находим теги а и вытаскиваем из низ ссылки 
        self.find_a()

        # Находим теги форм и раскладываем их на состовляющие 
        self.find_forms()

        #
        self.find_password()


    def find_password(self):
    	# Список синонимов для поля ввода пароля
    	pwd_list = ['password', 'login', 'passwd', 'pwd']

    	#если такой тег найдется - сохранить 
    	for tag in self.soup('input'):
    		if tag['type'] == 'password' or tag.name in pwd_list or tag.get('id') in pwd_list:
    			self.password.append(utils.xpath_soup(tag))

    	

    def find_forms(self):
        # Extract all <form> and their <inpus>
        for form_tag in self.soup("form"):
            form_xpath = utils.xpath_soup(form_tag)
            self.forms[form_xpath] = {
                'text' : [],
                'submit' : [],
                'button' : [],
                'checkbox' : [],
                'password' : [],
                'radio' : [],
            }

            for element in form_tag('input'):
                
                # Для каждой формы на странице сохраняем xpath до следующих input-элементов
                if element['type'] in ['text', 'submit', 'button', 'checkbox', 'password', 'radio']:
                    self.forms[form_xpath][element['type']].append(utils.xpath_soup(element))
            

    def find_a(self):
        # Находим ссылк на странице (+ валидация этих ссылок)
        for i in self.soup('a', href=True):
            link = i['href']
            if not validators.url(i['href']):
                link = self.base_url + link

            # Проверяем нет ли стоп слов в нашей ссылке
            mark = 0
            for stop_word in self.stop_words:
                if stop_word in link:
                    mark = 1

            # Проверяем не внешняя ли это ссылка (внешнюю сохраним)
            if self.base_url not in link:
                mark = 1
            elif validators.url(link):
            	self.external_url.append(link)

            if validators.url(link) and mark == 0:
                self.links.append(link)

