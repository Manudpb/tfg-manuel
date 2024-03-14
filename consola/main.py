import requests
import pandas
import os
import config
import mysql.connector
import time
import json
import subprocess


def menu():
        choice = None
        while choice != '0':
            print('Seleciona accion:')
            print('1.Crear base de datos')
            print('2.Cargar csv de etherscan')
            print('3.Cargar csv de otra fuente')
            print('4.Realizar consulta')
            print('5.Compilar contrato')
            print('0.Salir')
            print('Opcion: ')
            choice = input()
            while(int(choice) < 0 or int(choice) > 5):
                 print('Acciones validas entre 0 y 5...')
                 choice = input()
            opciones[choice]()
            
def compilar_contrato():
    print('Introduce ruta del contrato a compilar')
    ruta = input()
    contrato = ruta[ruta.find('0x'):]
    print(contrato)
    print('Introduce version del compilador')
    version = input()
    subprocess.run(["solc-select","use",version,"--always-install"])
    subprocess.run(["solc", "-o", "compilados/"+contrato, "--bin",  "--asm", "--overwrite", ruta])


'''Función para crear la base de datos'''
def crear_bd():
    conn = mysql.connector.connect(host=config.hostdb, user=config.userdb, password=config.passdb)
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    listdb = cursor.fetchall()
    if(config.namedb,) in listdb:
        print("La base de datos ya existe")
        print()

    else:
        cursor.execute("CREATE DATABASE {}".format(config.namedb))    
        print("La base de datos se ha creado")
        print()



