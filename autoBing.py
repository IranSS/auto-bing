import pyautogui as autogui
import time as tm
import random as rd
import json

import os
import sys

import time as tm
import tkinter as tk

from tkinter import messagebox

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class autoBing:
    def __init__(self):

        apresentacao = "capture a posição do seu mouse na barra de pesquisa do navegador"
        self.mouse_x = ""
        self.mouse_y = ""
        self.qtd_repeticoes = 0

        self.root = tk.Tk()
        self.root.title("Auto bing")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        ico_path = resource_path("assets/AutoBingIcon.ico")
        self.root.iconbitmap(ico_path)

        #Frame
        frame = tk.Frame(self.root, padx=1, pady=1)
        frame.pack(expand=True)

        #apresentação
        self.texto_mouse_label = tk.Label(frame, text="Auto Bing", height=1, font=("Arial", 20), justify="center")
        self.texto_mouse_label.grid(row=1, column=0, columnspan=2, pady=0.5)

        self.text_capture_btn = tk.Label(frame, text=apresentacao, font=("Arial", 10), wraplength=400, justify="left")
        self.text_capture_btn.grid(row=2, column=0)
        
        #capturar onde a posição do mouse
        self.capture_mouse_btn = tk.Button(frame, text="Capturar posição do mouse", command=self.capture_mouse_position, wraplength=400, justify="center")
        self.capture_mouse_btn.grid(row=3, column=0, sticky="w")

        #definir campos
        self.text_x = tk.Label(frame, text="Posição x", font=("Arial"), wraplength=400, justify="center")
        self.text_x.grid(row=4, column=0, sticky="w")

        self.campo_x = tk.Entry(frame, font=("Arial"), width=40, justify="left")
        self.campo_x.grid(row=5, column=0, sticky="w")

        self.text_y = tk.Label(frame, text="Posição Y", font=("Arial"))
        self.text_y.grid(row=6, column=0, sticky="w")

        self.campo_y = tk.Entry(frame, font=("Arial"), width=40, justify="left")
        self.campo_y.grid(row=7, column=0, sticky="w")

        #numero de repetições
        self.qtd_repeticoes = tk.Label(frame, text="número de repetições", font=("Arial"))
        self.qtd_repeticoes.grid(row=9, column=0, sticky="w")

        self.campo_qtd_repeticoes = tk.Entry(frame, font=("Arial"), width=40, justify="left")
        self.campo_qtd_repeticoes.grid(row=10, column=0, sticky="w")

        #Salvar conteudos
        self.definir = tk.Button(frame, text="Definir quantidade", command=self.salvarConteudos, justify="center")
        self.definir.grid(row=11, column=0, sticky="w")

        
        #Botão de iniciar o assistente
        self.start_btn = tk.Button(frame, text="Começar", command=self.click_assistent_start, wraplength=400, justify="center")
        self.start_btn.grid(row=12, column=1, sticky="e")

        try:
            with open("dados.json", "r") as f:
                data = json.load(f)
                self.mouse_x = data.get("x", "")
                self.mouse_y = data.get("y", "")
                self.campo_x.insert(0, self.mouse_x)
                self.campo_y.insert(0, self.mouse_y)

                self.qtd_repeticoes = data.get("repeticoes", "")
                self.campo_qtd_repeticoes.insert(0, self.qtd_repeticoes)
        except FileNotFoundError:
            pass

        self.root.mainloop()

    def click_assistent_start(self):
        # Pag da uma pausa na aplicação durante um determinado tempo
        autogui.PAUSE = 0.5
        
        autogui.press("win")
        autogui.write("edge")
        autogui.press("enter")

        # laço de repetição do python, pode ser comparado com um forEach 35
        for cont in range(int(self.qtd_repeticoes)):
            # gera um número aleatorio
            numero_aleatorio = rd.randint(1, 500)
            tm.sleep(5.0)
            autogui.write(str(numero_aleatorio + 1))
            tm.sleep(0.5)
            autogui.press("enter")
            autogui.click(int(self.campo_x.get()), int(self.campo_y.get()))
            cont += 1

        tm.sleep(2.0)
        autogui.hotkey("alt", "f4")

    def capture_mouse_position(self):
        # contagem em segundos para o script rodar
        tm.sleep(5)
        position_mouse = autogui.position()
        print(position_mouse)
        messagebox.showinfo("Posição do mouse", f"Posição do mouse: {position_mouse.x} x {position_mouse.y}")

    def definir_xy(self):
        self.mouse_x = self.campo_x.get()
        self.mouse_y = self.campo_y.get()
        self.qtd_repeticoes = self.campo_qtd_repeticoes.get()
        print(self.mouse_x, "x", self.mouse_y)
        self.salvar_posicoes()

    def salvarConteudos(self):
        with open("dados.json", "w") as f:
            json.dump({"x": self.campo_x.get(), "y": self.campo_y.get(), "repeticoes": self.campo_qtd_repeticoes.get()}, f)
    
autoBing()