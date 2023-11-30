import uvicorn
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from src.routes import contacts, auth, users

app = FastAPI()

# create route so i don't need to add contacts/... everytime to my routes functions
app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# async def startup() -> None:
#     """
#     The startup function is called when the application starts up.
#     It's a good place to initialize things that are needed by your app, like database connections or caches.
    
#     :return: None
#     """
#     r = redis.Redis(host='localhost', port=6379, db=0, encoding='utf-8', decode_responses=True)
#     await FastAPILimiter.init(r)

@app.get("/")
async def read_root():
    """
    The read_root function returns a JSON object with the message: Hello World.
    
    :return: A dict
    """
    return {"message": "Hello World"}

# start server, main:app - name of the file and app - Fastapi, reload=True - for authomatical reload
if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)