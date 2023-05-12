from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from apscheduler.schedulers.background import BackgroundScheduler

DATABASE_URL = "sqlite:///./test.db"  # Change this to your actual database URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class TabInfo(Base):
    __tablename__ = "tabs"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    title = Column(String)
    text = Column(Text)

Base.metadata.create_all(bind=engine)

class TabData(BaseModel):
    url: str
    title: str
    text: str

class Message(BaseModel):
    text: str

app = FastAPI()

origins = [
    "chrome-extension://jbpiganbopfklakhmdfocjckeeclpmmm",  # Replace this with your extension's ID
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_chatbot_response(message):
    # This function is just a placeholder. Replace it with your actual chatbot model.
    # For now, it just repeats the input message.
    return message

def delete_old_tabs():
    db: Session = SessionLocal()
    num_tabs = db.query(TabInfo).count()
    if num_tabs > 10:
        num_tabs_to_delete = num_tabs - 10
        old_tabs_ids = db.query(TabInfo.id).order_by(TabInfo.id).limit(num_tabs_to_delete).all()
        for tab_id in old_tabs_ids:
            db.query(TabInfo).filter(TabInfo.id == tab_id[0]).delete(synchronize_session=False)
        db.commit()
    db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_tabs, 'interval', minutes=1)
scheduler.start()

@app.post("/store")
async def store_tab_data(tabdata: TabData):
    db = SessionLocal()
    db_tab = TabInfo(url=tabdata.url, title=tabdata.title, text=tabdata.text)
    db.add(db_tab)
    db.commit()
    db.refresh(db_tab)
    print(f"Stored tab data: {db_tab.id}, {db_tab.url}, {db_tab.title}")  # Print tab data
    print(f"Tab content: {db_tab.text}")  # Print tab content
    db.close()
    return {"response": "Data stored successfully"}


@app.post("/process")
async def process_message(message: Message):
    # Process the input message with the chatbot model and get the response
    response = get_chatbot_response(message.text)
    print(f"Received message: {message.text}")  # Print received message
    return {"response": response}