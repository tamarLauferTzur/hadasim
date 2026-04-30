from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from auth import get_current_teacher, make_token
from database import init_db
from models import Location, User
from schemas import LoginRequest, RegisterRequest, StudentsScope, UpdateLocationRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return RedirectResponse(url="/app/")


@app.post("/register")
async def register(data: RegisterRequest):
    if data.role not in ("student", "teacher"):
        raise HTTPException(status_code=400, detail="role must be student or teacher")
    existing = await User.find_one(User.user_id == data.user_id)
    if existing is not None:
        raise HTTPException(status_code=400, detail="user already exists")
    user = User(
        user_id=data.user_id,
        name=data.name,
        class_name=data.class_name,
        role=data.role,
        password=data.password,
    )
    await user.insert()
    return {"message": "registered"}


@app.post("/login")
async def login(data: LoginRequest):
    user = await User.find_one(User.user_id == data.user_id)
    if user is None or user.password != data.password:
        raise HTTPException(status_code=401, detail="wrong id or password")
    user.token = make_token()
    await user.save()
    return {"token": user.token}


@app.post("/update_location")
async def update_location(data: UpdateLocationRequest):
    user = await User.find_one(User.user_id == data.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    user.location = Location(coordinates=data.coordinates, time=data.time)
    await user.save()
    return {"message": "location updated"}


@app.get("/me")
async def get_me(teacher: User = Depends(get_current_teacher)):
    return {
        "user_id": teacher.user_id,
        "name": teacher.name,
        "class_name": teacher.class_name,
        "role": teacher.role,
        "location": teacher.location,
    }


@app.get("/students")
async def get_students(
    scope: StudentsScope = StudentsScope.MY_CLASS,
    teacher: User = Depends(get_current_teacher),
):
    if scope == StudentsScope.ALL_STUDENTS:
        users = await User.find(User.role == "student").to_list()
    elif scope == StudentsScope.ALL_TEACHERS:
        users = await User.find(User.role == "teacher").to_list()
    else:
        users = await User.find(
            User.role == "student",
            User.class_name == teacher.class_name,
        ).to_list()
    return [
        {
            "user_id": u.user_id,
            "name": u.name,
            "class_name": u.class_name,
            "role": u.role,
            "location": u.location,
        }
        for u in users
    ]


@app.get("/students/{student_id}/location")
async def get_student_location(student_id: int, teacher: User = Depends(get_current_teacher)):
    student = await User.find_one(User.user_id == student_id)
    if student is None or student.role != "student":
        raise HTTPException(status_code=404, detail="student not found")
    if student.class_name != teacher.class_name:
        raise HTTPException(status_code=403, detail="not your class")
    return student.location


app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)