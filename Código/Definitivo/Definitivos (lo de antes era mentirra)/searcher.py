#!/usr/bin/env python
"""
Alumnos:
	Miguel Edo Goterris
	Andrey Kramer Savelev
	Luis Serrano Hernández
	Risheng Ye

Ampliaciones hechas:
	permuterms
	indices adicionales
	parentesis
	terminos consecutivos
"""
import re
import sys
import pickle
from project_indexer import clean_text
import shlex
import json
import bisect

#lista con tods los id de noticias. Necesaria para la operacion Not
NOTICIA = []

#Diccionario simple para hacer pruebas temporales
dic = {}

#Lista con los terminos buscados. Se actualiza con cada consulta.
BUSCADOS = []
#Nodo basico para el arbol de operaciones
class Nodo:
	def __init__(self):
		raise NotImplementedError
	#Calculo del valor de las operaciones de forma recursiva
	def getValor(self):
		raise NotImplementedError

#Nodo que simplemente guarda una palabra y devuelve su lista de docId
class Valor(Nodo):

	def __init__(self, palabra):
		self.palabra = palabra

	def getValor(self):
		if(" " in self.palabra):
			try:
				values = text2news(self.palabra, index_term2news)
			except:
				values = []
		elif(self.palabra.startswith("title:")):
			if(self.palabra[6:] in index_titleterm2news):
				values = index_titleterm2news[self.palabra[6:]]
			else:
				values = []
		elif(self.palabra.startswith("date:")):
			if(self.palabra[5:] in index_date2news):
				values = index_date2news[self.palabra[5:]]
			else:
				values = []
		elif(self.palabra.startswith("keywords:")):
			if(self.palabra[9:] in index_keyword2news):
				values = index_keyword2news[self.palabra[9:]]
			else:
				values = []
		else:
			if(self.palabra in dic):
				values = list(recuperarDic(self.palabra).keys())
			else:
				values = []
			BUSCADOS.append(self.palabra)
		values.sort()
		return values

#Clases de operacions binarias
class binOp(Nodo):

	def __init__(self, nodoI,nodoD):
		self.nodoI = nodoI
		self.nodoD = nodoD

	def getValor(self):
		return self.exec()

#Clase del nodo de la operacion AND
class And(binOp):
	#Calculo
	def exec(self):
		ret = []
		contadorI = 0
		valorI = self.nodoI.getValor()
		contadorD = 0
		valorD = self.nodoD.getValor()

		while (contadorI < len( valorI )) and (contadorD < len( valorD )):
			if valorI[contadorI] == valorD[contadorD]:
				ret += [valorI[contadorI]]
				contadorI += 1
				contadorD += 1
			elif(valorI[contadorI] < valorD[contadorD]):
				contadorI += 1
			else:
				contadorD += 1

		return ret



class Or(binOp):
	#Calculo
	def exec(self):
		ret = []
		contadorI = 0
		valorI = self.nodoI.getValor()
		contadorD = 0
		valorD = self.nodoD.getValor()

		while (contadorI < len( valorI )) and (contadorD < len( valorD )):
			if valorI[contadorI] == valorD[contadorD]:
				ret += [valorI[contadorI]]
				contadorI += 1
				contadorD += 1
			elif(valorI[contadorI] < valorD[contadorD]):
				ret += [valorI[contadorI]]
				contadorI += 1
			else:
				ret += [valorD[contadorD]]
				contadorD += 1

		while (contadorI < len( valorI )):
			ret += [valorI[contadorI]]
			contadorI += 1
		while (contadorD < len( valorD )):
			ret += [valorD[contadorD]]
			contadorD += 1
		return ret


class Not(Nodo):
	def __init__(self, nodo):
		self.nodo = nodo

	def getValor(self):
		return self.exec()

	def exec(self):
		ret = []
		contadorNodo = 0
		contadorDOCID = 0
		valor = self.nodo.getValor()
		while (contadorNodo < len( valor )) and (contadorDOCID < len( NOTICIA )):
			if valor[contadorNodo] == NOTICIA[contadorDOCID]:
				contadorNodo += 1
				contadorDOCID += 1
			else:
				ret += [NOTICIA[contadorDOCID]]
				contadorDOCID += 1

		while (contadorDOCID < len( NOTICIA )):
			ret += [NOTICIA[contadorDOCID]]
			contadorDOCID += 1
		return ret


#TODO: metodo temporal para poder hacer pruebas
"""
Devuelve lis de los DocID de una palabra

:param palabra: palabra
:return: lista docID
	"""
def recuperarDic(palabra):
	return dic[palabra]

