#!/usr/bin/env python3

import time
import sqlite3
import ESL
import os
import sys

# Configurações do ESL - ajuste conforme o seu event_socket.conf.xml no FreeSWITCH
ESL_HOST = "127.0.0.1"
ESL_PORT = "8021"
ESL_PASSWORD = "ClueCon"  # Altere se necessário

# Caminho absoluto para o banco SQLite
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logins.db")

def init_db():
    """Cria a tabela no SQLite se não existir."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS freeswitch_logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT,
            user TEXT,
            domain TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_login(event_name, user, domain, timestamp):
    """Insere um registro de login no banco."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO freeswitch_logins (event_name, user, domain, timestamp)
        VALUES (?, ?, ?, ?)
    """, (event_name, user, domain, timestamp))
    conn.commit()
    conn.close()

def handle_event(event):
    """Manipula cada evento recebido do FreeSWITCH."""
    event_name = event.getHeader("Event-Name")
    user = event.getHeader("variable_sip_auth_username") or event.getHeader("from") or "desconhecido"
    domain = event.getHeader("variable_sip_auth_realm") or "desconhecido"
    timestamp = event.getHeader("Event-Date-Local") or time.strftime('%Y-%m-%d %H:%M:%S')

    # Ajuste aqui se quiser capturar outros eventos além de 'CHANNEL_AUTHENTICATE' e 'REGISTER'
    if event_name in ("CHANNEL_AUTHENTICATE", "REGISTER"):
        salvar_login(event_name, user, domain, timestamp)

def main():
    # Inicializa o banco
    init_db()

    # Conecta ao Event Socket do FreeSWITCH
    con = ESL.ESLconnection(ESL_HOST, ESL_PORT, ESL_PASSWORD)
    if not con.connected():
        print(f"[ERRO] Não foi possível conectar ao ESL em {ESL_HOST}:{ESL_PORT} com a senha '{ESL_PASSWORD}'")
        sys.exit(1)

    # Inscreve-se em todos os eventos, ou troque "ALL" por algo mais específico se quiser reduzir tráfego
    con.events("plain", "ALL")

    print("[INFO] Conexão ESL estabelecida. Escutando eventos...")

    # Loop para receber eventos indefinidamente
    while True:
        e = con.recvEvent()
        if e:
            handle_event(e)
        else:
            time.sleep(0.1)

if __name__ == "__main__":
    main()
