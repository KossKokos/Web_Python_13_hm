from datetime import date
from pydantic import BaseModel, Field, EmailStr


class ContactModel(BaseModel):
    first_name: str = Field(min_length=3, max_length=50, default='contact firstname')
    last_name: str = Field(min_length=3, max_length=60, default='contact lastname')
    email: EmailStr = Field(default='example@mail.com')
    phone_number: str = Field(min_length=10, max_length=20, default='+38 (000) 000 00 00')
    birth_date: date
    description: str = Field(max_length=300,  default='some additional info, not required')
  

class ContactResponce(BaseModel):
    id: int = 1
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=60)
    email: EmailStr
    phone_number: str = Field(min_length=10, max_length=20)
    birth_date: date
    description: str = Field(max_length=300)

    class Config:
        orm_mode = True


class ContactFirstNameUpdate(BaseModel):
    first_name: str = Field(min_length=3, max_length=50) 


class ContactLastNameUpdate(BaseModel):
    last_name: str = Field(min_length=3, max_length=60)
    

class ContactEmailUpdate(BaseModel):
    email: EmailStr


class ContactPhoneUpdate(BaseModel):
    phone_number: str = Field(min_length=10, max_length=20)


class ContactBirthdateUpdate(BaseModel):
    birth_date: date


class ContactDescriptionUpdate(BaseModel):
    description: str = Field(max_length=300)
    

