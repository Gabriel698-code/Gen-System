# 🏢 Gen-System | Assistente Executivo e Micro-SaaS de IA

Gen-System é um assistente de IA local alimentado pelo Google Gemini, focado em guiar novos empreendedores. Ele atua como um consultor com modos especializados (Jurídico, Financeiro, Viabilidade), analisa arquivos multimodais (PDF, Excel, Word, Imagens) e possui um frontend completo para emissão automatizada de NF-e/NFC-e, contratos, recibos e planilhas.

---

## 🚀 Tecnologias Utilizadas

Este projeto foi construído utilizando uma arquitetura híbrida (Frontend Vanilla + Backend Python):

* **Inteligência Artificial:** Google Generative AI (Gemini Flash/Pro)
* **Backend:** Python, FastAPI, Uvicorn
* **Interface Principal:** PyWebview (Desktop App experience)
* **Dashboard de Métricas:** Streamlit
* **Banco de Dados:** SQLite3 (Local)
* **Frontend:** HTML5, CSS3, Vanilla JavaScript
* **Geração de Documentos:** `fpdf` (PDFs), `python-docx` (Word), `openpyxl` e `pandas` (Excel)
* **Pesquisa Web Integrada:** `duckduckgo_search` (Deep Search)

---

## 📁 Estrutura do Projeto

* `main.py`: O coração do sistema (API, Cérebro da IA e roteamento).
* `dashboard.py`: Painel de métricas e histórico financeiro.
* `*.html` *(index, nfe_simples, contrato, etc)*: Telas de interface do usuário.
* `formularios/` e `characters/`: Recursos e assets visuais.

*(Nota: O banco de dados `leads.db`, os documentos gerados e os arquivos de configuração locais são ignorados no repositório por questões de segurança. O sistema os cria automaticamente durante o uso).*

---

## ⚙️ Como Instalar e Rodar

Para executar o Gen-System na sua máquina, é necessário ter o **Python 3.10+** instalado.

**1. Clone o repositório:**
```bash
git clone [https://github.com/SEU_USUARIO/gen-system.git](https://github.com/SEU_USUARIO/gen-system.git)
cd gen-system

pip install fastapi uvicorn pydantic pywebview streamlit google-generativeai fpdf python-docx openpyxl pandas PyPDF2 duckduckgo_search

python main.py

🔑 Primeiro Acesso e Ativação
O Gen-System possui uma arquitetura segura (Local-first). Ao rodar o comando python main.py pela primeira vez, a janela do aplicativo será aberta apresentando a Tela de Ativação.

Para usar o sistema:

Clique no link fornecido na tela para gerar sua chave gratuita do Google Gemini (Google AI Studio).

Cole a chave no campo indicado.

Clique em Ativar Sistema.

O Gen-System validará a chave em tempo real e criará o arquivo user_config.json de forma segura e criptografada, liberando o acesso a todas as funcionalidades.

💡 Principais Funcionalidades
💬 Consultoria de IA Especializada: Modos com foco em Análise Financeira, Jurídica, Marketing e Viabilidade de Negócios.

🧾 Emissor de NF-e e NFC-e: Formulário completo e offline-first para geração de XML validado no padrão SEFAZ, com modais interativos para CFOP/NCM/UN.

📄 Geração Autônoma de Documentos: Criação de contratos, recibos e ordens de serviço (PDF/Word) a partir de comandos de texto.

📊 Planilhas Dinâmicas: Cria controles de estoque, precificação e fluxo de caixa em .xlsx.

👁️ Análise Multimodal: Capacidade de ler e interpretar documentos Word, PDFs, planilhas Excel e imagens submetidas no chat.

🌐 Deep Search Integrado: O sistema faz buscas na internet em tempo real para consultar leis atualizadas e cotações financeiras antes de formular a resposta.
