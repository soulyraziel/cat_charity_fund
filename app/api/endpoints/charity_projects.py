from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_project_name_duplicate, check_charity_project_exists,
    check_project_invested, check_project_new_full_amount,
    check_project_is_closed
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.crud.invest import invest
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)


router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjectDB]
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    '''
    Возвращает список всех проектов.
    '''
    all_projects = await charity_project_crud.get_multi(session)
    return all_projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def create_new_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    '''
    Создаёт благотворительный проект:

    - **name**: уникальное название проекта
    - **description**: описание проекта
    - **full_amount**: требуемая сумма
    '''
    await check_project_name_duplicate(charity_project.name, session)
    donations_to_invest = await donation_crud.get_objects_to_invest(session)
    new_project = await charity_project_crud.create(
        charity_project,
        session,
        need_to_invest=bool(donations_to_invest)
    )
    if donations_to_invest:
        new_project, changed_donations = invest(
            new_project, donations_to_invest
        )
        for donation in changed_donations:
            session.add(donation)
    session.add(new_project)
    await session.commit()
    await session.refresh(new_project)
    return new_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def remove_meeting_room(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    '''
    Удаляет благотворительный проект
    '''
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    await check_project_invested(charity_project)
    await check_project_is_closed(charity_project)
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def partially_update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    '''
    Изменяет благотворительный проект:

    - **name**: уникальное название проекта
    - **description**: описание проекта
    - **full_amount**: требуемая сумма
    '''
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    if obj_in.full_amount:
        await check_project_new_full_amount(
            charity_project, obj_in.full_amount
        )
    await check_project_is_closed(charity_project)
    if obj_in.name is not None:
        await check_project_name_duplicate(obj_in.name, session)
    if obj_in.full_amount == charity_project.invested_amount:
        charity_project.fully_invested = True
        charity_project.close_date = datetime.now()
    charity_project = await charity_project_crud.update(
        charity_project, obj_in, session
    )
    return charity_project
