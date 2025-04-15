import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import logging
from datetime import datetime
from PIL import Image, ImageTk
from database import get_connection
from config import FONT_NAME, ICON_PATH, MAIN_WIDTH, MAIN_HEIGHT, PROG_NAME, PROG_VERSION, SOCIAL_ICONS, SOCIAL_LINKS
from globals import current_dashboard

# --- Janela de Controle de Débitos/Créditos ---
class DebitosWindow:
    instance = None

    def __init__(self, pos_x=100, pos_y=100):
        if DebitosWindow.instance is not None and tk.Toplevel.winfo_exists(DebitosWindow.instance.win):
            DebitosWindow.instance.win.deiconify()
            DebitosWindow.instance.win.lift()
            DebitosWindow.instance.win.focus_force()
            return
        
        DebitosWindow.instance = self

        self.win = tk.Toplevel()
        self.win.title("Controle de Débitos/Créditos")
        self.win.geometry(f"500x400+{pos_x}+{pos_y}")
        self.win.resizable(False, False)
        try:
            self.icon = tk.PhotoImage(file=ICON_PATH)
            self.win.iconphoto(True, self.icon)
        except Exception as e:
            logging.error("Ícone não carregado: %s", e)
        self.setup_widgets()
        self.load_all_clients()

    def setup_widgets(self):
        search_frame = tk.Frame(self.win)
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Buscar Cliente (Nome ou CPF):", font=(FONT_NAME, 10)).pack(side="left", padx=5)
        self.entry_search = tk.Entry(search_frame, width=30, font=(FONT_NAME, 10))
        self.entry_search.pack(side="left", padx=5)
        tk.Button(search_frame, text="Pesquisar", command=self.search_client, font=(FONT_NAME, 10)).pack(side="left", padx=5)
        self.tree = ttk.Treeview(self.win, columns=("ID", "Nome", "Saldo"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Saldo", text="Saldo")
        self.tree.column("ID", width=30)
        self.tree.column("Nome", width=150)
        self.tree.column("Saldo", width=80)
        self.tree.pack(pady=10, fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        adjust_frame = tk.Frame(self.win)
        adjust_frame.pack(pady=10)
        tk.Label(adjust_frame, text="Saldo Atual:", font=(FONT_NAME, 10)).pack(side="left", padx=5)
        self.label_saldo = tk.Label(adjust_frame, text="0", font=(FONT_NAME, 10))
        self.label_saldo.pack(side="left", padx=5)
        tk.Label(adjust_frame, text="Ajuste (+/-):", font=(FONT_NAME, 10)).pack(side="left", padx=5)
        self.entry_adjust = tk.Entry(adjust_frame, width=10, font=(FONT_NAME, 10))
        self.entry_adjust.pack(side="left", padx=5)
        tk.Button(adjust_frame, text="Aplicar", command=self.apply_adjustment, font=(FONT_NAME, 10)).pack(side="left", padx=5)

    def load_all_clients(self):
        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, nome, saldo FROM clientes
                ORDER BY id
            """)
            resultados = cur.fetchall()
            cur.close()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for row in resultados:
                self.tree.insert("", tk.END, values=row)
        except Exception as e:
            logging.error("Erro ao carregar clientes (débito): %s", e)
            messagebox.showerror("Erro", "Erro interno na pesquisa.")
        finally:
            conn.close()

    def search_client(self):
        termo = self.entry_search.get().strip()
        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            if termo:
                cur.execute("""
                    SELECT id, nome, saldo FROM clientes
                    WHERE nome ILIKE %s OR cpf ILIKE %s
                    ORDER BY id
                """, (f"{termo}%", f"%{termo}%"))
            else:
                cur.execute("""
                    SELECT id, nome, saldo FROM clientes
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
            logging.error("Erro na pesquisa de clientes (débito): %s", e)
            messagebox.showerror("Erro", "Erro interno na pesquisa.")
        finally:
            conn.close()

    def on_select(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            self.selected_id = values[0]
            self.label_saldo.config(text=str(values[2]))
        else:
            self.selected_id = None

    def apply_adjustment(self):
        if not hasattr(self, 'selected_id') or not self.selected_id:
            messagebox.showerror("Erro", "Selecione um cliente primeiro!")
            return
        try:
            adjust_value = float(self.entry_adjust.get())
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor numérico para ajuste.")
            return
        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            cur.execute("UPDATE clientes SET saldo = saldo + %s WHERE id = %s", (adjust_value, self.selected_id))
            conn.commit()
            cur.close()
            messagebox.showinfo("Sucesso", "Saldo atualizado com sucesso!")
            self.search_client()
            self.entry_adjust.delete(0, tk.END)
            from globals import current_dashboard
            if current_dashboard is not None:
                current_dashboard.refresh_data()
        except Exception as e:
            logging.error("Erro ao atualizar saldo: %s", e)
            messagebox.showerror("Erro", "Erro interno ao atualizar saldo.")
        finally:
            conn.close()
