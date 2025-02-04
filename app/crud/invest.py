from datetime import datetime
from typing import Union

from app.models import CharityProject, Donation


def close_object(
    target_object: Union[CharityProject, Donation]
) -> Union[CharityProject, Donation]:
    target_object.invested_amount = target_object.full_amount
    target_object.fully_invested = True
    target_object.close_date = datetime.now()
    return target_object


def invest(
    target: Union[CharityProject, Donation],
    sources: list[Union[CharityProject, Donation]]
) -> tuple[
    Union[CharityProject, Donation], list[Union[CharityProject, Donation]]
]:
    changed_sources = []
    target.invested_amount = 0
    for source in sources:
        sum_to_invest = min(
            (source.full_amount - source.invested_amount),
            (target.full_amount - target.invested_amount)
        )
        source.invested_amount += sum_to_invest
        target.invested_amount += sum_to_invest
        if source.invested_amount == source.full_amount:
            source = close_object(source)
        changed_sources.append(source)
        if target.invested_amount == target.full_amount:
            target = close_object(target)
            break
    return target, changed_sources
