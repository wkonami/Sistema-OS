import tkinter as tk
from tkinter import messagebox
import logging
from database import get_connection
from security import check_password
from config import FONT_NAME, ICON_PATH, LOGIN_WIDTH, LOGIN_HEIGHT
from views.dashboard import DashboardWindow

class LoginWindow:
    def __init__(self, master):
        self.master = master
        master.title("Login")
        master.geometry(f"{LOGIN_WIDTH}x{LOGIN_HEIGHT}")
        master.resizable(False, False)
        try:
            self.icon = tk.PhotoImage(file=ICON_PATH)
            master.iconphoto(True, self.icon)
        except Exception as e:
            logging.error("Ícone não carregado: %s", e)
        tk.Label(master, text="Usuário:", font=(FONT_NAME, 10)).pack(pady=5)
        self.entry_username = tk.Entry(master, font=(FONT_NAME, 10))
        self.entry_username.pack()
        self.entry_username.focus_set()
        tk.Label(master, text="Senha:", font=(FONT_NAME, 10)).pack(pady=5)
        self.entry_password = tk.Entry(master, show="*", font=(FONT_NAME, 10))
        self.entry_password.pack()
        tk.Button(master, text="Entrar", command=self.login, font=(FONT_NAME, 10)).pack(pady=10)

        # Associa o Enter ao método de login
        self.entry_password.bind("<Return>", lambda event: self.login())
        # Também permite pressionar Enter no campo de usuário
        self.entry_username.bind("<Return>", lambda event: self.entry_password.focus())

    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        if not username or not password:
            messagebox.showerror("Erro", "Preencha usuário e senha.")
            return
        conn = get_connection()
        if conn is None:
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE username=%s", (username,))
            result = cur.fetchone()
            if result and check_password(password, result[0]):
                self.master.destroy()
                DashboardWindow(username)
            else:
                messagebox.showerror("Erro", "Usuário ou senha inválidos!")
            cur.close()
        except Exception as e:
            logging.error("Erro na autenticação: %s", e)
            messagebox.showerror("Erro", "Erro interno durante a autenticação.")
        finally:
            conn.close()
