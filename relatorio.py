import os
import pandas as pd
import re
import ast

def get_report_map():
    """Lê o arquivo projeto.md e extrai o dicionário REPORT_MAP."""
    try:
        with open('projeto.md', 'r', encoding='utf-8') as f:
            content = f.read()
        # Extrai o conteúdo do bloco de código python
        python_code_block = re.search(r'```python(.*?)```', content, re.DOTALL)
        if python_code_block:
            python_code = python_code_block.group(1).strip()
            # Encontra a atribuição do dicionário
            report_map_str_match = re.search(r'REPORT_MAP\s*=\s*(\{.*\})', python_code, re.DOTALL)
            if report_map_str_match:
                report_map_str = report_map_str_match.group(1)
                # Remove comments from the string
                report_map_str = re.sub(r'#.*?\n', '\n', report_map_str)
                return ast.literal_eval(report_map_str)
    except Exception as e:
        print(f"Erro ao ler e processar o arquivo projeto.md: {e}")
    return None

def clean_col_names(df):
    """Limpa e padroniza os nomes das colunas de um DataFrame."""
    new_columns = {}
    for col in df.columns:
        try:
            new_col = col.encode('latin1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            new_col = col
        new_col = re.sub(r'Questionrio:|Frum:', '', new_col)
        new_col = re.sub(r'\(Real\)', '', new_col)
        new_col = new_col.strip()
        new_columns[col] = new_col
    df = df.rename(columns=new_columns)
    return df

def process_file(file_path, report_map):
    """Lê um arquivo ODS, limpa os dados e retorna um DataFrame padronizado."""
    try:
        df = pd.read_excel(file_path)
        df = clean_col_names(df)

        file_name = os.path.basename(file_path)
        file_parts = file_name.replace(' Notas.ods', '').split('-')
        
        turma_code = file_parts[0]
        disciplina_code = file_parts[1]

        turma_name = report_map.get("turma", {}).get(turma_code, turma_code)
        disciplina_name = report_map.get("disciplina", {}).get(disciplina_code, disciplina_code)

        n1_col = [col for col in df.columns if 'AVALIAÇÃO 01' in col and 'total' not in col][0]
        n2_col = [col for col in df.columns if 'AVALIAÇÃO 02' in col and 'total' not in col][0]
        media_col = [col for col in df.columns if 'Média da Disciplina' in col][0]

        df_processed = df[['Nome', 'Sobrenome', n1_col, n2_col, media_col]].copy()
        df_processed.rename(columns={
            n1_col: 'AV1',
            n2_col: 'AV2',
            media_col: 'MediaFinal'
        }, inplace=True)

        df_processed['Curso'] = turma_name
        df_processed['Disciplina'] = disciplina_name
        
        df_processed['Aluno'] = df_processed['Nome'].str.strip() + ' ' + df_processed['Sobrenome'].str.strip()
        df_processed['Aluno'] = df_processed['Aluno'].str.title()

        for col in ['AV1', 'AV2', 'MediaFinal']:
            df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce').fillna(0)

        df_processed.dropna(subset=['Nome', 'Sobrenome'], inplace=True)

        return df_processed

    except Exception as e:
        print(f"Erro ao processar o arquivo {os.path.basename(file_path)}: {e}")
        return None

# --- Script Principal ---
input_folder = 'inputs_ods'
output_folder = 'output'
output_file = os.path.join(output_folder, 'relatorio_consolidado.csv')

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

report_map = get_report_map()
if not report_map:
    print("Não foi possível carregar o mapa de relatório. Usando nomes de arquivo padrão.")
    report_map = {"turma": {}, "disciplina": {}}

all_data = []
od_files = [f for f in os.listdir(input_folder) if f.endswith('.ods')]

for file_name in od_files:
    file_path = os.path.join(input_folder, file_name)
    
    print(f"Processando arquivo: {file_name}...")
    processed_df = process_file(file_path, report_map)
    
    if processed_df is not None:
        all_data.append(processed_df)

if all_data:
    final_df = pd.concat(all_data, ignore_index=True)

    final_df = final_df[['Curso', 'Disciplina', 'Aluno', 'AV1', 'AV2', 'MediaFinal']]

    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\nRelatório consolidado foi salvo com sucesso em: {output_file}")
    print(f"Total de {len(final_df)} registros processados.")
else:
    print("\nNenhum dado foi processado. Verifique os erros acima.")
