from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..rewards.models import RewardCreate, RewardUpdate, RewardOut
from ..rewards.service import list_rewards, get_reward, create_reward, update_reward, delete_reward


router = APIRouter(prefix="/rewards", tags=["rewards"])


@router.get("/", response_model=List[RewardOut])
def list_rewards_endpoint(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    token: str = Header(...),
):
    return list_rewards(db, token, limit, offset)


@router.get("/{reward_id}", response_model=RewardOut)
def get_reward_endpoint(
    reward_id: int,
    db: Session = Depends(get_db),
    token: str = Header(...),
):
    return get_reward(db, token, reward_id)


@router.post("/add", response_model=RewardOut)
def create_reward_endpoint(
    payload: RewardCreate,
    db: Session = Depends(get_db),
    token: str = Header(...),
):
    return create_reward(db, token, payload)


@router.put("/{reward_id}", response_model=RewardOut)
def update_reward_endpoint(
    reward_id: int,
    payload: RewardUpdate,
    db: Session = Depends(get_db),
    token: str = Header(...),
):
    return update_reward(db, token, reward_id, payload)


@router.delete("/{reward_id}")
def delete_reward_endpoint(
    reward_id: int,
    db: Session = Depends(get_db),
    token: str = Header(...),
):
    return delete_reward(db, token, reward_id)


