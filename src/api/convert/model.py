from pydantic import BaseModel
from typing import Optional, Any

class ApiResponse(BaseModel):
    status: str
    message: str 
    data: Optional[Any] = None
   