"""
:param consultaString: String que representa una consulta
:return: array formado a partir del string donde cada elemento es una operacion, parentesis o palabra
"""
def stringToArray(consultaString):
	noSpaces = shlex.split(consultaString)
	parentesis = []
	parentesisAux = []
	BUSCADOS = []
	for i in noSpaces:
		parentesis += list(filter(('').__ne__, re.split('([^\w\*\:\-\? "])', i)))

	for i in parentesis:
		if(i.startswith("title:")):
				parentesisAux.append("title:" + clean_text(i[6:]))
		elif(i.startswith("date:")):
				parentesisAux.append(i)
		elif(i.startswith("keywords:")):
				parentesisAux.append("keywords:" + clean_text(i[9:]))
		elif(i not in ['(',')','NOT','AND','OR']):
			if('*' not in i and '?' not in i):
				parentesisAux.append(clean_text(i))
			#Limpiamos la palabra y volvemos a insertar el asterisco en su posicion
			else:
				if('*' in i):
					pos = i.find('*')
					clean = clean_text(i.replace('*', ''))
					reinsert = clean[:pos] + '*' + clean[pos:]
				elif('?' in i):
					pos = i.find('?')
					clean = clean_text(i.replace('?', ''))
					reinsert = clean[:pos] + '?' + clean[pos:]
				matches = recover_from_permuterm(reinsert,index_permuterm)
				parentesisAux.append('(')
				flag = True
				for m in matches:
					if(flag):
						parentesisAux.append(m)
						flag = False
					else:
						parentesisAux.append('OR')
						parentesisAux.append(m)

					
				parentesisAux.append(')')
		else:
			parentesisAux.append(i)
	
	return parentesisAux


def finParentesis(consultaArray,posIni):
	if consultaArray[posIni] != '(':
		return -1

	contadorParentesis = 0;
	for pos, simbolo in enumerate(consultaArray[posIni:]):
		if simbolo == '(':
			contadorParentesis += 1
		elif simbolo == ')':
			contadorParentesis -= 1

		if contadorParentesis == 0:
			return pos+posIni

"""
Dado un array de consulta y la posicion de un parentesis de cierre devuelve
el parentesis de abertura con el que hace pareja

:param consultaArray: array que representa consulta (obtenido con stringToArray)
:param posIni: Posicion del parentesis cuya pareja queremos encontrar
:return: posicion del parentesis que forma pareja
"""
def iniParentesis(consultaArray,posIni):
	if consultaArray[posIni] != ')':
		return -1

	contadorParentesis = 0;
	for pos, simbolo in reversed(list(enumerate(consultaArray[:posIni+1]))):
		if simbolo == '(':
			contadorParentesis += 1
		elif simbolo == ')':
			contadorParentesis -= 1

		if contadorParentesis == 0:
			return pos


"""
separa un array de consulta en 3 partes para su facil insercion como nodo

:param consultaArray: array que representa consulta (obtenido con stringToArray)
:return: tripleta que contiene [nodo,op,nodo] (los nodos tipo valor y
not tienen el primer nodo como una lista vacia)
"""
def nextNodo(consultaArray):
	consultaArray = eliminarTodosParentesisExternos(consultaArray)

	if len(consultaArray) == 1:
		return ([],"valor",consultaArray)
	else:
		if consultaArray[-1] == ')':
			parentesisIniDer = iniParentesis(consultaArray,len(consultaArray)-1)
			nodoDer = consultaArray[parentesisIniDer:]
			consultaArray = consultaArray[:parentesisIniDer]
		else:
			nodoDer = [consultaArray[-1] ]
			consultaArray = consultaArray[:-1]

		op = consultaArray[-1]
		consultaArray = consultaArray[:-1]

		nodoIz = consultaArray

		return (nodoIz,op,nodoDer)


"""
De forma recursiva, calculando todos los nextNodo() va insertando las operaciones en los nodos

:param consultaArray: array que representa consulta (obtenido con stringToArray)
:return: arbol de operaciones
"""
def crearArbol(consultaArray):
	siguienteNodo = nextNodo(consultaArray)
	tipo = siguienteNodo[1]
	return {
		"valor": lambda: Valor(siguienteNodo[2][0]),
		"NOT": lambda: Not(crearArbol(siguienteNodo[2])),
		"AND": lambda: And(crearArbol(siguienteNodo[0]),crearArbol(siguienteNodo[2])),
		"OR": lambda: Or(crearArbol(siguienteNodo[0]),crearArbol(siguienteNodo[2])),
	}[tipo]()

def hayParentesisExterno(consultaArray):
	return finParentesis(consultaArray,0) == len(consultaArray) -1

def eliminarTodosParentesisExternos(consultaArray):
	while hayParentesisExterno(consultaArray):
		consultaArray = consultaArray[1:-1]
	return consultaArray


#Recuperacion con wildcard queries

