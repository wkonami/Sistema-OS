import tkinter as tk
from tkinter import messagebox
import psycopg2

# Configurações do banco de dados
DB_HOST = '201.24.173.85'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = 'qaaz123'

def get_connection():
    try:
        conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        return conn
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados:\n{e}")
        return None

def create_tables():
    conn = get_connection()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        # Cria tabela de usuários
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(50) NOT NULL
            )
        """)
        # Cria tabela de clientes
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                telefone VARCHAR(20),
                data_nascimento DATE,
                cep VARCHAR(10),
                cidade VARCHAR(50),
                estado CHAR(2),
                cpf VARCHAR(14) UNIQUE,
                cnpj VARCHAR(18) UNIQUE
            );
        """)
        conn.commit()
        # Insere usuário padrão se não existir
        cur.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cur.fetchone():
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ("admin", "admin"))
            conn.commit()
        cur.close()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao criar as tabelas:\n{e}")
    finally:
        conn.close()

class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.title("Login")
        master.geometry("300x150")
        master.resizable(False, False)
        
        tk.Label(master, text="Usuário:").pack(pady=5)
        self.entry_username = tk.Entry(master)
        self.entry_username.pack()

        tk.Label(master, text="Senha:").pack(pady=5)
        self.entry_password = tk.Entry(master, show="*")
        self.entry_password.pack()

        tk.Button(master, text="Entrar", command=self.login).pack(pady=10)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        
        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cur.fetchone()
            if user:
                messagebox.showinfo("Sucesso", "Login efetuado com sucesso!")
                self.master.destroy()
                MainWindow()
            else:
                messagebox.showerror("Erro", "Usuário ou senha inválidos!")
            cur.close()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na autenticação:\n{e}")
        finally:
            conn.close()

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cadastro de Clientes")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        tk.Label(self.root, text="Cadastro de Clientes", font=("Arial", 14)).pack(pady=10)
        
        # Nome
        tk.Label(self.root, text="Nome:").pack(pady=5)
        self.entry_nome = tk.Entry(self.root, width=50)
        self.entry_nome.pack()

        # Telefone
        tk.Label(self.root, text="Telefone:").pack(pady=5)
        self.entry_telefone = tk.Entry(self.root, width=50)
        self.entry_telefone.pack()
        
        # Data_nascimento
        tk.Label(self.root, text="Data_nascimento:").pack(pady=5)
        self.entry_data_nascimento = tk.Entry(self.root, width=50)
        self.entry_data_nascimento.pack()
        
        # Cpf
        tk.Label(self.root, text="Cpf:").pack(pady=5)
        self.entry_cpf = tk.Entry(self.root, width=50)
        self.entry_cpf.pack()

        # Email
        tk.Label(self.root, text="Email:").pack(pady=5)
        self.entry_email = tk.Entry(self.root, width=50)
        self.entry_email.pack()

        tk.Button(self.root, text="Cadastrar Cliente", command=self.cadastrar_cliente).pack(pady=15)

        self.root.mainloop()

    def cadastrar_cliente(self):
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        telefone = self.entry_telefone.get().strip()
        cpf = self.entry_cpf.get().strip()
        data_nascimento = self.entry_data_nascimento.get().strip()

        if not nome:
            messagebox.showerror("Erro", "O campo nome é obrigatório!")
            return

        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO clientes (nome, email, telefone, cpf, data_nascimento) VALUES (%s, %s, %s, %s, %s)", (nome, email, telefone, cpf, data_nascimento))
            conn.commit()
            cur.close()
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
            # Limpa os campos
            self.entry_nome.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            self.entry_telefone.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar o cliente:\n{e}")
        finally:
            conn.close()

if __name__ == "__main__":
    create_tables()
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()
