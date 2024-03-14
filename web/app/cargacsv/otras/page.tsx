'use client'
import CSVTable from "@/components/csvtable/csvtable"
import Tooltip from "@/components/tooltip/tooltip"
import { ChangeEvent, useState } from "react"
export default function CargacsvOtras(){
    const[isCsvSet, setCsv] = useState<string>("")
    const[getDataToSend, setDataToSend] = useState<string>("")
    const[isChecked, setChecked] = useState<boolean>(false)
    const[isLoading, setLoaded] = useState<boolean>(false)
    const[isSuccess, setSuccess] = useState<boolean>(false)
    const[isError, setError] = useState<boolean>(false)
    const[getFuente, setFuente] = useState<string>("")
    const[getFormato, setFormato] = useState<string[]>([])
    const[isErrorFormato,setErrorFormato] = useState<boolean>(false)

    async function readText(e:ChangeEvent<HTMLInputElement>) {
      if(e.target.files !== null){
        var fList:FileList = e.target.files
        var text = await fList.item(0)?.text();
        setDataToSend(""+preprocesarCSV(text))
      }
    }
    function preprocesarCSV(csv:String|undefined){
      if(csv != undefined){
        var listaBool = csv.split("\n").map(valor => valor.split(',').length > 1)
        var csvSplit = csv.split("\n")
      
        for (let index = 0; index < listaBool.length; index++) {
          if(!listaBool[index])csvSplit.splice(index,1)
        }
        csv = csvSplit.join("\n")
      }
      return csv
    } 
    const callMyScriptApi = async () => {
      setLoaded(true)
      setError(false)
      setSuccess(false)
      const dataToSend = {'csv':getDataToSend,'checked':isChecked,'fuente':getFuente,'formato':getFormato}
      try {
          const response = await fetch('http://localhost:5000/api/carga-otras', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify(dataToSend)
          }).then(response =>{setLoaded(false); setSuccess(true)}).catch(error =>{setLoaded(false);console.error('Error:', error);setError(true)
        })
          
      } catch (error) {
          console.error('Error:', error);
      }
    }
  function handlerFormato(e: ChangeEvent<HTMLInputElement>){
    var valores = e.target.value.split(',')
    valores = valores.map(valor =>
      valor.trim()
    )
    if(valores.includes("address")){
      setErrorFormato(false)
      setFormato(valores)
    }else{
      setErrorFormato(true)
    }

  }

    return(
      
      <main className="flex flex-col space-y-5 items-center justify-between text-black mb-5">
        {isCsvSet === "" ? <p>Introduce el CSV a cargar</p>: isCsvSet.endsWith(".csv") ? <p>CSV seleccionado</p>:<p>El archivo a cargar tiene que ser un CSV</p>}
        <div className= {isCsvSet.endsWith(".csv") ?'flex space-x-10':'flex flex-col'}>
          <div className=" flex flex-col space-y-5 items-center">
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
              {isCsvSet.endsWith(".csv")?<CSVTable csvData={getDataToSend} />:<></>}

          </div>
          <div className=" flex flex-col space-y-5 items-center">
                <p>Introduce la fuente del CSV</p>
                <input onChange={(e)=>setFuente(e.target.value)} className="placeholder:italic placeholder:text-slate-400 block bg-white w-full border border-slate-300 rounded-md py-2 pl-3 pr-3 shadow-sm focus:outline-none focus:border-sky-500 focus:ring-sky-500 focus:ring-1 sm:text-sm" placeholder="Introduce la fuente..." type="text"/>
                
                <div className="flex"><p>Introduce el formato del CSV separado por comas</p>
                <Tooltip text={"El formato a introducir tiene que tener un campo 'address', los campos deben estar separados por ','"} children={
                   <svg width="12" height="12" fill="#0075ff" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 93.936 93.936"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <g> <path d="M80.179,13.758c-18.342-18.342-48.08-18.342-66.422,0c-18.342,18.341-18.342,48.08,0,66.421 c18.342,18.342,48.08,18.342,66.422,0C98.521,61.837,98.521,32.099,80.179,13.758z M44.144,83.117 c-4.057,0-7.001-3.071-7.001-7.305c0-4.291,2.987-7.404,7.102-7.404c4.123,0,7.001,3.044,7.001,7.404 C51.246,80.113,48.326,83.117,44.144,83.117z M54.73,44.921c-4.15,4.905-5.796,9.117-5.503,14.088l0.097,2.495 c0.011,0.062,0.017,0.125,0.017,0.188c0,0.58-0.47,1.051-1.05,1.051c-0.004-0.001-0.008-0.001-0.012,0h-7.867 c-0.549,0-1.005-0.423-1.047-0.97l-0.202-2.623c-0.676-6.082,1.508-12.218,6.494-18.202c4.319-5.087,6.816-8.865,6.816-13.145 c0-4.829-3.036-7.536-8.548-7.624c-3.403,0-7.242,1.171-9.534,2.913c-0.264,0.201-0.607,0.264-0.925,0.173 s-0.575-0.327-0.693-0.636l-2.42-6.354c-0.169-0.442-0.02-0.943,0.364-1.224c3.538-2.573,9.441-4.235,15.041-4.235 c12.36,0,17.894,7.975,17.894,15.877C63.652,33.765,59.785,38.919,54.73,44.921z"></path> </g> </g></svg>}>
                  </Tooltip></div>
                <input onChange={(e)=>handlerFormato(e)} className="placeholder:italic placeholder:text-slate-400 block bg-white w-full border border-slate-300 rounded-md py-2 pl-3 pr-3 shadow-sm focus:outline-none focus:border-sky-500 focus:ring-sky-500 focus:ring-1 sm:text-sm" placeholder="Introduce el formato..." type="text"/>
                {isErrorFormato ? <p className="text-red-600">Es obligatorio el campo "address"...</p>:<></>}
              <div className="flex space-x-4">
                <p>Marca para borrar la linea del formato </p>
                <input onChange={()=>setChecked(old => !old)} type="checkbox"/>
                <Tooltip text={"Si en el previsualizado la primera linea es el formato y no datos marca"} children={
                   <svg width="12" height="12" fill="#0075ff" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 93.936 93.936"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <g> <path d="M80.179,13.758c-18.342-18.342-48.08-18.342-66.422,0c-18.342,18.341-18.342,48.08,0,66.421 c18.342,18.342,48.08,18.342,66.422,0C98.521,61.837,98.521,32.099,80.179,13.758z M44.144,83.117 c-4.057,0-7.001-3.071-7.001-7.305c0-4.291,2.987-7.404,7.102-7.404c4.123,0,7.001,3.044,7.001,7.404 C51.246,80.113,48.326,83.117,44.144,83.117z M54.73,44.921c-4.15,4.905-5.796,9.117-5.503,14.088l0.097,2.495 c0.011,0.062,0.017,0.125,0.017,0.188c0,0.58-0.47,1.051-1.05,1.051c-0.004-0.001-0.008-0.001-0.012,0h-7.867 c-0.549,0-1.005-0.423-1.047-0.97l-0.202-2.623c-0.676-6.082,1.508-12.218,6.494-18.202c4.319-5.087,6.816-8.865,6.816-13.145 c0-4.829-3.036-7.536-8.548-7.624c-3.403,0-7.242,1.171-9.534,2.913c-0.264,0.201-0.607,0.264-0.925,0.173 s-0.575-0.327-0.693-0.636l-2.42-6.354c-0.169-0.442-0.02-0.943,0.364-1.224c3.538-2.573,9.441-4.235,15.041-4.235 c12.36,0,17.894,7.975,17.894,15.877C63.652,33.765,59.785,38.919,54.73,44.921z"></path> </g> </g></svg>}>
                </Tooltip>
              </div>

          </div>
          
        </div>
        <div className="flex items-center space-x-5">
          <button onClick={callMyScriptApi} className="bg-blue-500 flex space-x-3 disabled:cursor-not-allowed hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full" disabled={!isCsvSet.endsWith(".csv") || isLoading || isErrorFormato || getFuente == ""}>{isLoading ? <p>Cargando csv</p>:<p>Cargar csv</p>}
            {isLoading ? <svg width="24" height="24" viewBox="0 0 24 24">
              <path fill="white" d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z" opacity=".25"/><path fill="white" d="M12,4a8,8,0,0,1,7.89,6.7A1.53,1.53,0,0,0,21.38,12h0a1.5,1.5,0,0,0,1.48-1.75,11,11,0,0,0-21.72,0A1.5,1.5,0,0,0,2.62,12h0a1.53,1.53,0,0,0,1.49-1.3A8,8,0,0,1,12,4Z" className="origin-center animate-spin"/>
            </svg> :<></>}
          </button>
          {isError ? <p className="text-red-600">Error al cargar el CSV</p>:<></>}
          {isSuccess ? <p className="text-green-600">CSV cargado con éxito</p>:<></>}
        </div>
      </main>    
      )
}