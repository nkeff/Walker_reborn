from selenium import webdriver
import logging

import Bypass

def main(url):
    logging.debug('Начало работы')

    walker = Bypass.Bypass(url, '.', 20)
    walker.process_service()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    shell_url = "http://aidbox.ru:8001/cutia.php"
    #shell_url = "https://www.bmstu.ru/"
    main(shell_url)