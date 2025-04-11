import tkinter as tk
from database import create_tables
from views.login import LoginWindow

def main():
    create_tables()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
