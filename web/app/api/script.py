import json
import os
import tempfile
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas
import mysql.connector
import requests
import subprocess
from google.cloud import bigquery

app = Flask(__name__)
CORS(app)


dir = 'contracts'
ruta_root = '../../../'
apikey = 'U1HXXVYK99KDZU8YDTA5KCKV3TFUVDTUWH'
namedb = 'tfgdatabase'
hostdb = '127.0.0.1'
passdb = 'root'
portdb = '3306'
userdb = 'root'

@app.route('/api/carga-eth', methods=['POST'])
def carga_address_eth():
    conn = mysql.connector.connect(user=userdb,
                            password=passdb,
                            host=hostdb,
                            db = namedb
                            )

    os.makedirs(ruta_root+dir,exist_ok=True)
    dataClient = request.json
    colnames = ['tx','address','name']
    csv = dataClient.get('csv')
    csv = csv.replace(",",";")
    csv = csv.replace("\r",",")
    csv = csv.replace('"',"")
    x = csv.split("\n")
    
    matriz = [n.split(';') for n in x]

    dataClientDF = pandas.DataFrame(data=matriz,columns=colnames)
    if(dataClient.get('checked') == True):data = pandas.DataFrame(dataClientDF[1:],columns=colnames) #sin preprocesado
    else: data = dataClientDF
    data = data.reset_index(drop=True)

    print(data)

    addresses = data.address.tolist()
    respuestas1 = []    #para guardar la respuesta de la primera llamada de la api
    contractCreators = []   #para guardar la respuesta de la segunda llamada de la api
    rutas = []
    for address in addresses:
        url = 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address=' + address + '&apikey=' + apikey
        resp = requests.get(url=url).json()
        url = 'https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses=' + address + '&apikey=' + apikey
        resp2 = requests.get(url=url).json()
        print('Contract ' + address + ' ' + resp['message'])
        respuesta1 = {'compilerversion':resp['result'][0]['CompilerVersion'],'optimization':resp['result'][0]['OptimizationUsed'],'runs':resp['result'][0]['Runs'],'evmversion':resp['result'][0]['EVMVersion'], 'licensetype':resp['result'][0]['LicenseType'],'fuente':'etherscan'}
        respuestas1.append(respuesta1)
        contractCreators.append(resp2['result'][0]['contractCreator'])
        try:
            #si SourceCode empieza con {{ entonces estamos en el caso de un contrato que está compuesto 
            #por varios contratos, en este caso se crea un nuevo directorio con la address como nombre y 
            #tantos archivos como contratos tenga
            if(resp['result'][0]['SourceCode'].startswith("{{")): 
                path = ruta_root + dir + '\\' + address
                path = path.replace("/","\\")
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
                f = open(ruta_root+dir + '/' + address + '.sol', "w")
                rutas.append(ruta_root+dir + '/' + address + '.sol')
                f.write(resp['result'][0]['SourceCode']) #.encode('utf-8')
                f.close()


        except:
            #si falla se escribe la address en un csv
            g = open(ruta_root+dir + '/errors.csv', "a")
            g.write(address + '\n')
            g.close()

    #Union de todos los datos en un dataframe df
    dataframe1 = pandas.DataFrame(respuestas1,columns=['compilerversion' ,'optimization', 'runs', 'evmversion', 'licensetype','fuente'])
    dataframe2 = pandas.DataFrame(contractCreators,columns=['contractcreator'])
    dataframe3 = pandas.DataFrame(rutas,columns=['ruta'])

    df = pandas.concat(objs=[data,dataframe1,dataframe2,dataframe3],axis=1)
    #crea la tabla contracts si no existe
    cursor = conn.cursor()
    createquery = ('CREATE TABLE IF NOT EXISTS contracts (tx VARCHAR(250), PRIMARY KEY(address),name VARCHAR(250),compilerversion VARCHAR(250),optimization VARCHAR(250),runs VARCHAR(250),evmversion VARCHAR(250),licensetype VARCHAR(250),fuente VARCHAR(250),contractcreator VARCHAR(250),ruta VARCHAR(250))')
    cursor.execute(createquery)

    #Insercion en la base de datos, se ignoran entradas duplicadas
    insertquery = ("INSERT IGNORE INTO contracts (tx,address,name,compilerversion,optimization,runs,evmversion,licensetype,fuente,contractcreator,ruta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

    for i,row in df.iterrows():
        cursor.execute(insertquery, tuple(row))
    conn.commit()
    conn.close()

    #crea directorio csv_out
    #os.system(f'mkdir {ruta_root}csv_out')
    os.makedirs(ruta_root+"csv_out",exist_ok=True)

    #Generacion del csv en el directorio /csv_out
    df.to_csv(ruta_root +'csv_out/etherscan_'+ time.strftime('%d-%m-%Y') +'.csv')
    print('Generado etherscan_' + time.strftime('%d-%m-%Y') +'.csv')
    print()


    return jsonify({'message': 'Data received successfully'})

@app.route('/api/carga-otras',methods=['POST'])
def carga_address_otras():
    conn = mysql.connector.connect(user=userdb,
                            password=passdb,
                            host=hostdb,
                            db = namedb
                            )
    os.makedirs(ruta_root+dir,exist_ok=True)

    dataClient = request.json
    fuente = dataClient.get('fuente')
    formatoTotal = dataClient.get('formato')
    obligatorios = ['compilerversion' ,'optimization', 'runs', 'evmversion', 'licensetype','fuente','contractcreator','ruta']
    formatoTotal.extend(obligatorios)

    tabla = 'contracts_' + fuente

    colnames = ['tx','address','name']
    csv = dataClient.get('csv')
    csv = csv.replace(",",";")
    csv = csv.replace("\r",",")
    csv = csv.replace('"',"")
    x = csv.split("\n")
    
    matriz = [n.split(';') for n in x]

    dataClientDF = pandas.DataFrame(data=matriz,columns=colnames)
    if(dataClient.get('checked') == True):data = pandas.DataFrame(dataClientDF[1:-1],columns=colnames) #sin preprocesado
    else: data = dataClientDF

    data = data.reset_index(drop=True)

    addresses = data.address.tolist()
    respuestas1 = []    #para guardar la respuesta de la primera llamada de la api
    contractCreators = []   #para guardar la respuesta de la segunda llamada de la api
    rutas = []
    for address in addresses:
        url = 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address=' + address + '&apikey=' + apikey
        resp = requests.get(url=url).json()
        url = 'https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses=' + address + '&apikey=' + apikey
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
                path = ruta_root + dir + '\\' + address
                path = path.replace("/","\\")
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
                f = open(ruta_root+dir + '/' + address + '.sol', "w")
                rutas.append(ruta_root+dir + '/' + address + '.sol')
                f.write(resp['result'][0]['SourceCode']) #.encode('utf-8')
                f.close()


        except:
            #si falla se escribe la address en un csv
            g = open(ruta_root+dir + '/errors.csv', "a")
            g.write(address + '\n')
            g.close()

    #Union de todos los datos en un dataframe df
    dataframe1 = pandas.DataFrame(respuestas1,columns=['compilerversion' ,'optimization', 'runs', 'evmversion', 'licensetype','fuente'])
    dataframe2 = pandas.DataFrame(contractCreators,columns=['contractcreator'])
    dataframe3 = pandas.DataFrame(rutas,columns=['ruta'])

    df = pandas.concat(objs=[data,dataframe1,dataframe2,dataframe3],axis=1)
    #crea la tabla contracts si no existe
    cursor = conn.cursor()
    createquery = (f'CREATE TABLE IF NOT EXISTS {tabla} (' + ' VARCHAR(250), '.join(formatoTotal) + ' VARCHAR(250), PRIMARY KEY (address))')
    cursor.execute(createquery)

    #Insercion en la base de datos, se ignoran entradas duplicadas
    insertquery = (f'INSERT IGNORE INTO {tabla} (' + ', '.join(formatoTotal) + ') VALUES (' + ', '.join(['%s' for i in range(len(formatoTotal))]) + ')')

    for i,row in df.iterrows():
        cursor.execute(insertquery, tuple(row))
    conn.commit()
    conn.close()

    #crea directorio csv_out
    #os.system(f'mkdir {ruta_root}csv_out')
    os.makedirs(ruta_root+"csv_out",exist_ok=True)

    #Generacion del csv en el directorio /csv_out
    df.to_csv(ruta_root + 'csv_out/'+fuente +'_'+ time.strftime('%d-%m-%Y') +'.csv')
    print('Generado '+ fuente+ '_' + time.strftime('%d-%m-%Y') +'.csv')
    print()


    return jsonify({'message': 'Data received successfully'})

@app.route('/api/consultas-anteriores',methods=['GET'])
def consultas_anteriores():
    conn = mysql.connector.connect(user=userdb,
                    password=passdb,
                    host=hostdb,
                    db = namedb
                    )
    cursor = conn.cursor()
    createquery = ('CREATE TABLE IF NOT EXISTS consultas (nombre_consulta VARCHAR(250) PRIMARY KEY,consulta VARCHAR(250),fecha VARCHAR(250))')
    cursor.execute(createquery)
    query = ("SELECT nombre_consulta,consulta FROM consultas")
    cursor.execute(query)
    listConsultas = cursor.fetchall()
    print(listConsultas)
    cursor.close()
    conn.close()

    consultas_anteriores = [consulta[0] for consulta in listConsultas]
    consultas = [consulta[1] for consulta in listConsultas]


    return jsonify({'consultas_lista': consultas_anteriores,'consultas':consultas})

        

@app.route('/api/tables', methods=['GET'])
def get_tables():
        
    conn = mysql.connector.connect(user=userdb,
                            password=passdb,
                            host=hostdb,
                            db = namedb
                            )        
    cursor = conn.cursor()

    cursor.execute("SHOW TABLES")

    listTables = cursor.fetchall()

    cursor.close()
    conn.close()

    table_names = [table[0] for table in listTables]

    return jsonify({'tables': table_names})

@app.route('/api/consulta-bq', methods=['POST'])
def consultabq():
    conn = mysql.connector.connect(user=userdb,
                        password=passdb,
                        host=hostdb,
                        db = namedb
                        )
    data = request.json
    query = data.get('consulta')
    nombre = data.get('nombre')
    token = data.get('token')
    print(query)
    print(nombre)
    client = bigquery.Client.from_service_account_json(token)
    query_job = client.query(query)
    rows = query_job.result()
    print("address min max count")
    for row in rows:
        print(row[0],row[1],row[2],row[3])
    return jsonify({'ruta': ruta_root+'consultas_out_bq/' + query + '.csv','csv':''})


@app.route('/api/consulta', methods=['POST'])
def consulta():
    conn = mysql.connector.connect(user=userdb,
                        password=passdb,
                        host=hostdb,
                        db = namedb
                        )
    
    data = request.json
    query = data.get('consulta')
    query = query.replace('todas','*')

    nombre = data.get('nombre')
    cursor = conn.cursor()
    createquery = ('CREATE TABLE IF NOT EXISTS consultas (consulta VARCHAR(250),nombre_consulta VARCHAR(250) PRIMARY KEY,fecha VARCHAR(250))')
    cursor.execute(createquery)
    insertquery = ("INSERT IGNORE INTO consultas (nombre_consulta,consulta,fecha) VALUES (%s,%s, %s)")
    val = (nombre,query,time.strftime('%d-%m-%Y'))
    cursor.execute(insertquery,val)
    columnas = ['*','address','compilerversion' ,'optimization', 'runs', 'evmversion', 'licensetype','fuente','contractcreator','ruta']

    formatoArr = [valor for valor in columnas if valor in query.lower()]
    formato = ','.join(formatoArr)

    if('*' in query):
        formato = ','.join(columnas[1:])
    elif('address' not in formato):
        query = query[:len("select")] + ' address,' + query[len('address'):]
        formato = 'address,'+formato    
    print(formato)
    print(query)
    cursor.execute(query)
    res = cursor.fetchall()

    os.makedirs(ruta_root+"consultas_out",exist_ok=True)

    f = open(ruta_root+'consultas_out/' + nombre +"_"+time.strftime('%d-%m-%Y') + '.csv' , "w")
    csvCompleto = formato +'\n'
    f.write(formato + '\n')
    for x in res:
        csvCompleto += ','.join(map(str, x))
        csvCompleto += '\n'
        f.write(','.join(map(str, x)))
        f.write('\n')
    f.close()
    conn.commit()
    conn.close()

    return jsonify({'ruta': 'consultas_out/' +nombre+'_'+time.strftime('%d-%m-%Y') + '.csv','csv':csvCompleto})

@app.route('/api/compilar', methods=['POST'])
def compilar_contrato():
    
    data = request.json
    nombre = data.get('contrato')
    version = data.get('version')
    texto = data.get('contratoTexto')
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
        temp_file.write(texto)
        temp_file_path = temp_file.name
        
    subprocess.run(["solc-select","use",version,"--always-install"])
    subprocess.run(["solc", "-o", ruta_root+"compilados/"+nombre, "--bin",  "--asm","--overwrite", temp_file_path])
    
    return jsonify({})

if __name__ == '__main__':
    app.run(debug=True)