import requests
import pandas
import os
import config
import mysql.connector
import time
import json

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
createquery = ('CREATE TABLE IF NOT EXISTS contracts (tx VARCHAR(250),address VARCHAR(250),name VARCHAR(250),compilerversion VARCHAR(250),optimization VARCHAR(250),runs VARCHAR(250),evmversion VARCHAR(250),licensetype VARCHAR(250),fuente VARCHAR(250),contractcreator VARCHAR(250),ruta VARCHAR(250))')
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
