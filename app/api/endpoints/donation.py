from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.crud.invest import invest
from app.models import User
from app.schemas.donation import (
    DonationBase, DonationDB, DonationCreate
)


router = APIRouter()


@router.get(
    '/',
    response_model=list[DonationDB],
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    '''
    Возвращает список всех пожертвований.
    '''
    donations = await donation_crud.get_multi(session)
    return donations


@router.post(
    '/',
    response_model=DonationCreate,
    response_model_exclude_none=True
)
async def create_new_donation(
        donation: DonationBase,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    '''
    Сделать пожертвование:

    - **full_amount**: сумма пожертвования
    - **comment**: комментарий
    '''
    projects_to_invest = await charity_project_crud.get_objects_to_invest(
        session
    )
    new_donation = await donation_crud.create(
        donation,
        session,
        user,
        bool(projects_to_invest)
    )
    if projects_to_invest:
        new_donation, changed_projects = invest(
            new_donation,
            projects_to_invest
        )
        for project in changed_projects:
            session.add(project)
    session.add(new_donation)
    await session.commit()
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/my',
    response_model=list[DonationCreate],
    dependencies=[Depends(current_user)]
)
async def get_my_donations(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
):
    '''
    Возвращает список пожертвований пользователя, выполняющего запрос.
    '''
    donations = await donation_crud.get_donations_by_user(session, user)
    return donations
