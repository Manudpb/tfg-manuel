import json
import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas
import mysql.connector
import requests

app = Flask(__name__)
CORS(app)


#db_host = os.getenv("hostdb")
#db_port = os.getenv("portdb")
#db_name = os.getenv("namedb")
#db_user = os.getenv("userdb")
#db_password = os.getenv("passdb")

#apikey = os.getenv("apikey")

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
    if(dataClient.get('checked') == False):data = pandas.DataFrame(dataClientDF[2:],columns=colnames) #sin preprocesado
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
    createquery = ('CREATE TABLE IF NOT EXISTS contracts (tx VARCHAR(250),address VARCHAR(250),name VARCHAR(250),compilerversion VARCHAR(250),optimization VARCHAR(250),runs VARCHAR(250),evmversion VARCHAR(250),licensetype VARCHAR(250),fuente VARCHAR(250),contractcreator VARCHAR(250),ruta VARCHAR(250))')
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
    if(dataClient.get('checked') == False):data = pandas.DataFrame(dataClientDF[2:],columns=colnames) #sin preprocesado
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

    print(query)
    cursor = conn.cursor()


    cursor.execute(query)
    os.makedirs(ruta_root+"consultas_out",exist_ok=True)
    query = query.replace('>','mayor')
    query = query.replace('<','menor')
    f = open(ruta_root+'consultas_out/' + query.replace('*','todas') + '.csv' , "w")
    for x in cursor:
        f.write(','.join(map(str, x)))
        f.write('\n')
    f.close()
    
    return jsonify({'ruta': ruta_root+'consultas_out/' + query.replace('*','todas') + '.csv'})

if __name__ == '__main__':
    app.run(debug=True)