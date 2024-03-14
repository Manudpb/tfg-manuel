'use client'
import React, { Dispatch, ReactNode, SetStateAction, createContext, useContext, useState } from 'react';


type ContextProp = {
    getFuente:string
    setFuente:Dispatch<SetStateAction<string>>
}

const FuenteContextDefaultValues: ContextProp = {
    getFuente: 'eth',
    setFuente: () => {},
};
const FuenteContext = createContext<ContextProp>(FuenteContextDefaultValues);
export function useSharedFuente(){
    return useContext(FuenteContext)
}
type Props = {
    children: ReactNode;
}
export function ContextProvider({ children }:Props) {
  const [getFuente, setFuente] = useState<string>('eth');
    const value = {
        getFuente,setFuente
    }
  return (
    <FuenteContext.Provider value={value}>
      {children}
    </FuenteContext.Provider>
  );
};

