import ctypes
import json
import os
import sys
import time as tm
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

import pyautogui as autogui

from .automation_engine import AutomationConfig, AutomationEngine, ClickPreset
from .config_manager import ConfigManager


class AutoBing:
    def __init__(self):
        self.root = tk.Tk()
        
        self.engine = AutomationEngine(status_callback=self.set_status)
        self.config_manager = ConfigManager()
        self.presets = []
        self.theme = "light"

        bg = "#f3f6fb"
        bg_input = "#ffffff"
        fg = "#111827"
        accent = "#2563eb"

        # configs
        self.root.title("Auto Search")
        self.root.geometry("980x720")
        self.root.resizable(False, False)
        self.root.configure(bg=bg)
        self._set_window_icon()

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Card.TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground=accent)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground=fg)
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("Accent.TButton", background=accent, foreground="white")
        style.map("Accent.TButton", background=[("active", "#3b82f6")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=16)

        self.main_tab = ttk.Frame(self.notebook, padding=12, style="Card.TFrame")
        self.presets_tab = ttk.Frame(self.notebook, padding=12, style="Card.TFrame")
        self.notebook.add(self.main_tab, text="Principal")
        self.notebook.add(self.presets_tab, text="Pontos personalizados")

        self.build_main_tab(bg, fg, bg_input)
        self.build_presets_tab(bg, fg, bg_input)

        self.theme_var = tk.StringVar(value=self.theme)
        self.theme_switch = ttk.Combobox(self.root, textvariable=self.theme_var, values=["light", "dark"], state="readonly", width=12)
        self.theme_switch.pack(anchor="e", padx=16, pady=(0, 8))
        ttk.Button(self.root, text="Aplicar tema", command=self.apply_theme).pack(anchor="e", padx=16, pady=(0, 8))

        self.status_label = ttk.Label(self.root, text="Pronto para começar.", wraplength=900)
        self.status_label.pack(anchor="w", padx=16, pady=(0, 12))

        self.load_settings()
        self.root.mainloop()

    def _set_window_icon(self):
        candidates = []
        base_dir = Path(__file__).resolve().parent.parent

        if getattr(sys, "_MEIPASS", None):
            candidates.extend([
                Path(sys._MEIPASS) / "assets" / "icon.ico",
                Path(sys._MEIPASS) / "icon.ico",
            ])

        candidates.extend([
            base_dir / "assets" / "icon.ico",
            base_dir / "icon.ico",
        ])

        icon_path = None
        for candidate in candidates:
            if candidate.exists():
                icon_path = candidate
                break

        if not icon_path:
            return

        icon_path = str(icon_path)

        try:
            self.root.iconbitmap(default=icon_path)
            self.root.wm_iconbitmap(icon_path)
        except Exception:
            pass

        if os.name == "nt":
            try:
                user32 = ctypes.windll.user32
                hwnd = self.root.winfo_id()
                LR_LOADFROMFILE = 0x10
                LR_DEFAULTSIZE = 0x40
                IMAGE_ICON = 1
                WM_SETICON = 0x80
                ICON_SMALL = 0
                ICON_BIG = 1

                small_icon = user32.LoadImageW(None, icon_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE | LR_DEFAULTSIZE)
                big_icon = user32.LoadImageW(None, icon_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE | LR_DEFAULTSIZE)

                if small_icon:
                    user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, small_icon)
                if big_icon:
                    user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, big_icon)

                self.root.update_idletasks()
            except Exception:
                pass

    def build_main_tab(self, bg, fg, bg_input):
        left = ttk.Frame(self.main_tab, padding=(0, 0, 12, 0), style="Card.TFrame")
        left.grid(row=0, column=0, sticky="nsew")
        right = ttk.Frame(self.main_tab, padding=(0, 0, 0, 0), style="Card.TFrame")
        right.grid(row=0, column=1, sticky="nsew")

        ttk.Label(left, text="Auto Search", style="Title.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        ttk.Label(left, text="Automação completa com busca, URL, cliques e pontos personalizados.", style="Subtitle.TLabel", wraplength=420).grid(row=1, column=0, sticky="w", pady=(0, 12))

        ttk.Label(left, text="URL (opcional)").grid(row=2, column=0, sticky="w", pady=(0, 4))
        self.campo_url = ttk.Entry(left, width=42)
        self.campo_url.grid(row=3, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(left, text="Texto de busca (opcional)").grid(row=4, column=0, sticky="w", pady=(0, 4))
        self.campo_busca = ttk.Entry(left, width=42)
        self.campo_busca.grid(row=5, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(left, text="Navegador").grid(row=6, column=0, sticky="w", pady=(0, 4))
        self.browser_var = tk.StringVar(value="edge")
        self.browser_menu = ttk.Combobox(left, textvariable=self.browser_var, values=["edge", "chrome", "firefox"], state="readonly", width=39)
        self.browser_menu.grid(row=7, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(left, text="Repetições").grid(row=8, column=0, sticky="w", pady=(0, 4))
        self.campo_qtd_repeticoes = ttk.Entry(left, width=42)
        self.campo_qtd_repeticoes.grid(row=9, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(left, text="Espera entre etapas (segundos)").grid(row=10, column=0, sticky="w", pady=(0, 4))
        self.campo_espera = ttk.Entry(left, width=42)
        self.campo_espera.grid(row=11, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(left, text="Clique padrão").grid(row=12, column=0, sticky="w", pady=(0, 4))
        self.default_click_mode = tk.StringVar(value="default")
        click_mode_frame = ttk.Frame(left, style="Card.TFrame")
        click_mode_frame.grid(row=13, column=0, sticky="ew", pady=(0, 6))
        ttk.Radiobutton(click_mode_frame, text="Padrão", variable=self.default_click_mode, value="default").grid(row=0, column=0, sticky="w", padx=(0, 12))
        ttk.Radiobutton(click_mode_frame, text="Off", variable=self.default_click_mode, value="off").grid(row=0, column=1, sticky="w", padx=(0, 12))
        ttk.Radiobutton(click_mode_frame, text="Preset", variable=self.default_click_mode, value="preset").grid(row=0, column=2, sticky="w")

        ttk.Label(left, text="Coordenadas do clique padrão (X, Y)").grid(row=14, column=0, sticky="w", pady=(8, 4))
        pos_frame = ttk.Frame(left, style="Card.TFrame")
        pos_frame.grid(row=15, column=0, sticky="ew", pady=(0, 6))
        self.campo_x = ttk.Entry(pos_frame, width=10)
        self.campo_x.grid(row=0, column=0, padx=(0, 6))
        self.campo_y = ttk.Entry(pos_frame, width=10)
        self.campo_y.grid(row=0, column=1)

        ttk.Label(left, text="Preset do clique padrão").grid(row=16, column=0, sticky="w", pady=(8, 4))
        self.default_click_preset = ttk.Combobox(left, values=[], state="readonly", width=39)
        self.default_click_preset.grid(row=17, column=0, sticky="ew", pady=(0, 6))

        button_frame = ttk.Frame(left, style="Card.TFrame")
        button_frame.grid(row=18, column=0, sticky="w", pady=(0, 10))
        ttk.Button(button_frame, text="Capturar posição", command=self.capture_mouse_position).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(button_frame, text="Salvar", command=self.salvarConteudos).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(button_frame, text="Iniciar", command=self.click_assistent_start, style="Accent.TButton").grid(row=0, column=2)

        ttk.Label(right, text="Ações extras e cliques").grid(row=0, column=0, sticky="w", pady=(0, 4))
        ttk.Label(right, text="Exemplos:\nurl: https://site.com\npesquisar: python\nesperar: 2\nclick: 100,200\nclicks: 100,200; 500,300\npreset: canto-superior-esquerdo\nclick_padrao: off\nkey: enter", foreground="gray", wraplength=320).grid(row=1, column=0, sticky="w", pady=(0, 4))
        self.campo_acoes = tk.Text(right, height=15, width=46, bg=bg_input, fg=fg, insertbackground=fg, relief="solid")
        self.campo_acoes.grid(row=2, column=0, sticky="nsew")

        self.main_tab.columnconfigure(0, weight=1)
        self.main_tab.columnconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

    def build_presets_tab(self, bg, fg, bg_input):
        ttk.Label(self.presets_tab, text="Gerencie pontos de clique personalizados para cantos e áreas frequentes.", wraplength=650).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        form = ttk.Frame(self.presets_tab, padding=(0, 0, 12, 0), style="Card.TFrame")
        form.grid(row=1, column=0, sticky="nsew")

        ttk.Label(form, text="Nome do ponto").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.preset_name = ttk.Entry(form, width=28)
        self.preset_name.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        ttk.Label(form, text="Coordenadas X, Y").grid(row=2, column=0, sticky="w", pady=(0, 4))
        coord_frame = ttk.Frame(form, style="Card.TFrame")
        coord_frame.grid(row=3, column=0, sticky="ew", pady=(0, 6))
        self.preset_x = ttk.Entry(coord_frame, width=10)
        self.preset_x.grid(row=0, column=0, padx=(0, 6))
        self.preset_y = ttk.Entry(coord_frame, width=10)
        self.preset_y.grid(row=0, column=1)

        buttons = ttk.Frame(form, style="Card.TFrame")
        buttons.grid(row=4, column=0, sticky="w", pady=(8, 0))
        ttk.Button(buttons, text="Adicionar ponto", command=self.add_preset).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(buttons, text="Remover selecionado", command=self.remove_preset).grid(row=0, column=1)

        list_frame = ttk.Frame(self.presets_tab, padding=(0, 0, 0, 0), style="Card.TFrame")
        list_frame.grid(row=1, column=1, sticky="nsew")
        ttk.Label(list_frame, text="Pontos salvos").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self.preset_listbox = tk.Listbox(list_frame, height=12, width=42, bg=bg_input, fg=fg, relief="solid")
        self.preset_listbox.grid(row=1, column=0, sticky="nsew")

        self.presets_tab.columnconfigure(0, weight=1)
        self.presets_tab.columnconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)

    def set_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def apply_theme(self):
        self.theme = self.theme_var.get()
        self.update_theme(self.theme)
        self.save_settings()

    def update_theme(self, theme):
        if theme == "dark":
            bg = "#111827"
            bg_input = "#1f2937"
            fg = "#f9fafb"
            accent = "#60a5fa"
        else:
            bg = "#f3f6fb"
            bg_input = "#ffffff"
            fg = "#111827"
            accent = "#2563eb"

        self.root.configure(bg=bg)
        self.main_tab.configure(style="Card.TFrame")
        self.presets_tab.configure(style="Card.TFrame")
        self.status_label.configure(background=bg, foreground=fg)

        style = ttk.Style(self.root)
        style.configure("Card.TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), foreground=accent)
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground=fg)
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("Accent.TButton", background=accent, foreground="white")
        style.map("Accent.TButton", background=[("active", "#3b82f6")])

        for widget in [self.campo_url, self.campo_busca, self.browser_menu, self.campo_qtd_repeticoes, self.campo_espera, self.campo_x, self.campo_y, self.campo_acoes, self.preset_name, self.preset_x, self.preset_y, self.preset_listbox]:
            if widget is not None:
                try:
                    widget.configure(bg=bg_input, fg=fg)
                except Exception:
                    pass

        self.root.update_idletasks()

    def load_settings(self):
        try:
            data = self.config_manager.load()
            self.theme = data.get("theme", "light")
            self.theme_var.set(self.theme)
            self.update_theme(self.theme)
            self.campo_url.insert(0, data.get("url", ""))
            self.campo_busca.insert(0, data.get("busca", ""))
            self.browser_var.set(data.get("browser", "edge"))
            self.campo_qtd_repeticoes.insert(0, data.get("repeticoes", ""))
            self.campo_espera.insert(0, data.get("espera", "0.5"))
            self.campo_x.insert(0, data.get("x", ""))
            self.campo_y.insert(0, data.get("y", ""))
            self.campo_acoes.insert("1.0", data.get("acoes", ""))
            self.default_click_mode.set(data.get("default_click_mode", "default"))
            self.default_click_preset.set(data.get("default_click_preset", ""))

            preset_entries = data.get("click_presets", [])
            self.presets = []
            for preset in preset_entries:
                self.presets.append(ClickPreset(name=preset.get("name", ""), x=int(preset.get("x", 0)), y=int(preset.get("y", 0))))
            self.refresh_presets()
            self.update_default_click_preset_options()
        except FileNotFoundError:
            self.campo_qtd_repeticoes.insert(0, "5")
            self.campo_espera.insert(0, "0.5")
            self.campo_x.insert(0, "500")
            self.campo_y.insert(0, "300")
            self.default_click_mode.set("default")
            self.default_click_preset.set("")
            self.presets = [
                ClickPreset("canto-superior-esquerdo", 50, 50),
                ClickPreset("canto-superior-direito", 1900, 50),
                ClickPreset("canto-inferior-esquerdo", 50, 1000),
                ClickPreset("canto-inferior-direito", 1900, 1000),
            ]
            self.refresh_presets()
            self.update_default_click_preset_options()
        except json.JSONDecodeError:
            self.set_status("Arquivo de configurações inválido. Um novo arquivo será criado.")

    def update_default_click_preset_options(self):
        preset_names = [preset.name for preset in self.presets]
        self.default_click_preset.configure(values=preset_names)
        if preset_names:
            current_value = self.default_click_preset.get()
            if current_value not in preset_names:
                self.default_click_preset.set(preset_names[0])

    def save_settings(self):
        data = {
            "url": self.campo_url.get(),
            "busca": self.campo_busca.get(),
            "browser": self.browser_var.get(),
            "repeticoes": self.campo_qtd_repeticoes.get(),
            "espera": self.campo_espera.get(),
            "x": self.campo_x.get(),
            "y": self.campo_y.get(),
            "default_click_mode": self.default_click_mode.get(),
            "default_click_preset": self.default_click_preset.get(),
            "acoes": self.campo_acoes.get("1.0", tk.END),
            "theme": self.theme,
            "click_presets": [
                {"name": preset.name, "x": preset.x, "y": preset.y}
                for preset in self.presets
            ],
        }
        self.config_manager.save(data)

    def add_preset(self):
        name = self.preset_name.get().strip()
        x_value = self.preset_x.get().strip()
        y_value = self.preset_y.get().strip()
        if not name or not x_value or not y_value:
            messagebox.showwarning("Dados incompletos", "Informe nome, X e Y para adicionar um ponto.")
            return

        try:
            x = int(x_value)
            y = int(y_value)
        except ValueError:
            messagebox.showerror("Dados inválidos", "As coordenadas devem ser números inteiros.")
            return

        self.presets.append(ClickPreset(name=name, x=x, y=y))
        self.refresh_presets()
        self.update_default_click_preset_options()
        self.preset_name.delete(0, tk.END)
        self.preset_x.delete(0, tk.END)
        self.preset_y.delete(0, tk.END)
        self.save_settings()
        messagebox.showinfo("Ponto adicionado", f"Ponto '{name}' salvo com sucesso.")

    def remove_preset(self):
        selection = self.preset_listbox.curselection()
        if not selection:
            messagebox.showwarning("Seleção ausente", "Selecione um ponto na lista para remover.")
            return
        index = selection[0]
        del self.presets[index]
        self.refresh_presets()
        self.update_default_click_preset_options()
        self.save_settings()

    def refresh_presets(self):
        self.preset_listbox.delete(0, tk.END)
        for preset in self.presets:
            self.preset_listbox.insert(tk.END, f"{preset.name} -> ({preset.x}, {preset.y})")

    def click_assistent_start(self):
        try:
            repeticoes = int(self.campo_qtd_repeticoes.get().strip() or 0)
            if repeticoes <= 0:
                raise ValueError("Informe um número de repetições maior que zero.")
            espera = float(self.campo_espera.get().strip() or 0.5)
            x = int(self.campo_x.get().strip() or 0)
            y = int(self.campo_y.get().strip() or 0)
        except ValueError as exc:
            messagebox.showerror("Dados inválidos", str(exc))
            return

        self.save_settings()
        self.set_status("Iniciando automação...")

        try:
            selected_default_click_preset = self.default_click_preset.get().strip()
            config = AutomationConfig(
                browser=self.browser_var.get(),
                search_text=self.campo_busca.get().strip(),
                url=self.campo_url.get().strip(),
                repetitions=repeticoes,
                wait_time=espera,
                default_click=(x, y),
                default_click_mode=self.default_click_mode.get(),
                default_click_preset=selected_default_click_preset,
                click_presets=self.presets,
                custom_actions=self.campo_acoes.get("1.0", tk.END),
            )
            self.engine.run(config)
            self.set_status("Automação concluída com sucesso.")
            messagebox.showinfo("Concluído", "A automação foi executada com sucesso.")
        except Exception as exc:  # pragma: no cover - runtime safety
            self.set_status(f"Erro: {exc}")
            messagebox.showerror("Erro na automação", str(exc))

    def capture_mouse_position(self):
        self.set_status("Aguardando 3 segundos para capturar a posição do mouse...")
        tm.sleep(3)
        position_mouse = autogui.position()
        self.campo_x.delete(0, tk.END)
        self.campo_y.delete(0, tk.END)
        self.campo_x.insert(0, str(position_mouse.x))
        self.campo_y.insert(0, str(position_mouse.y))
        self.preset_x.delete(0, tk.END)
        self.preset_y.delete(0, tk.END)
        self.preset_x.insert(0, str(position_mouse.x))
        self.preset_y.insert(0, str(position_mouse.y))
        messagebox.showinfo("Posição do mouse", f"Posição do mouse: {position_mouse.x} x {position_mouse.y}")
        self.set_status("Posição capturada com sucesso.")

    def salvarConteudos(self):
        self.save_settings()
        messagebox.showinfo("Dados salvos", "As informações foram salvas em dados.json")


def main():
    AutoBing()
