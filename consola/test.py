
def quitar_imports(t):
    texto_sin_imports = ""
    bloque_import = False
    for linea in t.split('\n'):
        if("SPDX-License-Identifier" in linea):
            print()
        elif(bloque_import):
            if(linea.endswith(';')):
                bloque_import = False
        elif(linea.startswith('import') and not linea.endswith(';')):
            bloque_import = True
        elif(linea.startswith('import') and linea.endswith(';')):
            print()
        else:
            texto_sin_imports += linea + '\n'
    return texto_sin_imports


g = open('../contracts/0x0b2d2B374f4BEc8176A59ecD9B6bf8c7922931dD/0x0b2d2B374f4BEc8176A59ecD9B6bf8c7922931dD.sol',"r")

lines = g.readlines()


f = open('../contracts/0x0b2d2B374f4BEc8176A59ecD9B6bf8c7922931dD/0x0b2d2B374f4BEc8176A59ecD9B6bf8c7922931dD' , "w")
f.write(quitar_imports(''.join(lines)))
f.close()