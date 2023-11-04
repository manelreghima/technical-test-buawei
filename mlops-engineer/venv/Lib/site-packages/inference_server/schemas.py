from pydantic import Base64Bytes, BaseModel


class InferencePayload(BaseModel):
    image: Base64Bytes


class InferenceResult(BaseModel):
    category: str
