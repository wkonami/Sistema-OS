import tkinter as tk
from tkinter import ttk, messagebox
import logging
from database import get_connection
from config import FONT_NAME

class SelecionarClienteWindow:
    instance = None
    def __init__(self, callback, pos_x=100, pos_y=100):
        if SelecionarClienteWindow.instance is not None and tk.Toplevel.winfo_exists(SelecionarClienteWindow.instance):
            SelecionarClienteWindow.instance.win.deiconify()
            SelecionarClienteWindow.instance.win.lift()
            SelecionarClienteWindow.instance.win.focus_force()
            return
        
        SelecionarClienteWindow.instance = self
        
        self.callback = callback
        self.win = tk.Toplevel()
        self.win.title("Selecionar Cliente")
        self.win.geometry(f"600x400+{pos_x}+{pos_y}")
        self.win.resizable(True, True)
        
        # Frame de pesquisa
        search_frame = tk.Frame(self.win)
        search_frame.pack(pady=5, fill="x", padx=10)
        
        tk.Label(search_frame, text="ID:", font=(FONT_NAME, 10)).pack(side="left", padx=5)
        self.entry_id = tk.Entry(search_frame, width=10, font=(FONT_NAME, 10))
        self.entry_id.pack(side="left", padx=5)
        
        tk.Label(search_frame, text="Nome:", font=(FONT_NAME, 10)).pack(side="left", padx=5)
        self.entry_nome = tk.Entry(search_frame, width=20, font=(FONT_NAME, 10))
        self.entry_nome.pack(side="left", padx=5)
        
        tk.Button(search_frame, text="Pesquisar", command=self.search_clients, font=(FONT_NAME, 10)).pack(side="left", padx=5)
        
        # Treeview para listar clientes
        self.tree = ttk.Treeview(self.win, columns=("ID", "Nome", "CPF", "Email"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("CPF", text="CPF")
        self.tree.heading("Email", text="Email")
        self.tree.column("ID", width=50)
        self.tree.column("Nome", width=150)
        self.tree.column("CPF", width=100)
        self.tree.column("Email", width=150)
        self.tree.pack(pady=5, fill="both", expand=True, padx=10)
        
        # Botão para confirmar seleção
        btn = tk.Button(self.win, text="Selecionar", command=self.select_client, font=(FONT_NAME, 10))
        btn.pack(pady=10)
        
        self.load_all_clients()

    def load_all_clients(self):
        """Carrega todos os clientes ordenados por ID e os exibe na Treeview."""
        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, nome, cpf, email FROM clientes ORDER BY id")
            clientes = cur.fetchall()
            cur.close()
            # Limpa a Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            # Insere os clientes
            for cli in clientes:
                self.tree.insert("", tk.END, values=cli)
        except Exception as e:
            logging.error("Erro ao carregar clientes na seleção: %s", e)
        finally:
            conn.close()

    def search_clients(self):
        """Pesquisa clientes com base no ID e/ou nome informados."""
        cid = self.entry_id.get().strip()
        cname = self.entry_nome.get().strip()
        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            query = "SELECT id, nome, cpf, email FROM clientes WHERE 1=1 "
            params = []
            if cid:
                query += "AND id = %s "
                params.append(cid)
            if cname:
                query += "AND nome ILIKE %s "
                params.append(f"%{cname}%")
            query += "ORDER BY id"
            cur.execute(query, tuple(params))
            clientes = cur.fetchall()
            cur.close()
            # Atualiza a Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            for cli in clientes:
                self.tree.insert("", tk.END, values=cli)
        except Exception as e:
            logging.error("Erro na pesquisa de clientes na seleção: %s", e)
        finally:
            conn.close()

    def select_client(self):
        """Retorna os dados do cliente selecionado para o callback e fecha a janela."""
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Erro", "Selecione um cliente!")
            return
        client_data = self.tree.item(selected, "values")
        self.callback(client_data)
        self.win.destroy()
        SelecionarClienteWindow.instance = None

