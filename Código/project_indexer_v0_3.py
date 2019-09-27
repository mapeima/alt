#! -*- encoding: utf8 -*-

import re
import sys
import pickle
import os
import json
# insort permite insertar elementos de forma ordenada partiendo de una lista que ya lo está
from bisect import insort
from unicodedata import normalize

clean_re = re.compile('\W+')
def clean_text(text):
    # Se quitan caracteres de puntuación
    text = clean_re.sub(' ', text)
    # Se quitan los acentos, dieresis etc.
    trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
    text = normalize('NFKC', normalize('NFKD', text).translate(trans_tab))
    # Se pasa a minúsculas
    return text.lower()
    
def save_object(object, file_name):
    with open(file_name, 'wb') as fh:
        pickle.dump(object, fh)

def save_objects(objects_list, file_name):
    with open(file_name, 'wb') as fh:
        for obj in objects_list:
            pickle.dump(obj, fh)

def load_json(filename):
    with open(filename) as fh:
        obj = json.load(fh)
    return obj

def doc_walker(docsdir, indexdir, debug_mode):
    """
    DESCRIPCIÓN:

        Recorre todos los documentos del directorio y genera el índice

    PARAMETROS:

        - docsdir -> Directorio a recorrer

        - indexdir -> Directorio en el que se creará el índice
        
        - debug_mode -> Pos que va a ser
    
    """
    # Diccionario: docid -> Ubicación del documento
    index_docid2path = {}
    # Diccionario : newsid -> docid
    index_news2docid = {}
    # Diccionario : term -> newsid
    index_term2news = {}
    # Lista de de permutaciones. Cada permutación apunta a los términos de los que puede provenir.
    # Puede haber tuplas con la misma permutación, pero tendrán distinto término.
    index_permuterm = []
    docid = 1
    newsid = 1
    # Una iteración por cada carpeta en el directorio
    for dirname, subdirs, files in os.walk(docsdir):
        if debug_mode:
            print("Se han encontrado {} archivos en el directorio {}".format(len(files), dirname))
        # Una iteración por cada archivo en la carpeta
        for filename in files:
            index_docid2path[docid] = filename
            fullname = os.path.join(dirname, filename)
            noticias = load_json(fullname)
            if debug_mode:
                print("Se han encontrado {} noticias en el archivo {}".format(len(noticias), filename))
            # Una iteración por cada noticia dentro del fichero
            for noticia in noticias:
                index_news2docid[newsid] = docid
                content = noticia["article"]
                title = noticia["title"]
                content = clean_text(content)
                content = content.split()
                if debug_mode:
                    print("Se han encontrado {0} términos en la noticia {1}".format(len(content), title))
                # Una iteración por cada término dentro de la noticia
                for term in content:
                    # Si el término es nuevo se obtienen sus permutaciones
                    if not term in index_term2news.keys():
                        permuterm_indexer(term, index_permuterm)
                    newslist = index_term2news.get(term)
                    # Se añade el id de la noticia al término si no lo estaba ya
                    if not newslist:
                        index_term2news[term] = [newsid]
                    elif not newsid in newslist:
                        newslist.append(newsid)
                        index_term2news[term] = newslist
                    newsid = newsid + 1
            docid = docid + 1

    if debug_mode:
        print("El índice de noticias es el siguiente: {}".format(index_news2docid))
        print("El índice de documentos es el siguiente: {}".format(index_docid2path))
        print("El índice de términos es el siguiente: {}".format(index_term2news))
        print("El índice permuterm es el siguiente: {}".format(index_permuterm))

    objects2save = [index_news2docid, index_docid2path, index_term2news, index_permuterm]
    save_objects(objects2save, indexdir)

def permuterm_indexer(term, permutation_list):
    """
    DESCRIPCIÓN:

        Obtiene todas las rotaciones del término y las añade a la lista de rotaciones global. La
        inserción se hace de forma ordenada

    PARAMETROS:

        - term -> Término a permutar

        - permutation_list -> Lista ordenada alfabéticamente de las permutaciones de todos lo
        términos analizados hasat el momento

    NOTA:

        El hecho de que la lista sea ordenada no sólo ayuda a que la búsqueda sea más sencilla
        y eficiente, también permite una inserción ordenada muy rápida
    
    """
    term_aux = term + '$'
    for i in range(0, len(term_aux)):
        permutation = term_aux[i:] + term_aux[:i]
        insort(permutation_list,(permutation, term))

def syntax():
    print("Use the correct syntax:\n\t-First argument:Path of the collection\n\t-Second Argument:Path to save the index")
    sys.exit()
    

if __name__ == '__main__':

    debug = False
    
    if len(sys.argv) > 2:
        docsdir = sys.argv[1]
        indexdir = sys.argv[2]
        if len(sys.argv) > 3:
            debug = sys.argv[3]
    else:
        syntax()
    
    doc_walker(docsdir, indexdir, debug)

