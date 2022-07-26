# TODO:попробовать асинхронно пройтись по всем папкам для скачивания книг
# https://stackoverflow.com/questions/9110593/asynchronous-requests-with-python-requests
# TODO: как ускорить это говно???
import json
import logging

import requests
from bs4 import BeautifulSoup


ROOT_URL = 'http://elibrary.misis.ru/browse.php'
FOLDER_URL = 'http://elibrary.misis.ru/browse.php?fFolderId={}&page_size=1000'
DOCUMENT_URL = 'http://elibrary.misis.ru/action.php?kt_path_info=ktcore.SecViewPlugin.actions.document&fDocumentId={}'
PAGE_URL = 'https://elibrary.misis.ru/plugins/SecView/getDoc.php?id={}}&page={}&type=large/slow'  # первый параметр - id
                                                                                                  # второй параметр - номер страницы
AUTH_URL = 'http://elibrary.misis.ru/login.php'
LOGIN = "2104105"
PWD = "Егор"
DISCOVERED = 0


class User:
    _id: int
    name: str

    def login(self, s: requests.Session):
        response = s.post(AUTH_URL, {
            'action': 'login',
            'cookieverify': '',
            'redirect': '',
            'username': self._id,
            'password': self.name,
            'language': 'ru_UN'
        })
        if response.status_code != 200:
            raise Exception(f"something went wrong: {response.status_code}")
        print(response.status_code)


class Document:
    _id: int
    name: str

    def __init__(self, id_: int):
        self._id = id

    def json(self):
        return {
            "id": self._id,
            "name": self.name
        }

    def get_url(self):
        return DOCUMENT_URL.format(self._id)

    def get_book(self):
        return []


class Folder:
    _id: int
    name: str
    items: dict[str, list[tuple[int, str]]]  # может содержать папки и документы

    def __init__(self, id_: int, s: requests.Session):

        self._id = id_
        self.url = FOLDER_URL.format(self._id)
        self.items = {
            "folders": [],
            "documents": []
        }
        response = requests.Response()
        try:
            response = s.get(self.url)
        except requests.exceptions.Timeout as e:
            logging.warning(f"Time out {e}")
        except ConnectionError as e:
            logging.warning(f"Network error:{e}")
        if response.status_code != 200:
            raise Exception(f"something went wrong: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find_all('tbody')
        rows = table[0].select('td.browse_column.title.sort_on')
        for r in rows:
            a = r.find_all('a')[0]
            # определение типов в папке
            if 'fDocumentId' in a['href']:
                id_ = int(a["href"][75:])
                name = a.getText()
                self.items['documents'].append((id_, name))
                logging.info(f'doc with id: {a["href"][75:]}')
            elif 'fFolderId' in a['href']:
                id_ = int(a["href"][46:])
                name = a.getText()
                self.items['folders'].append((id_, name))
                logging.info(f'folder with id: {a["href"][46:]}')
            else:
                logging.warning(f'uknown entity: {"fDocumentId" in a["href"]}, {a["href"]}')

    def add(self, item):
        # adds item to folder
        if isinstance(item, Folder) or isinstance(item, Document):
            self.items.append(item)
        else:
            raise Exception(f"item must be type: Document or Folder not {type(item)}")

    def get_url(self):
        return FOLDER_URL.format(self._id)

    def json(self):
        return {
            "id": self._id,
            # "url" : self.url,
            "items": self.items
        }


def get_page():
    # plugins/SecView/getDoc.php?id=9570&page=0&type=small/fast
    pass


def login(s: requests.Session):
    response = s.post(AUTH_URL, {
        'action': 'login',
        'cookieverify': '',
        'redirect': '',
        'username': LOGIN,
        'password': PWD,
        'language': 'ru_UN'
    })
    if response.status_code != 200:
        raise Exception(f"something went wrong: {response.status_code}")
    print(response.status_code)


def main():
    session = requests.Session()
    login(session)
    f = Folder(1, session)
    with open("result.json", "w", encoding="utf-8") as file:
        json.dump(f.json(), file, indent=4)
    print(f.json())


if __name__ == '__main__':
    main()
