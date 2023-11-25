
from fastapi import APIRouter, Depends, Depends, HTTPException, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session


from src.services.auth import service_auth
from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas import users as schema_users, token as schema_token
from src.services.email import send_email, send_reset_password_email
from src.schemas.email import RequestEmail
from src.schemas.users import ChangePassword

router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(body: schema_users.UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'User with email: {body.email} already exists')
    body.password = service_auth.get_password_hash(body.password)
    user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {'user': user, 'detail': 'User successfully created, please check your email for verification'}


@router.post("/login", response_model=schema_token.TokenResponce, status_code=status.HTTP_202_ACCEPTED)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email is not confirmed')
    if not service_auth.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await service_auth.create_access_token(data={"sub": user.email})
    refresh_token = await service_auth.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=schema_token.TokenResponce)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await service_auth.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        user.refresh_token = None
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    access_token = await service_auth.create_access_token(data={"sub": email})
    refresh_token = await service_auth.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirm_email(token: str, db: Session = Depends(get_db)):
    email = await service_auth.decode_email_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    if user.confirmed:
        return {'message': 'Email is already confirmed'}
    await repository_users.confirmed_email(email, db)
    return {'message': 'email is confirmed'}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_task: BackgroundTasks, 
                        request: Request, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user.confirmed:
        return {'message': 'Email is already confirmed'}
    if user:
        background_task.add_task(send_email, user.email, user.username, request.base_url)
    return 'Check your email for further information'


@router.post('/reset_password')
async def reset_password_request(body: RequestEmail, background_task: BackgroundTasks,
                          request: Request, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        background_task.add_task(send_reset_password_email, user.email, user.username, request.base_url)
    return 'Check your email for further information'


@router.patch('/change_password/{token}')
async def reset_password(body: ChangePassword, token: str, db: Session = Depends(get_db)):
    email = await service_auth.decode_email_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    body.new_password = service_auth.get_password_hash(body.new_password)
    await repository_users.change_password(user, body.new_password, db)
    return "User's password was changed succesfully"
    