from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate

class UserRepository:
    def __init__(self):
        self.session: AsyncSession | None = None

    async def get_by_id(self, user_id: int) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address"""
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_filter(self, count: int | None = None, page: int | None = None, **kwargs) -> list[User]:
        query = select(User)
        if kwargs:
            for key, value in kwargs.items():
                if hasattr(User, key) and value is not None:
                    query = query.where(getattr(User, key) == value)
        
        if count is not None and page is not None:
            offset = (page - 1) * count
            query = query.offset(offset).limit(count)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, user_data: UserCreate = None, **kwargs) -> User:
        """Create user from UserCreate schema or kwargs (email, username, first_name, last_name)"""
        try:
            if user_data:
                user = User(
                    username=user_data.username,
                    email=user_data.email,
                    full_name=user_data.full_name
                )
            else:
                # Handle direct parameters for tests
                first_name = kwargs.get('first_name', '')
                last_name = kwargs.get('last_name', '')
                full_name = f"{first_name} {last_name}" if first_name or last_name else kwargs.get('full_name')
                
                user = User(
                    username=kwargs['username'],
                    email=kwargs['email'],
                    full_name=full_name
                )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except Exception as e:
            await self.session.rollback()
            raise e

    async def update(self, user_id: int, user_data: UserUpdate = None, **kwargs) -> User:
        """Update user with UserUpdate schema or kwargs (first_name, username, etc.)"""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        if user_data:
            update_data = user_data.model_dump(exclude_unset=True)
        else:
            update_data = kwargs
            # Handle first_name/last_name to full_name conversion
            if 'first_name' in update_data or 'last_name' in update_data:
                # Get current full_name parts or use provided
                current_parts = (user.full_name or '').split(' ', 1)
                first = update_data.get('first_name', current_parts[0] if current_parts else '')
                last = update_data.get('last_name', current_parts[1] if len(current_parts) > 1 else '')
                update_data['full_name'] = f"{first} {last}"
                update_data.pop('first_name', None)
                update_data.pop('last_name', None)

        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
