// app.js
// Frontend do Clarisse — comunica com a API FastAPI via fetch.
// Substitui toda a lógica de localStorage do projeto original.

const API = 'http://127.0.0.1:8000';

// ─── Carregar lista ao abrir a página ───
window.addEventListener('DOMContentLoaded', listarClientes);

// ─── Cadastrar cliente ───
async function cadastrarCliente() {
    const nome           = document.getElementById('nome').value.trim();
    const dataNascimento = document.getElementById('dataNascimento').value;
    const telefone       = document.getElementById('telefone').value.trim();
    const email          = document.getElementById('email').value.trim();

    if (!nome || !dataNascimento || !telefone || !email) {
        mostrarErro('Preencha todos os campos.');
        return;
    }

    try {
        const response = await fetch(`${API}/clientes`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nome,
                data_nascimento: dataNascimento,
                telefone,
                email
            })
        });

        if (!response.ok) {
            const erro = await response.json();
            mostrarErro(erro.detail || 'Erro ao cadastrar.');
            return;
        }

        limparFormulario();
        await listarClientes();

    } catch (e) {
        mostrarErro('Não foi possível conectar à API. A API está rodando?');
    }
}

// ─── Listar clientes ───
async function listarClientes() {
    const lista = document.getElementById('lista-clientes');

    try {
        const response = await fetch(`${API}/clientes`);
        const clientes = await response.json();

        if (clientes.length === 0) {
            lista.innerHTML = '<p class="vazio">Nenhum cliente cadastrado ainda.</p>';
            return;
        }

        lista.innerHTML = clientes.map(c => `
            <div class="cliente-card">
                <div class="cliente-info">
                    <p><strong>${c.nome}</strong></p>
                    <p>📅 ${formatarData(c.data_nascimento)}</p>
                    <p>📞 ${c.telefone}</p>
                    <p>📧 ${c.email}</p>
                </div>
                <div class="cliente-acoes">
                    <button class="danger" onclick="excluirCliente(${c.id}, '${c.nome}')">
                        Excluir
                    </button>
                </div>
            </div>
        `).join('');

    } catch (e) {
        lista.innerHTML = '<p class="vazio">Erro ao carregar clientes.</p>';
    }
}

// ─── Excluir cliente ───
async function excluirCliente(id, nome) {
    if (!confirm(`Excluir o cliente "${nome}"?`)) return;

    await fetch(`${API}/clientes/${id}`, { method: 'DELETE' });
    await listarClientes();
}

// ─── Utilitários ───
function limparFormulario() {
    ['nome', 'dataNascimento', 'telefone', 'email'].forEach(id => {
        document.getElementById(id).value = '';
    });
    esconderErro();
}

function mostrarErro(msg) {
    const el = document.getElementById('mensagem-erro');
    el.textContent = msg;
    el.classList.remove('hidden');
}

function esconderErro() {
    document.getElementById('mensagem-erro').classList.add('hidden');
}

function formatarData(dataISO) {
    const [ano, mes, dia] = dataISO.split('-');
    return `${dia}/${mes}/${ano}`;
}