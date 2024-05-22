import config
import mysql.connector
import os
import time


def realizar_consulta():
    #Conexion a la base de datos
    conn = mysql.connector.connect(user=config.userdb,
                              password=config.passdb,
                              host=config.hostdb,
                              db = config.namedb
                              )
    
    columnas = ['*','address','compilerversion' ,'optimization', 'runs', 'evmversion', 'licensetype','fuente','contractcreator','ruta']
    print()

    print('Puedes elegir entre varias consultas:')
    print('1.SELECT columnas FROM tabla')
    print('2.SELECT  columnas FROM tabla WHERE condicion')
    print('3.SELECT MIN(col) FROM tabla')
    print('4.SELECT MIN(col) FROM tabla WHERE cond')
    print('5.SELECT MAX(col) FROM tabla')
    print('6.SELECT MAX(col) FROM tabla WHERE cond')
    print('7.SELECT COUNT(col) FROM tabla')
    print('8.SELECT COUNT(col) FROM tabla WHERE cond')
    print('9.Crea tu propia consulta')

    choice = input()
    while(int(choice) > 9 or int(choice) < 1):
        print()
        print('Selecciona una consulta del 1 al 9')
        choice = input()
    cond = False
    print('Introduce un nombre para la consulta')
    nombre = input()
    if(int(choice) == 9):
        print('Introduce tu query: ')
        query = input()
        formatoArr = [valor for valor in columnas if valor in query]
        formato = ','.join(formatoArr)
        if('MIN'.lower() not in query.lower() and 'MAX'.lower() not in query.lower() and 'COUNT'.lower() not in query.lower()):
            if('*' in query):
                formato = ','.join(columnas[1:])
            elif('address' not in formato):
                query = query[:len("select")] + ' address,' + query[len('address'):]
                formato = 'address,'+formato    
    else:
        if(int(choice) % 2 == 0):
            cond = True



    vars = variables_queries[choice](columnas,cond)
    queriesSplit = queries[choice]
    query = ''
    for i in range(len(vars)):
        query = query + queriesSplit.split(sep=',')[i]+vars[i]
    print("Consulta: ")
    print(query)
    cursor = conn.cursor()
    createquery = ('CREATE TABLE IF NOT EXISTS consultas (consulta VARCHAR(250),nombre_consulta VARCHAR(250) PRIMARY KEY,fecha VARCHAR(250))')
    cursor.execute(createquery)
    insertquery = ("INSERT IGNORE INTO consultas (nombre_consulta,consulta,fecha) VALUES (%s,%s, %s)")
    val = (nombre,query,time.strftime('%d-%m-%Y'))
    cursor.execute(insertquery,val)
    cursor.execute(query)

    
    os.system('mkdir consultas_out')
    f = open('consultas_out/'+nombre+'_'+time.strftime('%d-%m-%Y')+'.csv', "w")
    if(vars[0] == '*'):
        columnas.remove('*')
        f.write(','.join(columnas) + '\n')
    else:
        f.write(vars[0] + '\n')
    for x in cursor:
        f.write(','.join(map(str, x)))
        f.write('\n')
    f.close()
    print('Generado ' + nombre+'_'+time.strftime('%d-%m-%Y') +'.csv')

    print()

def quitar_caracteres(s):
    query = s
    if('*' in query):
        query = query.replace('*','todas')
    if('>' in query):
        query = query.replace('>','mayor')
    if('<' in query):
        query = query.replace('<','menor')
    
    return query

def tablas_validas():
   #Conexion a la base de datos
    conn = mysql.connector.connect(user=config.userdb,
                              password=config.passdb,
                              host=config.hostdb,
                              db = config.namedb
                              )
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    listables = cursor.fetchall()
    print(listables)
    return listables

def operadores_validos():
    return ['<','>','=']


def columnas_tabla(c,cond):
    print('Introduce las columnas:')
    cols = input()
    colsSplit = [valor.strip() for valor in cols.split(sep=',')]
    while not all(item in c for item in colsSplit):
        print('Introduce columnas validas:')
        cols = input()
        colsSplit = [valor.strip() for valor in cols.split(sep=',')]
    cols = ','.join(colsSplit)
    tablas = tablas_validas()
    print('Introduce la tabla:')
    tabla = input()
    while (tabla,) not in tablas:
        print('Esa tabla no existe en la base de datos')
        input(tabla)
    if(cond == True):
        operadores = operadores_validos()
        print('Introduce la condicion (columna op numero): ')
        condicion = input()
        condicionSplit = condicion.split()
        while(condicionSplit[0] not in c or condicionSplit[1] not in operadores or isinstance(condicionSplit[2],int)):
            print('Introduce la condición, por ejemplo runs > 100:')
            print(condicionSplit[0])
            print(condicionSplit[1])
            print(condicionSplit[2])

            condicion = input()
            condicionSplit = input()
        return [cols,tabla,condicion]
    return [cols,tabla]


def columna_tabla(c,cond):
    print('Introduce la columna:')
    col = input()
    while col not in c:
        col = input()
    tablas = tablas_validas()
    print('Introduce la tabla:')
    tabla = input()
    while (tabla,) not in tablas:
        print('Esa tabla no existe en la base de datos')
        input(tabla)
    if(cond == True):
        operadores = operadores_validos()
        print('Introduce la condicion (columna op numero): ')
        condicion = input()
        condicionSplit = condicion.split()
        while(condicionSplit[0] not in c or condicionSplit[1] not in operadores or isinstance(condicionSplit[2],int)):
            print('Introduce la condición, por ejemplo runs > 100:')
            condicion = input()
            condicionSplit = input()
        return [col,tabla,condicion]
    return [col,tabla]


variables_queries = {
    '1': columnas_tabla,
    '2': columnas_tabla,
    '3': columna_tabla,
    '4': columnas_tabla,
    '5': columnas_tabla,
    '6': columna_tabla,
    '7': columna_tabla,
    '8': columna_tabla,
}

queries = {
    '1': 'SELECT , FROM ',
    '2': 'SELECT , FROM , WHERE ',
    '3': 'SELECT MIN( , )FROM ',
    '4': 'SELECT MIN( , )FROM , WHERE ',
    '5': 'SELECT MAX( , ) FROM ',
    '6': 'SELECT MAX( , ) FROM , WHERE ',
    '7': 'SELECT COUNT( , ) FROM ',
    '8': 'SELECT COUNT( , ) FROM , WHERE ',
}

realizar_consulta()