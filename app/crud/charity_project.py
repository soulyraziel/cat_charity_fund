from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        db_project_id = db_project_id.scalars().first()
        return db_project_id

    async def close_project(
        self,
        project: CharityProject,
        session: AsyncSession
    ) -> None:
        await session.execute(
            update(CharityProject).where(
                CharityProject.id == project.id
            ).values(
                fully_invested=True,
                close_date=datetime.now()
            )
        )


charity_project_crud = CRUDCharityProject(CharityProject)
