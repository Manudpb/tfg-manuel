"use client"
import Link from "next/link";
import Dropdown from "./dropdown/dropdown";
import { useState } from "react";

export default function Navbar(){
  const [getFuente,setFuente] = useState<number>()
  const menuItems = ["eth","otras"];

    return (
        <div className="text-black flex min-w-full flex-row justify-between  p-10 mb-10 border-b-2 border-gray-200">
          <Link href={"/"} className="hover:text-brandBlue">Home</Link>
          <div className="flex h-full flex-row justify-between space-x-10 ">
              {getFuente === undefined ? (
                <Link href={"/cargacsv/eth"} className="hover:text-brandBlue">
                  Cargar csv 
                </Link>)
                :(
                <Link href={"/cargacsv/" + menuItems[getFuente]} className="hover:text-brandBlue">
                  Cargar csv 
                </Link>)
              }
              
              <Link href={"/busqueda"} className="hover:text-brandBlue">Búsqueda en tiempo real </Link>
              <div className="hover:text-brandBlue h-full">
                <Dropdown getFuente={getFuente} setFuente={setFuente} />
              </div>
          <Link href={"https://etherscan.io/exportData?type=open-source-contract-codes"} rel="noreferrer" target="_blank" className="hover:text-brandBlue">Etherscan contratos verificados</Link>
        </div>
      </div>
    )
}