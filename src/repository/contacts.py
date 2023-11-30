
from datetime import date, timedelta
from fastapi import HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas.contacts import (
    ContactModel, 
    ContactFirstNameUpdate, 
    ContactLastNameUpdate, 
    ContactEmailUpdate,
    ContactBirthdateUpdate,
    ContactPhoneUpdate,
    ContactDescriptionUpdate
    )

from src.database.models import User


async def get_contacts(user, skip: int, limit: int, db: Session):
    """
    The get_contacts function returns a list of contacts for the user.
    
    :param user: logged user's object from the database
    :param skip: int: Skip the first n contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the function
    :return: A list of contacts
    """
    return db.query(Contact).filter(Contact.user_id==user.id).offset(skip).limit(limit).all()


async def get_contact_by_id(contact_id: int, user: User, db: Session):
    """
    The get_contact_by_id function returns a contact object from the database.
        The function takes in an integer representing the id of a contact, and an user's object from db.
        It also takes in a Session object to query the database with.
        If no such contact exists, it raises HTTPException 404 Not Found.
    
    :param contact_id: int: Specify the id of the contact to be retrieved
    :param user: User: logged user's object from database
    :param db: Session: Access the database
    :return: A contact object
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    return contact


async def get_contact_by_firstname(contact_firstname: str, user: User, db: Session):
    """
    The get_contact_by_firstname function returns a contact object based on the first name of the contact.
        If no such contact exists, an HTTP 404 error is raised.
    
    :param contact_firstname: str: Specify the first name of the contact to be retrieved
    :param user: User: logged user's object from database
    :param db: Session: Access the database
    :return: The contact object
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.first_name==contact_firstname)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    return contact


async def get_contact_by_lastname(contact_lastname: str, user: User, db: Session):
    """
    The get_contact_by_lastname function returns a contact object based on the last name of the contact.
        If no such contact exists, an HTTP 404 error is raised.
    
    :param contact_lastname: str: Specify the last name of the contact we want to retrieve
    :param user: User: logged user's object from database
    :param db: Session: Access the database
    :return: The contact object
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.last_name==contact_lastname)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    return contact


async def get_contact_by_email(contact_email: str, user: User, db: Session):
    """
    The get_contact_by_email function returns a contact object from the database based on the email address provided.
        If no contact is found, an HTTP 404 error is raised.
    
    :param contact_email: str: Get the email of the contact
    :param user: User: logged user's object from database
    :param db: Session: Access the database
    :return: The contact with the specified email address
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.email==contact_email)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    return contact


async def get_birthdays(user: User, db: Session):
    """
    The get_birthdays function returns a list of contacts whose birthdays are in the current week.
    
    :param user: User: logged user's object from database
    :param db: Session: Access the database
    :return: A list of contacts
    """
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
    """
    The add_contact function creates a new contact in the database.
        It takes a ContactModel object as input and returns the newly created ContactModel object.
        If there is already an existing contact with that first name, it will return an error.
    
    :param body: ContactModel: Get the data from the request body
    :param user: User: logged user's object from database
    :param db: Session: Access the database
    :return: The contact object
    """
    contact = db.query(Contact).filter(Contact.first_name==body.first_name).first()
    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Contact with this first name already exists')
    contact = Contact(**body.dict())
    contact.user_id = user.id
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, user: User, db: Session):
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            user (User): The user who is deleting the contact.
            db (Session): A connection to our database session, used for querying and committing changes.
    
    :param contact_id: int: Specify the id of the contact to be deleted
    :param user: User: logged user's object from database
    :param db: Session: Access the database
    :return: The deleted contact
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    db.delete(contact)
    db.commit()
    return contact


