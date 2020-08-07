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

            # Проверяем не внешняя ли это ссылка
            if self.base_url not in link:
                mark = 1

            if validators.url(link) and mark == 0:
                self.links.append(link)

