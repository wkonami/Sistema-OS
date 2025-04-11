# views/os.py
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
from database import get_connection
from config import FONT_NAME, ICON_PATH, MAIN_WIDTH, MAIN_HEIGHT, PROG_NAME, PROG_VERSION
from views.selecionar_cliente import SelecionarClienteWindow

# ---------------------------
# Janela de Gerenciamento de Ordens de Serviço
# ---------------------------
class OrdemServicoWindow:
    def __init__(self, pos_x=100, pos_y=100):
        self.win = tk.Toplevel()
        self.win.title("Ordens de Serviço")
        self.win.geometry(f"800x600+{pos_x}+{pos_y}")
        self.win.minsize(800, 600)
        self.win.rowconfigure(1, weight=1)
        self.win.columnconfigure(0, weight=1)
        try:
            self.icon = tk.PhotoImage(file=ICON_PATH)
            self.win.iconphoto(True, self.icon)
        except Exception as e:
            logging.error("Erro ao carregar ícone: %s", e)
        self.setup_widgets()
        self.load_all_os()
        self.win.mainloop()

    def setup_widgets(self):
        # Área de Pesquisa
        search_frame = tk.Frame(self.win)
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        search_frame.columnconfigure(3, weight=1)
        tk.Label(search_frame, text="Pesquisar por:", font=(FONT_NAME, 10)).grid(row=0, column=0, padx=5)
        self.search_criteria = tk.StringVar(value="nome")
        tk.Radiobutton(search_frame, text="Nome", variable=self.search_criteria, value="nome", font=(FONT_NAME, 10))\
            .grid(row=0, column=1, padx=5)
        tk.Radiobutton(search_frame, text="OS", variable=self.search_criteria, value="os", font=(FONT_NAME, 10))\
            .grid(row=0, column=2, padx=5)
        self.entry_search = tk.Entry(search_frame, font=(FONT_NAME, 10))
        self.entry_search.grid(row=0, column=3, sticky="ew", padx=5)
        tk.Button(search_frame, text="Pesquisar", command=self.search_os, font=(FONT_NAME, 10))\
            .grid(row=0, column=4, padx=5)

        # Tabela de OS
        self.tree = ttk.Treeview(self.win, 
                                 columns=("OS", "Cliente ID", "Equipamento", "Nº Série", "Data Entrada", "Usuário", "Situação"), 
                                 show="headings")
        self.tree.heading("OS", text="OS")
        self.tree.heading("Cliente ID", text="Cliente ID")
        self.tree.heading("Equipamento", text="Equipamento")
        self.tree.heading("Nº Série", text="Nº Série")
        self.tree.heading("Data Entrada", text="Data Entrada")
        self.tree.heading("Usuário", text="Usuário")
        self.tree.heading("Situação", text="Situação")
        self.tree.column("OS", width=50)
        self.tree.column("Cliente ID", width=80)
        self.tree.column("Equipamento", width=150)
        self.tree.column("Nº Série", width=100)
        self.tree.column("Data Entrada", width=120)
        self.tree.column("Usuário", width=100)
        self.tree.column("Situação", width=100)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        # Permite também disparar a ação de conferir ao pressionar Enter
        self.tree.bind("<Double-1>", lambda event: self.conferir_os())
        self.tree.bind("<Return>", lambda event: self.conferir_os())

        # Área de Ações – Botões "Nova OS" e "Conferir OS"
        btn_frame = tk.Frame(self.win)
        btn_frame.grid(row=2, column=0, sticky="se", padx=10, pady=10)
        tk.Button(btn_frame, text="Nova OS", command=self.criar_os, font=(FONT_NAME, 10))\
            .pack(side="left", padx=5)
        tk.Button(btn_frame, text="Conferir OS", command=self.conferir_os, font=(FONT_NAME, 10))\
            .pack(side="left", padx=5)

    def load_all_os(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = get_connection()
        if conn is None:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.", parent=self.win)
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT os, id_cliente, equipamento, numero_serie, 
                       to_char(data_entrada, 'DD/MM/YYYY HH24:MI') as data_entrada,
                       usuario, situacao
                FROM ordens_servico
                ORDER BY data_entrada ASC
            """)
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            cur.close()
        except Exception as e:
            logging.error("Erro ao carregar ordens de serviço: %s", e)
            messagebox.showerror("Erro", "Erro ao carregar ordens de serviço.", parent=self.win)
        finally:
            conn.close()

    def search_os(self):
        criterio = self.search_criteria.get()   # "nome" ou "os"
        termo = self.entry_search.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        conn = get_connection()
        if conn is None:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.", parent=self.win)
            return
        try:
            cur = conn.cursor()
            if criterio == "os":
                try:
                    os_number = int(termo)
                    cur.execute("""
                        SELECT os, id_cliente, equipamento, numero_serie, 
                               to_char(data_entrada, 'DD/MM/YYYY HH24:MI') as data_entrada,
                               usuario, situacao
                        FROM ordens_servico
                        WHERE os = %s
                        ORDER BY data_entrada ASC
                    """, (os_number,))
                except ValueError:
                    messagebox.showerror("Erro", "O número da OS deve ser numérico.", parent=self.win)
                    cur.close()
                    return
            else:
                cur.execute("""
                    SELECT os, id_cliente, equipamento, numero_serie, 
                           to_char(data_entrada, 'DD/MM/YYYY HH24:MI') as data_entrada,
                           usuario, situacao
                    FROM ordens_servico
                    WHERE equipamento ILIKE %s
                    ORDER BY data_entrada ASC
                """, (f"%{termo}%",))
            rows = cur.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=row)
            cur.close()
        except Exception as e:
            logging.error("Erro na pesquisa de OS: %s", e)
            messagebox.showerror("Erro", "Erro interno na pesquisa.", parent=self.win)
        finally:
            conn.close()

    def criar_os(self):
        # Abre fluxo de criação de OS: primeiro seleciona o cliente
        def callback(client_data):
            CriarOSWindow(client_data)
            self.load_all_os()  # Atualiza a tabela de OS após criação
        SelecionarClienteWindow(callback, pos_x=self.win.winfo_x()+30, pos_y=self.win.winfo_y()+30)

    def conferir_os(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Erro", "Selecione uma OS para conferir.", parent=self.win)
            return
        os_data = self.tree.item(selected, "values")
        AlterarOSWindow(os_data)
        self.load_all_os()  # Atualiza a tabela após fechamento da janela de alteração

# ---------------------------
# Janela de Criar OS
# ---------------------------
class CriarOSWindow:
    def __init__(self, client_data, pos_x=150, pos_y=150):
        self.client_data = client_data
        # Usuário logado (stub – em produção, obtenha do login)
        self.usuario = "admin"
        self.win = tk.Toplevel()
        self.win.title("Criar OS")
        self.win.geometry(f"600x500+{pos_x}+{pos_y}")
        self.win.minsize(600, 400)
        try:
            self.icon = tk.PhotoImage(file=ICON_PATH)
            self.win.iconphoto(True, self.icon)
        except Exception as e:
            logging.error("Erro ao carregar ícone na Criar OS: %s", e)
        self.setup_widgets()

    def setup_widgets(self):
        header_frame = tk.Frame(self.win)
        header_frame.pack(fill="x", padx=10, pady=10)
        next_os = self.get_next_os_number()
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        tk.Label(header_frame, text=f"OS: {next_os}", font=(FONT_NAME, 12, "bold")).pack(side="left", padx=10)
        tk.Label(header_frame, text=f"Cliente: {self.client_data[0]} - {self.client_data[1]}", font=(FONT_NAME, 12, "bold")).pack(side="left", padx=10)
        tk.Label(header_frame, text=f"Aberta em: {now_str}", font=(FONT_NAME, 12, "bold")).pack(side="left", padx=10)

        form_frame = tk.Frame(self.win)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Label(form_frame, text="Equipamento:", font=(FONT_NAME, 10)).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.entry_equip = tk.Entry(form_frame, font=(FONT_NAME, 10))
        self.entry_equip.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        tk.Label(form_frame, text="Número de Série:", font=(FONT_NAME, 10)).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.entry_serie = tk.Entry(form_frame, font=(FONT_NAME, 10))
        self.entry_serie.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        tk.Label(form_frame, text="Descrição:", font=(FONT_NAME, 10)).grid(row=2, column=0, sticky="ne", pady=5, padx=5)
        self.text_descricao = tk.Text(form_frame, height=5, font=(FONT_NAME, 10))
        self.text_descricao.grid(row=2, column=1, sticky="ew", pady=5, padx=5)
        tk.Label(form_frame, text="Observações:", font=(FONT_NAME, 10)).grid(row=3, column=0, sticky="ne", pady=5, padx=5)
        self.text_obs = tk.Text(form_frame, height=3, font=(FONT_NAME, 10))
        self.text_obs.grid(row=3, column=1, sticky="ew", pady=5, padx=5)
        form_frame.columnconfigure(1, weight=1)

        btn_frame = tk.Frame(self.win)
        btn_frame.pack(fill="x", padx=10, pady=10)
        tk.Button(btn_frame, text="Criar OS", command=self.criar_os, font=(FONT_NAME, 10))\
            .pack(side="right", anchor="e")

    def get_next_os_number(self):
        conn = get_connection()
        next_os = 1
        if conn is None:
            return next_os
        try:
            cur = conn.cursor()
            cur.execute("SELECT MAX(os) FROM ordens_servico")
            result = cur.fetchone()
            if result and result[0]:
                next_os = result[0] + 1
            cur.close()
        except Exception as e:
            logging.error("Erro ao obter o próximo número de OS: %s", e)
        finally:
            conn.close()
        return next_os

    def criar_os(self):
        equipamento = self.entry_equip.get().strip()
        numero_serie = self.entry_serie.get().strip()
        descricao = self.text_descricao.get("1.0", tk.END).strip()
        observacoes = self.text_obs.get("1.0", tk.END).strip()
        if not equipamento:
            messagebox.showerror("Erro", "O campo equipamento é obrigatório.", parent=self.win)
            return
        conn = get_connection()
        if conn is None:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.", parent=self.win)
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO ordens_servico (id_cliente, equipamento, numero_serie, usuario, descricao, observacoes, situacao)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.client_data[0],
                equipamento,
                numero_serie,
                self.usuario,
                descricao,
                observacoes,
                "aberto"  # Situação padrão
            ))
            conn.commit()
            cur.close()
            messagebox.showinfo("Sucesso", "Ordem de Serviço criada com sucesso!", parent=self.win)
            self.win.destroy()
        except Exception as e:
            logging.error("Erro ao criar a OS: %s", e)
            messagebox.showerror("Erro", "Erro interno ao criar a OS.", parent=self.win)
        finally:
            conn.close()

# ---------------------------
# Janela de Alterar OS
# ---------------------------
class AlterarOSWindow:
    def __init__(self, os_data, pos_x=150, pos_y=150):
        """
        os_data: tuple com os dados da OS selecionada (ex: (os, id_cliente, equipamento, numero_serie, data_entrada, usuario, situacao))
        """
        self.os_data = os_data
        self.win = tk.Toplevel()
        self.win.title("Alterar OS")
        self.win.geometry(f"600x500+{pos_x}+{pos_y}")
        self.win.minsize(600, 400)
        try:
            self.icon = tk.PhotoImage(file=ICON_PATH)
            self.win.iconphoto(True, self.icon)
        except Exception as e:
            logging.error("Erro ao carregar ícone na Alterar OS: %s", e)
        self.setup_widgets()
        self.load_os_details()

    def setup_widgets(self):
        header_frame = tk.Frame(self.win)
        header_frame.pack(fill="x", padx=10, pady=10)
        # Cabeçalho exibindo número da OS, dados do cliente e data de abertura (obtida do os_data)
        tk.Label(header_frame, text=f"OS: {self.os_data[0]}", font=(FONT_NAME, 12, "bold")).pack(side="left", padx=10)
        tk.Label(header_frame, text=f"Cliente ID: {self.os_data[1]}", font=(FONT_NAME, 12, "bold")).pack(side="left", padx=10)
        tk.Label(header_frame, text=f"Aberta em: {self.os_data[4]}", font=(FONT_NAME, 12, "bold")).pack(side="left", padx=10)
        
        form_frame = tk.Frame(self.win)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        tk.Label(form_frame, text="Equipamento:", font=(FONT_NAME, 10)).grid(row=0, column=0, sticky="e", pady=5, padx=5)
        self.entry_equip = tk.Entry(form_frame, font=(FONT_NAME, 10))
        self.entry_equip.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        tk.Label(form_frame, text="Número de Série:", font=(FONT_NAME, 10)).grid(row=1, column=0, sticky="e", pady=5, padx=5)
        self.entry_serie = tk.Entry(form_frame, font=(FONT_NAME, 10))
        self.entry_serie.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        tk.Label(form_frame, text="Descrição:", font=(FONT_NAME, 10)).grid(row=2, column=0, sticky="ne", pady=5, padx=5)
        self.text_descricao = tk.Text(form_frame, height=5, font=(FONT_NAME, 10))
        self.text_descricao.grid(row=2, column=1, sticky="ew", pady=5, padx=5)
        tk.Label(form_frame, text="Observações:", font=(FONT_NAME, 10)).grid(row=3, column=0, sticky="ne", pady=5, padx=5)
        self.text_obs = tk.Text(form_frame, height=3, font=(FONT_NAME, 10))
        self.text_obs.grid(row=3, column=1, sticky="ew", pady=5, padx=5)
        tk.Label(form_frame, text="Situação:", font=(FONT_NAME, 10)).grid(row=4, column=0, sticky="e", pady=5, padx=5)
        # Permite alterar a situação para os valores válidos
        self.situacao_combobox = ttk.Combobox(form_frame, 
                                              values=["aberto", "finalizado", "recusado"],
                                              font=(FONT_NAME, 10))
        self.situacao_combobox.grid(row=4, column=1, sticky="w", pady=5, padx=5)
        form_frame.columnconfigure(1, weight=1)

        btn_frame = tk.Frame(self.win)
        btn_frame.pack(fill="x", padx=10, pady=10)
        tk.Button(btn_frame, text="Salvar Alterações", command=self.salvar_alteracoes, font=(FONT_NAME, 10))\
            .pack(side="right", anchor="e")

    def load_os_details(self):
        """Carrega os dados da OS selecionada nos campos para edição."""
        # Os valores da os_data já foram passados no callback
        self.entry_equip.insert(0, self.os_data[2])
        self.entry_serie.insert(0, self.os_data[3])
        # Descrição e observações podem não estar presentes; se estiverem, insira-os.
        # Neste stub, vamos assumir que os campos são strings vazias se None.
        if self.os_data[5]:
            self.entry_usuario = self.os_data[5]
        else:
            self.entry_usuario = ""
        # Para simplificar, vamos deixar descricao e observacoes vazias:
        self.text_descricao.insert("1.0", "")
        self.text_obs.insert("1.0", "")
        # Situação é carregada do os_data:
        self.situacao_combobox.set(self.os_data[6])

    def salvar_alteracoes(self):
        equipamento = self.entry_equip.get().strip()
        numero_serie = self.entry_serie.get().strip()
        descricao = self.text_descricao.get("1.0", tk.END).strip()
        observacoes = self.text_obs.get("1.0", tk.END).strip()
        situacao = self.situacao_combobox.get().strip()
        if not equipamento:
            messagebox.showerror("Erro", "O campo equipamento é obrigatório.", parent=self.win)
            return
        conn = get_connection()
        if conn is None:
            messagebox.showerror("Erro", "Não foi possível conectar ao banco de dados.", parent=self.win)
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE ordens_servico
                SET equipamento=%s, numero_serie=%s, descricao=%s, observacoes=%s, situacao=%s
                WHERE os = %s
            """, (equipamento, numero_serie, descricao, observacoes, situacao, self.os_data[0]))
            conn.commit()
            cur.close()
            messagebox.showinfo("Sucesso", "OS alterada com sucesso!", parent=self.win)
            self.win.destroy()
        except Exception as e:
            logging.error("Erro ao salvar alterações na OS: %s", e)
            messagebox.showerror("Erro", "Erro interno ao salvar alterações.", parent=self.win)
        finally:
            conn.close()