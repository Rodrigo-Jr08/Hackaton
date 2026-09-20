import sqlite3

def visualizar_banco():
    conn = sqlite3.connect('hackathon_sigaa.db')
    cursor = conn.cursor()

    # Busca todas as tabelas existentes no banco
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = cursor.fetchall()

    if not tabelas:
        print("Nenhuma tabela encontrada no banco de dados.")
        return

    print("========================================")
    print("      INSPEÇÃO DO BANCO DE DADOS        ")
    print("========================================")

    for (nome_tabela,) in tabelas:
        if nome_tabela == 'sqlite_sequence':
            continue

        print(f"\n>>> TABELA: {nome_tabela.upper()}")

        # Pega os nomes das colunas
        cursor.execute(f"PRAGMA table_info({nome_tabela})")
        colunas = [coluna[1] for coluna in cursor.fetchall()]
        print("Colunas:", " | ".join(colunas))
        print("-" * 50)

        # Pega as linhas/registros
        cursor.execute(f"SELECT * FROM {nome_tabela}")
        linhas = cursor.fetchall()

        if not linhas:
            print("(Tabela vazia)")
        else:
            for linha in linhas:
                linha_formatada = []
                for valor in linha:
                    val_str = str(valor)
                    # Encurta o embedding para não poluir a tela
                    if len(val_str) > 40:
                        val_str = val_str[:20] + "... [VETOR]"
                    linha_formatada.append(val_str)
                print(" | ".join(linha_formatada))

    conn.close()

if __name__ == "__main__":
    visualizar_banco()