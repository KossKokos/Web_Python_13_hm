from typing import List

from pydantic import EmailStr
from fastapi import APIRouter, Depends, Path, status
from fastapi.security import HTTPBearer
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import contacts as schemas_contacts
from src.repository import contacts as repository_contacts
from src.services.auth import service_auth
from src.database.models import User, Contact

router = APIRouter(prefix='/contacts', tags=["contacts"])
security = HTTPBearer()


@router.get('/', response_model=List[schemas_contacts.ContactResponce], 
                 description='No more than 3 requests each 4 seconds',
                #  dependencies = [Depends(RateLimiter(times=3, seconds=4))],
                 status_code=status.HTTP_200_OK)
async def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                        current_user: User = Depends(service_auth.get_current_user)):
    """
    The read_contacts function returns a list of contacts for the current user.
        The skip and limit parameters are used to paginate the results.
    
    
    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    """
    contacts = await repository_contacts.get_contacts(current_user, skip, limit, db)
    return contacts


@router.get('/birthdays', response_model=List[schemas_contacts.ContactResponce],
                          description='No more than 3 requests each 4 seconds',)
                        #   dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def read_birthdays(db: Session = Depends(get_db), 
                         current_user: User = Depends(service_auth.get_current_user)):
    """
    The read_birthdays function returns a list of contacts with birthdays in the current week.
        The function requires an authenticated user.
    
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    """
    contacts = await repository_contacts.get_birthdays(current_user, db)
    return contacts

# adding parametr {contact_id} to path and finding a contact using that id
@router.get('/{contact_id}', response_model=schemas_contacts.ContactResponce,
                             description='No more than 3 requests each 4 seconds',
                             status_code=status.HTTP_200_OK)
                            #  dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def read_contact_by_id(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                             current_user: User = Depends(service_auth.get_current_user)):
    """
    The read_contact_by_id function returns a contact by its id.
        Args:
            contact_id (int): The id of the contact to be returned.
            db (Session, optional): A database session object for interacting with the database. Defaults to Depends(get_db).
            current_user (User, optional): The user currently logged in and making this request. Defaults to Depends(service_auth.get_current_user).
        Returns:
            Contact: A single Contact object matching the given id.
    
    :param contact_id: int: Get the contact_id from the url
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user from the database
    :return: A contact object
    """
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user, db)
    return contact


@router.get('/firstname/{contact_first_name}', response_model=schemas_contacts.ContactResponce,
                                               description='No more than 3 requests each 4 seconds',
                                               status_code=status.HTTP_200_OK,)
                                            #    dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def read_contact_by_firstname(contact_first_name : str = Path(min_length=3, max_length=50), db: Session = Depends(get_db),
                                    current_user: User = Depends(service_auth.get_current_user)):
    """
    The read_contact_by_firstname function returns a contact object based on the first name of the contact.
        The function takes in a string representing the first name of the contact, and returns an object containing all information about that specific user.
    
    :param contact_first_name : str: Get the contact by first name
    :param max_length: Specify the maximum length of the string
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user information
    :return: A contact object
    """
    contact = await repository_contacts.get_contact_by_firstname(contact_first_name, current_user, db)
    return contact


