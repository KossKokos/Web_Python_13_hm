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
from src.database.models import User

router = APIRouter(prefix='/contacts', tags=["contacts"])
security = HTTPBearer()


@router.get('/', response_model=List[schemas_contacts.ContactResponce], 
                 description='No more than 3 requests each 4 seconds',
                 dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                        current_user: User = Depends(service_auth.get_current_user)):
    contacts = await repository_contacts.get_contacts(current_user, skip, limit, db)
    return contacts


@router.get('/birthdays', response_model=List[schemas_contacts.ContactResponce],
                          description='No more than 3 requests each 4 seconds',
                          dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def read_birthdays(db: Session = Depends(get_db), 
                         current_user: User = Depends(service_auth.get_current_user)):
    contacts = await repository_contacts.get_birthdays(current_user, db)
    return contacts

# adding parametr {contact_id} to path and finding a contact using that id
@router.get('/{contact_id}', response_model=schemas_contacts.ContactResponce,
                             description='No more than 3 requests each 4 seconds',
                             dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def read_contact_by_id(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                             current_user: User = Depends(service_auth.get_current_user)):
    contact = await repository_contacts.get_contact_by_id(contact_id, current_user, db)
    return contact


@router.get('/firstname/{contact_first_name}', response_model=schemas_contacts.ContactResponce,
                                               description='No more than 3 requests each 4 seconds',
                                               dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def read_contact_by_firstname(contact_first_name : str = Path(min_length=3, max_length=50), db: Session = Depends(get_db),
                                    current_user: User = Depends(service_auth.get_current_user)):
    contact = await repository_contacts.get_contact_by_firstname(contact_first_name, current_user, db)
    return contact


@router.get('/lastname/{contact_last_name}', response_model=schemas_contacts.ContactResponce,
                                             description='No more than 3 requests each 4 seconds',
                                             dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def read_contact_by_lastname(contact_last_name: str = Path(min_length=3, max_length=60), db: Session = Depends(get_db),
                                   current_user: User = Depends(service_auth.get_current_user)):
    contact = await repository_contacts.get_contact_by_lastname(contact_last_name, current_user, db)
    return contact


@router.get('/email/{contact_email}', response_model=schemas_contacts.ContactResponce,
                                      description='No more than 3 requests each 4 seconds',
                                      dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def read_contact_by_email(contact_email: EmailStr, db: Session = Depends(get_db),
                                current_user: User = Depends(service_auth.get_current_user)):
    contact = await repository_contacts.get_contact_by_email(contact_email, current_user, db)
    return contact

# adding a form ContactModel so user can create new contact by filling this form
@router.post('/', response_model=schemas_contacts.ContactResponce, status_code=status.HTTP_201_CREATED,
                  description='No more than 3 contacts each 10 seconds',
                  dependencies = [Depends(RateLimiter(times=3, seconds=10))])
async def create_contact(body: schemas_contacts.ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    contact = await repository_contacts.add_contact(body, current_user, db)
    return contact

# adding a form ContactFirstName so user can update old name by including new one in this form
@router.patch('/first_name/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                          description='No more than 3 requests each 4 seconds',
                                          dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def update_contact_firstname(body: schemas_contacts.ContactFirstNameUpdate, contact_id: int = Path(ge=1), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    contact = await repository_contacts.update_contact_firstname(body, contact_id, current_user, db)
    return contact


@router.patch('/last_name/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                         description='No more than 3 requests each 4 seconds',
                                         dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def update_contact_lastname(body: schemas_contacts.ContactLastNameUpdate, contact_id: int = Path(ge=1), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    contact = await repository_contacts.update_contact_lastname(body, contact_id, current_user, db)
    return contact


@router.patch('/email/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                     description='No more than 3 requests each 4 seconds',
                                     dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def update_contact_email(body: schemas_contacts.ContactEmailUpdate, contact_id: int = Path(ge=1), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    contact = await repository_contacts.update_contact_email(body, contact_id, current_user, db)
    return contact


@router.patch('/phone/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                     description='No more than 3 requests each 4 seconds',
                                     dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def update_contact_phone(body: schemas_contacts.ContactPhoneUpdate, contact_id: int = Path(ge=1), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    contact = await repository_contacts.update_contact_phone(body, contact_id, current_user, db)
    return contact


@router.patch('/birthdate/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                         description='No more than 3 requests each 4 seconds',              
                                         dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def update_contact_birthdate(body: schemas_contacts.ContactBirthdateUpdate, contact_id: int = Path(ge=1), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    contact = await repository_contacts.update_contact_birthdate(body, contact_id, current_user, db)
    return contact


@router.patch('/description/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                           description='No more than 3 requests each 4 seconds',
                                           dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def update_contact_description(body: schemas_contacts.ContactDescriptionUpdate, contact_id: int = Path(ge=1), 
                         db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    contact = await repository_contacts.update_contact_description(body, contact_id, current_user, db)
    return contact

# delete contact by using contact_id
@router.delete('/{contact_id}', response_model=schemas_contacts.ContactResponce,
                                description='No more than 3 requests each 4 seconds',
                                dependencies = [Depends(RateLimiter(times=3, seconds=4))])
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(service_auth.get_current_user)):
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)
    return contact