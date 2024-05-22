import subprocess


print('Introduce ruta del contrato a compilar')
ruta = input()
contrato = ruta[ruta.find('0x'):]
print(contrato)
print('Introduce version del compilador')
version = input()
subprocess.run(["solc-select","use",version,"--always-install"])
subprocess.run(["solc", "-o", "compilados/"+contrato, "--bin",  "--asm","--opcodes", "--overwrite", ruta])
