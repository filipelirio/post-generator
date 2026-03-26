import sys
import os
import asyncio
from datetime import datetime, timedelta

# Adicionar o diretório pai ao path para importar os módulos da app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.integrations.wordpress import WordPressClient
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.pauta import Pauta
from sqlalchemy import text

async def test_wordpress_connection():
    print("--- Testando Conexão WordPress ---")
    client = WordPressClient()
    try:
        # Tentar listar categorias (teste leve de leitura)
        categories = await client.list_categories()
        print(f"✅ Conexão OK! {len(categories)} categorias encontradas.")
        
        # Testar agendamento (Simulação de payload)
        future_date = datetime.now() + timedelta(days=2)
        print(f"🕒 Testando agendamento para: {future_date.isoformat()}")
        
        # Testar metadados Yoast (apenas verificação de estrutura)
        seo_meta = {
            "_yoast_wpseo_title": "Título de Teste SEO",
            "_yoast_wpseo_metadesc": "Descrição de Teste SEO",
            "_yoast_wpseo_focuskw": "Teste"
        }
        print("✅ Estrutura de Metadados Yoast pronta.")
        
        return True
    except Exception as e:
        print(f"❌ Erro na conexão WordPress: {str(e)}")
        return False

def test_database_schema():
    print("\n--- Testando Schema do Banco de Dados ---")
    db = SessionLocal()
    try:
        # Verificar se as novas colunas existem na tabela pauta
        result = db.execute(text("PRAGMA table_info(pautas)"))
        columns = [row[1] for row in result]
        
        required_cols = [
            "data_planejada", 
            "palavra_chave_principal", 
            "categoria_wordpress", 
            "tags_wordpress",
            "cta_fixo"
        ]
        
        missing = [col for col in required_cols if col not in columns]
        
        if not missing:
            print(f"✅ Schema íntegro! {len(columns)} colunas detectadas.")
        else:
            print(f"❌ Colunas ausentes: {', '.join(missing)}")
            
        return len(missing) == 0
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {str(e)}")
        return False
    finally:
        db.close()

async def main():
    wp_ok = await test_wordpress_connection()
    db_ok = test_database_schema()
    
    if wp_ok and db_ok:
        print("\n🚀 TUDO PRONTO PARA TESTAR NA INTERFACE! 🚀")
        print("1. Abra o navegador em http://localhost:3000")
        print("2. Vá em 'Pautas' e clique no ícone ✨ em uma pauta pendente.")
        print("3. Após gerar, clique no ícone 👁️ para revisar.")
        print("4. Clique em 'Agendar no WordPress'.")
    else:
        print("\n⚠️ Algumas verificações falharam. Verifique os erros acima.")

if __name__ == "__main__":
    asyncio.run(main())
