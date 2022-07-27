# TODO:попробовать асинхронно пройтись по всем папкам для скачивания книг
# TODO: Хранение документов и папок в бд
import requests
from src.schemas import UserSchema, FolderSchema
import logging
logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%d/%m/%Y %I:%M:%S %p',
    filename='example.log',
    encoding='utf-8',
    level=logging.DEBUG)


def main():
    s = requests.Session()
    u = UserSchema()
    u.login(s)
    # http://elibrary.misis.ru/action.php?kt_path_info=ktcore.SecViewPlugin.actions.document&fDocumentId=9570
    f = FolderSchema(1, s)
    logging.info(f.json())


if __name__ == '__main__':
    main()