'''Con esta función podemos descargar fuentes de contratos con un csv proporcionado por el usuario
y almacenar información importante en la base de datos para posteriormente realizar consultas.
Guarda toda la información en la misma tabla contracts por lo que el usuario debe proporcionar un csv 
que tenga el formato de etherscan: "Txhash","ContractAddress","ContractName"'''
def carga_addresses_etherscan():
    #Conexion a la base de datos
    conn = mysql.connector.connect(user=config.userdb,
                              password=config.passdb,
                              host=config.hostdb,
                              db = config.namedb
                              )

    #crea directorio contracts
    os.system('mkdir ' + config.dir)

    print('Introduce la fuente de las addresses: ')
    fuente = input()

    print('Introduce la ruta del csv:')
    ruta = input()

    colnames = ['tx','address','name']


    #Pregunta al usuario se ha preprocesado el csv si no se eliminan las 2 primeras filas del csv
    print('¿Esta el csv preprocesado, sin header?(s/n)')
    valid = {"si": True, "s": True,"n": False, "no": False,}
    pp = input()
    while(pp.lower() not in valid):
        print('Tienes que responder si o no...')
        pp = input()
    if(valid[pp]):data = pandas.read_csv(ruta, names=colnames) #con preprocesado
    else: data = pandas.read_csv(ruta,skiprows=2, names=colnames) #sin preprocesado


    print(data)

    addresses = data.address.tolist()
    respuestas1 = []    #para guardar la respuesta de la primera llamada de la api
    contractCreators = []   #para guardar la respuesta de la segunda llamada de la api
    rutas = []
    for address in addresses:
        url = 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address=' + address + '&apikey=' + config.apikey
        resp = requests.get(url=url).json()
        url = 'https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses=' + address + '&apikey=' + config.apikey
        resp2 = requests.get(url=url).json()
        print('Contract ' + address + ' ' + resp['message'])
        respuesta1 = {'compilerversion':resp['result'][0]['CompilerVersion'],'optimization':resp['result'][0]['OptimizationUsed'],'runs':resp['result'][0]['Runs'],'evmversion':resp['result'][0]['EVMVersion'], 'licensetype':resp['result'][0]['LicenseType'],'fuente':fuente}
        respuestas1.append(respuesta1)
        contractCreators.append(resp2['result'][0]['contractCreator'])
        try:
            #si SourceCode empieza con {{ entonces estamos en el caso de un contrato que está compuesto 
            #por varios contratos, en este caso se crea un nuevo directorio con la address como nombre y 
            #tantos archivos como contratos tenga
            if(resp['result'][0]['SourceCode'].startswith("{{")): 
                path = config.dir + '\\' + address
                rutas.append(path)
                #os.mkdir(path)
                os.system('mkdir ' + path)
                x = resp['result'][0]['SourceCode']
                x = x[1:-1]
                res_dictionary = json.loads(x)
                for contract in res_dictionary['sources']:
                    contractD = contract.split(sep='/')
                    f = open(path +'/' + contractD[-1] , "w")
                    f.write(res_dictionary['sources'][contract]['content'])
                    f.close()
            else:
                #si SourceCode no empieza con {{ simplemente se crea el archivo con la address como nombre 
                #y se escribe el codigo fuente en el archivo
                f = open(config.dir + '/' + address + '.sol', "w")
                rutas.append(config.dir + '/' + address + '.sol')
                f.write(resp['result'][0]['SourceCode']) #.encode('utf-8')
                f.close()


        except:
            #si falla se escribe la address en un csv
            g = open(config.dir + '/errors.csv', "a")
            g.write(address + '\n')
            g.close()

    #Union de todos los datos en un dataframe df
    dataframe1 = pandas.DataFrame(respuestas1,columns=['compilerversion' ,'optimization', 'runs', 'evmversion', 'licensetype','fuente'])
    dataframe2 = pandas.DataFrame(contractCreators,columns=['contractcreator'])
    dataframe3 = pandas.DataFrame(rutas,columns=['ruta'])

    df = pandas.concat(objs=[data,dataframe1,dataframe2,dataframe3],axis=1)

    #crea la tabla contracts si no existe
    cursor = conn.cursor()
    createquery = ('CREATE TABLE IF NOT EXISTS contracts (tx VARCHAR(250),address VARCHAR(250),name VARCHAR(250),compilerversion VARCHAR(250),optimization VARCHAR(250),runs VARCHAR(250),evmversion VARCHAR(250),licensetype VARCHAR(250),fuente VARCHAR(250),contractcreator VARCHAR(250),ruta VARCHAR(250),PRIMARY KEY(address))')
    cursor.execute(createquery)

    #Insercion en la base de datos, se ignoran entradas duplicadas
    insertquery = ("INSERT IGNORE INTO contracts (tx,address,name,compilerversion,optimization,runs,evmversion,licensetype,fuente,contractcreator,ruta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

    for i,row in df.iterrows():
        cursor.execute(insertquery, tuple(row))
    conn.commit()
    conn.close()

    #crea directorio csv_out
    os.system('mkdir csv_out')

    #Generacion del csv en el directorio /csv_out
    df.to_csv(os.getcwd() + '/csv_out/etherscan_'+ time.strftime('%d-%m-%Y') +'.csv')
    print('Generado etherscan_' + time.strftime('%d-%m-%Y') +'.csv')
    print()

'''Con esta función a diferencia de carga_addresses_etherscan el usuario puede proporcionar cualquier csv
que contenga una columna de address, crea una tabla dentro de la base de datos con nombre contracts_fuente
y con las columnas proporcionadas por el usuario más las obligatorias'''
def carga_addresses_otros():
    #Conexion a la base de datos
    conn = mysql.connector.connect(user=config.userdb,
                              password=config.passdb,
                              host=config.hostdb,
                              db = config.namedb
                              )

    #crea directorio contracts
    os.system('mkdir ' + config.dir)

    #pide la fuente
    print('Introduce la fuente de las addresses: ')
    fuente = input()



    #el formato del csv por ejemplo address,block_timestamp,bytecode
    print('Introduce el formato del csv: ')
    formato = input()
    formatoTotal = [valor.strip() for valor in formato.split(",")]

    #el unico requsito es que el csv tenga el campo address
    while("address" not in formatoTotal):
        print('Es obligatorio que el csv de entrada tenga el campo "address"...')
        print('Introduce el formato del csv: ')
        formato = input()
        formatoTotal = [valor.strip() for valor in formato.split(",")]

    #pide la ruta del csv
    print('Introduce la ruta del csv:')
    ruta = input()

    #pregunta al usuario si tiene el formato en el csv
    print('¿Contiene el csv el formato?(Si es que si se asume en la primera linea)')
    valid = {"si": True, "s": True,"n": False, "no": False,}
    pp = input()
    while(pp.lower() not in valid):
        print('Tienes que responder si o no...')
        pp = input()
    if(valid[pp]):data = pandas.read_csv(ruta) #con formato
    else: data = pandas.read_csv(ruta,names=formatoTotal) #sin formato


    print(data)
    #columnas obligatorias que tendran todas las tablas
    obligatorios = ['compilerversion' ,'optimization', 'runs', 'evmversion', 'licensetype','fuente','contractcreator','ruta']
    formatoTotal.extend(obligatorios)

    #el nombre de la tabla será contracts_fuente
    tabla = 'contracts_' + fuente

    #si la tabla de la fuente no existe la crea
    createquery = (f'CREATE TABLE IF NOT EXISTS {tabla} (' + ' VARCHAR(250), '.join(formatoTotal) + ' VARCHAR(250), PRIMARY KEY (address))')
    cursor = conn.cursor()
    cursor.execute(createquery)




    addresses = data.address.tolist()
    respuestas1 = []    #para guardar la respuesta de la primera llamada de la api
    contractCreators = []   #para guardar la respuesta de la segunda llamada de la api
    rutas = [] #para guardar la ruta donde esté el codigo fuente
    for address in addresses:
        url = 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address=' + address + '&apikey=' + config.apikey
        resp = requests.get(url=url).json()
        url = 'https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses=' + address + '&apikey=' + config.apikey
        resp2 = requests.get(url=url).json()
        print('Contract ' + address + ' ' + resp['message'])
        respuesta1 = {'compilerversion':resp['result'][0]['CompilerVersion'],'optimization':resp['result'][0]['OptimizationUsed'],'runs':resp['result'][0]['Runs'],'evmversion':resp['result'][0]['EVMVersion'], 'licensetype':resp['result'][0]['LicenseType'],'fuente':fuente}
        respuestas1.append(respuesta1)
        contractCreators.append(resp2['result'][0]['contractCreator'])
        try:
            #si SourceCode empieza con {{ entonces estamos en el caso de un contrato que está compuesto 
            #por varios contratos, en este caso se crea un nuevo directorio con la address como nombre y 
            #tantos archivos como contratos tenga
            if(resp['result'][0]['SourceCode'].startswith("{{")): 
                path = config.dir + '\\' + address
                rutas.append(path)
                #os.mkdir(path)
                os.system('mkdir ' + path)
                x = resp['result'][0]['SourceCode']
                x = x[1:-1]
                res_dictionary = json.loads(x)
                for contract in res_dictionary['sources']:
                    contractD = contract.split(sep='/')
                    f = open(path +'/' + contractD[-1] , "w")
                    f.write(res_dictionary['sources'][contract]['content'])
                    f.close()
            else:
                #si SourceCode no empieza con {{ simplemente se crea el archivo con la address como nombre 
                #y se escribe el codigo fuente en el archivo
                f = open(config.dir + '/' + address + '.sol', "w")
                rutas.append(config.dir + '/' + address + '.sol')
                f.write(resp['result'][0]['SourceCode']) #.encode('utf-8')
                f.close()


        except:
            #si falla se escribe la address en un csv
            g = open(config.dir + '/errors.csv', "a")
            g.write(address + '\n')
            g.close()

    #Union de todos los datos en un dataframe df
    dataframe1 = pandas.DataFrame(respuestas1,columns=['compilerversion' ,'optimization', 'runs', 'evmversion', 'licensetype','fuente'])
    dataframe2 = pandas.DataFrame(contractCreators,columns=['contractcreator'])
    dataframe3 = pandas.DataFrame(rutas,columns=['ruta'])

    df = pandas.concat(objs=[data,dataframe1,dataframe2,dataframe3],axis=1)

    #crea la tabla contracts si no existe
    cursor = conn.cursor()
    createquery = (f'CREATE TABLE IF NOT EXISTS {tabla} (' + ' VARCHAR(250), '.join(formatoTotal) + ' VARCHAR(250),' +' PRIMARY KEY (address))')
    cursor.execute(createquery)

    #Insercion en la base de datos, se ignoran entradas duplicadas
    cursor = conn.cursor()
    insertquery = (f'INSERT IGNORE INTO {tabla} (' + ', '.join(formatoTotal) + ') VALUES (' + ', '.join(['%s' for i in range(len(formatoTotal))]) + ')')

    #insertquery = ("INSERT IGNORE INTO contracts (tx,address,name,compilerversion,optimization,runs,evmversion,licensetype,fuente,contractcreator) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

    for i,row in df.iterrows():
        cursor.execute(insertquery, tuple(row))
    conn.commit()
    conn.close()

    #crea directorio csv_out
    os.system('mkdir csv_out')

    #Generacion del csv en el directorio /csv_out
    df.to_csv(os.getcwd() + '/csv_out/'+fuente +'_'+ time.strftime('%d-%m-%Y') +'.csv')
    print('Generado '+ fuente+ '_' + time.strftime('%d-%m-%Y') +'.csv')
    print()

def salir():
    print('Saliendo...')

'''Con esta función podemos elegir entre una lista de consultas, proporcionarle variables 
(columna/s,tabla o condicion) y obtener los resultados en formato csv
'''
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
    choice = input()
    while(int(choice) > 8 or int(choice) < 1):
        print()
        print('Selecciona una consulta del 1 al 8')
        choice = input()
    cond = False
    if(int(choice) % 2 == 0):
        cond = True
    vars = variables_queries[choice](columnas,cond)

    queriesSplit = queries[choice]
    query = ''
    for i in range(len(vars)):
        query = query + queriesSplit.split(sep=',')[i]+vars[i]
    print(query)
    cursor = conn.cursor()
    cursor.execute(query)

    
    os.system('mkdir consultas_out')
    f = open('consultas_out/'+quitar_caracteres_invalidos(query)+'.csv', "w")
    if(vars[0] == '*'):
        columnas.remove('*')
        f.write(','.join(columnas) + '\n')
    else:
        f.write(vars[0] + '\n')
    for x in cursor:
        f.write(','.join(map(str, x)))
        f.write('\n')
    f.close()
    
    print()

def quitar_caracteres_invalidos(s):
    if('*' in s):
        s = s.replace('*','todas')
    if('>' in s):
        s = s.replace('>','mayor')
    if('<' in s):
        s =  s.replace('<','menor')
    return s

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
    tablas = []
    for i in listables :
        tablas.append(i[0])
    
    print()
    print('Tablas válidas: '+ ', '.join(tablas))
    return listables

def operadores_validos():
    return ['<','>','=']


def columnas_tabla(c,cond):
    print()
    print('Introduce las columnas:')
    cols = input()
    colsSplit = cols.split(sep=',')
    while not all(item in c for item in colsSplit):
        print()
        print('Introduce columnas validas('+ ','.join(c) +'):')
        cols = input()
        colsSplit = cols.split(sep=',')
    tablas = tablas_validas()
    print('Introduce la tabla:')
    tabla = input()
    while (tabla,) not in tablas:
        print()
        print('Esa tabla no existe en la base de datos')
        tabla = input()
    if(cond == True):
        operadores = operadores_validos()
        
        print()
        print('Introduce la condicion (columna op numero): ')
        condicion = input()
        condicionSplit = condicion.split()
        while(condicionSplit[0] not in c or condicionSplit[1] not in operadores or not condicionSplit[2].isnumeric()):
            print()
            print('Introduce la condición, por ejemplo runs > 100:')
            condicion = input()
            condicionSplit = condicion.split()
        return [cols,tabla,condicion]
    return [cols,tabla]


def columna_tabla(c,cond):
    c.remove('*')
    print()
    print('Introduce la columna:')
    col = input()
    while col not in c:
        print()
        print('Introduce una columna valida('+ ','.join(c) +'):')
        col = input()
    tablas = tablas_validas()
    print('Introduce la tabla:')
    tabla = input()
    while (tabla,) not in tablas:
        print()
        print('Esa tabla no existe en la base de datos')
        input(tabla)
    if(cond == True):
        operadores = operadores_validos()
        print()
        print('Introduce la condicion (columna op numero): ')
        condicion = input()
        condicionSplit = condicion.split()
        while(condicionSplit[0] not in c or condicionSplit[1] not in operadores or not condicionSplit[2].isnumeric()):
            print()
            print('Introduce la condición, por ejemplo runs > 100:')
            
            condicion = input()
            condicionSplit = condicion.split()
        return [col,tabla,condicion]
    return [col,tabla]


variables_queries = {
    '1': columnas_tabla,
    '2': columnas_tabla,
    '3': columna_tabla,
    '4': columna_tabla,
    '5': columna_tabla,
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

opciones = {
    '1': crear_bd,
    '2': carga_addresses_etherscan,
    '3': carga_addresses_otros,
    '4': realizar_consulta,
    '5': compilar_contrato,
    '0':salir
}

def main():
    menu()

if __name__ == "__main__":
    main()
