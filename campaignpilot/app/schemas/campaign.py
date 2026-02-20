from pydantic import BaseModel


class OutreachSendResponse(BaseModel):
    campaign_id: int
    request_id: int
    task_id: str
    status: str
    idempotent_replay: bool = False
