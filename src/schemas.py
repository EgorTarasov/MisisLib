"""
TODO: Переписать весь функционал в модель
"""
import requests
from bs4 import BeautifulSoup
import logging

ROOT_URL = 'http://elibrary.misis.ru/browse.php'

DOCUMENT_URL = 'http://elibrary.misis.ru/action.php?kt_path_info=ktcore.SecViewPlugin.actions.document&fDocumentId={}'
PAGE_URL = 'https://elibrary.misis.ru/plugins/SecView/getDoc.php?id={}&page={}&type=large/slow'  # первый параметр - id


class UserSchema:
    _id: str = 'гость'
    name: str = 'гость'
    AUTH_URL = 'http://elibrary.misis.ru/login.php'

    def login(self, s: requests.Session):
        response = s.post(self.AUTH_URL, {
            'action': 'login',
            'cookieverify': '',
            'redirect': '',
            'username': self._id,
            'password': self.name,
            'language': 'ru_UN'
        })
        if response.status_code != 200:
            raise Exception(f"something went wrong: {response.status_code}")
        logging.info(f'successfully loggined to elib with {self._id} {self.name}')


class DocumentSchema:
    _id: int
    name: str

    def __init__(self, id_: int, name_: str):
        self._id = id_
        self.name = name_

    def json(self):
        return {
            "id": self._id,
            "name": self.name
        }

    def get_url(self):
        return DOCUMENT_URL.format(self._id)

    def get(self, s: requests.Session):
        response = s.get(DOCUMENT_URL.format(self._id))
        logging.info(f'found doc {self._id}')
        if response.status_code != 200:
            raise Exception(f"something went wrong {response.status_code}")
        
        page = 0
        logging.info(f'started downloading {self._id}')
        while True:
            response = s.get(PAGE_URL.format(self._id, page))
            print(response.text)
            page += 1


class FolderSchema:
    _id: int
    name: str
    items: dict[str, list[tuple[int, str]]]  # может содержать папки и документы
    FOLDER_URL = 'http://elibrary.misis.ru/browse.php?fFolderId={}&page_size=1000'

    def __init__(self, id_: int, s: requests.Session):

        self._id = id_
        self.items = {
            "folders": [],
            "documents": []
        }
        response = requests.Response()
        try:
            response = s.get(self.FOLDER_URL.format(self._id))
        except requests.exceptions.Timeout as e:
            logging.error(f"Time out {e}")
        except ConnectionError as e:
            logging.error(f"Network error:{e}")
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
                # print(f'doc with id: {a["href"][75:]}')
            elif 'fFolderId' in a['href']:
                id_ = int(a["href"][46:])
                name = a.getText()
                self.items['folders'].append((id_, name))
                # print(f'folder with id: {a["href"][46:]}')
            else:
                logging.warning(f'uknown entity: {a["href"]}')

    def get_url(self):
        return self.FOLDER_URL.format(self._id)

    def json(self):
        return {
            "id": self._id,
            "items": self.items
        }
