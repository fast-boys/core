from typing import List, Dict, Optional
from pydantic import BaseModel


class UserInfoResponse(BaseModel):
    username: str
    profileImage: str
