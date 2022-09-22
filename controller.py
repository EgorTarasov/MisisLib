import os
import time
from PIL import Image

import models as models
from loader import Session

from progress.bar import IncrementalBar
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
    image_name = "test_pages/{}.png"

    def __init__(self, debug=False) -> None:
        self.db_session = None

        # initializing selenium driver
        options = Options()
        if debug:
            options.headless = False
        else:
            options.headless = True
        options.add_argument("window-size=1920,1080")
        self.__driver = webdriver.Chrome("drivers/chromedriver", options=options)

        self.__auth_delay = 2

        self.__auth()

    def __del__(self):
        print("deleted controller")
        #self.__driver.quit()
        #time.sleep(self.__auth_delay)

    def get_folder(self):
        """
        Получение содержания папки
        """
        pass

    def __get_doc(self, doc_id: int):
        """
        Получение пути / документа
        """
        if self.db_session == None:
            self.db_session = Session()
        d = self.db_session.query(models.Document).filter_by(id=doc_id).one()
        self.db_session = None
        return (doc_id, d.name)

    def __auth(self, user_id: str = "2104105", name: str = "Егор"):

        auth = False
        self.__driver.get(AUTH_URL)
        while not auth:
            try:
                input_login = self.__driver.find_element(By.NAME, "username")
            except NoSuchElementException:
                continue
            input_login.send_keys(user_id)
            input_password = self.__driver.find_element(By.NAME, "password")
            input_password.send_keys(name)
            self.__driver.find_element(
                By.CSS_SELECTOR, "#formbox > form > div > input[type=submit]"
            ).click()
            time.sleep(self.__auth_delay)
            auth = True

    def __get_page_count(self, document_id: int) -> int:
        self.__driver.get(DOCUMENT_URL.format(document_id))
        time.sleep(5)
        return int(
            self.__driver.find_element(By.CSS_SELECTOR, "#SecView-page-count").text
        )

    def __create_pdf(self, document_id: int):

        dir_path = r'/test_pages/'

        page_count = len(os.listdir(os.getcwd()+dir_path))

        # create pdf from images
        #TODO: достать название документа и кол-во странициз БД
        _, name = self.__get_doc(doc_id=document_id)
        images = [
            Image.open(self.image_name.format(i)).convert("RGB") for i in range(page_count)
        ]

        pdf_path = os.getcwd() + f"/books/{name}.pdf"

        images[0].save(
            pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
        )
        for path in os.listdir(os.getcwd()+dir_path):
            p = os.path.join(os.getcwd()+dir_path, path)
            os.remove(os.path.join(p))

    def download_doc(self, document_id: int):

        page_count = self.__get_page_count(document_id=document_id)
        page = 0
        bar = IncrementalBar('Pages downloaded', max=page_count)

        while page < page_count - 1:
            try:
                self.__driver.find_element(By.ID, "loadingEffect")
            except NoSuchElementException:
                with open(self.image_name.format(page), "wb") as file:
                    file.write(
                        self.__driver.find_element(
                            By.CSS_SELECTOR, "#SecViewPluginInner > div > img"
                        ).screenshot_as_png
                    )
                self.__driver.find_element(
                    By.CSS_SELECTOR,
                    "#SecViewPlugin > div.centerPart > div > div > div.controlBlock > div.navigationControlBlock > a.right",
                ).click()
                page += 1
                bar.next()
                continue
        bar.finish()
        self.__create_pdf(document_id=document_id)

    def find_doc(self, doc_name: str):
        result = []
        if self.db_session is None:
            self.db_session = Session()
        docs = self.db_session.query(models.Document).all()
        for i in docs:
            if doc_name in i.name:
                result.append(i)
        return result


l = LibController(debug=False)
id = l.find_doc("Основы")
print("".join([f"{i.id} {i.name}\n" for i in id]))
l.download_doc(int(input()))
