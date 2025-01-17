import pyautogui as autogui
import time as tm

# tempo para o script rodar
tm.sleep(5)
# fala exatamente a posição do mouse, necessario importar as bibliotecas acima.
# coloque o mouse na na barra de pesquisar do Edge para ele capturar a posição
print(autogui.position())