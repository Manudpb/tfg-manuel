'use client'
import CSVTable from "@/components/csvtable/csvtable"
import Dropdown2 from "@/components/dropdown2/drowpdown2"
import { FormEvent, useEffect, useRef, useState } from "react"



export default function Busqueda(){
  const [isJSONSet, setJSON] = useState<string>("")
  const [getCol,setCol] = useState<number>()
  const [getRuta, setRuta] = useState<string>("")
  const [isSuccess, setSuccess] = useState<boolean>(false)
  const [isError, setError] = useState<boolean>(false)
  const [getTables, setTables] = useState<string[]>([])
  const [getTablesNum,setTablesNum]=useState<number>()
  const [getConsultaNum,setConsultaNum] = useState<number>()
  const [getConsulta,setConsulta] = useState<string>("")
  const [getCondicion,setCondicion] = useState<string>("")
  const [getCSVCompleto,setCSVCompleto] = useState<string>("")
  const [getNombreConsulta,setNombreConsulta] = useState<string>("")
  const [getConsultaAntNum,setConsultaAntNum] = useState<number>()
  const [getConsultaAnt,setConsultaAnt] = useState<string[]>([])
  const [getConsultaNombreAnt,setConsultaNombreAnt] = useState<string[]>([])




  const columnas = ['Todas','Address','Compilerversion' ,'Optimization', 'Runs', 'Evmversion', 'Licensetype','Fuente','Contractcreator','Ruta']
  const consultas = ['SELECT FROM ',
  'SELECT FROM WHERE',
  'SELECT MIN( )FROM',
  'SELECT MIN( )FROM WHERE',
  'SELECT MAX( ) FROM',
  'SELECT MAX( ) FROM WHERE',
  'SELECT COUNT( ) FROM',
  'SELECT COUNT( ) FROM WHERE',
  'Consulta propia',
  'Bigquery',
  'Consultas anteriores']

  
const queries = [
  'SELECT , FROM ',
  'SELECT , FROM , WHERE ',
  'SELECT MIN( , )FROM ',
  'SELECT MIN( , )FROM , WHERE ',
  'SELECT MAX( , ) FROM ',
  'SELECT MAX( , ) FROM , WHERE ',
  'SELECT COUNT( , ) FROM ',
  'SELECT COUNT( , ) FROM , WHERE ',
  'Tu consulta',
  'Bigquery',
  'Consultas anteriores']


  function buildQuery(selectedColumn: string, selectedConsulta: string, selectedTable: string,condicion:string) {
    let querySplit = selectedConsulta.split(",")
    let query = ''
    if(querySplit.length === 2)query = querySplit[0]+selectedColumn+querySplit[1]+selectedTable
    else query =  querySplit[0]+selectedColumn.toLowerCase()+querySplit[1]+selectedTable.toLocaleLowerCase()+querySplit[2]+condicion

    return query
  }
    const callMyScriptApi = async () => {
    let consulta = ""
    setError(false)
    setSuccess(false)
    if(getConsultaNum != 8 && getConsultaNum != 9 &&  getConsultaNum !== undefined && getTablesNum !== undefined && getCol !== undefined){
      consulta = buildQuery(columnas[getCol],queries[getConsultaNum],getTables[getTablesNum],getCondicion)
    }
    if(getConsultaNum == 8 )consulta = getConsulta
    if(getConsultaNum == 9){
      consulta = getConsulta
      const dataToSend = {'consulta':consulta,'nombre':getNombreConsulta,'token':isJSONSet}
      const response = await fetch('http://localhost:5000/api/consulta-bq', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    }).then(response =>{ setSuccess(true); response.json().then(data => {setRuta(data.ruta); setCSVCompleto(data.csv)}) }).catch(error =>{console.error('Error:', error);setError(true)
  })
    }else if(getConsultaNum == 10 && getConsultaAntNum !== undefined) {
      const dataToSend = {'consulta':getConsultaAnt[getConsultaAntNum],'nombre':getConsultaNombreAnt[getConsultaAntNum]}
      const response = await fetch('http://localhost:5000/api/consulta', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify(dataToSend)
      }).then(response =>{ setSuccess(true); response.json().then(data => {setRuta(data.ruta); setCSVCompleto(data.csv)}) }).catch(error =>{console.error('Error:', error);setError(true)
    })
    }else{
    const dataToSend = {'consulta':consulta,'nombre':getNombreConsulta}
    const response = await fetch('http://localhost:5000/api/consulta', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    }).then(response =>{ setSuccess(true); response.json().then(data => {setRuta(data.ruta); setCSVCompleto(data.csv)}) }).catch(error =>{console.error('Error:', error);setError(true)
  })
}
}

