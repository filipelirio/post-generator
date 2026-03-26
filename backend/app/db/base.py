# Importar todos os modelos aqui para que o Base.metadata os conheça
# Isso garante que o create_all no main.py funcione corretamente.
from app.db.base_class import Base
from app.models.pauta import Pauta, PautaStatus
from app.models.article import ArticleDraft, ArticleVersion
from app.models.publication import PublicationRecord
