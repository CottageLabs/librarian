from librarian import components
from librarian.librarian import Librarian


def main():
    vector_store = components.get_vector_store()
    lib = Librarian(vector_store=vector_store)
    # lib.drop_vector_store()
    lib.add_file('/home/kk/Library/AI/deeplearning/Bharath Ramsundar, Peter Eastman, Patrick Walters, Vijay Pande - Deep Learning for the Life Sciences_ Applying Deep Learning to Genomics, Microscopy, Drug Discovery, and More (2019, O’Reilly Media) - libgen.li.pdf')

if __name__ == '__main__':
    main()