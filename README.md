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
