---
name: fastapi-backend
description: Build FastAPI backend with routes and middleware. Use when creating API endpoints.
---

When building FastAPI backend:

1. **Main app** (main.py):
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware

   app = FastAPI(title="Todo API")

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Routes** (routers/todos.py):
   ```python
   from fastapi import APIRouter, Depends, HTTPException
   from sqlalchemy.orm import Session

   router = APIRouter()

   @router.get("/todos")
   def list_todos(db: Session = Depends(get_db)):
       return db.query(Task).all()

   @router.post("/todos")
   def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
       db_task = Task(**todo.model_dump())
       db.add(db_task)
       db.commit()
       return db_task
   ```

3. **Dependencies** (database.py):
   ```python
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker

   engine = create_engine(DATABASE_URL)
   SessionLocal = sessionmaker(bind=engine)

   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   ```

4. **Pydantic schemas** (schemas.py):
   ```python
   from pydantic import BaseModel

   class TodoCreate(BaseModel):
       title: str
       description: str | None = None
       priority: str = "medium"
   ```

5. **Run server**: `uvicorn main:app --reload`
