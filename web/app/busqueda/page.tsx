'use client'
import CSVTable from "@/components/csvtable/csvtable"
import Dropdown2 from "@/components/dropdown2/drowpdown2"
import { useEffect, useState } from "react"



export default function Busqueda(){
  const [getCol,setCol] = useState<number>()
  const[getRuta, setRuta] = useState<string>("")
  const[isSuccess, setSuccess] = useState<boolean>(false)
  const[isError, setError] = useState<boolean>(false)
  const [getTables, setTables] = useState<string[]>([])
  const [getTablesNum,setTablesNum]=useState<number>()
  const [getConsultaNum,setConsultaNum] = useState<number>()
  const [getConsulta,setConsulta] = useState<string>("")
  const [getCondicion,setCondicion] = useState<string>("")
  const [getCSVCompleto,setCSVCompleto] = useState<string>("")


  const columnas = ['Todas','Address','Compilerversion' ,'Optimization', 'Runs', 'Evmversion', 'Licensetype','Fuente','Contractcreator','Ruta']
  const consultas = ['SELECT FROM ',
  'SELECT FROM WHERE',
  'SELECT MIN( )FROM',
  'SELECT MIN( )FROM WHERE',
  'SELECT MAX( ) FROM',
  'SELECT MAX( ) FROM WHERE',
  'SELECT COUNT( ) FROM',
  'SELECT COUNT( ) FROM WHERE',
  'Consulta propia']

  
const queries = [
  'SELECT , FROM ',
  'SELECT , FROM , WHERE ',
  'SELECT MIN( , )FROM ',
  'SELECT MIN( , )FROM , WHERE ',
  'SELECT MAX( , ) FROM ',
  'SELECT MAX( , ) FROM , WHERE ',
  'SELECT COUNT( , ) FROM ',
  'SELECT COUNT( , ) FROM , WHERE ',
  'Tu consulta']


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
    if(getConsultaNum != 8 && getConsultaNum !== undefined && getTablesNum !== undefined && getCol !== undefined){
      consulta = buildQuery(columnas[getCol],queries[getConsultaNum],getTables[getTablesNum],getCondicion)
    }
    if(getConsultaNum == 8)consulta = getConsulta
    const dataToSend = {'consulta':consulta}
    const response = await fetch('http://localhost:5000/api/consulta', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    }).then(response =>{ setSuccess(true); response.json().then(data => {setRuta(data.ruta); setCSVCompleto(data.csv)}) }).catch(error =>{console.error('Error:', error);setError(true)
  })
}

  const fetchData = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/tables')
      const responseData = await response.json()
      setTables(responseData.tables)
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  };
  useEffect(() => {
    fetchData()
  },[]); 


  
  
    return(
      <main className="flex flex-col space-y-10 items-center justify-between mb-5 text-black">
        <div className="flex items-center justify-between space-x-10">
          <Dropdown2 nombre={"Columnas"} getItem={getCol} setItem={setCol} menuItems={columnas}/>
          <Dropdown2 nombre={"Tablas"} getItem={getTablesNum} setItem={setTablesNum} menuItems={getTables}/>
          <Dropdown2 nombre={"Consultas"} getItem={getConsultaNum} setItem={setConsultaNum} menuItems={consultas}/>
          {getConsultaNum !== undefined && getConsultaNum % 2 == 1 ?<input onChange={(e)=>setCondicion(e.target.value)} className="flex placeholder:italic min-w-[200px] py-3 px-4 placeholder:text-white text-white bg-brandBlue w-full rounded-md pl-3 pr-3 shadow-sm focus:outline-none focus:border-sky-500 focus:ring-sky-500 focus:ring-1 sm:text-sm" placeholder="Introduce la condicion..." type="text"/>:<></>}
          {getConsultaNum === 8 ?<input onChange={(e)=>setConsulta(e.target.value)} className="flex placeholder:italic min-w-[200px] py-3 px-4 placeholder:text-white text-white bg-brandBlue w-full rounded-md pl-3 pr-3 shadow-sm focus:outline-none focus:border-sky-500 focus:ring-sky-500 focus:ring-1 sm:text-sm" placeholder="Introduce la consulta..." type="text"/>:<></> }
        </div>
        <div>
          {getConsultaNum !== undefined && getTablesNum !== undefined && getCol !== undefined ?
            <div className="flex flex-col items-center space-y-5">
              <button onClick={callMyScriptApi} className="bg-brandBlue hover:bg-brandBlueHover min-w-[200px] w-fit py-3 px-4 flex justify-center gap-x-2 text-white rounded-md ">Ejecutar consulta</button>
                <p>Consulta: {buildQuery(columnas[getCol],queries[getConsultaNum],getTables[getTablesNum],getCondicion)}</p>
            </div>
          :
          (getConsultaNum == 8 ?
            <div className="flex flex-col items-center space-y-5">

            <button disabled={getConsulta.length < 10} onClick={callMyScriptApi} className="bg-brandBlue hover:bg-brandBlueHover min-w-[200px] w-fit py-3 px-4 flex justify-center gap-x-2 text-white rounded-md ">Ejecutar consulta</button>
            <p>Consulta: {getConsulta}</p>
          </div>
          :<button disabled className="bg-brandBlue cursor-not-allowed min-w-[200px] py-3 px-4 flex justify-center gap-x-2 text-white rounded-md ">Ejecutar consulta</button>
          )}
        </div>
        {isSuccess ?<CSVTable csvData={getCSVCompleto} />:<></>}
        {isError ? <p className="text-red-600">Error al realizar la consulta</p>:<></>}
        {isSuccess ? <p className="text-green-600">Consulta ejecutada con éxito y resultado guardado en {getRuta}</p>:<></>}

      </main>    
      )
}