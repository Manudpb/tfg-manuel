'use client'
import { ChangeEvent, useState } from "react"

export default function CargacsvEth(){
    const[isCsvSet, setCsv] = useState<string>("")
    const[getDataToSend, setDataToSend] = useState<string>("")
    const[isChecked, setChecked] = useState<boolean>(false)

    async function readText(e:ChangeEvent<HTMLInputElement>) {
      if(e.target.files !== null){
        var fList:FileList = e.target.files
        var text = await fList.item(0)?.text();
        setDataToSend(""+text)
      }
    }
    const callMyScriptApi = async () => {
      const dataToSend = {'csv':getDataToSend,'checked':isChecked}
      console.log(JSON.stringify(dataToSend))
      try {
          const response = await fetch('http://localhost:5000/api/carga-eth', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify(dataToSend)
          }).then(response =>{console.log(response)}).catch(error =>{  console.error('Error:', error);
        })
          
      } catch (error) {
          console.error('Error:', error);
      }
    }
    return(
      <main className="flex flex-col items-center justify-between text-black">
        <div className=" flex flex-col space-y-5 items-center">
          {isCsvSet === "" ? <p>Introduce el CSV a cargar</p>: isCsvSet.endsWith(".csv") ? <p>CSV cargado</p>:<p>El archivo a cargar tiene que ser un CSV</p>}
            <input onChange={(e)=>{readText(e); setCsv(e.target.value)}} type="file" accept=".csv" 
            className="cursor-pointer block w-full text-sm text-gray-500
              file:cursor-pointer
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibol
              file:bg-violet-50 
              hover:file:text-brandBlue
              hover:file:bg-violet-100
            "/>
            <div className="flex space-x-4">
              <p>Marca si está preprocesado el csv</p>
              <input onChange={()=>setChecked(old => !old)} type="checkbox"/>
            </div>
            <button onClick={callMyScriptApi} className="bg-blue-500 disabled:cursor-not-allowed hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full" disabled={!isCsvSet.endsWith(".csv")}>Cargar csv</button>
        </div>

      </main>    
      )
}