import { Dispatch, SetStateAction, useState } from 'react'
import styles from './styles.module.css'

interface DropdownProps{
    getFuente:number|undefined
    setFuente:Dispatch<SetStateAction<number|undefined>>
}
export default function Dropdown({getFuente,setFuente}:DropdownProps) {
    const menuItems = ["Ethereum","Otra"]
    return (
        <>
            <div className= {styles.dropdown}>
                <button
                    className="hover:text-blue-400"
                >{getFuente === undefined ? "Fuentes":menuItems[getFuente]}</button>
                <div className={styles.dropdowncontent}>
                    {
                        menuItems.map((item,i) =>
                            <p
                                key={i}
                                className="hover:bg-zinc-300 hover:text-zinc-500 px-4 py-1"
                                onClick={()=>setFuente(i)}
                            >{item}</p>
                        )
                    }
                </div>
            </div>

        </>
    )
}