async def update_contact_firstname(body: ContactFirstNameUpdate, contact_id: int, user: User, db: Session):
    """
    The update_contact_firstname function updates the first name of a contact.
        Args:
            body (ContactFirstNameUpdate): The new first name for the contact.
            contact_id (int): The id of the contact to update.
            user (User): The current user, used to verify that they own this resource.
            db (Session, optional): SQLAlchemy Session instance, defaults to None.
    
    :param body: ContactFirstNameUpdate: Pass the new first name to the function
    :param contact_id: int: Identify the contact to be updated
    :param user: User: logged user's object from database
    :param db: Session: Access the database
    :return: A contact object
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    contact.first_name = body.first_name
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact_lastname(body: ContactLastNameUpdate, contact_id: int, user: User, db: Session):
    """
    The update_contact_lastname function updates the last name of a contact in the database.
        The function takes three arguments:
            - body: A ContactLastNameUpdate object containing the new last name for a contact
            - contact_id: An integer representing the id of a specific contact to update
            - user: A User object representing an authenticated user making this request
    
    :param body: ContactLastNameUpdate: Access the last_name field of the contactlastnameupdate class
    :param contact_id: int: Identify the contact to be updated
    :param user: User: logged user's object from database
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    contact.last_name = body.last_name
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact_email(body: ContactEmailUpdate, contact_id: int, user: User, db: Session):
    """
    The update_contact_email function updates the email of a contact in the database.
    
    Args:
        body (ContactEmailUpdate): The new email for the contact.
        contact_id (int): The id of the contact to update.
        user (User): The current user, used to verify that they own this resource.  

    :param body: ContactEmailUpdate: Pass the email address to be updated
    :param contact_id: int: Identify the contact to update
    :param user: User: Ensure that the user is authenticated and has access to the contact they are trying to update
    :param db: Session: Access the database
    :return: A contact object
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    contact.email = body.email
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact_phone(body: ContactPhoneUpdate, contact_id: int, user: User, db: Session):
    """
    The update_contact_phone function updates a contact's phone number.
        Args:
            body (ContactPhoneUpdate): The new phone number for the contact.
            contact_id (int): The id of the contact to update.
            user (User): The current logged in user, used to determine which contacts belong to this user.
            db (Session, optional): SQLAlchemy Session instance, used when updating a database record.
    
    :param body: ContactPhoneUpdate: Pass the phone number to be updated
    :param contact_id: int: Identify the contact to be updated
    :param user: User: logged user's object from database
    :param db: Session: Access the database
    :return: A contact object
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    contact.phone_number = body.phone_number
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact_birthdate(body: ContactBirthdateUpdate, contact_id: int, user: User, db: Session):
    """
    The update_contact_birthdate function updates the birthdate of a contact.
        Args:
            body (ContactBirthdateUpdate): The new birth date for the contact.
            contact_id (int): The id of the contact to update.
            user (User): The current logged in user, used to determine if they have access to this resource.
            db (Session, optional): SQLAlchemy Session instance, used when creating a Contact object or querying for one.
    
    :param body: ContactBirthdateUpdate: Pass the data from the request body to this function
    :param contact_id: int: Identify the contact to update
    :param user: User: logged user's object from database
    :param db: Session: Access the database
    :return: The updated contact
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    contact.birth_date = body.birth_date
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact_description(body: ContactDescriptionUpdate, contact_id: int, user: User, db: Session):
    """
    The update_contact_description function updates the description of a contact.
        Args:
            body (ContactDescriptionUpdate): The new description for the contact.
            contact_id (int): The id of the contact to update.
            user (User): The current user, used to verify that they own this resource.
            db (Session, optional): SQLAlchemy Session. Defaults to None.
    
    :param body: ContactDescriptionUpdate: Pass the description to update
    :param contact_id: int: Identify which contact to update
    :param user: User: Identify the user who is making the request
    :param db: Session: Pass the database session to the function
    :return: The updated contact
    """
    contact = db.query(Contact).filter(and_(Contact.user_id==user.id, Contact.id==contact_id)).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Contact does not exist')
    contact.description = body.description
    db.commit()
    db.refresh(contact)
    return contact