const paragraphRef = useRef<HTMLParagraphElement>(null);
useEffect(() => {
  if (paragraphRef.current) {
    paragraphRef.current.textContent = "";
  }
}, []);
const handleTextChange = () => {
  console.log(paragraphRef.current?.textContent)
  if (paragraphRef.current) {
    setConsulta(paragraphRef.current.textContent || "");
    const selection = window.getSelection();
    const range = selection?.getRangeAt(0);
    if (range) {
      selection?.removeAllRanges();
      selection?.addRange(range);
    }
  }
};

  const fetchDataTables = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/tables')
      const responseData = await response.json()
      if(responseData.tables.indexOf('consultas') != -1)
      responseData.tables.splice(responseData.tables.indexOf('consultas'),1)
      setTables(responseData.tables)
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  };

  const fetchDataConsultas = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/consultas-anteriores')
      const responseData = await response.json()
      setConsultaNombreAnt(responseData.consultas_lista)
      setConsultaAnt(responseData.consultas)
    } 
    catch (error) {
      console.error('Error fetching data:', error)
    }
  }

  useEffect(() => {
    fetchDataTables()
  },[]); 

  useEffect(()=>{
    if(getConsultaNum == 10){
      fetchDataConsultas()
    }
  },[getConsultaNum])
  
    return(
      <main className="flex flex-col space-y-10 items-center justify-between mb-5 text-black">
        <div className="flex items-center justify-between space-x-10">
          {getConsultaNum === undefined || getConsultaNum < 8 ?
          <>
            <Dropdown2 nombre={"Columnas"} getItem={getCol} setItem={setCol} menuItems={columnas}/>
            <Dropdown2 nombre={"Tablas"} getItem={getTablesNum} setItem={setTablesNum} menuItems={getTables}/>
          </>
            :
            ( getConsultaNum === 10 ? <Dropdown2 nombre={"Consultas "} getItem={getConsultaAntNum} setItem={setConsultaAntNum} menuItems={getConsultaNombreAnt}/>:<></>)
          }
          <Dropdown2 nombre={"Consultas"} getItem={getConsultaNum} setItem={setConsultaNum} menuItems={consultas}/>
          {getConsultaNum === 9 ? 
          <div  className=" flex flex-col space-y-5 items-center">          
            {isJSONSet === "" ? <p>Introduce el token de bigquery a cargar</p>: isJSONSet.endsWith(".json") ? <p>Token de bigquery seleccionado</p>:<p>El token tiene que ser un JSON</p>}
            <input onChange={(e)=>{setJSON(e.target.value)}} type="file" accept=".json"
            className="cursor-pointer flex  w-full text-sm text-gray-500
              file:cursor-pointer
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibol
              file:bg-brandBlue 
              file:text-white
              hover:file:bg-brandBlueHover
            "/>
          </div>:<></>}
          {getConsultaNum !== undefined && getConsultaNum % 2 == 1 && getConsultaNum !== 9 ?<input onChange={(e)=>setCondicion(e.target.value)} className="flex placeholder:italic min-w-[200px] py-3 px-4 placeholder:text-white text-white bg-brandBlue w-full rounded-md pl-3 pr-3 shadow-sm focus:outline-none focus:border-sky-500 focus:ring-sky-500 focus:ring-1 sm:text-sm" placeholder="Introduce la condicion..." type="text"/>:<></>}
        </div>
        <div className="flex flex-col space-y-10 items-center justify-between">
          <input onChange={(e)=>setNombreConsulta(e.target.value)} className="flex placeholder:italic min-w-[300px] py-3 px-4 placeholder:text-white text-white bg-brandBlue rounded-md pl-3 pr-3 shadow-sm focus:outline-none focus:border-sky-500 focus:ring-sky-500 focus:ring-1 sm:text-sm" placeholder="Introduce un nombre para la consulta..." type="text"/>
          {getConsultaNum !== undefined && getConsultaNum < 8 && getTablesNum !== undefined && getCol !== undefined && getNombreConsulta !== "" ?
            <div className="flex flex-col items-center space-y-5">
              <button onClick={callMyScriptApi} className="bg-brandBlue hover:bg-brandBlueHover min-w-[200px] w-fit py-3 px-4 flex justify-center gap-x-2 text-white rounded-md ">Ejecutar consulta</button>
              <p>Consulta: {buildQuery(columnas[getCol],queries[getConsultaNum],getTables[getTablesNum],getCondicion)}</p>
            </div>
            :
            (getConsultaNum == 8 ?
              <div className="flex flex-col items-center space-y-5">
                <button disabled={getConsulta.length < 10 || getNombreConsulta === ""} onClick={callMyScriptApi} className="bg-brandBlue disabled:cursor-not-allowed hover:bg-brandBlueHover min-w-[200px] w-fit py-3 px-4 flex justify-center gap-x-2 text-white rounded-md ">Ejecutar consulta</button>
                <p>Consulta: </p>
                <div className="border border-gray-300 rounded-md  w-full max-h-60 overflow-auto">
                  <p ref={paragraphRef} className=" whitespace-pre-wrap break-words p-2 focus:outline-none" onBlur={handleTextChange} contentEditable="true">{getConsulta}</p>
                </div>
              </div>
              :
              (getConsultaNum == 9?
                <div className="flex flex-col items-center space-y-5">
                  <p>Consulta: </p>
                  <div className="border border-gray-300 rounded-md  w-full max-h-60 overflow-auto">
                    <p ref={paragraphRef} className=" whitespace-pre-wrap break-words p-2 focus:outline-none"
                          onBlur={handleTextChange} contentEditable="true">{getConsulta}</p>
                  </div>
                  <button disabled={getConsulta.length < 10 || getNombreConsulta === "" || !isJSONSet.endsWith('.json')} onClick={callMyScriptApi} className="bg-brandBlue disabled:cursor-not-allowed hover:bg-brandBlueHover min-w-[200px] w-fit py-3 px-4 flex justify-center gap-x-2 text-white rounded-md ">Ejecutar consulta</button>
                </div>
                :
                  (getConsultaNum == 10? 
                    <div className="flex flex-col items-center space-y-5">
                      
                      {getConsultaAntNum !== undefined ? <><p>Consulta: </p>
                      <div className="border border-gray-300 rounded-md  w-full max-h-60 overflow-auto">
                        <p ref={paragraphRef} className=" whitespace-pre-wrap break-words p-2 focus:outline-none"
                              onBlur={handleTextChange} contentEditable="true">{getConsultaAnt[getConsultaAntNum]}</p>
                      </div>
                      </>:<></>}
                      <button disabled={getConsulta.length < 10 || getNombreConsulta === ""} onClick={callMyScriptApi} className="bg-brandBlue disabled:cursor-not-allowed hover:bg-brandBlueHover min-w-[200px] w-fit py-3 px-4 flex justify-center gap-x-2 text-white rounded-md ">Ejecutar consulta</button>
                    </div>
                  :
                  <button disabled className="bg-brandBlue cursor-not-allowed min-w-[200px] py-3 px-4 flex justify-center gap-x-2 text-white rounded-md ">Ejecutar consulta</button>
                  )
              )
            )
          }
        </div>                            
        {isSuccess ?<CSVTable csvData={getCSVCompleto} />:<></>}
        {isError ? <p className="text-red-600">Error al realizar la consulta</p>:<></>}
        {isSuccess ? <p className="text-green-600">Consulta ejecutada con éxito y resultado guardado en {getRuta}</p>:<></>}

      </main>    
      )
}