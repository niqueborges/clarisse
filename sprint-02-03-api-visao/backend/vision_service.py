# vision_service.py
# Serviço de análise de emoções usando face_recognition + FER
# Substitui Amazon Rekognition

import face_recognition
from fer import FER
import cv2
import json
from pathlib import Path

# Inicializa o detector de emoções
detector_emocao = FER(mtcnn=True)

def analisar_imagem(caminho_imagem: str) -> dict:
    """
    Analisa uma imagem e retorna as emoções detectadas.
    
    Args:
        caminho_imagem: Caminho para o arquivo de imagem
        
    Returns:
        dict com resultado da análise ou erro
    """
    try:
        # Verifica se o arquivo existe
        if not Path(caminho_imagem).exists():
            return {"erro": "Arquivo não encontrado"}
        
        # Carrega a imagem
        imagem = face_recognition.load_image_file(caminho_imagem)
        
        # Detecta faces na imagem
        localizacoes_faces = face_recognition.face_locations(imagem)
        
        if len(localizacoes_faces) == 0:
            return {"erro": "Nenhuma face detectada na imagem"}
        
        # Analisa emoções com FER
        imagem_cv = cv2.imread(caminho_imagem)
        resultado_emocoes = detector_emocao.detect_emotions(imagem_cv)
        
        if not resultado_emocoes:
            return {"erro": "Não foi possível analisar as emoções"}
        
        # Pega a primeira face detectada
        emocoes = resultado_emocoes[0]['emotions']
        
        # Encontra a emoção dominante
        emocao_dominante = max(emocoes, key=emocoes.get)
        confianca = emocoes[emocao_dominante] * 100  # Converte pra porcentagem
        
        # Traduz emoções para português
        traducao_emocoes = {
            'angry': 'raiva',
            'disgust': 'nojo',
            'fear': 'medo',
            'happy': 'feliz',
            'sad': 'triste',
            'surprise': 'surpresa',
            'neutral': 'neutro'
        }
        
        emocao_pt = traducao_emocoes.get(emocao_dominante, emocao_dominante)
        
        # Monta o resultado
        resultado = {
            "sucesso": True,
            "faces_detectadas": len(localizacoes_faces),
            "emocao_dominante": emocao_pt,
            "emocao_original": emocao_dominante,
            "confianca": round(confianca, 2),
            "todas_emocoes": {
                traducao_emocoes[k]: round(v * 100, 2) 
                for k, v in emocoes.items()
            },
            "resultado_completo": json.dumps(resultado_emocoes, ensure_ascii=False)
        }
        
        return resultado
        
    except Exception as e:
        return {
            "erro": f"Erro ao processar imagem: {str(e)}"
        }


def validar_imagem(caminho: str) -> tuple[bool, str]:
    """
    Valida se o arquivo é uma imagem válida.
    
    Returns:
        (bool, mensagem): True se válido, False se inválido
    """
    extensoes_validas = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    caminho_obj = Path(caminho)
    
    if not caminho_obj.exists():
        return False, "Arquivo não encontrado"
    
    if caminho_obj.suffix.lower() not in extensoes_validas:
        return False, f"Formato inválido. Use: {', '.join(extensoes_validas)}"
    
    # Tenta abrir com OpenCV
    try:
        img = cv2.imread(str(caminho))
        if img is None:
            return False, "Arquivo corrompido ou não é uma imagem"
        return True, "Imagem válida"
    except Exception as e:
        return False, f"Erro ao ler imagem: {str(e)}"