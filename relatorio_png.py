import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime
import re

# Configuração do estilo dos gráficos
sns.set_theme(style="whitegrid")

file_path = 'output/relatorio_consolidado.csv'
try:
    # Carrega os dados do CSV gerado pelo script principal
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
        print(f"\nGerando gráfico para o curso: {curso_selecionado}")
        print(f"Disciplina: {disciplina_selecionada}")
    else:
        print(f"\nCombinação de curso e disciplina não encontrada. Verifique os valores selecionados.")
        print(f"Curso selecionado: '{curso_selecionado}'")
        print(f"Disciplina selecionada: '{disciplina_selecionada}'")


if not df_filtrado.empty:
    df_plot = df_filtrado.sort_values('media_final', ascending=False)
    
    media_geral_turma = df_plot['media_final'].mean()
    
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(data=df_plot, x='media_final', y='aluno', orient='h')
    
    for p in ax.patches:
        width = p.get_width()
        ax.text(width + 0.2, p.get_y() + p.get_height() / 2, f'{width:.1f}', va='center')
    
    ax.axvline(x=media_geral_turma, color='red', linestyle='--', linewidth=2, label=f'Média da Turma ({media_geral_turma:.2f})')
    ax.legend()
    
    ax.set_xlim(0, 11)
    # Título formatado para melhor legibilidade
    data_geracao = datetime.now().strftime('%d/%m/%Y %H:%M')
    plt.title(f'Notas Finais - {disciplina_selecionada}\n({curso_selecionado})\nGerado em: {data_geracao}', fontsize=16)
    plt.xlabel('Média Final', fontsize=12)
    plt.ylabel('Aluno', fontsize=12)
    plt.xticks(np.arange(0, 11, 1))
    plt.tight_layout()
    
    # Sanitiza os nomes para criar um nome de arquivo seguro
    safe_curso = sanitize_filename(curso_selecionado)
    safe_disciplina = sanitize_filename(disciplina_selecionada)
    output_png_path = f'output/relatorio_{safe_curso}_{safe_disciplina}.png'
    plt.savefig(output_png_path, dpi=300, bbox_inches='tight')
    
    print(f"Gráfico atualizado salvo em: {output_png_path}")
    plt.show()
else:
    print("Não há dados para gerar o gráfico.")