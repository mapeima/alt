#! -*- encoding: utf8 -*-
"""
Alumnos:
	Miguel Edo Goterris
	Andrey Kramer Savelev
	Luis Serrano Hernández
	Risheng Ye

"""

import re
import sys
import pickle
# insort permite insertar elementos de forma ordenada partiendo de una lista que ya lo está
from bisect import insort
from unicodedata import normalize

clean_re = re.compile('\W+')
def clean_text(text):
    # Se quitan caracteres de puntuación
    text = clean_re.sub(' ', text)
    # Se quitan los acentos, dieresis etc.
    trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
    text = normalize('NFKC', normalize('NFKD', unicode(text)).translate(trans_tab))
    text = str(text)
    # Se pasa a minúsculas
    return text.lower()

def split_text(text):
    # Consideraremos separadores de términos los espacios, los saltos de línea y los tabuladores
    return [i for i in re.split(' |\n|\t',text) if i]
    
def save_object(object, file_name):
    with open(file_name, 'wb') as fh:
        pickle.dump(object, fh)

def doc_walker(docdir, indexdir):
    # Diccionario: Palabra -> Lista de posiciones en el texto
    index_of_words = {}
    with open(docdir, 'r') as fh:
        text = fh.read()
        text = clean_text(text)
        content = split_text(text)
        pos = 0;
        for word in content:
            pos = pos + 1;
            current_word_positions = index_of_words.get(word, "")
            if not current_word_positions:
                index_of_words[word] = [pos]
            else:
                current_word_positions.append(pos)
                index_of_words[word] = current_word_positions
    save_object(index_of_words, indexdir)
    print(index_of_words)
            


def syntax():
    print("Use the correct syntax:\n\t-First argument:Path of the documetn\t-Second Argument:Path to save the index")
    sys.exit()
    
if __name__ == '__main__':
    
    if len(sys.argv) > 2:
        docdir = sys.argv[1]
        indexdir = sys.argv[2]
    else:
        syntax()
    
    doc_walker(docdir, indexdir)

