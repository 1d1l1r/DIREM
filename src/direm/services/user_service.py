from dataclasses import dataclass

from direm.db.models import User
from direm.domain.schedules import validate_timezone
from direm.i18n import normalize_language_code
from direm.repositories.users import UserRepository


@dataclass(frozen=True)
class TelegramUserProfile:
    telegram_user_id: int
    chat_id: int
    username: str | None
    first_name: str | None
    language_code: str | None = None


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def get_by_telegram_user_id(self, telegram_user_id: int) -> User | None:
        return await self.user_repository.get_by_telegram_user_id(telegram_user_id)

    async def register_or_update_from_telegram(self, profile: TelegramUserProfile) -> User:
        user = await self.user_repository.get_by_telegram_user_id(profile.telegram_user_id)
        if user is None:
            return await self.user_repository.create(
                telegram_user_id=profile.telegram_user_id,
                chat_id=profile.chat_id,
                username=profile.username,
                first_name=profile.first_name,
                timezone="UTC",
                language_code=normalize_language_code(profile.language_code),
            )

        return await self.user_repository.update_profile(
            user,
            chat_id=profile.chat_id,
            username=profile.username,
            first_name=profile.first_name,
        )

    async def update_timezone(self, user: User, timezone: str) -> User:
        validated_timezone = validate_timezone(timezone)
        return await self.user_repository.update_timezone(user, validated_timezone)

    async def update_language(self, user: User, language_code: str) -> User:
        return await self.user_repository.update_language(user, normalize_language_code(language_code))
