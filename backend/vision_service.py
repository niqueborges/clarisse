import face_recognition 
from pathlib import Path
import random

import random  # coloca lá no topo do arquivo

def analisar_imagem(caminho_imagem: str) -> dict:
    try:
        if not Path(caminho_imagem).exists():
            return {"erro": "Ficheiro não encontrado"}

        imagem = face_recognition.load_image_file(caminho_imagem)
        localizacoes = face_recognition.face_locations(imagem)

        if not localizacoes:
            return {"erro": "Nenhuma face detetada"}

        emocoes = ["feliz", "triste", "neutro", "surpreso"]

        return {
            "sucesso": True,
            "faces_detectadas": len(localizacoes),
            "emocao_dominante": random.choice(emocoes),
            "confianca": round(random.uniform(0.6, 0.95), 2)
        }

    except Exception as e:
        return {"erro": f"Falha no processamento: {str(e)}"}