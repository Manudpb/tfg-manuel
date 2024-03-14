import { Dispatch, SetStateAction, useState } from 'react'
import styles from './styles.module.css'
import { useSharedFuente } from '@/context/context'

function rutaToFuente(ruta:string){
    if(ruta == 'eth')return 'Ethereum'
    else return 'Otra'
}

export default function Dropdown() {
    const menuItems = ["Ethereum","Otra"]
    const menuItemsRuta = ["eth", "otras"]
    const {getFuente, setFuente} = useSharedFuente();
    const [isFirst, setFirst] = useState<boolean>(true)
    return (
        <>
            <div className= {styles.dropdown}>
                <button
                    className="hover:text-blue-400"
                >{isFirst ? "Fuentes":rutaToFuente(getFuente)}</button>
                <div className={styles.dropdowncontent}>
                    {
                        menuItems.map((item,i) =>
                            <p
                                key={i}
                                className="hover:bg-zinc-300 hover:text-zinc-500 px-4 py-1"
                                onClick={()=>{setFuente(menuItemsRuta[i]);setFirst(false);}}
                            >{item}</p>
                        )
                    }
                </div>
            </div>

        </>
    )
}