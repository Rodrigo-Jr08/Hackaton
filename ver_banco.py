import sqlite3

conn = sqlite3.connect('hackathon_sigaa.db')
cursor = conn.cursor()

cursor.execute("SELECT matricula, nome FROM alunos")
registos = cursor.fetchall()

print(f"Total de alunos na base de dados: {len(registos)}\n")
for matricula, nome in registos:
    print(f"Matrícula: {matricula} | Nome: {nome}")

conn.close()