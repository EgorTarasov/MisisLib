# TODO: basic add logging

import os
import json
import time
import logging
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
page_download_time = {}


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
        self.__debug = debug
        if self.__debug:
            options.headless = False
        else:
            options.headless = True
        with open("timing.json", "r") as file:
            self.page_download_time = dict(json.load(file))
        options.add_argument("window-size=1920,1080")
        # FIXME: DeprecationWarning:executable_path has been deprecated, please pass in a Service object
        #   self.__driver = webdriver.Chrome("drivers/chromedriver", options=options)
        self.__driver = webdriver.Chrome("drivers/chromedriver", options=options)
        self.page_download_time = {}

        self.__auth_delay = 2
        self.__auth()

    # def __del__(self):
    #     f = open("timing.json", "w")
    #     json.dump(self.page_download_time, f, indent=4)
    #     print("deleted controller")

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
        t1 = time.time()
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
        logging.info(f"logged in: {time.time()} sec")

    def __get_page_count(self, document_id: int) -> int:
        t1 = time.time()
        self.__driver.get(DOCUMENT_URL.format(document_id))
        time.sleep(5)
        logging.info(f"page_count: {document_id} t: {time.time() - t1}")
        return int(
            self.__driver.find_element(By.CSS_SELECTOR, "#SecView-page-count").text
        )

    def __create_pdf(self, document_id: int):

        dir_path = r"/test_pages/"

        page_count = len(os.listdir(os.getcwd() + dir_path)) - 1

        # create pdf from images
        # TODO: достать название документа и кол-во странициз БД
        _, name = self.__get_doc(doc_id=document_id)
        images = [
            Image.open(self.image_name.format(i)).convert("RGB")
            for i in range(page_count)
        ]

        pdf_path = os.getcwd() + f"/books/{name}.pdf"

        images[0].save(
            pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
        )
        for path in os.listdir(os.getcwd() + dir_path):
            p = os.path.join(os.getcwd() + dir_path, path)
            os.remove(os.path.join(p))

    def download_doc(self, document_id: int):

        page_count = self.__get_page_count(document_id=document_id)
        page = 0
        bar = IncrementalBar("Pages downloaded", max=page_count)
        self.page_download_time[document_id] = []
        t1 = time.time()
        start_time = t1
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
                self.page_download_time[document_id] += [time.time() - t1]
                t1 = time.time()
                bar.next()
                continue

        bar.finish()
        logging.info(f"downloaded {document_id} t: {time.time() - start_time}")
        logging.info(
            f"downloaded {document_id} t_avg: {self.page_download_time, sum(page_download_time) / len(self.page_download_time)}"
        )
        self.__create_pdf(document_id=document_id)

    def fast_download(self, document_id: int):
        page_count = self.__get_page_count(document_id=document_id)
        page = 0
        # max_time = 30 sec
        # 2 sec per page -> 15 pages per thread??

        t1 = time.time()

        def download_pages(document_id: int, start_page: int, page_count: int):
            cur_page = start_page

            while cur_page < start_page + page_count - 1:
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
                    cur_page += 1
                    continue

            pass

        logging.info(f"{time.time() - t1}")
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


if __name__ == "__main__":
    logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)
    debug = True
    l = LibController(debug=debug)
    l.download_doc(9187)
    # while True:
    #     try:
    #         i = input("Enter document name: ")
    #         if not i.isdigit():
    #             print("")
    #             continue
    #         r = l.find_doc(i)
    #         if len(r) == 0:
    #             logging.warning("Nothing found")
    #             continue
    #         print("".join([f"{i.id} {i.name}\n" for i in r]))
    #         l.download_doc(int(input()))
    #     except KeyboardInterrupt:
    #         logging.info("exiting...")
    #         del l
    #         exit(0)
