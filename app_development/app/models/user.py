from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100))

    @property
    def first_name(self) -> str:
        """Extract first name from full_name"""
        if self.full_name:
            parts = self.full_name.split(' ', 1)
            return parts[0] if parts else ''
        return ''

    @property
    def last_name(self) -> str:
        """Extract last name from full_name"""
        if self.full_name:
            parts = self.full_name.split(' ', 1)
            return parts[1] if len(parts) > 1 else ''
        return ''

