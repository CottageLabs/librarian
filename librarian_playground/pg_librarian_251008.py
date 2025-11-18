from librarian import components
from librarian.core.librarian import Librarian


def main():
    vector_store = components.get_vector_store()
    lib = Librarian(vector_store=vector_store)
    # lib.drop_collection()
    lib.add_file('/home/kk/Library/AI/deeplearning/Bharath Ramsundar, Peter Eastman, Patrick Walters, Vijay Pande - Deep Learning for the Life Sciences_ Applying Deep Learning to Genomics, Microscopy, Drug Discovery, and More (2019, O’Reilly Media) - libgen.li.pdf')


def main2():
    vector_store = components.get_vector_store()
    lib = Librarian(vector_store=vector_store)
    path = 'https://github.com/dypsilon/frontend-dev-bookmarks.git'
    results = lib.add_by_path(path)


def main3():
    lib = Librarian()
    lib.switch_collection('tmp10')
    lib.drop_collection()
    lib.switch_collection('tmp10')
    p = '/home/kk/note/bookmark/general_bookmark.md'
    # p = '/home/kk/Library/AI/AI for Data Science_ Artificial Intelligence Frameworks and Functionality for Deep Learning, Optimization, and Beyond ( PDFDrive ).pdf'
    lib.add_file(p)

    for r in lib.find_all_files():
        print(r)



if __name__ == '__main__':
    main3()