from pydantic import BaseModel
from .user import User, UserCreate, UserUpdate
from .cycle import Cycle, CycleCreate, CycleUpdate
from .token import Token, TokenPayload
from .password_reset import PasswordRecoveryRequest, PasswordResetConfirm

class Msg(BaseModel):
    msg: str
