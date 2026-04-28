from direm.db.models import User
from direm.repositories.base import Repository
from sqlalchemy import select


class UserRepository(Repository[User]):
    model = User

    async def get_by_telegram_user_id(self, telegram_user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_user_id == telegram_user_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        telegram_user_id: int,
        chat_id: int,
        username: str | None,
        first_name: str | None,
        timezone: str = "UTC",
        language_code: str = "ru",
    ) -> User:
        user = User(
            telegram_user_id=telegram_user_id,
            chat_id=chat_id,
            username=username,
            first_name=first_name,
            timezone=timezone,
            language_code=language_code,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_profile(
        self,
        user: User,
        *,
        chat_id: int,
        username: str | None,
        first_name: str | None,
    ) -> User:
        user.chat_id = chat_id
        user.username = username
        user.first_name = first_name
        await self.session.flush()
        return user

    async def update_timezone(self, user: User, timezone: str) -> User:
        user.timezone = timezone
        await self.session.flush()
        return user

    async def update_language(self, user: User, language_code: str) -> User:
        user.language_code = language_code
        await self.session.flush()
        return user
