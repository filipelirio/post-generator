import sqlite3
import os

# Caminho para o banco de dados (pode variar dependendo de onde o script é executado)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "app.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Banco de dados não encontrado em {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Novas colunas a serem adicionadas
    new_columns = [
        ("prioridade", "TEXT"),
        ("categoria_principal", "TEXT"),
        ("titulo_base", "TEXT"),
        ("estagio_do_funil", "TEXT"),
        ("angulo_seo", "TEXT"),
        ("pergunta_principal_do_usuario", "TEXT"),
        ("resumo_da_pauta", "TEXT"),
        ("outline_h2_h3", "TEXT"),
        ("topicos_proibidos", "TEXT"),
        ("nivel_de_profundidade", "TEXT"),
        ("formato_do_artigo", "TEXT"),
        ("tamanho_estimado", "TEXT"),
        ("perguntas_frequentes_desejadas", "TEXT"),
        ("restricoes_editoriais", "TEXT"),
        ("objetivo_de_conversao", "TEXT"),
        ("produto_relacionado", "TEXT"),
        ("servico_relacionado", "TEXT"),
        ("cta_secundario", "TEXT"),
        ("bloco_promocional_1", "TEXT"),
        ("bloco_promocional_2", "TEXT"),
        ("link_de_destino_cta", "TEXT"),
        ("momento_do_anuncio", "TEXT"),
        ("tipo_de_anuncio", "TEXT"),
        ("artigos_relacionados_internos", "TEXT"),
        ("anchors_internas_sugeridas", "TEXT"),
        ("cluster_tematica", "TEXT"),
        ("artigo_pilar", "TEXT"),
        ("links_externos_autoridade", "TEXT"),
        ("referencias_complementares", "TEXT"),
        ("ideia_imagem_capa", "TEXT"),
        ("prompt_imagem_capa", "TEXT"),
        ("texto_na_imagem", "TEXT"),
        ("paleta_sugerida", "TEXT"),
        ("elementos_visuais_obrigatorios", "TEXT"),
        ("elementos_visuais_proibidos", "TEXT"),
        ("proporcao_imagem", "TEXT"),
        ("alt_text", "TEXT"),
        ("legenda_imagem", "TEXT"),
        ("data_planejada", "DATETIME")
    ]

    for col_name, col_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE pauta ADD COLUMN {col_name} {col_type}")
            print(f"Coluna {col_name} adicionada com sucesso.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Coluna {col_name} já existe.")
            else:
                print(f"Erro ao adicionar {col_name}: {e}")

    # Migração de dados de colunas renomeadas (opcional, para segurança)
    try:
        # faq_desejada -> perguntas_frequentes_desejadas
        cursor.execute("UPDATE pauta SET perguntas_frequentes_desejadas = faq_desejada WHERE faq_desejada IS NOT NULL")
        # restricoes -> restricoes_editoriais
        cursor.execute("UPDATE pauta SET restricoes_editoriais = restricoes WHERE restricoes IS NOT NULL")
        # instrucoes_imagem_capa -> ideia_imagem_capa
        cursor.execute("UPDATE pauta SET ideia_imagem_capa = instrucoes_imagem_capa WHERE instrucoes_imagem_capa IS NOT NULL")
        print("Dados de colunas legadas migrados com sucesso.")
    except Exception as e:
        print(f"Aviso na migração de dados internos: {e}")

    conn.commit()
    conn.close()
    print("Migração concluída.")

if __name__ == "__main__":
    migrate()
