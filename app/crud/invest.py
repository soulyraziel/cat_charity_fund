from datetime import datetime
from typing import Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def get_invest_objects(
    model: Union[CharityProject, Donation],
    session: AsyncSession
) -> list[Union[CharityProject, Donation]]:
    objects = await session.execute(
        select(model).where(model.fully_invested == 0).order_by(
            model.id.desc()
        )
    )
    objects = objects.scalars().all()
    return objects


async def close_object(object: Union[CharityProject, Donation]) -> None:
    object.invested_amount = object.full_amount
    object.fully_invested = True
    object.close_date = datetime.now()


async def invest(
    object_in: Union[CharityProject, Donation],
    session: AsyncSession
):
    if isinstance(object_in, Donation):
        model = CharityProject
    else:
        model = Donation
    objects_to_invest = await get_invest_objects(model, session)
    object_in_balance = object_in.full_amount
    while objects_to_invest and object_in_balance > 0:
        object = objects_to_invest.pop()
        object_balance = object.full_amount - object.invested_amount
        if object_balance > object_in_balance:
            object.invested_amount += object_in_balance
            object_in_balance = 0
            await close_object(object_in)
        elif object_balance == object_in_balance:
            object_in_balance = 0
            await close_object(object_in)
            await close_object(object)
        else:
            object_in_balance -= object_balance
            object_in.invested_amount += object_balance
            await close_object(object)
        session.add(object)
    session.add(object_in)
    await session.commit()
    await session.refresh(object_in)
    return object_in
