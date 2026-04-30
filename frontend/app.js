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
                <div style="display: flex; gap: 15px; align-items: center; margin-bottom: 15px;">
                    <div class="cliente-foto">
                        ${c.foto_path 
                            ? `<img src="${API}${c.foto_path}" alt="Foto" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover;">` 
                            : `<div style="width: 60px; height: 60px; border-radius: 50%; background: #eee; display: flex; align-items: center; justify-content: center; font-size: 0.8em; color: #999;">Sem foto</div>`}
                    </div>
                    <div class="cliente-info">
                        <p style="margin: 0;"><strong>${c.nome}</strong></p>
                        <p style="margin: 0; font-size: 0.9em;">📅 ${formatarData(c.data_nascimento)} | 📞 ${c.telefone}</p>
                        <p style="margin: 0; font-size: 0.9em;">📧 ${c.email}</p>
                    </div>
                </div>
                <div class="cliente-acoes" style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <input type="file" id="file-${c.id}" style="display: none;" accept="image/*" onchange="uploadFoto(${c.id}, this.files[0])">
                    <button onclick="document.getElementById('file-${c.id}').click()">📷 Enviar Foto</button>
                    <button onclick="verAnalises(${c.id})">📊 Ver Análises</button>
                    <button class="danger" onclick="excluirCliente(${c.id}, '${c.nome}')">🗑️ Excluir</button>
                </div>
                <div id="analises-${c.id}" class="cliente-analises hidden" style="margin-top: 15px; border-top: 1px dashed #ccc; padding-top: 10px;"></div>
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

// ─── Upload de Foto e Análise ───
async function uploadFoto(clienteId, file) {
    if (!file) return;

    const formData = new FormData();
    formData.append('foto', file);

    try {
        const response = await fetch(`${API}/clientes/${clienteId}/analise`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const erro = await response.json();
            alert(erro.detail || 'Erro ao enviar foto.');
            return;
        }

        alert('Foto enviada e analisada com sucesso!');
        await listarClientes(); // Atualiza a lista para carregar a foto
    } catch (e) {
        alert('Não foi possível conectar à API para upload.');
    }
}

// ─── Visualizar Análises ───
async function verAnalises(clienteId) {
    const container = document.getElementById(`analises-${clienteId}`);
    
    // Ocultar se já estiver visível (Toggle)
    if (!container.classList.contains('hidden') && container.innerHTML !== '') {
        container.classList.add('hidden');
        return;
    }

    try {
        const response = await fetch(`${API}/clientes/${clienteId}`);
        if (!response.ok) throw new Error('Falha ao buscar detalhes do cliente.');
        const cliente = await response.json();

        if (!cliente.analises || cliente.analises.length === 0) {
            container.innerHTML = '<p class="vazio" style="font-size: 0.9em; color: #666;">Nenhuma análise de imagem encontrada para este cliente.</p>';
        } else {
            container.innerHTML = '<h4 style="margin: 0 0 10px 0;">Histórico de Análises</h4>' + cliente.analises.map(a => `
                <div class="analise-item" style="display: flex; gap: 10px; align-items: center; margin-top: 10px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: #fafafa;">
                    <img src="${API}${a.foto_path}" alt="Análise" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;">
                    <div>
                        <p style="margin: 0; font-size: 0.9em;"><strong>Emoção Dominante:</strong> <span style="text-transform: capitalize;">${a.emocao_dominante || 'N/A'}</span></p>
                        <p style="margin: 0; font-size: 0.8em; color: #666;">Confiança: ${a.confianca_emocao ? (a.confianca_emocao * 100).toFixed(1) + '%' : 'N/A'}</p>
                        <p style="margin: 0; font-size: 0.8em; color: #666;">📅 ${new Date(a.data_analise).toLocaleString()}</p>
                    </div>
                </div>
            `).join('');
        }
        container.classList.remove('hidden');
    } catch (e) {
        alert('Erro ao carregar o histórico de análises.');
    }
}

// ... (mantenha as constantes e funções listarClientes/cadastrarCliente que você já tem) ...

// Função para abrir o seletor de arquivo e enviar a foto para análise
async function analisarFoto(clienteId) {
    // 1. Cria um input de arquivo temporário (invisível) para o usuário escolher a foto
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/jpeg, image/png, image/jpg';

    // 2. Quando o usuário escolher o arquivo...
    fileInput.onchange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        // O FormData é obrigatório para enviar arquivos (UploadFile no FastAPI)
        const formData = new FormData();
        formData.append('foto', file); // 'foto' é o nome exato do parâmetro no nosso main.py

        // Dá um feedback visual para o usuário
        const container = document.getElementById(`analises-${clienteId}`);
        if(container) container.innerHTML = "<p>⏳ Analisando imagem com IA...</p>";

        try {
            // 3. Envia o POST para a nossa nova rota no backend
            const response = await fetch(`${API}/clientes/${clienteId}/analise`, {
                method: 'POST',
                body: formData // Não colocamos Content-Type, o navegador ajusta sozinho para FormData
            });

            if (!response.ok) {
                const erro = await response.json();
                mostrarErro(erro.detail || 'Erro ao analisar a imagem.');
                if(container) container.innerHTML = "<p class='erro'>❌ Falha na análise.</p>";
                return;
            }

            const resultado = await response.json();
            
            // 4. Se deu certo, atualiza a lista para mostrar a nova foto/emoção
            await listarClientes(); 

            // Opcional: mostrar um alerta de sucesso
            alert(`Análise concluída! Emoção detectada: ${resultado.emocao_dominante}`);

        } catch (e) {
            mostrarErro('Erro de conexão ao tentar enviar a imagem.');
        }
    };

    // Abre a janelinha de escolha de arquivo do Windows/Mac
    fileInput.click();
}


// Função para renderizar as análises dentro do card do cliente
function renderizarAnalises(cliente) {
    // Se o cliente não tiver análises (ou se a lista estiver vazia), mostra um texto padrão
    if (!cliente.analises || cliente.analises.length === 0) {
        return `<p class="sem-analise">Nenhuma análise de imagem registrada.</p>`;
    }

    // Pega a última análise feita (assumindo que queremos mostrar a mais recente)
    const ultimaAnalise = cliente.analises[cliente.analises.length - 1];

    // Monta o HTML com a foto e o resultado da emoção
    return `
        <div class="resultado-analise">
            <img src="${API}${ultimaAnalise.foto_path}" alt="Foto analisada" class="foto-miniatura">
            <div class="dados-emocao">
                <p><strong>Emoção:</strong> <span class="badge-emocao">${ultimaAnalise.emocao_dominante}</span></p>
                <p><small>Analisado em: ${new Date(ultimaAnalise.data_analise).toLocaleDateString('pt-BR')}</small></p>
            </div>
        </div>
    `;
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