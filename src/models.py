"""

"""
import requests
from bs4 import BeautifulSoup


ROOT_URL = 'http://elibrary.misis.ru/browse.php'

DOCUMENT_URL = 'http://elibrary.misis.ru/action.php?kt_path_info=ktcore.SecViewPlugin.actions.document&fDocumentId={}'
PAGE_URL = 'https://elibrary.misis.ru/plugins/SecView/getDoc.php?id={}&page={}&type=large/slow'  # первый параметр - id




class User:
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
        print(response.status_code)


class Document:
    _id: int
    name: str

    def __init__(self, id_: int):
        self._id = id_

    def json(self):
        return {
            "id": self._id,
            "name": self.name
        }

    def get_url(self):
        return DOCUMENT_URL.format(self._id)

    def get(self, s: requests.Session):
        response = s.get(DOCUMENT_URL.format(self._id))
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(f"something went wrong {response.status_code}")
        
        page = 0
        print(PAGE_URL.format(self._id, page))
        while True:
            response = s.get(PAGE_URL.format(self._id, page))
            print(response.text)
            page += 1


class Folder:
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
            print(f"Time out {e}")
        except ConnectionError as e:
            print(f"Network error:{e}")
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
                print(f'doc with id: {a["href"][75:]}')
            elif 'fFolderId' in a['href']:
                id_ = int(a["href"][46:])
                name = a.getText()
                self.items['folders'].append((id_, name))
                print(f'folder with id: {a["href"][46:]}')
            else:
                print(f'uknown entity: {"fDocumentId" in a["href"]}, {a["href"]}')

    def add(self, item):
        # adds item to folder
        if isinstance(item, Folder) or isinstance(item, Document):
            self.items.append(item)
        else:
            raise Exception(f"item must be type: Document or Folder not {type(item)}")

    def get_url(self):
        return self.FOLDER_URL.format(self._id)

    def json(self):
        return {
            "id": self._id,
            "items": self.items
        }
