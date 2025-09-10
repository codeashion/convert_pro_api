from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from typing import List
from ..rewards.models import Reward, RewardCreate, RewardUpdate, RewardOut
from ..auth import verify_token


def list_rewards(db: Session, token: str, limit: int = 100, offset: int = 0) -> List[RewardOut]:
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])

        query = (
            select(Reward)
            .where(Reward.user_id == user_id)
            .order_by(Reward.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        rows = db.execute(query).scalars().all()
        return [RewardOut.from_orm(row) for row in rows]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list rewards: {str(e)}")


def get_reward(db: Session, token: str, reward_id: int) -> RewardOut:
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        row = db.execute(
            select(Reward).where(and_(Reward.id == reward_id, Reward.user_id == user_id))
        ).scalars().first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found")
        return RewardOut.from_orm(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reward: {str(e)}")


def create_reward(db: Session, token: str, data: RewardCreate) -> RewardOut:
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        row = Reward(
            user_id=user_id,
            reward=data.reward,
            points=data.points,
            requested_by=data.requested_by,
            created_by=data.created_by,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return RewardOut.from_orm(row)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create reward: {str(e)}")


def update_reward(db: Session, token: str, reward_id: int, data: RewardUpdate) -> RewardOut:
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        row = db.execute(
            select(Reward).where(and_(Reward.id == reward_id, Reward.user_id == user_id))
        ).scalars().first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found")
        for field, value in data.dict(exclude_unset=True).items():
            setattr(row, field, value)
        db.commit()
        db.refresh(row)
        return RewardOut.from_orm(row)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update reward: {str(e)}")


def delete_reward(db: Session, token: str, reward_id: int) -> dict:
    try:
        payload = verify_token(token)
        user_id = int(payload["id"])
        row = db.execute(
            select(Reward).where(and_(Reward.id == reward_id, Reward.user_id == user_id))
        ).scalars().first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reward not found")
        db.delete(row)
        db.commit()
        return {"statusCode": 200, "status": True, "message": "Reward deleted", "data": None}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete reward: {str(e)}")


