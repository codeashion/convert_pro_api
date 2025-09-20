from fastapi import APIRouter, Depends, status, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..reward_request_redeem.service import (
	get_all_reward_requests, get_reward_request_by_id, create_reward_request, update_reward_request, delete_reward_request
)
from ..reward_request_redeem.model import RewardRequestRedeemCreate, RewardRequestRedeemUpdate, RewardRequestRedeemOut
from pydantic import BaseModel
from ..database import get_db

router = APIRouter(prefix="/reward-request-redeem", tags=["reward-request-redeem"])

# Use POST for list and detail endpoints to force OpenAPI to require request body
@router.get("/", response_model=List[RewardRequestRedeemOut])
def get_reward_requests_endpoint(
	token: str = Header(...),
	db: Session = Depends(get_db)
):
	return get_all_reward_requests(db, token)

@router.get("/redeemed", response_model=List[RewardRequestRedeemOut])
def get_redeemed_requests_endpoint(
	token: str = Header(...),
	db: Session = Depends(get_db)
):
	from ..reward_request_redeem.service import get_all_redeemed_requests
	return get_all_redeemed_requests(db, token)

@router.get("/{request_id}", response_model=RewardRequestRedeemOut)
def get_reward_request_endpoint(
	request_id: int,
	token: str = Header(...),
	db: Session = Depends(get_db)
):
	return get_reward_request_by_id(db, request_id, token)

@router.post("/add", response_model=RewardRequestRedeemOut)
def create_reward_request_endpoint(
	data: RewardRequestRedeemCreate,
	token: str = Header(...),
	db: Session = Depends(get_db)
):
	return create_reward_request(db, data, token)


# Request body schema for update
class RedeemStatusUpdate(BaseModel):
	redeem_status: int

@router.put("/{request_id}", response_model=RewardRequestRedeemOut)
def update_reward_request_endpoint(
	request_id: int,
	data: RedeemStatusUpdate,
	token: str = Header(...),
	db: Session = Depends(get_db)
):
	from datetime import date
	from ..reward_request_redeem.model import RewardRequestRedeemUpdate
	update_data = RewardRequestRedeemUpdate(redeem_date=date.today(), redeem_status=data.redeem_status)
	return update_reward_request(db, request_id, update_data, token)

@router.delete("/{request_id}")
def delete_reward_request_endpoint(
	request_id: int,
	token: str = Header(...),
	db: Session = Depends(get_db)
):
	return delete_reward_request(db, request_id, token)
