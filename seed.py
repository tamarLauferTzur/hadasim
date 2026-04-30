import asyncio
import random
from datetime import datetime, timezone

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from models import Coordinates, DMS, Location, User


def decimal_to_dms(value):
    degrees = int(value)
    minutes_full = abs(value - degrees) * 60
    minutes = int(minutes_full)
    seconds = int(round((minutes_full - minutes) * 60))
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        degrees += 1 if value >= 0 else -1
    return DMS(degrees=degrees, minutes=minutes, seconds=seconds)


def random_location_near(lat, lng, jitter=0.05):
    rand_lat = lat + random.uniform(-jitter, jitter)
    rand_lng = lng + random.uniform(-jitter, jitter)
    return Location(
        coordinates=Coordinates(
            latitude=decimal_to_dms(rand_lat),
            longitude=decimal_to_dms(rand_lng),
        ),
        time=datetime.now(timezone.utc),
    )


FIRST_NAMES = [
    "Alice", "Bob", "Carol", "Dan", "Eve", "Frank", "Grace", "Hank",
    "Ivy", "Jack", "Kate", "Liam", "Maya", "Noah", "Olivia", "Paul",
    "Quinn", "Ruth", "Sam", "Tara", "Uri", "Vera", "Will", "Xena",
    "Yara", "Zane",
]

LAST_NAMES = [
    "Cohen", "Levi", "Mizrahi", "Peretz", "Friedman", "Katz", "Goldberg",
    "Shapiro", "Avraham", "Ben-David", "Mor", "Tal", "Sharabi", "Azulay",
]

CLASSES = {
    "1A": (31.78, 35.21),
    "1B": (32.08, 34.78),
    "2A": (32.79, 34.99),
    "2B": (31.25, 34.79),
}


async def main():
    random.seed(42)

    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(database=client.school, document_models=[User])

    await User.delete_all()

    teacher_specs = [
        (1, "Teacher One",   "1A"),
        (2, "Teacher Two",   "1B"),
        (3, "Teacher Three", "2A"),
        (4, "Teacher Four",  "2B"),
    ]
    teachers = []
    for user_id, name, class_name in teacher_specs:
        center_lat, center_lng = CLASSES[class_name]
        teacher = User(
            user_id=user_id,
            name=name,
            class_name=class_name,
            role="teacher",
            password="1234",
            location=random_location_near(center_lat, center_lng),
        )
        await teacher.insert()
        teachers.append(teacher)

    next_student_id = 1001
    students_per_class = 25

    for class_name, (center_lat, center_lng) in CLASSES.items():
        for i in range(students_per_class):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            has_location = random.random() < 0.85
            location = random_location_near(center_lat, center_lng) if has_location else None

            student = User(
                user_id=next_student_id,
                name=f"{first} {last}",
                class_name=class_name,
                role="student",
                password="pw",
                location=location,
            )
            await student.insert()
            next_student_id += 1

    print("Seed complete.")
    print(f"Created {len(teachers)} teachers and {len(CLASSES) * students_per_class} students.")
    print()
    print("Simple teacher login -> ID: 1   password: 1234   (class 1A)")
    print("Other teachers: IDs 2, 3, 4 (classes 1B, 2A, 2B), all with password 1234")


if __name__ == "__main__":
    asyncio.run(main())
