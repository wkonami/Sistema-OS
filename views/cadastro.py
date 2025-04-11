import re
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import logging
from datetime import datetime
from PIL import Image, ImageTk
from database import get_connection
from config import FONT_NAME, ICON_PATH, MAIN_WIDTH, MAIN_HEIGHT, PROG_NAME, PROG_VERSION, SOCIAL_ICONS, SOCIAL_LINKS
from globals import current_dashboard

# --- Janela de Cadastro/Pesquisa de Clientes ---
class CadastroWindow:
    def __init__(self, pos_x=100, pos_y=100):
        self.win = tk.Toplevel()
        self.win.title("Cadastro e Pesquisa de Clientes")
        self.win.geometry(f"{MAIN_WIDTH}x{MAIN_HEIGHT}+{pos_x}+{pos_y}")
        self.win.resizable(False, False)
        try:
            self.icon = tk.PhotoImage(file=ICON_PATH)
            self.win.iconphoto(True, self.icon)
        except Exception as e:
            logging.error("Ícone não carregado: %s", e)
        self.setup_widgets()
        self.load_all_clients()

    def setup_widgets(self):
        frame_cadastro = tk.LabelFrame(self.win, text="Cadastro de Clientes", padx=10, pady=10, font=(FONT_NAME, 10))
        frame_cadastro.pack(padx=10, pady=10, fill="x")
        tk.Label(frame_cadastro, text="Nome:", font=(FONT_NAME, 10)).grid(row=0, column=0, sticky="e", pady=5)
        self.entry_nome = tk.Entry(frame_cadastro, width=40, font=(FONT_NAME, 10))
        self.entry_nome.grid(row=0, column=1, pady=5)
        self.entry_nome.focus_set()
        tk.Label(frame_cadastro, text="CPF:", font=(FONT_NAME, 10)).grid(row=1, column=0, sticky="e", pady=5)
        self.entry_cpf = tk.Entry(frame_cadastro, width=40, font=(FONT_NAME, 10))
        self.entry_cpf.grid(row=1, column=1, pady=5)
        self.entry_cpf.bind("<KeyRelease>", self.format_cpf)
        tk.Label(frame_cadastro, text="Data de Nascimento:", font=(FONT_NAME, 10)).grid(row=2, column=0, sticky="e", pady=5)
        self.entry_data_nasc = tk.Entry(frame_cadastro, width=40, font=(FONT_NAME, 10))
        self.entry_data_nasc.grid(row=2, column=1, pady=5)
        self.entry_data_nasc.bind("<KeyRelease>", self.format_date)
        tk.Label(frame_cadastro, text="Email:", font=(FONT_NAME, 10)).grid(row=3, column=0, sticky="e", pady=5)
        self.entry_email = tk.Entry(frame_cadastro, width=40, font=(FONT_NAME, 10))
        self.entry_email.grid(row=3, column=1, pady=5)
        tk.Label(frame_cadastro, text="Telefone:", font=(FONT_NAME, 10)).grid(row=4, column=0, sticky="e", pady=5)
        self.entry_telefone = tk.Entry(frame_cadastro, width=40, font=(FONT_NAME, 10))
        self.entry_telefone.grid(row=4, column=1, pady=5)
        tk.Button(frame_cadastro, text="Cadastrar Cliente", command=self.cadastrar_cliente, font=(FONT_NAME, 10))\
            .grid(row=5, column=0, columnspan=2, pady=10)
        frame_pesquisa = tk.LabelFrame(self.win, text="Pesquisar Clientes", padx=10, pady=10, font=(FONT_NAME, 10))
        frame_pesquisa.pack(padx=10, pady=10, fill="both", expand=True)
        tk.Label(frame_pesquisa, text="Nome ou CPF:", font=(FONT_NAME, 10)).grid(row=0, column=0, sticky="e", pady=5)
        self.entry_pesquisa = tk.Entry(frame_pesquisa, width=30, font=(FONT_NAME, 10))
        self.entry_pesquisa.grid(row=0, column=1, pady=5)
        tk.Button(frame_pesquisa, text="Pesquisar", command=self.pesquisar_clientes, font=(FONT_NAME, 10))\
            .grid(row=0, column=2, padx=5, pady=5)
        self.tree = ttk.Treeview(frame_pesquisa, columns=("ID", "Nome", "CPF", "Data Nasc", "Email", "Telefone", "Saldo"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("CPF", text="CPF")
        self.tree.heading("Data Nasc", text="Data Nasc")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Telefone", text="Telefone")
        self.tree.heading("Saldo", text="Saldo")
        self.tree.column("ID", width=30)
        self.tree.column("Nome", width=120)
        self.tree.column("CPF", width=100)
        self.tree.column("Data Nasc", width=90)
        self.tree.column("Email", width=150)
        self.tree.column("Telefone", width=90)
        self.tree.column("Saldo", width=80)
        self.tree.grid(row=1, column=0, columnspan=3, pady=10, sticky="nsew")
        frame_pesquisa.grid_rowconfigure(1, weight=1)
        frame_pesquisa.grid_columnconfigure(1, weight=1)

    def format_date(self, event):
        text = self.entry_data_nasc.get()
        digits = re.sub(r'\D', '', text)
        new_text = ''
        if len(digits) >= 1:
            new_text += digits[:2]
        if len(digits) >= 3:
            new_text += '/' + digits[2:4]
        if len(digits) >= 5:
            new_text += '/' + digits[4:8]
        self.entry_data_nasc.delete(0, tk.END)
        self.entry_data_nasc.insert(0, new_text)

    def format_cpf(self, event):
        text = self.entry_cpf.get()
        digits = re.sub(r'\D', '', text)
        new_text = ''
        if len(digits) >= 1:
            new_text += digits[:3]
        if len(digits) >= 4:
            new_text += '.' + digits[3:6]
        if len(digits) >= 7:
            new_text += '.' + digits[6:9]
        if len(digits) >= 10:
            new_text += '-' + digits[9:11]
        self.entry_cpf.delete(0, tk.END)
        self.entry_cpf.insert(0, new_text)

    def cadastrar_cliente(self):
        nome = self.entry_nome.get().strip()
        cpf = self.entry_cpf.get().strip()
        data_nasc = self.entry_data_nasc.get().strip()
        email = self.entry_email.get().strip()
        telefone = self.entry_telefone.get().strip()
        if not nome:
            messagebox.showerror("Erro", "O campo nome é obrigatório!")
            return
        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            try:
                dia, mes, ano = data_nasc.split('/')
                data_iso = f"{ano}-{mes}-{dia}"
            except Exception:
                data_iso = None
            cur.execute(
                "INSERT INTO clientes (nome, cpf, data_nasc, email, telefone) VALUES (%s, %s, %s, %s, %s)",
                (nome, cpf, data_iso, email, telefone)
            )
            conn.commit()
            cur.close()
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            self.entry_nome.delete(0, tk.END)
            self.entry_cpf.delete(0, tk.END)
            self.entry_data_nasc.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            self.entry_telefone.delete(0, tk.END)
            self.entry_nome.focus_set()
            self.load_all_clients()
            from globals import current_dashboard
            if current_dashboard is not None:
                current_dashboard.refresh_data()
        except Exception as e:
            logging.error("Erro ao cadastrar cliente: %s", e)
            messagebox.showerror("Erro", "Erro interno ao cadastrar o cliente.")
        finally:
            conn.close()

    def pesquisar_clientes(self):
        termo = self.entry_pesquisa.get().strip()
        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            if termo:
                cur.execute("""
                    SELECT id, nome, cpf, to_char(data_nasc, 'DD/MM/YYYY') as data_nasc, email, telefone, saldo 
                    FROM clientes
                    WHERE nome ILIKE %s OR cpf ILIKE %s
                    ORDER BY id
                """, (f"{termo}%", f"%{termo}%"))
            else:
                cur.execute("""
                    SELECT id, nome, cpf, to_char(data_nasc, 'DD/MM/YYYY') as data_nasc, email, telefone, saldo 
                    FROM clientes
                    ORDER BY id
                """)
            resultados = cur.fetchall()
            cur.close()
            for item in self.tree.get_children():
                self.tree.delete(item)
            if resultados:
                for row in resultados:
                    self.tree.insert("", tk.END, values=row)
            else:
                messagebox.showinfo("Informação", "Nenhum cliente encontrado!")
        except Exception as e:
            logging.error("Erro na pesquisa de clientes: %s", e)
            messagebox.showerror("Erro", "Erro interno na pesquisa.")
        finally:
            conn.close()

    def load_all_clients(self):
        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, nome, cpf, to_char(data_nasc, 'DD/MM/YYYY') as data_nasc, email, telefone, saldo
                FROM clientes
                ORDER BY id
            """)
            resultados = cur.fetchall()
            cur.close()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in resultados:
                self.tree.insert("", tk.END, values=row)
        except Exception as e:
            logging.error("Erro ao carregar clientes: %s", e)
        finally:
            conn.close()
