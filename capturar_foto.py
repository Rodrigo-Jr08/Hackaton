import cv2
import os

def capturar_foto_matricula():
    pasta = 'fotos_matricula'
    if not os.path.exists(pasta):
        os.makedirs(pasta)

    print("=== CADASTRO RÁPIDO DE FOTO ===")
    matricula = input("Digite a Matrícula: ").strip()
    nome = input("Digite o Nome (sem espaços compostos): ").strip()

    if not matricula or not nome:
        print("Matrícula e nome são obrigatórios!")
        return

    cap = cv2.VideoCapture(0)
    print("\n[Instruções]: Olhe para a câmera e aperte ESPAÇO para tirar a foto (ou 'Q' para cancelar).")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Desenha um guia central na tela
        h, w, _ = frame.shape
        cv2.rectangle(frame, (int(w*0.3), int(h*0.15)), (int(w*0.7), int(h*0.85)), (0, 255, 0), 2)
        cv2.putText(frame, f"Posicione o rosto de {nome}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Captura de Foto de Matricula", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Tecla Espaço tira a foto
            caminho_arquivo = os.path.join(pasta, f"{matricula}_{nome}.jpg")
            
            # Recorta ou salva o frame limpo (sem os retângulos verdes desenhados)
            cap.grab() # limpa o buffer
            _, frame_limpo = cap.read()
            cv2.imwrite(caminho_arquivo, frame_limpo)
            
            print(f"Foto salva com sucesso em: {caminho_arquivo}")
            break
        elif key == ord('q'):
            print("Captura cancelada.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capturar_foto_matricula()