import cv2
import sqlite3
import json
import time
from datetime import datetime
from deepface import DeepFace
from scipy.spatial.distance import cosine

# ================= CONFIGURAÇÕES =================
TIPO_CAMERA = "ENTRADA"  # Quando for rodar a câmera de saída, mude para "SAIDA"
CAMERA_ID = 0            # 0 é a webcam padrão do notebook
LIMIAR_DISTANCIA = 0.40  # Para o FaceNet, distância cosseno < 0.40 indica a mesma pessoa
PULAR_FRAMES = 10        # Analisa 1 rosto a cada 10 frames (evita travar o PC)
# =================================================

def carregar_banco_para_ram():
    conn = sqlite3.connect('hackathon_sigaa.db')
    cursor = conn.cursor()
    
    # Cria a tabela de logs se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs_presenca (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT,
            nome TEXT,
            tipo TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()

    # Carrega os alunos matriculados
    cursor.execute("SELECT matricula, nome, embedding FROM alunos")
    alunos = cursor.fetchall()
    
    banco_em_memoria = []
    for matricula, nome, embedding_str in alunos:
        banco_em_memoria.append({
            "matricula": matricula,
            "nome": nome,
            "embedding": json.loads(embedding_str)
        })
        
    return conn, banco_em_memoria

def registrar_log(conn, matricula, nome):
    cursor = conn.cursor()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO logs_presenca (matricula, nome, tipo, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (matricula, nome, TIPO_CAMERA, agora))
    conn.commit()
    print(f"[{agora}] {TIPO_CAMERA} registrada: {nome}")

def main():
    conn, banco_alunos = carregar_banco_para_ram()
    print(f"Banco carregado com {len(banco_alunos)} alunos.")
    
    cap = cv2.VideoCapture(CAMERA_ID)
    contador_frames = 0
    
    # Dicionário para evitar "spam" de logs se a pessoa ficar parada na frente da câmera
    ultimo_registro = {}

    print(f"Iniciando Câmera de {TIPO_CAMERA}...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        contador_frames += 1
        
        # Só roda a IA pesada a cada X frames
        if contador_frames % PULAR_FRAMES == 0:
            try:
                # enforce_detection=False é crucial: se não tiver rosto no frame, ele não crasha
                representacoes = DeepFace.represent(frame, model_name="Facenet", detector_backend="mtcnn", enforce_detection=False)
                
                if len(representacoes) > 0 and representacoes[0].get("face_confidence", 0) > 0:
                    vetor_camera = representacoes[0]["embedding"]
                    
                    melhor_match = None
                    menor_distancia = 1.0 # Distância máxima inicial
                    
                    # Compara quem está na câmera com todo o banco de alunos
                    for aluno in banco_alunos:
                        dist = cosine(vetor_camera, aluno["embedding"])
                        if dist < menor_distancia:
                            menor_distancia = dist
                            melhor_match = aluno

                    # Se a distância for menor que o limiar, é a pessoa!
                    if menor_distancia < LIMIAR_DISTANCIA:
                        nome_detectado = melhor_match["nome"]
                        matricula_detectada = melhor_match["matricula"]
                        
                        # Regra de Cooldown: Só registra no banco de novo após 10 segundos
                        tempo_atual = time.time()
                        tempo_ultimo = ultimo_registro.get(matricula_detectada, 0)
                        
                        if (tempo_atual - tempo_ultimo) > 10:
                            registrar_log(conn, matricula_detectada, nome_detectado)
                            ultimo_registro[matricula_detectada] = tempo_atual

                        # Desenha na tela para o Show dos jurados!
                        cv2.putText(frame, f"{nome_detectado} ({TIPO_CAMERA})", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
            except Exception as e:
                pass # Ignora erros de frame sem rosto perfeitamente visível

        cv2.imshow(f"Hackathon - Câmera {TIPO_CAMERA}", frame)
        
        # Aperte 'q' para fechar a câmera
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    conn.close()

if __name__ == "__main__":
    main()