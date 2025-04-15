# views/vendas.py
import tkinter as tk
from tkinter import messagebox, ttk
import logging
from database import get_connection
from config import FONT_NAME, ICON_PATH
from views.selecionar_cliente import SelecionarClienteWindow

class VendasWindow:
    instance = None  # Variável de classe para armazenar a instância ativa

    def __init__(self, pos_x=100, pos_y=100):
        # Verifica se já existe uma instância e se a janela ainda está aberta.
        if VendasWindow.instance is not None and tk.Toplevel.winfo_exists(VendasWindow.instance.win):
            VendasWindow.instance.win.deiconify()
            # Traz a janela já aberta para frente e sai da inicialização.
            VendasWindow.instance.win.lift()
            VendasWindow.instance.win.focus_force()
            return
        
        # Se não existe, cria a nova janela e a armazena na variável de classe.
        VendasWindow.instance = self

        self.win = tk.Toplevel()
        self.win.title("Vendas")
        self.win.geometry(f"700x550+{pos_x}+{pos_y}")
        self.win.minsize(600, 400)
        self.win.rowconfigure(0, weight=0)
        self.win.rowconfigure(1, weight=1)
        self.win.rowconfigure(2, weight=0)
        self.win.columnconfigure(0, weight=1)
        self.sale_items = []  # Lista para armazenar itens da venda
        self.selected_client = None
        self.setup_widgets()

    def setup_widgets(self):
        # --- Linha 0: Seleção de Cliente ---
        client_frame = tk.Frame(self.win)
        client_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        client_frame.columnconfigure(1, weight=1)
        self.label_client = tk.Label(client_frame, text="Nenhum cliente selecionado", font=(FONT_NAME, 10))
        self.label_client.grid(row=0, column=0, padx=5)
        tk.Button(client_frame, text="Selecionar Cliente", command=self.selecionar_cliente, font=(FONT_NAME, 10))\
            .grid(row=0, column=1, padx=5, sticky="e")

        # --- Linha 1: Área de Produtos e Itens da Venda ---
        middle_frame = tk.Frame(self.win)
        middle_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.columnconfigure(1, weight=1)
        middle_frame.rowconfigure(1, weight=1)

        # Área de produtos (lado esquerdo) – organizada horizontalmente
        product_frame = tk.LabelFrame(middle_frame, text="Produtos", font=(FONT_NAME, 10))
        product_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        product_frame.columnconfigure(0, weight=1)
        product_frame.rowconfigure(1, weight=1)
        # Linha para pesquisa de produtos
        tk.Label(product_frame, text="Produto:", font=(FONT_NAME, 10)).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.entry_product = tk.Entry(product_frame, font=(FONT_NAME, 10))
        self.entry_product.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        tk.Button(product_frame, text="Pesquisar", command=self.search_product, font=(FONT_NAME, 10))\
            .grid(row=0, column=2, padx=5, pady=2)
        # Treeview de produtos – exibe todos os produtos por padrão
        self.prod_tree = ttk.Treeview(product_frame, columns=("ID", "Nome", "Preço", "Estoque"), show="headings", height=6)
        self.prod_tree.heading("ID", text="ID")
        self.prod_tree.heading("Nome", text="Nome")
        self.prod_tree.heading("Preço", text="Preço")
        self.prod_tree.heading("Estoque", text="Estoque")
        self.prod_tree.column("ID", width=30)
        self.prod_tree.column("Nome", width=150)
        self.prod_tree.column("Preço", width=80)
        self.prod_tree.column("Estoque", width=80)
        self.prod_tree.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=2)
        self.prod_tree.bind("<<TreeviewSelect>>", self.on_product_select)
        self.search_product()  # Carrega todos os produtos inicialmente

        # Área de quantidade e botões de incremento/decremento
        quantity_frame = tk.Frame(product_frame)
        quantity_frame.grid(row=2, column=0, columnspan=3, pady=5)
        tk.Label(quantity_frame, text="Quantidade:", font=(FONT_NAME, 10)).pack(side="left", padx=5)
        self.entry_quantity = tk.Entry(quantity_frame, width=5, font=(FONT_NAME, 10))
        self.entry_quantity.insert(0, "1")
        self.entry_quantity.pack(side="left", padx=5)
        tk.Button(quantity_frame, text="+", command=self.increment_quantity, font=(FONT_NAME, 10))\
            .pack(side="left", padx=3)
        tk.Button(quantity_frame, text="-", command=self.decrement_quantity, font=(FONT_NAME, 10))\
            .pack(side="left", padx=3)
        self.entry_quantity.bind("<KeyRelease>", self.update_item_total)
        tk.Label(quantity_frame, text="Valor Item:", font=(FONT_NAME, 10)).pack(side="left", padx=5)
        self.label_item_total = tk.Label(quantity_frame, text="0.00", font=(FONT_NAME, 10))
        self.label_item_total.pack(side="left", padx=5)
        tk.Button(product_frame, text="Adicionar Item", command=self.add_item, font=(FONT_NAME, 10))\
            .grid(row=3, column=0, columnspan=3, pady=5)
        tk.Button(product_frame, text="Excluir Item Selecionado", command=self.remove_item, font=(FONT_NAME, 10))\
            .grid(row=4, column=0, columnspan=3, pady=5)

        # Área de itens da venda (lado direito)
        sale_frame = tk.LabelFrame(middle_frame, text="Itens da Venda", font=(FONT_NAME, 10))
        sale_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        sale_frame.rowconfigure(0, weight=1)
        sale_frame.columnconfigure(0, weight=1)
        self.sale_tree = ttk.Treeview(sale_frame, columns=("Produto", "Quantidade", "Valor Item"), show="headings")
        self.sale_tree.heading("Produto", text="Produto")
        self.sale_tree.heading("Quantidade", text="Quantidade")
        self.sale_tree.heading("Valor Item", text="Valor Item")
        self.sale_tree.column("Produto", width=150)
        self.sale_tree.column("Quantidade", width=80)
        self.sale_tree.column("Valor Item", width=80)
        self.sale_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # --- Linha 2: Total e Forma de Pagamento ---
        bottom_frame = tk.Frame(self.win)
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        bottom_frame.columnconfigure(0, weight=1)
        tk.Label(bottom_frame, text="Total Venda:", font=(FONT_NAME, 10)).grid(row=0, column=0, sticky="w", padx=5)
        self.label_total = tk.Label(bottom_frame, text="0.00", font=(FONT_NAME, 10))
        self.label_total.grid(row=0, column=1, sticky="w", padx=5)
        tk.Label(bottom_frame, text="Forma de Pagamento:", font=(FONT_NAME, 10)).grid(row=0, column=2, sticky="w", padx=5)
        self.payment_combobox = ttk.Combobox(bottom_frame, 
                                             values=["credito", "debito", "pix", "dinheiro", "a prazo"], 
                                             font=(FONT_NAME, 10))
        self.payment_combobox.grid(row=0, column=3, sticky="w", padx=5)
        
        # Botão de Finalizar Venda, fixado no canto inferior direito
        finalize_frame = tk.Frame(self.win)
        finalize_frame.grid(row=3, column=0, sticky="se", padx=10, pady=10)
        tk.Button(finalize_frame, text="Finalizar Venda", command=self.confirm_sale, font=(FONT_NAME, 10))\
            .pack(anchor="e")
        
    def selecionar_cliente(self):
        SelecionarClienteWindow(self.client_selected, pos_x=self.win.winfo_x()+30, pos_y=self.win.winfo_y()+30)

    def client_selected(self, client_data):
        self.selected_client = client_data  # Dados: (id, nome, cpf, email)
        self.label_client.config(text=f"{client_data[0]} - {client_data[1]}")

    def increment_quantity(self):
        try:
            qty = int(self.entry_quantity.get())
        except:
            qty = 1
        qty += 1
        self.entry_quantity.delete(0, tk.END)
        self.entry_quantity.insert(0, str(qty))
        self.update_item_total(None)

    def decrement_quantity(self):
        try:
            qty = int(self.entry_quantity.get())
        except:
            qty = 1
        if qty > 1:
            qty -= 1
        self.entry_quantity.delete(0, tk.END)
        self.entry_quantity.insert(0, str(qty))
        self.update_item_total(None)

    def search_product(self):
        termo = self.entry_product.get().strip()
        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            if termo:
                cur.execute("""
                    SELECT id, nome, preco, estoque FROM produtos
                    WHERE nome ILIKE %s
                    ORDER BY id
                """, (f"{termo}%",))
            else:
                cur.execute("SELECT id, nome, preco, estoque FROM produtos ORDER BY id")
            produtos = cur.fetchall()
            cur.close()
            for item in self.prod_tree.get_children():
                self.prod_tree.delete(item)
            for prod in produtos:
                self.prod_tree.insert("", tk.END, values=prod)
        except Exception as e:
            logging.error("Erro na pesquisa de produtos: %s", e)
        finally:
            conn.close()

    def on_product_select(self, event):
        selected = self.prod_tree.focus()
        if selected:
            values = self.prod_tree.item(selected, "values")
            self.selected_product = {
                "id": values[0],
                "nome": values[1],
                "preco": float(values[2]),
                "estoque": int(values[3])
            }
            self.update_item_total(None)

    def update_item_total(self, event):
        if hasattr(self, 'selected_product'):
            try:
                qty = int(self.entry_quantity.get())
            except:
                qty = 1
            total = self.selected_product["preco"] * qty
            self.label_item_total.config(text=f"{total:.2f}")

    def add_item(self):
        if not hasattr(self, 'selected_product'):
            messagebox.showerror("Erro", "Selecione um produto!")
            return
        try:
            qty = int(self.entry_quantity.get())
        except:
            messagebox.showerror("Erro", "Quantidade inválida!")
            return
        if qty <= 0 or qty > self.selected_product["estoque"]:
            messagebox.showerror("Erro", "Quantidade inválida ou maior que o estoque!")
            return
        total = self.selected_product["preco"] * qty
        item = {
            "produto_id": self.selected_product["id"],
            "produto_nome": self.selected_product["nome"],
            "quantidade": qty,
            "valor_item": total
        }
        self.sale_items.append(item)
        self.sale_tree.insert("", tk.END, values=(item["produto_nome"], qty, f"{total:.2f}"))
        self.update_sale_total()
        self.entry_product.delete(0, tk.END)
        self.entry_quantity.delete(0, tk.END)
        self.entry_quantity.insert(0, "1")
        self.label_item_total.config(text="0.00")

    def remove_item(self):
        selected_items = self.sale_tree.selection()
        if not selected_items:
            messagebox.showerror("Erro", "Selecione um item para excluir!")
            return
        for sid in selected_items:
            values = self.sale_tree.item(sid, "values")
            prod_nome = values[0]
            qty = int(values[1])
            valor = float(values[2])
            for i, item in enumerate(self.sale_items):
                if item["produto_nome"] == prod_nome and item["quantidade"] == qty and abs(item["valor_item"] - valor) < 0.01:
                    del self.sale_items[i]
                    break
            self.sale_tree.delete(sid)
        self.update_sale_total()

    def update_sale_total(self):
        total = sum(item["valor_item"] for item in self.sale_items)
        self.label_total.config(text=f"{total:.2f}")

    def confirm_sale(self):
        if not self.selected_client:
            messagebox.showerror("Erro", "Selecione um cliente para a venda!")
            return
        try:
            client_id = int(self.selected_client[0])
        except:
            messagebox.showerror("Erro", "Cliente inválido!")
            return
        forma = self.payment_combobox.get().strip()
        if forma not in ["credito", "debito", "pix", "dinheiro", "a prazo"]:
            messagebox.showerror("Erro", "Selecione uma forma de pagamento válida!")
            return
        if not self.sale_items:
            messagebox.showerror("Erro", "Adicione itens à venda!")
            return
        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            for item in self.sale_items:
                cur.execute("""
                    INSERT INTO vendas (cliente_id, produto_id, quantidade, valor_total, forma_pagamento)
                    VALUES (%s, %s, %s, %s, %s)
                """, (client_id, item["produto_id"], item["quantidade"], item["valor_item"], forma))
                cur.execute("""
                    UPDATE produtos SET estoque = estoque - %s WHERE id = %s
                """, (item["quantidade"], item["produto_id"]))
            conn.commit()
            cur.close()
            messagebox.showinfo("Sucesso", "Venda realizada com sucesso!")
            self.win.destroy()
            VendasWindow.instance = None  # Limpa a referência para permitir nova instância
            # Se houver referência global da dashboard, atualize-a
            try:
                from globals import current_dashboard
                if current_dashboard is not None:
                    current_dashboard.refresh_data()
            except ImportError:
                pass
        except Exception as e:
            logging.error("Erro ao confirmar venda: %s", e)
            messagebox.showerror("Erro", "Erro interno ao confirmar venda.")
        finally:
            conn.close()

    def selecionar_cliente(self):
        SelecionarClienteWindow(self.client_selected, pos_x=self.win.winfo_x()+30, pos_y=self.win.winfo_y()+30)

    def client_selected(self, client_data):
        self.selected_client = client_data
        self.label_client.config(text=f"{client_data[0]} - {client_data[1]}")
