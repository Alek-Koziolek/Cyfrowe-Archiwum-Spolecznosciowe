import asyncio

from sqlalchemy import select

from app.config import settings
from app.database import engine, async_session, Base
from app.models.hierarchy import HierarchyNode, HierarchyLevel
from app.models.user import User, UserRole
from app.utils.security import hash_password


WOJEWODZTWA = [
    "Dolnośląskie",
    "Kujawsko-Pomorskie",
    "Lubelskie",
    "Lubuskie",
    "Łódzkie",
    "Małopolskie",
    "Mazowieckie",
    "Opolskie",
    "Podkarpackie",
    "Podlaskie",
    "Pomorskie",
    "Śląskie",
    "Świętokrzyskie",
    "Warmińsko-Mazurskie",
    "Wielkopolskie",
    "Zachodniopomorskie",
]


def slugify(name: str) -> str:
    replacements = {
        "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n",
        "ó": "o", "ś": "s", "ź": "z", "ż": "z",
    }
    slug = name.lower()
    for pl, ascii_char in replacements.items():
        slug = slug.replace(pl, ascii_char)
    return slug.replace(" ", "-")


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        for name in WOJEWODZTWA:
            slug = slugify(name)
            result = await db.execute(
                select(HierarchyNode).where(HierarchyNode.slug == slug)
            )
            if not result.scalar_one_or_none():
                node = HierarchyNode(
                    name=name,
                    slug=slug,
                    level=HierarchyLevel.WOJEWODZTWO,
                    parent_id=None,
                )
                db.add(node)

        await db.commit()
        print(f"Seeded {len(WOJEWODZTWA)} voivodeships.")

    async with async_session() as db:
        result = await db.execute(
            select(User).where(User.email == settings.ADMIN_EMAIL)
        )
        if not result.scalar_one_or_none():
            admin = User(
                email=settings.ADMIN_EMAIL,
                display_name="Administrator",
                password_hash=hash_password(settings.ADMIN_DEFAULT_PASSWORD),
                role=UserRole.ADMIN,
            )
            db.add(admin)
            await db.commit()
            print(f"Seeded admin account: {settings.ADMIN_EMAIL} / {settings.ADMIN_DEFAULT_PASSWORD}")
        else:
            print(f"Admin account already exists: {settings.ADMIN_EMAIL}")


if __name__ == "__main__":
    asyncio.run(seed())