def recover_from_permuterm(term, permuterm):
    # Determina el modo de actuar según el tipo de comodín    
    single_mode = False
    if term.find("?") > - 1:
        lwildcard = term.find("?")
        rwildcard = lwildcard
        single_mode = True
    else:
        lwildcard = term.find("*")
        rwildcard = term.rfind("*")
    # Se devolverán los términos del permuterm que comiencen con el prefijo
    prefix = ""
    # Para X -> X
    if lwildcard < 0:
        return [term]
    # Usan solo un comodín
    elif lwildcard == rwildcard:
        # Para X* -> $X*
        if lwildcard == len(term) - 1:
            if not single_mode:
                prefix = '$' + term.replace("*","")
            else:
                prefix = '$' + term.replace("?","")
        # Para *X -> X$*
        elif lwildcard == 0:
            if not single_mode:
                prefix = term.replace("*","") + '$'
            else:
                prefix = term.replace("?","") + '$'
        # Para X*Y -> Y$X*
        else:
            X = term[:lwildcard]
            Y = term[lwildcard + 1:]
            prefix = Y + '$' + X
    # Para *X* -> X*
    else:
        if not single_mode:
            prefix = term.replace("*","")
        else:
            prefix = term.replace("?","")

    terms = []
    # Empieza la búsqueda de las palabras que coinciden con el prefijo
    start_point = bisect.bisect_left(permuterm, (prefix, ""))
    # Mientras las palabras empiezen por el prefijo
    while permuterm[start_point][0].find(prefix) > - 1:
        # Si se usa el comodín ? solo puede remplazarse un carácter
        if single_mode and len(term) != len(permuterm[start_point][1]):
            start_point = start_point + 1
            continue
        # Se añade el término para devolver
        terms.append(permuterm[start_point][1])
        start_point = start_point + 1
    return terms

#Recuperacion con indices posicionales

def split_text(text):
    # Consideraremos separadores de términos los espacios, los saltos de línea y los tabuladores
    return [i for i in re.split(' |\n|\t',text) if i]

def text2news(text, index_term2news):
    text = split_text(clean_text(text))
    res = []
    try:
        news = index_term2news[text[0]].keys()
    except:
        return res
    for term in text[1:]:
        try:
            news = intersection(news, index_term2news[term].keys())
        except:
            return res

    for newsid in news:
        postings = [index_term2news[text[0]][newsid]]
        for term in text[1:]:
            postings.append(index_term2news[term][newsid])               

        for pos in postings[0]:
            encontrado = True
            auxpos = pos
            r = range(1, len(postings))
            for i in r:
                auxpos = auxpos + 1
                if auxpos not in postings[i]:
                    encontrado = False
                    break
            if encontrado:
                res.append(newsid)
                break
                
    return res 
                

def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3

    
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


def processQuery(query):
	queryArray =  stringToArray(query)
	arbol = crearArbol(queryArray)
	try:
		return arbol.getValor()
	except:
		return False

def show(news):
	files = [index_docid2path[index_news2docid[n][0]] for n in news]
	cont = 0
	for file in files:
		with open(str(file)) as f:
			data = json.load(f)
			noti = data[index_news2docid[news[cont]][1] - 1]
			if len(news) < 3:
				print("File:" + "./" + str(file))
				print("Fecha: " + noti['date'])
				print("Titular: " + noti['title'])
				print("Keywords: " + noti['keywords'])
				print("Cuerpo: " + noti['article'])
			elif len(news) < 6:
				print("File:" + "./" + str(file))
				print("Fecha: " + noti['date'])
				print("Titular: " + noti['title'])
				print("Keywords: " + noti['keywords'])
				print("Snippet: ")
				min = 10000000
				max = -2
				limpio = clean_text(noti['article'])
				for w in BUSCADOS:
					indices = [index for index, value in enumerate(limpio.split()) if value == w]
					if(len(indices) > 0 and indices[0] < min):
						min = indices[0]
					elif(len(indices) > 0 and indices[-1] > max):
						max = indices[-1]

				if(min > 3):
					min -= 3
				if(max < min):
					max = min + 100
				if(len(BUSCADOS) == 0):
					min = 0
					max = 100

				print(" ".join(limpio.split()[min:max+4]))

			else:
				print("./" + str(file) + "   " + noti['date'] + "  " + noti['title'] + "  Keywords: " + noti['keywords'])

		cont += 1
				

if __name__ == '__main__':
	filename = sys.argv[1]
	with open(filename, 'rb') as fh:
		index_news2docid, index_docid2path, index_term2news, index_permuterm, index_titleterm2news,index_date2news,index_keyword2news = pickle.load(fh)
	dic = index_term2news
	NOTICIA = list(index_news2docid.keys())
	if (len(sys.argv) < 3):
		while(True):
			query = input("Query: ")
			if(query == ""):
				sys.exit()
			else:
				BUSCADOS = []
				try:
                                        result = processQuery(query)                                
                                        if(result):
                                                show(result)
                                        else:
                                                print("No coincidences found")
				except:
                                        print("The query process failed")

	else:
		query = " ".join(stringToArray(sys.argv[2]))
		print(query)
		BUSCADOS = []
		try:
                        result = processQuery(query)                                
                        if(result):
                                show(result)
                        else:
                                print("No coincidences found")
		except:
                        print("The query process failed")
