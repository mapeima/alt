import sys
import pickle

def obtain_indexes(filename):
    try:
        with open(filename, 'rb') as fh:
            index_news2docid = pickle.load(fh)
            index_docid2path = pickle.load(fh)
            index_term2news = pickle.load(fh)
            index_permuterm = pickle.load(fh)
            index_titleterm2news = pickle.load(fh)
            return index_news2docid, index_docid2path, index_term2news, index_permuterm

    except:
        print("The file + " + filename + " could not be opened or is not valid\n")
        sys.exit()

if __name__ == '__main__':
    filename = sys.argv[1]
    with open(filename, 'rb') as fh:
        index_news2docid, index_docid2path, index_term2news, index_permuterm, index_titleterm2news,index_date2news,index_keyword2news = pickle.load(fh)
    
    print("El índice de noticias es el siguiente: {}\n\ty su longitud es: {}".format(index_news2docid,len(index_news2docid)))
    print("El índice de documentos es el siguiente: {}\n\ty su longitud es: {}".format(index_docid2path,len(index_docid2path)))
    print("El índice de términos es el siguiente: {}\n\ty su longitud es: {}".format(index_term2news,len(index_term2news)))
    print("El índice permuterm es el siguiente: {}\n\ty su longitud es: {}".format(index_permuterm,len(index_permuterm)))
    print("El índice de términos en títulos es el siguiente: {}\n\ty su longitud es: {}".format(index_titleterm2news,len(index_titleterm2news)))
    print("El índice de fechas es el siguiente: {}\n\ty su longitud es: {}".format(index_date2news,len(index_date2news)))
    print("El índice de categorías es el siguiente: {}\n\ty su longitud es: {}".format(index_keyword2news,len(index_keyword2news)))
