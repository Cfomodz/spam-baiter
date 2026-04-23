from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import ContactGroup, PhoneNumber
from ..schemas import (
    ContactGroupCreate,
    ContactGroupOut,
    ContactGroupUpdate,
    PhoneNumberAssign,
    PhoneNumberCreate,
    PhoneNumberOut,
)

router = APIRouter()


@router.get("/groups", response_model=list[ContactGroupOut])
async def list_groups(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ContactGroup)
        .options(selectinload(ContactGroup.phone_numbers))
        .order_by(ContactGroup.updated_at.desc())
    )
    return result.scalars().all()


@router.post("/groups", response_model=ContactGroupOut)
async def create_group(
    body: ContactGroupCreate, db: AsyncSession = Depends(get_db)
):
    group = ContactGroup(name=body.name, notes=body.notes)
    db.add(group)
    await db.commit()
    await db.refresh(group, attribute_names=["phone_numbers"])
    return group


@router.put("/groups/{group_id}", response_model=ContactGroupOut)
async def update_group(
    group_id: int,
    body: ContactGroupUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ContactGroup)
        .options(selectinload(ContactGroup.phone_numbers))
        .where(ContactGroup.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if body.name is not None:
        group.name = body.name
    if body.notes is not None:
        group.notes = body.notes
    await db.commit()
    await db.refresh(group, attribute_names=["phone_numbers"])
    return group


@router.delete("/groups/{group_id}")
async def delete_group(group_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ContactGroup).where(ContactGroup.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    await db.delete(group)
    await db.commit()
    return {"ok": True}


@router.post("/numbers", response_model=PhoneNumberOut)
async def add_number(
    body: PhoneNumberCreate, db: AsyncSession = Depends(get_db)
):
    seq = None
    if body.group_id:
        result = await db.execute(
            select(func.count())
            .select_from(PhoneNumber)
            .where(PhoneNumber.group_id == body.group_id)
        )
        count = result.scalar() or 0
        seq = count + 1

    phone = PhoneNumber(
        number=body.number,
        label=body.label,
        group_id=body.group_id,
        sequence_num=seq,
    )
    db.add(phone)
    await db.commit()
    await db.refresh(phone)
    return phone


@router.put("/numbers/{number_id}/assign", response_model=PhoneNumberOut)
async def assign_number(
    number_id: int,
    body: PhoneNumberAssign,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PhoneNumber).where(PhoneNumber.id == number_id)
    )
    phone = result.scalar_one_or_none()
    if not phone:
        raise HTTPException(status_code=404, detail="Number not found")

    count_result = await db.execute(
        select(func.count())
        .select_from(PhoneNumber)
        .where(PhoneNumber.group_id == body.group_id)
    )
    count = count_result.scalar() or 0

    phone.group_id = body.group_id
    phone.sequence_num = count + 1
    await db.commit()
    await db.refresh(phone)
    return phone


@router.delete("/numbers/{number_id}")
async def delete_number(number_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PhoneNumber).where(PhoneNumber.id == number_id)
    )
    phone = result.scalar_one_or_none()
    if not phone:
        raise HTTPException(status_code=404, detail="Number not found")
    await db.delete(phone)
    await db.commit()
    return {"ok": True}


@router.get("/recent", response_model=list[PhoneNumberOut])
async def recent_numbers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PhoneNumber).order_by(PhoneNumber.created_at.desc()).limit(20)
    )
    return result.scalars().all()
