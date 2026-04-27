from direm.db.models import UserState
from direm.repositories.base import Repository


class UserStateRepository(Repository[UserState]):
    model = UserState
