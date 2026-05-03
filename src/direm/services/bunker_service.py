from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from direm.db.models import User
from direm.repositories.users import UserRepository


@dataclass(frozen=True)
class BunkerState:
    active: bool
    activated_at: datetime | None


class BunkerService:
    def __init__(
        self,
        user_repository: UserRepository,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.user_repository = user_repository
        self.clock = clock or (lambda: datetime.now(UTC))

    async def get_current_state(self, user: User) -> BunkerState:
        active, activated_at = await self.user_repository.get_bunker_state(user)
        return BunkerState(active=active, activated_at=activated_at)

    async def activate(self, user: User) -> BunkerState:
        if user.bunker_active and user.bunker_activated_at is not None:
            return await self.get_current_state(user)

        activated = await self.user_repository.activate_bunker(user, activated_at=self._now_utc())
        return BunkerState(active=activated.bunker_active, activated_at=activated.bunker_activated_at)

    async def deactivate(self, user: User) -> BunkerState:
        if not user.bunker_active and user.bunker_activated_at is None:
            return await self.get_current_state(user)

        deactivated = await self.user_repository.deactivate_bunker(user)
        return BunkerState(active=deactivated.bunker_active, activated_at=deactivated.bunker_activated_at)

    def _now_utc(self) -> datetime:
        now = self.clock()
        if now.tzinfo is None:
            return now.replace(tzinfo=UTC)
        return now.astimezone(UTC)
