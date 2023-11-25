
from datetime import date, timedelta
from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas.contacts import ContactModel
from src.database.models import User


async def get_contacts(user, skip: int, limit: int, db: Session):
    return db.query(Contact).filter(Contact.user_id==user.id).offset(skip).limit(limit).all()


async def get_contact_by_id(contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    return contact


async def get_contact_by_firstname(contact_firstname: str, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.first_name==contact_firstname)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    return contact


async def get_contact_by_lastname(contact_lastname: str, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.last_name==contact_lastname)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    return contact


async def get_contact_by_email(contact_email: str, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.email==contact_email)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    return contact


async def get_birthdays(user: User, db: Session):
    current_date = date.today()
    current_week_dates = []
    for _ in range(7):
        current_date += timedelta(days=1)
        current_week_dates.append(current_date)
    contacts = db.query(Contact).filter(Contact.user_id==user.id).all()
    result = []
    for contact in contacts:
        needed_year = contact.birth_date.replace(year=current_date.year)
        if needed_year in current_week_dates:
            result.append(contact)
    return result


async def add_contact(body: ContactModel, user: User, db: Session):
    contact = db.query(Contact).filter_by(first_name=body.first_name).first()
    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Contact with this first name already exists')
    contact = Contact(**body.dict())
    contact.user_id = user.id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    db.delete(contact)
    db.commit()
    return contact


async def update_contact_firstname(body: ContactModel, contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    contact.first_name = body.first_name
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact_lastname(body: ContactModel, contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    contact.last_name = body.last_name
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact_email(body: ContactModel, contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    contact.email = body.email
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact_phone(body: ContactModel, contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    contact.phone_number = body.phone_number
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact_birthdate(body: ContactModel, contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    contact.birth_date = body.birth_date
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact_description(body: ContactModel, contact_id: int, user: User, db: Session):
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    contact.description = body.description
    db.commit()
    db.refresh(contact)
    return contact