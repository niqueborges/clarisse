# 🌿 Sprint 01 — Fundamentos e Cadastro de Clientes

## ✅ Status: concluído

---

## 📜 Sobre este módulo

O projeto original desta sprint consistia em um sistema de cadastro simples
usando **HTML, CSS, JavaScript e localStorage** — os dados viviam apenas
no navegador e não se comunicavam com nenhum outro módulo.

No **Clarisse**, essa sprint foi reimaginada como a **base de dados central**
do projeto inteiro. O cliente cadastrado aqui será o mesmo analisado nas
sprints seguintes — pela câmera, pelo chatbot, pela voz.

---

## 🔄 O que foi substituído e por quê

| Original | Clarisse | Motivo |
|---|---|---|
| `localStorage` | SQLite | Persistência real, acessível por todos os módulos |
| Lógica no navegador | API REST com FastAPI | Separação de responsabilidades |
| Sem validação de dados | Pydantic + SQLAlchemy | Dados confiáveis e tipados |
| Sem edição de registros | Rota `PUT /clientes/{id}` | CRUD completo |
| AWS Lambda / Serverless | FastAPI local | Sem custo, sem lock-in |
| AWS DynamoDB | SQLite | Banco leve, portátil, zero configuração |

---

## 🏗️ Arquitetura

sprint-01-fundamentos/
├── backend/
│   ├── main.py          ← API REST (FastAPI)
│   ├── models.py        ← Modelo de dados (SQLAlchemy)
│   ├── database.py      ← Conexão SQLite
│   └── requirements.txt
├── frontend/
│   ├── index.html       ← Interface do usuário
│   ├── app.js           ← Comunicação com a API via Fetch
│   └── css/
│       └── style.css
└── README.md

---

## 🔗 Conexão com as próximas sprints

O banco `clarisse.db` criado aqui será usado por todos os módulos:

| Sprint | O que usa daqui |
|---|---|
| 02-03 | Analisa imagem vinculada ao cliente |
| 04-05 | Chatbot busca clientes pelo nome |
| 08 | Detecta emoção na foto do cliente |
| 09-10 | Plataforma completa com todos os dados |

---

## 💻 Tecnologias utilizadas

![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

---

## 🚀 Como rodar

**1. Ative o ambiente virtual:**
```powershell
cd C:\dev\projetos\clarisse
venv\Scripts\Activate.ps1
```

**2. Instale as dependências:**
```powershell
cd sprint-01-fundamentos/backend
pip install -r requirements.txt
```

**3. Suba a API:**
```powershell
uvicorn main:app --reload
```

**4. Abra o frontend:**

Abra o arquivo `frontend/index.html` no navegador.

**5. Acesse a documentação da API:**

👉 http://127.0.0.1:8000/docs

---

## 🧠 O que aprendi nesta sprint

- Por que `localStorage` não escala e quando usar um banco de dados real
- Como criar uma **API REST** com FastAPI e suas rotas CRUD
- Como modelar dados com **SQLAlchemy** e validar com **Pydantic**
- O padrão de sessão `get_db()` e injeção de dependências
- Como o **frontend se comunica com o backend** via Fetch API
- O que é **CORS** e por que o navegador precisa dele
- Conventional Commits e versionamento profissional com Git

---

## 🤔 Dificuldades superadas

- Entender a diferença entre modelo SQLAlchemy e schema Pydantic
- Configurar CORS para o frontend conseguir chamar a API
- Instalar dependência faltante (`pydantic[email]`) e atualizar requirements

---

*Módulo do projeto [Clarisse](../README.md) —
reimplementação open source do
[CompassUOL PB 2024](https://github.com/niqueborges/CompassUol_PB_2024)*