'use client'
import { ChangeEvent, FormEvent, useEffect, useRef, useState } from "react";

export default function Compilar(){
    const[isSolSet, setSol] = useState<string>("")
    const[getContractName, setContractName] = useState<string>("")
    const[isLoading, setLoaded] = useState<boolean>(false)
    const[isSuccess, setSuccess] = useState<boolean>(false)
    const[isError, setError] = useState<boolean>(false)
    const[getVersion, setVersion] = useState<string>("")
    const[getPragmas,setPragmas] = useState<Set<string>>(new Set)
    const[getPragmasVersion, setPragmasVersion] = useState<Set<string>>(new Set)
    const[getData,setData] = useState<string>("")
    const stringArray = Array.from(getPragmas)
    const stringVersionArray = Array.from(getPragmasVersion)

    const paragraphRef = useRef<HTMLParagraphElement>(null);


    function parseVersion(versionString:string) {
      if (versionString.startsWith("^")) {
          return versionString.substring(1);
      } else if (versionString.startsWith('>')) {
          const version = versionString.substring(1).split(".");
          if(version[2] == "24"){
            version[1] = String(parseInt(version[1]) + 1);
            version[2] = "0";
          } else{
            version[2] = String(parseInt(version[2]) + 1);
          }
          return version.join(".");
      } else if (versionString.startsWith(">=")) {
          return versionString.substring(2);
      }else if (versionString.startsWith("<=")) {
        return versionString.substring(2);
    } else if (versionString.startsWith("<")) {
          const version = versionString.substring(1).split(".");
          if(version[2] == "0"){
            version[1] = String(parseInt(version[1]) - 1);
            version[2] = "24";
          } else{
            version[2] = String(parseInt(version[2]) - 1);
          }

          return version.join(".");
      } else {
          return versionString;
      }
  }

    const handleTextChange = () => {
      if (paragraphRef.current) {
        setData(paragraphRef.current.textContent || "");
        const selection = window.getSelection();
        const range = selection?.getRangeAt(0);
        if (range) {
          selection?.removeAllRanges();
          selection?.addRange(range);
        }
      }
    };
  
    useEffect(() => {
      if (paragraphRef.current) {
        paragraphRef.current.textContent = "";
      }
    }, []);
    async function readText(e:ChangeEvent<HTMLInputElement>) {
        if(e.target.files !== null){
          setContractName(e.target.files[0].name)
          var fList:FileList = e.target.files
          var text = await fList.item(0)?.text();
          var pragmas = []
          var pragmasVersion = []
          var pragma = text?.indexOf('pragma solidity')
          if(pragma != undefined && text != undefined){
            var textSplit = text.split('\n')
            for (let index = 0; index < textSplit.length; index++) {
                if(textSplit[index].indexOf('pragma solidity') != -1){ 
                  pragmasVersion.push((textSplit[index].substring(textSplit[index].indexOf('pragma solidity')+'pragma solidity'.length,textSplit[index].indexOf(';'))))
                  pragmas.push(textSplit[index].substring(textSplit[index].indexOf('pragma solidity'),textSplit[index].indexOf(';')))
                }
              }
                setPragmasVersion(new Set (pragmasVersion))
                setPragmas(new Set(pragmas))
                setData(text)
            }
        }
      }



    const callMyScriptApi = async () => {
        setLoaded(true)
        setError(false)
        setSuccess(false)
        console.log(getData)
        const dataToSend = {'contratoTexto':getData,'version':getVersion,'contrato':getContractName}
        try {
            const response = await fetch('http://localhost:5000/api/compilar', {
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
    return (
    <main className="flex flex-col m-5 space-y-5 items-center justify-between text-black">
        <div  className=" flex flex-col space-y-5 items-center">          
            {isSolSet === "" ? <p>Introduce el contrato a compilar</p>: isSolSet.endsWith(".sol") ? <p>Contrato seleccionado</p>:<p>El archivo a cargar tiene que ser un .sol</p>}
            <input onChange={(e)=>{ setSol(e.target.value);readText(e)}} type="file" accept=".sol"
            className="cursor-pointer flex  w-full text-sm text-gray-500
            file:cursor-pointer
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibol
            file:bg-violet-50 
            hover:file:text-brandBlue
            hover:file:bg-violet-100
            "/>
        </div>
        <div>
              <p>Introduce la version del compilador</p>
              <input value={getVersion} onChange={(e)=>setVersion(e.target.value)} className="placeholder:italic placeholder:text-slate-400 block bg-white w-full border border-slate-300 rounded-md py-2 pl-3 pr-3 shadow-sm focus:outline-none focus:border-sky-500 focus:ring-sky-500 focus:ring-1 sm:text-sm" placeholder="Introduce la version..." type="text"/>
            </div>
        <div  className=" flex flex-col space-y-5 items-center">          

            {isSolSet.endsWith(".sol")?
            <>
                <p>Pragmas extraido del contrato: </p>
                {stringVersionArray.map((str,index) =>(<p className="cursor-pointer" key={index} onClick={()=>setVersion(parseVersion(str.trim()))}>pragma solidity {parseVersion(str.trim())}</p>))}
                <div className="border border-gray-300 rounded-md  w-full max-h-80 overflow-auto">
                  <p ref={paragraphRef} className=" whitespace-pre-wrap break-words p-2 focus:outline-none"
                    onBlur={handleTextChange} contentEditable="true">{getData}</p>
                </div>
            </>
            :
            <></>}
            
            <button onClick={callMyScriptApi} className="bg-blue-500 flex space-x-3 disabled:cursor-not-allowed hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full" disabled={!isSolSet.endsWith(".sol") || isLoading || getContractName == ""}>{isLoading ? <p>Compilando</p>:<p>Compilar</p>}
              {isLoading ? <svg width="24" height="24" viewBox="0 0 24 24">
                <path fill="white" d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z" opacity=".25"/><path fill="white" d="M12,4a8,8,0,0,1,7.89,6.7A1.53,1.53,0,0,0,21.38,12h0a1.5,1.5,0,0,0,1.48-1.75,11,11,0,0,0-21.72,0A1.5,1.5,0,0,0,2.62,12h0a1.53,1.53,0,0,0,1.49-1.3A8,8,0,0,1,12,4Z" className="origin-center animate-spin"/>
              </svg> :<></>}
            </button>
            {isError ? <p className="text-red-600">Error al compilar el contrato</p>:<></>}
            {isSuccess ? <p className="text-green-600">Contrato cargado con éxito, archivos generados en carpeta compilados</p>:<></>}
        </div>
    </main>
    
    )
}