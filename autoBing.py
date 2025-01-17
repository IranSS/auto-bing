import pyautogui as pag
import time as tm
import random as rd

# Pag da uma pausa na aplicação durante um determinado tempo
pag.PAUSE = 0.5

# pag.press("") - usado para indicar qual tecla deve ser usada.
pag.press("win")
# pag.write("") - usado para esccrever em algo.
pag.write("edge")
pag.press("enter")

# laço de repetição do python, pode ser comparado igual um forEach
for cont in range(35):
    # gera um número aleatorio de 1 á 100
    numero_aleatorio = rd.randint(1, 100)
    # ele faz com que o próximo comando aguarde um determinado tempo para funcionar
    tm.sleep(5.0)
    pag.write(str(numero_aleatorio + 1))
    tm.sleep(0.5)
    pag.press("enter")
    # com ajuda do script auxiliar ele pega extamente onde está a pósição do mouse -> auxiliar.py
    # Em seguida coloque a posição script auxiliar forneceu.
    pag.click(x=396, y=110)
    cont += 1