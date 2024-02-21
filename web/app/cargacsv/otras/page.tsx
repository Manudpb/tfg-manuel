'use client'
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
        setDataToSend(""+text)
      }
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
      console.log(getFormato)
    }else{
      setErrorFormato(true)
    }

  }

    return(
      <main className="flex flex-col items-center justify-between text-black">
        <div className=" flex flex-col space-y-5 items-center">
          {isCsvSet === "" ? <p>Introduce el CSV a cargar</p>: isCsvSet.endsWith(".csv") ? <p>CSV seleccionado</p>:<p>El archivo a cargar tiene que ser un CSV</p>}
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
            <div>
              <p>Introduce la fuente del CSV</p>
              <input onChange={(e)=>setFuente(e.target.value)} className="placeholder:italic placeholder:text-slate-400 block bg-white w-full border border-slate-300 rounded-md py-2 pl-3 pr-3 shadow-sm focus:outline-none focus:border-sky-500 focus:ring-sky-500 focus:ring-1 sm:text-sm" placeholder="Introduce la fuente..." type="text"/>
            </div>
            <div>
              <p>Introduce el formato del CSV separado por comas</p>
              <input onChange={(e)=>handlerFormato(e)} className="placeholder:italic placeholder:text-slate-400 block bg-white w-full border border-slate-300 rounded-md py-2 pl-3 pr-3 shadow-sm focus:outline-none focus:border-sky-500 focus:ring-sky-500 focus:ring-1 sm:text-sm" placeholder="Introduce el formato..." type="text"/>
              {isErrorFormato ? <p className="text-red-600">Es obligatorio el campo "address"...</p>:<></>}
            </div>
            <button onClick={callMyScriptApi} className="bg-blue-500 flex space-x-3 disabled:cursor-not-allowed hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full" disabled={!isCsvSet.endsWith(".csv") || isLoading || isErrorFormato}>{isLoading ? <p>Cargando csv</p>:<p>Cargar csv</p>}
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