import sys
from controller import LibController

# TODO: Cli tool for downloading


# https://docs.python.org/3/library/argparse.html


def main(foo, bar, **kwargs):
    print(foo, bar, kwargs)
    pass


if __name__ == "__main__":
    main(
        sys.argv[1],  # foo
        sys.argv[2],  # bar
        **dict(arg.split("=") for arg in sys.argv[3:])
    )
    # l = LibController()
    # print("\n".join([f"{doc.id}, {doc.name}" for doc in l.find_doc("Мат")]))
    # doc_id = input("Введите id:")
    # l.download_doc(doc_id)
