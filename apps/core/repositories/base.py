"""
Base repository class following repository pattern.
"""
from typing import Generic, TypeVar, Optional, List, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from apps.core.database import Base

ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository class providing common CRUD operations.
    """
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def create(self, **kwargs) -> ModelType:
        """Create a new instance."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        return instance
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get instance by ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all instances with pagination."""
        result = await self.db.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update instance by ID."""
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await self.db.flush()
        return instance
    
    async def delete(self, id: int) -> bool:
        """Delete instance by ID."""
        instance = await self.get_by_id(id)
        if instance:
            await self.db.delete(instance)
            await self.db.flush()
            return True
        return False
    
    async def filter(self, **kwargs) -> List[ModelType]:
        """Filter instances by attributes."""
        query = select(self.model)
        for key, value in kwargs.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.db.execute(query)
        return list(result.scalars().all())
