import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import json
import re

# Configuração do estilo dos gráficos
sns.set_theme(style="whitegrid")


file_path = 'output/relatorio_consolidado.csv'
try:
    df = pd.read_csv(file_path)
    
    # --- AJUSTE DAS COLUNAS --- 
    # Renomeia as colunas para um padrão consistente (minúsculas)
    df.columns = ['curso', 'disciplina', 'aluno', 'av1', 'av2', 'media_final']
    
    # Cria a coluna 'status' com base na média final
    # Regra: Aprovado se media_final >= 6, senão Reprovado. Ajuste se necessário.
    df['status'] = np.where(df['media_final'] >= 6, 'Aprovado', 'Reprovado')
    # ---------------------------
    
    print("Dados carregados e preparados com sucesso!")
    print(df.head())
    
except FileNotFoundError:
    print(f"Erro: O arquivo não foi encontrado em '{file_path}'.")
    print("Por favor, execute o script de consolidação de relatórios primeiro.")
    df = pd.DataFrame() # Cria um DataFrame vazio para evitar erros

def sanitize_filename(name):
    """Remove caracteres inválidos e substitui espaços por underscores."""
    return re.sub(r'[^\w\.-]', '_', name)

def select_from_menu(options, title):
    """Exibe um menu de opções numeradas e retorna a opção escolhida pelo usuário."""
    print(f"\n--- {title} ---")
    for i, option in enumerate(options):
        print(f"[{i + 1}] {option}")
    
    while True:
        try:
            choice = int(input("Digite o número da sua escolha: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")

curso_disciplinas_dict = {}
curso_selecionado = None
disciplina_selecionada = None

if not df.empty:
    # Agrupa por curso e coleta as disciplinas únicas para cada um
    curso_disciplinas_dict = df.groupby('curso')['disciplina'].unique().apply(list).to_dict()
    
    # --- Menu Interativo de Seleção ---
    if curso_disciplinas_dict:
        # 1. Selecionar o curso
        cursos_disponiveis = list(curso_disciplinas_dict.keys())
        curso_selecionado = select_from_menu(cursos_disponiveis, "Selecione um Curso")

        # 2. Selecionar a disciplina
        disciplinas_disponiveis = curso_disciplinas_dict[curso_selecionado]
        disciplina_selecionada = select_from_menu(disciplinas_disponiveis, f"Selecione uma Disciplina para '{curso_selecionado}'")
    else:
        print("Não foi possível encontrar cursos ou disciplinas nos dados carregados.")

# Filtrando o DataFrame
df_filtrado = pd.DataFrame()
if curso_selecionado and disciplina_selecionada:
    if curso_selecionado in curso_disciplinas_dict and disciplina_selecionada in curso_disciplinas_dict[curso_selecionado]:
        df_filtrado = df[(df['curso'] == curso_selecionado) & (df['disciplina'] == disciplina_selecionada)].copy()
        print(f"\nGerando PDF para o curso: {curso_selecionado}")
        print(f"Disciplina: {disciplina_selecionada}")
    else:
        print(f"\nCombinação de curso e disciplina não encontrada. Verifique os valores selecionados.")
        print(f"Curso selecionado: '{curso_selecionado}'")
        print(f"Disciplina selecionada: '{disciplina_selecionada}'")

def gerar_pdf_simples(df_dados, curso, disciplina):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    pdf.cell(0, 10, 'Relatório de Notas', 0, 1, 'C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f'Curso: {curso}', 0, 1, 'L')
    pdf.cell(0, 10, f'Disciplina: {disciplina}', 0, 1, 'L')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 10)
    col_widths = [70, 20, 20, 30, 30]
    headers = ['Aluno', 'AV1', 'AV2', 'Média Final', 'Status']
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
    pdf.ln()

    pdf.set_font("Arial", '', 10)
    df_dados_sorted = df_dados.sort_values('media_final', ascending=False)
    for _, row in df_dados_sorted.iterrows():
        # Célula do Aluno (sempre preta)
        aluno = str(row.get('aluno', 'N/A')).encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(col_widths[0], 10, aluno, 1)
        
        # --- LÓGICA DE COR PARA NOTAS --- 
        # Nota AV1
        av1_val = row.get('av1', 0)
        if av1_val < 6:
            pdf.set_text_color(255, 0, 0) # Vermelho
        pdf.cell(col_widths[1], 10, str(av1_val), 1, 0, 'C')
        pdf.set_text_color(0, 0, 0) # Reseta para preto
        
        # Nota AV2
        av2_val = row.get('av2', 0)
        if av2_val < 6:
            pdf.set_text_color(255, 0, 0) # Vermelho
        pdf.cell(col_widths[2], 10, str(av2_val), 1, 0, 'C')
        pdf.set_text_color(0, 0, 0) # Reseta para preto
        
        # Média Final
        media_val = row.get('media_final', 0)
        if media_val < 6:
            pdf.set_text_color(255, 0, 0) # Vermelho
        pdf.cell(col_widths[3], 10, str(media_val), 1, 0, 'C')
        pdf.set_text_color(0, 0, 0) # Reseta para preto
        
        # Status
        status = str(row.get('status', 'N/A'))
        if status == 'Reprovado':
            pdf.set_text_color(255, 0, 0) # Vermelho
        pdf.cell(col_widths[4], 10, status, 1, 0, 'C')
        pdf.set_text_color(0, 0, 0) # Reseta para preto
        
        pdf.ln()
        
    # Sanitiza os nomes para criar um nome de arquivo seguro
    safe_curso = sanitize_filename(curso)
    safe_disciplina = sanitize_filename(disciplina)
    output_pdf_path = f'output/relatorio_{safe_curso}_{safe_disciplina}.pdf'
    pdf.output(output_pdf_path, 'F')
    return output_pdf_path

if not df_filtrado.empty:
    colunas_pdf = ['aluno', 'av1', 'av2', 'media_final', 'status']
    caminho_pdf = gerar_pdf_simples(df_filtrado[colunas_pdf], curso_selecionado, disciplina_selecionada)
    print(f"Relatório em PDF com cores salvo em: {caminho_pdf}")
else:
    print("Nenhum dado para gerar o PDF.")