from flask import Flask, request
from flask_cors import CORS
import pandas

app = Flask(__name__)
CORS(app)

@app.route('/api/script-eth', methods=['POST'])
def run_script():
    # Get data from request
    dataClient = request.data.decode('utf-8')



    colnames = ['tx','address','name']
    dataClient = dataClient.replace(",",";")
    dataClient = dataClient.replace("\r",",")
    x = dataClient[1:].split("\n")
    
    matriz = [n.split(';') for n in x]

    dataClientDF = pandas.DataFrame(data=matriz,columns=colnames)
    if(dataClient.startswith("1")):data = dataClientDF[1:] #sin preprocesado
    else: data = dataClientDF
    

    data = data.to_string()
    # Return the result
    return data

if __name__ == '__main__':
    app.run(debug=True)