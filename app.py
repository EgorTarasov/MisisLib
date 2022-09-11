from controller import LibController


if __name__ == "__main__":
    l = LibController()
    print("\n".join([f"{doc.id}, {doc.name}" for doc in l.find_doc("Мат")]))
    doc_id = input("Введите id:")
    l.download_doc(doc_id)