@router.get('/lastname/{contact_last_name}', response_model=schemas_contacts.ContactResponce,
                                             description='No more than 3 requests each 4 seconds',
                                             dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def read_contact_by_lastname(contact_last_name: str = Path(min_length=3, max_length=60), db: Session = Depends(get_db),
                                   current_user: User = Depends(service_auth.get_current_user)):
    """
    The read_contact_by_lastname function returns a contact by last name.
        Args:
            contact_last_name (str): The last name of the desired contact.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            current_user (User, optional): User object for the currently logged in user. Defaults to Depends(service_auth.get_current_user).
    
    :param contact_last_name: str: Pass the contact last name to the function
    :param max_length: Limit the length of the string
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user_id of the logged in user
    :return: A single contact with the same last name
    """
    contact = await repository_contacts.get_contact_by_lastname(contact_last_name, current_user, db)
    return contact


@router.get('/email/{contact_email}', response_model=schemas_contacts.ContactResponce,
                                      description='No more than 3 requests each 4 seconds',
                                      dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def read_contact_by_email(contact_email: EmailStr, db: Session = Depends(get_db),
                                current_user: User = Depends(service_auth.get_current_user)):
    """
    The read_contact_by_email function returns a contact by email.
        Args:
            contact_email (str): The email of the contact to be returned.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            current_user (User, optional): User object for the user making this request. Defaults to Depends(service_auth.get_current_user).
    
    :param contact_email: EmailStr: Get the email of a contact
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user information from the database
    :return: A contact object
    """
    contact = await repository_contacts.get_contact_by_email(contact_email, current_user, db)
    return contact

# adding a form ContactModel so user can create new contact by filling this form
@router.post('/', response_model=schemas_contacts.ContactResponce, status_code=status.HTTP_201_CREATED,
                  description='No more than 3 contacts each 10 seconds',)
                #   dependencies = [Depends(RateLimiter(times=3, seconds=10))])
async def create_contact(body: schemas_contacts.ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
        The function takes a body parameter, which is an instance of ContactModel.
        It also takes two optional parameters: db and current_user. 
        If no db parameter is passed, it will use the get_db() function to create one for you.
        current_user (User, optional): User object for the user making this request. Defaults to Depends(service_auth.get_current_user).
    
    :param body: schemas_contacts.ContactModel: Validate the request body
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: A contact object, from the database
    """
    contact = await repository_contacts.add_contact(body, current_user, db)
    return contact

# adding a form ContactFirstName so user can update old name by including new one in this form
@router.patch('/first_name/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                          description='No more than 3 requests each 4 seconds',
                                          status_code=status.HTTP_202_ACCEPTED,)
                                        #   dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def update_contact_firstname(body: schemas_contacts.ContactFirstNameUpdate, contact_id: int = Path(ge=1), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    """
    The update_contact_firstname function updates the firstname of a contact.
        The function takes in a body containing the new firstname, and an id for which contact to update.
        It also takes in current_user and db as dependencies.
    
    :param body: schemas_contacts.ContactFirstNameUpdate: Get the data from the request body
    :param contact_id: int: Identify the contact that is to be updated
    :param db: Session: Access the database
    :param current_user: User: Get the logged in user
    :return: The contact object that was updated
    """
    contact = await repository_contacts.update_contact_firstname(body, contact_id, current_user, db)
    return contact


@router.patch('/last_name/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                         description='No more than 3 requests each 4 seconds',
                                         dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def update_contact_lastname(body: schemas_contacts.ContactLastNameUpdate, contact_id: int = Path(ge=1), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    """
    The update_contact_lastname function updates the last name of a contact.
        Args:
            body (schemas_contacts.ContactLastNameUpdate): The new last name for the contact.
            contact_id (int): The ID of the contact to update.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            current_user (User, optional): User object for the user making this request. Defaults to Depends(service_auth.get_current_user).
    
    :param body: schemas_contacts.ContactLastNameUpdate: Get the data from the request body
    :param contact_id: int: Get the contact id from the path
    :param db: Session: Access the database
    :param current_user: User: Get the user information from the database
    :return: A contact object
    """
    contact = await repository_contacts.update_contact_lastname(body, contact_id, current_user, db)
    return contact


@router.patch('/email/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                     description='No more than 3 requests each 4 seconds',
                                     dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def update_contact_email(body: schemas_contacts.ContactEmailUpdate, contact_id: int = Path(ge=1), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    """
    The update_contact_email function updates the email address of a contact.
        The function takes in a ContactEmailUpdate object, which contains an email field. 
        It also takes in the id of the contact to be updated and returns that same contact with its new information.
    
    :param body: schemas_contacts.ContactEmailUpdate: Pass the data from the request body to the function
    :param contact_id: int: Get the contact_id from the url
    :param db: Session: Get the database session
    :param current_user: User: Get the user from the token
    :return: A contact object
    """
    contact = await repository_contacts.update_contact_email(body, contact_id, current_user, db)
    return contact


@router.patch('/phone/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                     description='No more than 3 requests each 4 seconds',
                                     dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def update_contact_phone(body: schemas_contacts.ContactPhoneUpdate, contact_id: int = Path(ge=1), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    """
    The update_contact_phone function updates a contact's phone number.
        Args:
            body (schemas_contacts.ContactPhoneUpdate): The updated phone number for the contact.
            contact_id (int): The ID of the contact to update their phone number in the database.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            current_user (User, optional): User object for the user making this request. Defaults to Depends(service_auth.get_current_user).
    
    :param body: schemas_contacts.ContactPhoneUpdate: Get the data from the request body
    :param contact_id: int: Identify the contact to update
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: A contact object
    """
    contact = await repository_contacts.update_contact_phone(body, contact_id, current_user, db)
    return contact


@router.patch('/birthdate/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                         description='No more than 3 requests each 4 seconds',              
                                         dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def update_contact_birthdate(body: schemas_contacts.ContactBirthdateUpdate, contact_id: int = Path(ge=1), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    """
    The update_contact_birthdate function updates the birthdate of a contact.
        The function takes in a ContactBirthdateUpdate object, which contains the new birthdate for the contact.
        It also takes in an integer representing the ID of the contact to be updated, and it uses this ID to find 
        that specific contact within our database.
        
        The function then calls upon update_contact_birthdate from repository_contacts, which is where all of our SQLAlchemy code is stored. 
         This function will update that specific user's birth date with whatever was passed into body
    
    :param body: schemas_contacts.ContactBirthdateUpdate: Get the data from the request body
    :param contact_id: int: Get the contact id from the url
    :param db: Session: Access the database
    :param current_user: User: Get the current user
    :return: A contact object
    """
    contact = await repository_contacts.update_contact_birthdate(body, contact_id, current_user, db)
    return contact


@router.patch('/description/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                           description='No more than 3 requests each 4 seconds',
                                           dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def update_contact_description(body: schemas_contacts.ContactDescriptionUpdate, contact_id: int = Path(ge=1), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    """
    The update_contact_description function updates the description of a contact.
        The function takes in a ContactDescriptionUpdate object, which contains the new description for the contact.
        It also takes in an integer representing the ID of the contact to be updated and two dependencies: 
        
            A database session (db)
            The current user (current_user)
    
    :param body: schemas_contacts.ContactDescriptionUpdate: Get the data from the request body
    :param contact_id: int: Identify the contact's that has to be updated
    :param db: Session: Access the database
    :param current_user: User: Get the current user
    :return: A contact object
    """
    contact = await repository_contacts.update_contact_description(body, contact_id, current_user, db)
    return contact

# delete contact by using contact_id
@router.delete('/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                description='No more than 3 requests each 4 seconds',
                                status_code=status.HTTP_202_ACCEPTED,)
                                # dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            db (Session): A connection to the database.
            current_user (User): The user who is making this request, as determined by service_auth's get_current_user function.
    
    :param contact_id: int: Specify the contact id of the contact to be deleted
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A contact object
    """
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)
    return contact