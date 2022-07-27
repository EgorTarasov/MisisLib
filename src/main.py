# TODO:попробовать асинхронно пройтись по всем папкам для скачивания книг
# https://stackoverflow.com/questions/9110593/asynchronous-requests-with-python-requests
# TODO: как ускорить это говно???
import requests
from models import User, Document, Folder


def main():
    s = requests.Session()
    u = User()
    u.login(s)
    # http://elibrary.misis.ru/action.php?kt_path_info=ktcore.SecViewPlugin.actions.document&fDocumentId=9570
    f = Folder(1, s)
    print(f.json())


if __name__ == '__main__':
    main()
