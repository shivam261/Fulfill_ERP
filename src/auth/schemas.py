from sqlmodel import SQLModel, Field
from typing import Optional

class Login_user_response(SQLModel):
    message: str="Login Successful"
    username: str

class Login_user_request(SQLModel):
    username: str
    password: str

class Register_user_response(SQLModel):
    message: str="Registration Successful"
    username: str