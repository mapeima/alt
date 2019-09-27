import sys
import pickle

def obtain_indexes(filename):
    try:
        with open(filename, 'rb') as fh:
            index_news2docid = pickle.load(fh)
            index_docid2path = pickle.load(fh)
            index_term2news = pickle.load(fh)
            index_permuterm = pickle.load(fh)
            return index_news2docid, index_docid2path, index_term2news, index_permuterm

    except:
        print("The file + " + filename + " could not be opened or is not valid\n")
        sys.exit()

if __name__ == '__main__':
    filename = sys.argv[1]
    index_news2docid, index_docid2path, index_term2news, index_permuterm = obtain_indexes(filename)
    print("El índice de noticias es el siguiente: {}".format(index_news2docid))
    print("El índice de documentos es el siguiente: {}".format(index_docid2path))
    print("El índice de términos es el siguiente: {}".format(index_term2news))
    print("El índice permuterm es el siguiente: {}".format(index_permuterm))
