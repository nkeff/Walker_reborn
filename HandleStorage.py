import logging
import validators

# Класс-хранилище 
# отвечает за хранение ссылок по которым будет гулять обходчик

class HandleStorage:
    def __init__(self, base_handlers, max_nesting_lvl):
        self.storage = []
        for i in range(max_nesting_lvl + 1):
            self.storage.append([])
        self.storage[0].append(base_handlers)

        # хранилище для всех ссылок (для проверки на уникальность)
        self.common_storage = [base_handlers]

        # ссылки которые будут обходиться только на новом уровне вложенности
        self.next_nestind_level_links = []

        # Текущий уровень вложенности
        self.nesting_level = 0
        self.max_nesting_level = max_nesting_lvl
        # порядковый номер ссылки на одном уровне 
        self.link_number = 0

        self.passed_ways = 0


    def add_links(self, links):
        # Добавляем уникальные ссылки на следующий уровень хранилища 
        for link in links:
            if link in self.common_storage:
                continue

            if validators.url(link):

                # На последнем уроввне добавляем ссылки в отдельное хранилище
                if self.nesting_level + 1 == self.max_nesting_level:
                    self.next_nestind_level_links.append(link)
                else:
                    self.common_storage.append(link)
                    self.storage[self.nesting_level + 1].append(link)


    def get_link(self):
        if self.link_number >= len(self.storage[self.nesting_level]):
            self.nesting_level += 1
            self.link_number = 0

        self.passed_ways += 1
        self.link_number += 1

        try:
        	res = self.storage[self.nesting_level][self.link_number - 1]
        except:
        	res = False
        return res


    def get_all_ways(self):
        return len(self.common_storage)

    def get_passed_ways(self):
        return self.passed_ways

    def get_future_ways(self):
        return len(self.next_nestind_level_links)

    def get_nesting_level(self):
        return self.nesting_level + 1

    def is_okey(self):
        if self.nesting_level == self.max_nesting_level - 1 and self.link_number == len(self.storage[self.nesting_level]):
            return False
        return True





        
