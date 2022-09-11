import os
import time
import logging
import json
import requests
from PIL import Image

from models import Folder, Document
from loader import Session


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

# from loader import Session

DOCUMENT_URL = "http://elibrary.misis.ru/action.php?kt_path_info=ktcore.SecViewPlugin.actions.document&fDocumentId={}"
PAGE_URL = "http://elibrary.misis.ru/plugins/SecView/getDoc.php?id={}&page={}&type=small/{}"  # проблема, не все страницы есть в fast / slow
AUTH_URL = "http://elibrary.misis.ru/login.php"


class LibController:
    folder_url = "http://elibrary.misis.ru/browse.php?fFolderId={}&page_size=1000"
    document_url = "http://elibrary.misis.ru/action.php?kt_path_info=ktcore.SecViewPlugin.actions.document&fDocumentId={}"
    page_url = "http://elibrary.misis.ru/plugins/SecView/getDoc.php?id={}&page={}&type=small/{}"
    pages_path = "pages/"

    def __init__(self) -> None:
        self.db_session = None

    def get_folder(self):
        """
        Получение содержания папки
        """
        pass

    def get_doc(self, doc_id: int):
        """
        Получение пути / документа
        """
        if self.db_session == None:
            self.db_session = Session()
        d = self.db_session.query(Document).filter_by(id=doc_id).one()
        self.db_session = None
        return (doc_id, d.name)

    def login(self):
        delay = 1
        user_id, name = 2104105, "Егор"
        self.driver.get(AUTH_URL)
        time.sleep(delay)
        input_login = self.driver.find_element(By.NAME, "username")
        input_login.send_keys(user_id)
        input_password = self.driver.find_element(By.NAME, "password")
        input_password.send_keys(name)
        self.driver.find_element(
            By.CSS_SELECTOR, "#formbox > form > div > input[type=submit]"
        ).click()
        time.sleep(delay)

    def download_doc(self, document_id: int):
        # TODO: create progress bar
        options = Options()
        options.headless = True
        options.add_argument("window-size=1920,1080")
        driver = webdriver.Chrome("drivers/chromedriver", options=options)
        delay = 2
        user_id, name = 2104105, "Егор"

        # Auth in eliblary
        auth = False
        driver.get(AUTH_URL)
        while not auth:
            try:
                input_login = driver.find_element(By.NAME, "username")
            except NoSuchElementException:
                continue
            input_login.send_keys(user_id)
            input_password = driver.find_element(By.NAME, "password")
            input_password.send_keys(name)
            submit_button = driver.find_element(
                By.CSS_SELECTOR, "#formbox > form > div > input[type=submit]"
            ).click()
            time.sleep(delay)
            auth = True

        # Auth in elibrary

        # goto document page and download images
        image_url = "http://elibrary.misis.ru/"
        driver.get(DOCUMENT_URL.format(document_id))
        time.sleep(5)
        page_count = int(
            driver.find_element(By.CSS_SELECTOR, "#SecView-page-count").text
        )

        image_name = "test_pages/{}.png"
        page = 0
        while page < page_count - 1:
            #
            # loadingEffect > div
            # id = loadingEffect
            #
            try:
                driver.find_element(By.ID, "loadingEffect")
            except NoSuchElementException:
                print(page)
                with open(image_name.format(page), "wb") as file:
                    file.write(
                        driver.find_element(
                            By.CSS_SELECTOR, "#SecViewPluginInner > div > img"
                        ).screenshot_as_png
                    )
                driver.find_element(
                    By.CSS_SELECTOR,
                    "#SecViewPlugin > div.centerPart > div > div > div.controlBlock > div.navigationControlBlock > a.right",
                ).click()
                page += 1
                continue
        # exit webdriver
        driver.close()
        # create pdf from images
        images = [
            Image.open(image_name.format(i)).convert("RGB") for i in range(page_count)
        ]

        pdf_path = os.getcwd() + f"/books/{document_id}.pdf"

        images[0].save(
            pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
        )

    def find_doc(self, doc_name: str):
        result = []
        if self.db_session == None:
            self.db_session = Session()
        docs = self.db_session.query(Document).all()
        for i in docs:
            if doc_name in i.name:
                result.append(i)
        return result

    def get_folder(self, folder_id, s, db_session):

        if folder_id == 0:

            f = Folder(
                id=0,
                name="папки",
                folder_id=0,
            )
            db_session.add(f)

        r = s.get(self.folder_url.format(folder_id))
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        table = soup.find_all("tbody")
        rows = table[0].select("td.browse_column.title.sort_on")
        for r in rows:
            a = r.find_all("a")[0]
            # определение типов в папке
            if "fDocumentId" in a["href"]:
                id_ = int(a["href"][75:])
                name = a.getText()
                print(f"Document: {id_}, {name}")
                d = Document(
                    id=id_,
                    folder_id=folder_id,
                    name=name,
                )
                db_session.add(d)
                # self.get_doc(id_, name).get(s)
                # print(f'doc with id: {a["href"][75:]}')
            elif "fFolderId" in a["href"]:
                id_ = int(a["href"][46:])
                name = a.getText()
                print(f"Folder: {id_}, {name}")
                f = Folder(id=id_, name=name, folder_id=folder_id)
                db_session.add(f)
                self.get_folder(id_, s, db_session=db_session)
                # print(f'folder with id: {a["href"][46:]}')
            else:
                print(f'uknown entity: {a["href"]}')

    def update_lib(self):
        # TODO: async
        """
        получение всех файлов в библиотеке
        """
        # TODO: получение всех зависимостей folder -> folder & folder -> file
        _folder_id = 0
        s = login()
        r = s.get(self.folder_url.format(_folder_id))
        if self.db_session != None:
            self.db_session = Session()
        self.get_folder(0, s)
        self.db_session.commit()
        self.db_session = None
        logging.info(f"updated lib")


# l = LibController()
# id = l.find_doc("2100")
# l.download_doc(id[0].id)
