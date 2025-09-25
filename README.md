# 📊 Gerador de Relatórios de Notas

Este projeto foi desenvolvido para auxiliar professores de cursos técnicos a automatizar a consolidação e análise de notas de alunos. A ferramenta lê múltiplas planilhas de notas no formato `.ods`, consolida os dados e gera diversos tipos de relatórios: um arquivo CSV centralizado, gráficos de desempenho por turma, relatórios em PDF e um painel web interativo.

## ✨ Funcionalidades

- **Consolidação Automática:** Processa múltiplos arquivos de notas (`.ods`) de diferentes turmas e disciplinas.
- **Relatório Centralizado:** Gera um único arquivo `relatorio_consolidado.csv` com todas as notas.
- **Visualização Gráfica:** Cria gráficos de barras (`.png`) comparando o desempenho dos alunos de uma disciplina específica.
- **Relatórios em PDF:** Gera tabelas de notas formatadas em PDF, destacando notas baixas para fácil identificação.
- **Painel Interativo:** Oferece um dashboard web (criado com Streamlit) para filtrar e visualizar os dados de forma dinâmica.
- **Manutenção Simplificada:** Permite atualizar a base de dados diretamente pelo painel web.

## 📂 Estrutura do Projeto

```
Relatorio_Notas/
├── inputs_ods/             # ⚠️ Coloque suas planilhas .ods aqui (ignorada pelo Git)
├── output/                 # 📂 Relatórios gerados (CSV, PNG, PDF) (ignorada pelo Git)
├── app.py                  # 🚀 Script do painel web interativo (Streamlit)
├── relatorio.py            # ⚙️ Script principal para consolidar os dados das planilhas
├── relatorio_pdf.py        # 📄 Script para gerar relatórios em PDF
├── relatorio_png.py        # 📈 Script para gerar gráficos de notas
├── projeto.md              # 🔧 Arquivo de configuração para mapear códigos de turma/disciplina
├── requirements.txt        # 📦 Lista de dependências do projeto
└── README.md               # 📖 Este arquivo
```

## 🛠️ Pré-requisitos

Antes de começar, garanta que você tenha o Python 3 instalado em seu computador.

## ⚙️ Instalação

Siga os passos abaixo para configurar o ambiente do projeto.

1.  **Clone o repositório:**
    ```bash
    git clone Relatorio_Notas

    cd Relatorio_Notas
    ```

2.  **Crie um ambiente virtual (recomendado):**
    Isso isola as dependências do projeto e evita conflitos com outros projetos Python.
    ```bash
    python -m venv venv
    ```

3.  **Ative o ambiente virtual:**
    -   No Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    -   No macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Instale as dependências:**
    O arquivo `requirements.txt` contém todas as bibliotecas necessárias.
    ```bash
    pip install -r requirements.txt
    ```

## 🔧 Configuração

Para que o sistema funcione corretamente, você precisa configurar duas coisas:

### 1. Mapeamento de Nomes (`projeto.md`)

O script `relatorio.py` usa o arquivo `projeto.md` para traduzir os códigos das turmas e disciplinas (presentes nos nomes dos arquivos `.ods`) para nomes completos e legíveis nos relatórios.

Abra o arquivo `projeto.md` e edite o dicionário `REPORT_MAP` para refletir suas turmas e disciplinas.

**Exemplo:**
```python
# Dentro de projeto.md
REPORT_MAP = {
    "turma": {
        "TDS": "Técnico em Desenvolvimento de Sistemas",
        "PJD": "Técnico em Programação de Jogos Digitais",
    },
    "disciplina": {
        "ARC": "Arquitetura de Computadores",
        "LPG": "Lógica de Programação",
    }
}
```

### 2. Arquivos de Notas (`.ods`)

- Crie uma pasta chamada `inputs_ods` na raiz do projeto.
- Coloque suas planilhas de notas (em formato `.ods`) dentro desta pasta.
- **Importante:** Os nomes dos arquivos devem seguir o padrão `CODIGOTURMA-CODIGODISCIPLINA Notas.ods`.
  - Exemplo: `TDS-ARC Notas.ods`

## 🚀 Como Usar

1.  **Consolidar os Dados:**
    Este é o primeiro passo. Execute o script `relatorio.py` para ler todos os arquivos da pasta `inputs_ods` e criar o `relatorio_consolidado.csv` na pasta `output`.
    ```bash
    python relatorio.py
    ```

2.  **Gerar Relatórios (Gráfico ou PDF):**
    Execute o script correspondente e siga o menu interativo no terminal para escolher o curso e a disciplina.
    ```bash
    python relatorio_png.py  # Para gerar um gráfico .png
    python relatorio_pdf.py  # Para gerar um relatório .pdf
    ```

3.  **Analisar no Painel Web:**
    Para uma análise mais detalhada e interativa, inicie o dashboard.
    ```bash
    streamlit run app.py
    ```
    Abra o navegador no endereço fornecido (geralmente `http://localhost:8501`). No painel, você pode filtrar os dados e até mesmo acionar a atualização (reexecução do `relatorio.py`) clicando no botão na aba "Manutenção".