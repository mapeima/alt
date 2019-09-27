#! -*- encoding: utf8 -*-

import re
import sys
import pickle
import os
import json

clean_re = re.compile('\W+')
def clean_text(text):
    return clean_re.sub(' ', text)
    
def save_object(object, file_name):
    with open(file_name, 'wb') as fh:
        pickle.dump(object, fh)

def load_json(filename):
    with open(filename) as fh:
        obj = json.load(fh)
    return obj

def doc_walker(docsdir, indexdir):
    # Una iteraciónpor cada carpteda em el directorio
    for dirname, subdirs, files in os.walk(docsdir):
        # Una iteración por cada archivo en el fichero
        for filename in files:
            #docid
            noticias=load_json(filename)
            for noticia in noticias:
                #newid
                noticia["article"]


def syntax():
    print("Use the correct syntax:\n\t-First argument:Path of the collection\n\t-Second Argument:Path to save the index")
    sys.exit()
    

if __name__ == '__main__':
    if len(sys.argv) > 2:
        docsdir = sys.argv[1]
        
    else:
        syntax()
    index_doc={}
    index_noticia={}
    index={}
    doc_walker(docsdir, indexdir)
        indexdir = sys.argv[2]
    