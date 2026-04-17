# vision_service.py
# Serviço de análise de imagens - versão simplificada
# Detecta faces, placeholder para emoções (expandir futuramente)

import face_recognition
import cv2
import json
from pathlib import Path

def analisar_imagem(caminho_imagem: str) -> dict:
    """
    Analisa uma imagem e detecta faces.
    Placeholder para análise de emoções (a ser implementado com modelo estável).
    """
    try:
        if not Path(caminho_imagem).exists():
            return {"erro": "Arquivo não encontrado"}
        
        # Carrega a imagem
        imagem = face_recognition.load_image_file(caminho_imagem)
        
        # Detecta faces
        localizacoes_faces = face_recognition.face_locations(imagem)
        
        if len(localizacoes_faces) == 0:
            return {"erro": "Nenhuma face detectada na imagem"}
        
        # Placeholder: análise de emoção será implementada com biblioteca estável
        # Por enquanto retorna "neutro" para manter a estrutura funcionando
        resultado = {
            "sucesso": True,
            "faces_detectadas": len(localizacoes_faces),
            "emocao_dominante": "neutro",
            "emocao_original": "neutral",
            "confianca": 85.0,
            "todas_emocoes": {
                "neutro": 85.0,
                "feliz": 5.0,
                "triste": 3.0,
                "surpresa": 2.0,
                "raiva": 2.0,
                "medo": 2.0,
                "nojo": 1.0
            },
            "resultado_completo": json.dumps({
                "faces": len(localizacoes_faces),
                "nota": "Análise de emoções será implementada em versão futura"
            })
        }
        
        return resultado
        
    except Exception as e:
        return {"erro": f"Erro ao processar imagem: {str(e)}"}


def validar_imagem(caminho: str) -> tuple[bool, str]:
    """Valida se o arquivo é uma imagem válida."""
    extensoes_validas = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    caminho_obj = Path(caminho)
    
    if not caminho_obj.exists():
        return False, "Arquivo não encontrado"
    
    if caminho_obj.suffix.lower() not in extensoes_validas:
        return False, f"Formato inválido. Use: {', '.join(extensoes_validas)}"
    
    try:
        img = cv2.imread(str(caminho))
        if img is None:
            return False, "Arquivo corrompido ou não é uma imagem"
        return True, "Imagem válida"
    except Exception as e:
        return False, f"Erro ao ler imagem: {str(e)}"