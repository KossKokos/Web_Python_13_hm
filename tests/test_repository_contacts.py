import sys
from pathlib import Path
from datetime import date
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from fastapi import HTTPException

path_root = Path(__file__).parent.parent
sys.path.append(str(path_root))

from src.database.models import User, Contact
from src.schemas.contacts import (
    ContactModel,
    ContactFirstNameUpdate,
    ContactLastNameUpdate,
    ContactEmailUpdate,
    ContactPhoneUpdate,
    ContactBirthdateUpdate,
    ContactDescriptionUpdate
)

from src.repository.contacts import (
    get_contacts,
    get_contact_by_id,
    get_contact_by_firstname,
    get_contact_by_lastname,
    get_contact_by_email,
    get_birthdays,
    add_contact,
    delete_contact,
    update_contact_firstname,
    update_contact_lastname,
    update_contact_email,
    update_contact_phone,
    update_contact_birthdate,
    update_contact_description
)


class TestContacts(unittest.IsolatedAsyncioTestCase):
    

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)


    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts( user=self.user, skip=0, limit=10, db=self.session)
        self.assertEqual(result, contacts)


    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_id(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as err:
            await get_contact_by_id(contact_id=1, user=self.user, db=self.session)

    async def test_get_contact_by_firstname_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_firstname(contact_firstname='first_name', user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_get_contact_by_first_name_not_found(self):
        self.session.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as err:
            await get_contact_by_lastname(contact_lastname='last_name', user=self.user, db=self.session)

        
    async def test_get_contact_by_email_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_email(contact_email='email', user=self.user, db=self.session)
        self.assertEqual(result, contact)


    async def test_get_contact_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        with self.assertRaises(HTTPException) as err:
            await get_contact_by_email(contact_email='email', user=self.user, db=self.session)

    
    async def test_get_birthdays_found(self):
        contacts = [
            Contact(birth_date=date(year=2005, month=12, day=1)), 
            Contact(birth_date=date(year=2005, month=12, day=2)), 
            Contact(birth_date=date(year=2005, month=12, day=3))
        ]
        self.session.query().filter().all.return_value = contacts
        result = await get_birthdays(user=self.user, db=self.session)
        self.assertEqual(result, contacts)


    async def test_get_birthdays_not_found(self):
        empty_list = list()
        self.session.query().filter().all.return_value = []
        result = await get_birthdays(user=self.user, db=self.session)
        self.assertListEqual(result, empty_list)

    
    async def test_add_contact(self):
        contact_model = ContactModel(
            first_name='firstname', 
            last_name='lastname', 
            email='example@com.com', 
            phone_number='3809999999', 
            birth_date=date(2000, month=2, day=2)
        )
        self.session.query().filter().first.return_value = None
        result = await add_contact(body=contact_model, user=self.user, db=self.session)
        self.assertEqual(result.first_name, contact_model.first_name)
        self.assertEqual(result.last_name, contact_model.last_name)
        self.assertEqual(result.birth_date, contact_model.birth_date)
        self.assertEqual(result.phone_number, contact_model.phone_number)
        self.assertEqual(result.email, contact_model.email)
        self.assertEqual(result.description, contact_model.description)
        self.assertTrue(hasattr(result, 'id'))

    
    async def test_delete_contact(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    
    async def test_update_contact_first_name(self):
        contact = Contact()
        body = ContactFirstNameUpdate(first_name='firstname')
        self.session.query().filter().first.return_value = contact
        result = await update_contact_firstname(body=body, contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertTrue(hasattr(result, 'id'))


    async def test_update_contact_last_name(self):
        contact = Contact()
        body = ContactLastNameUpdate(last_name='lastname')
        self.session.query().filter().first.return_value = contact
        result = await update_contact_lastname(body=body, contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result.last_name, body.last_name)
        self.assertTrue(hasattr(result, 'id'))


    async def test_update_contact_email(self):
        contact = Contact()
        body = ContactEmailUpdate(email='example@com.com')
        self.session.query().filter().first.return_value = contact
        result = await update_contact_email(body=body, contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result.email, body.email)
        self.assertTrue(hasattr(result, 'id'))


    async def test_update_contact_phone(self):
        contact = Contact()
        body = ContactPhoneUpdate(phone_number='3809999999')
        self.session.query().filter().first.return_value = contact
        result = await update_contact_phone(body=body, contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertTrue(hasattr(result, 'id'))


    async def test_update_contact_description(self):
        contact = Contact()
        body = ContactDescriptionUpdate(description='hello world')
        self.session.query().filter().first.return_value = contact
        result = await update_contact_description(body=body, contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result.description, body.description)
        self.assertTrue(hasattr(result, 'id'))


    async def test_update_contact_birthdate(self):
        contact = Contact()
        body = ContactBirthdateUpdate(birth_date=date(year=2000, month=12, day=1))
        self.session.query().filter().first.return_value = contact
        result = await update_contact_birthdate(body=body, contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result.birth_date, body.birth_date)
        self.assertTrue(hasattr(result, 'id'))


if __name__ == '__main__':
    unittest.main()