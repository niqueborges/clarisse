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

## ✨ Funcionalidades Atuais

O projeto evoluiu para uma aplicação Full-Stack funcional, contendo:
- **Gestão de Clientes:** Cadastro, listagem e exclusão de clientes (CRUD) armazenados em banco de dados relacional.
- **Análise de Imagem (IA):** Upload de fotos com integração ao serviço de visão computacional para detecção facial e análise de emoções.
- **Histórico de IA:** Registro das análises de cada cliente com métricas de confiança e emoções dominantes.
- **Ferramenta de IA Auxiliar:** Um utilitário customizado (`ai_tool`) para gerar contexto de código, facilitando a interação com LLMs para a manutenção do projeto.

---

## 🔄 AWS → Open Source: O Mapeamento

| Serviço AWS | Substituto utilizado |
|---|---|
| Amazon Rekognition | `face_recognition` (Python) |
| Amazon S3 | Armazenamento de arquivos local (`/uploads`) |
| DynamoDB | SQLite + SQLAlchemy |
| Lambda / Serverless | FastAPI (Backend) |
| Amazon Lex / Transcribe / Polly | *(Planejado para integrações futuras)* |

---

## 📁 Estrutura do projeto

```text
clarisse/
├── backend/           # API em FastAPI, Banco de dados (SQLite) e serviços de IA
├── frontend/          # Interface do usuário (HTML, CSS, Vanilla JS)
└── ai_tool/           # Ferramenta de construção de contexto para IA auxiliar
```

---

## 🛠️ Tecnologias

**Backend:** Python · FastAPI · SQLAlchemy · SQLite · `face_recognition`  
**Frontend:** HTML5 · CSS3 · JavaScript (Vanilla)  
**Ferramentas:** Uvicorn · Pydantic

---

## 📜 Licença

Projeto educacional e de portfólio, de autoria de **Monique da Silva Borges**.
Baseado em trabalho coletivo do Programa de Bolsas Compass UOL 2024.