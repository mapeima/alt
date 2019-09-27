import sys
import pickle
# Librería para la búsqueda binaria
import bisect
import re
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

def split_text(text):
    # Consideraremos separadores de términos los espacios, los saltos de línea y los tabuladores
    return [i for i in re.split(' |\n|\t',text) if i]

def text2news(text, index_term2news):
    text = split_text(clean_text(text))
    news = index_term2news[text[0]].keys()
    res = []
    for term in text[1:]:
        try:
            news = intersection(news, index_term2news[term].keys())
        except:
            return []

    for newsid in news:
        postings = [index_term2news[text[0]][newsid]]
        for term in text[1:]:
            postings.append(index_term2news[term][newsid])
        # pointers = [0 for i in range(len(postings))]
        for pos in postings[0]:
            encontrado = True
            auxpos = pos
            for i in range(1, len(postings) - 1):
                if auxpos + 1 not in postings[i]:
                    encontrado = False
                    break
            if encontrado:
                res.append(newsid)
                break
                
    return res 
                

def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3

if __name__ == '__main__':
    filename = sys.argv[1]
    term = sys.argv[2]
    with open(filename, 'rb') as fh:
        index_news2docid, index_docid2path, index_term2news, index_permuterm, index_titleterm2news,index_date2news,index_keyword2news = pickle.load(fh)
    print(text2news(term,index_term2news))
    
