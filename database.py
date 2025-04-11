# database.py
import psycopg2
import logging
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

def get_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        logging.error("Erro ao conectar ao banco de dados: %s", e)
        return None

def create_tables():
    conn = get_connection()
    if conn is None:
        return
    try:
        cur = conn.cursor()
        # Tabela de usuários
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(200) NOT NULL
            )
        """)
        # Tabela de clientes
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                cpf VARCHAR(20),
                data_nasc DATE,
                email VARCHAR(100),
                telefone VARCHAR(20),
                saldo NUMERIC DEFAULT 0
            )
        """)
        # Tabela de produtos
        cur.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT,
                preco NUMERIC,
                estoque INTEGER
            )
        """)
        # Tabela de vendas
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id SERIAL PRIMARY KEY,
                cliente_id INTEGER REFERENCES clientes(id),
                produto_id INTEGER REFERENCES produtos(id),
                quantidade INTEGER,
                valor_total NUMERIC,
                forma_pagamento VARCHAR(20),
                data TIMESTAMP DEFAULT NOW()
            )
        """)
        # Tabela de ordens de serviço
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ordens_servico (
                os SERIAL PRIMARY KEY,
                id_cliente INTEGER REFERENCES clientes(id),
                equipamento VARCHAR(200),
                numero_serie VARCHAR(100),
                data_entrada TIMESTAMP DEFAULT NOW(),
                usuario VARCHAR(50),
                descricao TEXT,
                observacoes TEXT,
                situacao VARCHAR(20) CHECK (situacao IN ('aberto', 'finalizado', 'recusado'))
            )
        """)
        conn.commit()
        # Insere usuário padrão "admin" (senha "123456") se não existir
        cur.execute("SELECT * FROM users WHERE username = %s", ('admin',))
        if not cur.fetchone():
            from security import hash_password
            senha_hash = hash_password("123456")
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ('admin', senha_hash))
            conn.commit()
        cur.close()
    except Exception as e:
        logging.error("Erro ao criar as tabelas: %s", e)
    finally:
        conn.close()
