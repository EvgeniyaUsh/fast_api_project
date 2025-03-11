from db.models import User


class UserDAL:
    def __init__(self, db_session):
        self.db_session = db_session

    async def create_user(self, name, surname, email):
        created_user = User(name=name, surname=surname, email=email)
        self.db_session.add(created_user)
        await self.db_session.flush()
        return created_user
