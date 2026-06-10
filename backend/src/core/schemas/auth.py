from pydantic import BaseModel, EmailStr

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str