'use client'
import { Dispatch, SetStateAction, useState } from 'react'

interface DropdownProps{
    getItem:number|undefined
    setItem:Dispatch<SetStateAction<number|undefined>>
    menuItems:string[]
    nombre:string
}
export default function Dropdown2({menuItems,getItem,setItem,nombre}:DropdownProps){
    const [isOpen, setIsOpen] = useState<boolean>(false)
    const transClass = isOpen
        ?
        "flex"
        :
        "hidden"
    return(
<>
            <div className="relative">
                <button
                    className="bg-brandBlue hover:bg-brandBlueHover min-w-[200px] py-3 px-4 flex justify-center gap-x-2 text-white rounded-md "
                    onClick={() => {
                        setIsOpen(old => !old);
                    }}
                >{getItem ===undefined ? <p>{nombre}</p>:<p className='align'>{menuItems[getItem]}</p>}</button>
                <div className={`absolute z-30 w-[250px] flex flex-col py-4 shadow-xl bg-[#f1f1f1] rounded-md ${transClass}`}>
                    {
                        menuItems.map((item,i) =>
                            <a
                                key={i}
                                className="hover:bg-zinc-300 hover:text-zinc-500 px-4 py-1"
                                onClick={() => {
                                    setIsOpen(old => !old)
                                    setItem(i)
                                }}
                            >{item}</a>
                        )
                    }
                </div>
            </div>
            {
                isOpen
                    ?
                    <div
                        className="fixed top-0 right-0 bottom-0 left-0 z-20"
                        onClick={() => {
                            setIsOpen(old => !old)
                        }}
                    ></div>
                    :
                    <></>
            }
        </>
    )
}