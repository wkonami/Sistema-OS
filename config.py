import os
import configparser
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do arquivo .env

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

# Dados de conexão (do .env)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'clientesdb')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# Configurações de janela e do programa
LOGIN_WIDTH = config.getint('window', 'login_width', fallback=300)
LOGIN_HEIGHT = config.getint('window', 'login_height', fallback=150)
MAIN_WIDTH = config.getint('window', 'main_width', fallback=650)
MAIN_HEIGHT = config.getint('window', 'main_height', fallback=550)
FONT_NAME = config.get('window', 'font', fallback='Arial')
ICON_PATH = config.get('personalization', 'icon_path', fallback='icone.png')
PROG_NAME = config.get('program', 'name', fallback='Sistema de Clientes')
PROG_VERSION = config.get('program', 'version', fallback='1.0')

# Configurações de redes sociais (com Twitter apontando para GitHub)
SOCIAL_ICONS = {
    "facebook": config.get('social', 'facebook_icon', fallback='facebook.png'),
    "twitter": config.get('social', 'twitter_icon', fallback='twitter.png'),
    "instagram": config.get('social', 'instagram_icon', fallback='instagram.png')
}
SOCIAL_LINKS = {
    "facebook": config.get('social', 'facebook_link', fallback='https://facebook.com/suapagina'),
    "twitter": config.get('social', 'twitter_link', fallback='https://github.com/seuusuario'),
    "instagram": config.get('social', 'instagram_link', fallback='https://instagram.com/suaperfil')
}