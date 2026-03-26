import pandas as pd
from typing import List, Dict, Any, Tuple
from app.schemas.pauta import PautaCreate
import io

# Mapeamento de colunas da planilha para o Schema Pydantic
COLUMN_MAPPING = {
    # Mapeamento Legado / Existente
    "area": "area",
    "subarea": "subarea",
    "tema": "tema",
    "palavra_chave_principal": "palavra_chave_principal",
    "palavras_chave_secundarias": "palavras_chave_secundarias",
    "intencao_de_busca": "intencao_de_busca",
    "publico_alvo": "publico_alvo",
    "objetivo_do_artigo": "objetivo_do_artigo",
    "tom_de_voz": "tom_de_voz",
    "topicos_obrigatorios": "topicos_obrigatorios",
    "restricoes": "restricoes_editoriais", # Renomeado
    "referencias_obrigatorias": "referencias_obrigatorias",
    "faq_desejada": "perguntas_frequentes_desejadas", # Renomeado
    "cta_principal": "cta_principal",
    "categoria_wordpress": "categoria_wordpress",
    "tags_wordpress": "tags_wordpress",
    "instrucoes_imagem_capa": "ideia_imagem_capa", # Renomeado
    "estilo_visual_capa": "estilo_visual_capa",
    "autor": "autor",
    "observacoes_editoriais": "observacoes_editoriais",
    
    # Novos Campos (Podem vir na planilha também)
    "prioridade": "prioridade",
    "categoria_principal": "categoria_principal",
    "titulo_base": "titulo_base",
    "estagio_do_funil": "estagio_do_funil",
    "angulo_seo": "angulo_seo",
    "pergunta_principal_do_usuario": "pergunta_principal_do_usuario",
    "resumo_da_pauta": "resumo_da_pauta",
    "outline_h2_h3": "outline_h2_h3",
    "topicos_proibidos": "topicos_proibidos",
    "nivel_de_profundidade": "nivel_de_profundidade",
    "formato_do_artigo": "formato_do_artigo",
    "tamanho_estimado": "tamanho_estimado",
    "objetivo_de_conversao": "objetivo_de_conversao",
    "produto_relacionado": "produto_relacionado",
    "servico_relacionado": "servico_relacionado",
    "cta_secundario": "cta_secundario",
    "bloco_promocional_1": "bloco_promocional_1",
    "bloco_promocional_2": "bloco_promocional_2",
    "link_de_destino_cta": "link_de_destino_cta",
    "momento_do_anuncio": "momento_do_anuncio",
    "tipo_de_anuncio": "tipo_de_anuncio",
    "artigos_relacionados_internos": "artigos_relacionados_internos",
    "anchors_internas_sugeridas": "anchors_internas_sugeridas",
    "cluster_tematica": "cluster_tematica",
    "artigo_pilar": "artigo_pilar",
    "links_externos_autoridade": "links_externos_autoridade",
    "referencias_complementares": "referencias_complementares"
}

def parse_excel_pautas(file_content: bytes) -> Tuple[List[PautaCreate], List[Dict[str, Any]]]:
    """
    Lê uma planilha Excel e converte as linhas em objetos PautaCreate.
    Retorna (lista_de_pautas_validas, lista_de_erros).
    """
    valid_pautas = []
    errors = []

    try:
        # Ler o Excel usando pandas
        df = pd.read_excel(io.BytesIO(file_content))
    except Exception as e:
        raise ValueError(f"Não foi possível ler o arquivo Excel: {str(e)}")

    # Normalizar nomes das colunas (remover espaços, lower case)
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

    # Verificar colunas obrigatórias (mínimo: 'tema')
    if "tema" not in df.columns:
        raise ValueError("A coluna 'tema' é obrigatória na planilha.")

    for index, row in df.iterrows():
        try:
            pauta_data = {}
            # Mapear colunas existentes
            for excel_col, schema_attr in COLUMN_MAPPING.items():
                if excel_col in df.columns:
                    val = row[excel_col]
                    # Tratar valores vazios (NaN)
                    if pd.isna(val):
                        pauta_data[schema_attr] = None
                    else:
                        pauta_data[schema_attr] = str(val).strip()
                else:
                    # Se a coluna não existe na planilha, preenche com None
                    pauta_data[schema_attr] = None

            # Ajustes específicos (caso precise de listas, por exemplo)
            # Para 'palavras_chave_secundarias', vamos manter como string separada por vírgula no banco
            # para simplificar. O Pydantic já aceita string.

            # Validação via Pydantic
            # Se 'tema' for nulo ou vazio, gera erro
            if not pauta_data.get("tema"):
                errors.append({"line": index + 2, "error": "Campo 'tema' não pode ser vazio."})
                continue

            pauta_create = PautaCreate(**pauta_data)
            valid_pautas.append(pauta_create)

        except Exception as e:
            errors.append({"line": index + 2, "error": str(e)})

    return valid_pautas, errors
