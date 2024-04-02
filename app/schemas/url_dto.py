from typing import Optional
from pydantic import BaseModel


class UrlDto(BaseModel):
    """
    URL 데이터 교환을 위한 DTO
    """

    url_id: int
    url: str
    status: str
    title: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
