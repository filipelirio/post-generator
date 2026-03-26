from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PublicationRecordResponse(BaseModel):
    id: int
    pauta_id: int
    
    wordpress_post_id: Optional[int] = None
    wordpress_url: Optional[str] = None
    wordpress_media_id: Optional[int] = None
    
    status: str
    published_at: datetime
    
    raw_response_json: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
