# 🌿 Clarisse

> *"Escrever é uma forma de não ter medo."* — Clarice Lispector

**Clarisse** é um projeto de IA acessível, construído inteiramente com ferramentas
gratuitas e de código aberto — sem depender de nenhum serviço de nuvem pago.

---

## 🧭 Origem e propósito

Este projeto é uma reimplementação independente dos trabalhos desenvolvidos durante
o **Programa de Bolsas Compass UOL 2024** (turma junho/2024), disponíveis em:

🔗 [CompassUol_PB_2024](https://github.com/niqueborges/CompassUol_PB_2024)

O objetivo original era demonstrar o uso de serviços AWS (Rekognition, Polly,
Transcribe, Lex, S3, DynamoDB). **Clarisse** parte dessa base e mostra que
as mesmas funcionalidades podem ser alcançadas com ferramentas abertas,
rodando localmente ou em qualquer ambiente — sem cartão de crédito, sem lock-in.

---

## 🔄 AWS → Open Source: o mapeamento

| Serviço AWS | Substituto utilizado |
|---|---|
| Amazon Rekognition | DeepFace / OpenCV |
| AWS Polly | gTTS / Coqui TTS |
| Amazon Transcribe | OpenAI Whisper (local) |
| Amazon Lex | Rasa / LLM local |
| Amazon S3 | Sistema de arquivos local |
| DynamoDB | SQLite |
| CloudWatch | Logging nativo Python |
| Lambda / Serverless | FastAPI / Flask |

---

## 📁 Estrutura do projeto

clarisse/
├── sprint-01-fundamentos/
├── sprint-02-03-api-visao/
├── sprint-04-05-chatbot/
├── sprint-06-07-voz/
├── sprint-08-emocoes/
└── sprint-09-10-projeto-final/

Cada módulo tem seu próprio `README.md` explicando o que foi aprendido,
o que foi substituído e como rodar.

---

## 🛠️ Tecnologias

Python · FastAPI · OpenCV · DeepFace · Whisper · gTTS · SQLite · HTML · CSS · JavaScript

---

## 📜 Licença

Projeto educacional e de portfólio, de autoria de **Monique da Silva Borges**.
Baseado em trabalho coletivo do Programa de Bolsas Compass UOL 2024.