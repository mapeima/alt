import sys
import pickle
# Librería para la búsqueda binaria
import bisect

def recover_from_permuterm(term, permuterm):
    lwildcard = term.find("*")
    rwildcard = term.rfind("*")
    # Se devolverán los términos del permuterm que comiencen con el prefijo
    prefix = ""
    # Para X -> X$
    if lwildcard < 0:
        return [term]
    # Usan solo un comodín
    elif lwildcard == rwildcard:
        # Para X* -> $X*
        if lwildcard == len(term) - 1:
            prefix = '$' + term.replace("*","")
        # Para *X -> X$*
        elif lwildcard == 0:
            prefix = term.replace("*","") + '$'
        # Para X*Y -> Y$X*
        else:
            X = term[:lwildcard]
            Y = term[lwildcard + 1:]
            prefix = Y + '$' + X
    # Para *X* -> X*
    else:
        prefix = term.replace("*","")

    terms = []
    # Empieza la búsqueda de las palabras que coinciden con el prefijo
    start_point = bisect.bisect_left(permuterm, (prefix, ""))
    # Mientras las palabras empiezen por el prefijo
    while permuterm[start_point][0].find(prefix) > - 1:
        # Se añade el término para devolver
        terms.append(permuterm[start_point][1])
        start_point = start_point + 1

    return terms
    
if __name__ == '__main__':
    filename = sys.argv[1]
    term = sys.argv[2]
    with open(filename, 'rb') as fh:
        index_news2docid, index_docid2path, index_term2news, index_permuterm, index_titleterm2news,index_date2news,index_keyword2news = pickle.load(fh)
    print("Del comodín {} en el índice {} obtenemos:\n{}".format(term, filename, recover_from_permuterm(term,index_permuterm)))
    
