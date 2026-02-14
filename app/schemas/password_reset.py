from pydantic import BaseModel, EmailStr

class PasswordRecoveryRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str
