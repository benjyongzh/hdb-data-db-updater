from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TableMetadata(BaseModel):
    id: int = Field(..., ge=0)
    table_id: int = Field(..., ge=0)
    created_at: datetime
    updated_at: datetime


class TableMetadataFilter(BaseModel):
    limit: int = 100
    offset: int = 0


class TableMetadataTouchRequest(BaseModel):
    table_id: Optional[int] = None
    table_name: Optional[str] = None

    def require_one(self) -> None:
        if self.table_id is None and (self.table_name is None or not self.table_name.strip()):
            raise ValueError("Provide either table_id or table_name")

