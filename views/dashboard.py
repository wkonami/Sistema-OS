# views/dashboard.py
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import logging
from datetime import datetime
from PIL import Image, ImageTk
from database import get_connection
from config import (FONT_NAME, ICON_PATH, MAIN_WIDTH, MAIN_HEIGHT, 
                    PROG_NAME, PROG_VERSION, SOCIAL_ICONS, SOCIAL_LINKS)
from globals import current_dashboard
from views.vendas import VendasWindow
from views.os import OrdemServicoWindow

class DashboardWindow:
    def __init__(self, username):
        global current_dashboard
        self.username = username
        self.root = tk.Tk()
        self.root.title(f"{PROG_NAME} - Dashboard")
        self.root.geometry(f"{MAIN_WIDTH}x{MAIN_HEIGHT}+0+0")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)
        try:
            self.icon = tk.PhotoImage(file=ICON_PATH)
            self.root.iconphoto(True, self.icon)
        except Exception as e:
            logging.error("Erro ao carregar ícone: %s", e)
        current_dashboard = self  # Atualiza a referência global
        self.original_social_images = {}
        self.social_labels = {}
        self.setup_widgets()
        self.root.mainloop()

    def setup_widgets(self):
        # Cabeçalho com informações e ícones de redes sociais
        self.header_frame = tk.Frame(self.root)
        self.header_frame.pack(pady=10, fill="x")
        tk.Label(self.header_frame, text=f"Usuário: {self.username}", 
                 font=(FONT_NAME, 12, "bold")).pack(side="left", padx=10)
        tk.Label(self.header_frame, text=f"{PROG_NAME}", 
                 font=(FONT_NAME, 12, "bold")).pack(side="left", padx=10)
        tk.Label(self.header_frame, text=f"Versão: {PROG_VERSION}", 
                 font=(FONT_NAME, 12, "bold")).pack(side="left", padx=10)
        # Redes Sociais
        self.social_frame = tk.Frame(self.header_frame)
        self.social_frame.pack(side="right", padx=10)
        for key in SOCIAL_ICONS:
            try:
                original = Image.open(SOCIAL_ICONS[key])
                self.original_social_images[key] = original
                target_height = 40
                ratio = original.width / original.height
                target_width = int(target_height * ratio)
                photo = ImageTk.PhotoImage(original.resize((target_width, target_height), Image.LANCZOS))
                lbl = tk.Label(self.social_frame, image=photo, cursor="hand2")
                lbl.image = photo
                lbl.pack(side="left", padx=5)
                lbl.bind("<Button-1>", lambda e, url=SOCIAL_LINKS[key]: webbrowser.open(url))
                self.social_labels[key] = lbl
            except Exception as e:
                logging.error("Erro ao carregar ícone de rede social (%s): %s", key, e)
        self.header_frame.bind("<Configure>", self.on_header_configure)

        # Botões de Navegação Superior
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=5, fill="x")
        tk.Button(nav_frame, text="Vendas", command=self.abrir_vendas, 
                  font=(FONT_NAME, 10)).pack(side="left", padx=10)
        tk.Button(nav_frame, text="Ordem de Serviço", command=self.abrir_os, 
                  font=(FONT_NAME, 10)).pack(side="left", padx=10)

        # Painéis principais: Aniversariantes e Clientes com Débitos/Créditos
        panels_frame = tk.Frame(self.root)
        panels_frame.pack(fill="both", expand=True, padx=10, pady=10)
        # Painel de Aniversariantes
        anivers_frame = tk.LabelFrame(panels_frame, text="Aniversariantes Hoje", font=(FONT_NAME, 10))
        anivers_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.anivers_tree = ttk.Treeview(anivers_frame, columns=("ID", "Nome", "Data Nasc"), show="headings")
        self.anivers_tree.heading("ID", text="ID")
        self.anivers_tree.heading("Nome", text="Nome")
        self.anivers_tree.heading("Data Nasc", text="Data Nasc")
        self.anivers_tree.column("ID", width=30)
        self.anivers_tree.column("Nome", width=120)
        self.anivers_tree.column("Data Nasc", width=90)
        self.anivers_tree.pack(fill="both", expand=True)
        # Painel de Clientes com Débitos/Créditos
        debitos_frame = tk.LabelFrame(panels_frame, text="Clientes com Débitos/Créditos", font=(FONT_NAME, 10))
        debitos_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        self.debitos_tree = ttk.Treeview(debitos_frame, columns=("ID", "Nome", "Saldo"), show="headings")
        self.debitos_tree.heading("ID", text="ID")
        self.debitos_tree.heading("Nome", text="Nome")
        self.debitos_tree.heading("Saldo", text="Saldo")
        self.debitos_tree.column("ID", width=30)
        self.debitos_tree.column("Nome", width=120)
        self.debitos_tree.column("Saldo", width=80)
        self.debitos_tree.pack(fill="both", expand=True)
        # Configura tags para cores
        self.debitos_tree.tag_configure("debit", foreground="red")
        self.debitos_tree.tag_configure("credit", foreground="green")

        # Botões inferiores fixados
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(pady=10, fill="x")
        tk.Button(bottom_frame, text="Cadastro/Pesquisa de Clientes", command=self.abrir_cadastro, 
                  font=(FONT_NAME, 10)).pack(side="left", padx=10)
        tk.Button(bottom_frame, text="Controlar Débitos/Créditos", command=self.abrir_debitos, 
                  font=(FONT_NAME, 10)).pack(side="left", padx=10)

        self.refresh_data()

    def on_header_configure(self, event):
        new_height = max(20, int(event.height * 0.8))
        for key, original in self.original_social_images.items():
            ratio = original.width / original.height
            new_width = int(new_height * ratio)
            resized = original.resize((new_width, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(resized)
            lbl = self.social_labels.get(key)
            if lbl:
                lbl.config(image=photo)
                lbl.image = photo

    def refresh_data(self):
        self.load_aniversariantes()
        self.load_debitos()

    def load_aniversariantes(self):
        for item in self.anivers_tree.get_children():
            self.anivers_tree.delete(item)
        hoje = datetime.now()
        dia_mes = hoje.strftime("%d/%m")
        conn = get_connection()
        if conn is None:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.", parent=self.win)
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, nome, to_char(data_nasc, 'DD/MM/YYYY') AS data_nasc 
                FROM clientes
                WHERE to_char(data_nasc, 'DD/MM') = %s
            """, (dia_mes,))
            for row in cur.fetchall():
                self.anivers_tree.insert("", tk.END, values=row)
            cur.close()
        except Exception as e:
            logging.error("Erro ao carregar aniversariantes: %s", e)
            messagebox.showerror("Erro", "Erro ao carregar aniversariantes.", parent=self.win)
        finally:
            conn.close()

    def load_debitos(self):
        for item in self.debitos_tree.get_children():
            self.debitos_tree.delete(item)
        conn = get_connection()
        if conn is None:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.", parent=self.win)
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, nome, saldo FROM clientes
                WHERE saldo <> 0
                ORDER BY saldo DESC
            """)
            for row in cur.fetchall():
                try:
                    saldo = float(row[2])
                    tag = "debit" if saldo > 0 else "credit" if saldo < 0 else ""
                except:
                    tag = ""
                self.debitos_tree.insert("", tk.END, values=row, tags=(tag,))
            cur.close()
        except Exception as e:
            logging.error("Erro ao carregar débitos: %s", e)
            messagebox.showerror("Erro", "Erro ao carregar débitos.", parent=self.win)
        finally:
            conn.close()

    def abrir_cadastro(self):
        x = self.root.winfo_x() + 30
        y = self.root.winfo_y() + 30
        from views.cadastro import CadastroWindow
        CadastroWindow(x, y)

    def abrir_debitos(self):
        x = self.root.winfo_x() + 30
        y = self.root.winfo_y() + 30
        from views.debitos import DebitosWindow
        DebitosWindow(x, y)

    def abrir_vendas(self):
        x = self.root.winfo_x() + 30
        y = self.root.winfo_y() + 30
        from views.vendas import VendasWindow
        VendasWindow(x, y)

    def abrir_os(self):
        x = self.root.winfo_x() + 30
        y = self.root.winfo_y() + 30
        from views.os import OrdemServicoWindow
        OrdemServicoWindow(x, y)
