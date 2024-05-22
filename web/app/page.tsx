'use client'

import { useSharedFuente } from "@/context/context";
import Link from "next/link";

export default function Home() {
  const {getFuente} = useSharedFuente();

  return (
    <main className="min-h-full flex flex-col justify-between text-black pb-10 px-10">
      <div className="flex flex-col items-center justify-between space-y-10 ">
        <h1 className="text-xl font-bold">Búsqueda de contratos Ethereum en tiempo real</h1>
        <p>Esta aplicación permite cargar contratos desplegados en la red principal de Ethereum de acuerdo con criterios de búsqueda complejos y recuperar su código fuente y las opciones de compilación que fueron utilizadas</p>
      </div>
      <div className="flex flex-row justify-around text-center">
        <div className="flex flex-col max-w-xs h-full space-y-6 items-center justify-between">
          <p>Carga tu propio csv de direcciones para descargar sus fuentes y realizar diversas consultas sobre ellas</p>
          <Link className="rounded-2xl p-10 hover:bg-brandBlueHover bg-brandBlue" href={"/cargacsv/"+getFuente}>Cargar CSV</Link>
        </div>
        <div className="flex flex-col max-w-xs space-y-6 items-center justify-between">
          <p>Sistema de consultas complejas</p>
          <Link className="rounded-2xl p-10 hover:bg-brandBlueHover bg-brandBlue" href={"/busqueda"}>Búsqueda de contratos</Link>
        </div>
        <div className="flex flex-col max-w-xs space-y-6 items-center justify-between">
          <p>Sistema de compilación de contratos</p>
          <Link className="rounded-2xl p-10 hover:bg-brandBlueHover bg-brandBlue" href={"/busqueda"}>Compilación de contratos</Link>
        </div>
      </div>
    </main>
  );
}
