
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from ..reward_request_redeem.model import RewardRequestRedeem, RewardRequestRedeemCreate, RewardRequestRedeemUpdate, RewardRequestRedeemOut
from ..auth import verify_token

def get_all_reward_requests(db: Session, token: str = None) -> list:
	from ..admin_users.models import FamilyMember
	
	# Get user_id from token
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))
	
	# Get all family members belonging to this parent (user_id)
	family_members = db.query(FamilyMember).filter(FamilyMember.user_id == user_id).all()
	family_member_ids = [member.id for member in family_members]
	
	if not family_member_ids:
		return []
	
	# Query reward requests only for this parent's family members
	query = select(RewardRequestRedeem).where(
		and_(
			RewardRequestRedeem.redeem_status == 0,
			RewardRequestRedeem.family_member_id.in_(family_member_ids)
		)
	).order_by(RewardRequestRedeem.created_at.desc())
	rewards = db.execute(query).scalars().all()
	result = []
	for r in rewards:
		member = db.query(FamilyMember).filter(FamilyMember.id == r.family_member_id).first()
		member_name = member.member_name if member else None
		reward_dict = RewardRequestRedeemOut.from_orm(r).dict()
		reward_dict["name"] = member_name
		reward_dict["family_member_name"] = member_name
		result.append(reward_dict)
	return result

def get_reward_request_by_id(db: Session, request_id: int, token: str = None) -> RewardRequestRedeemOut:
	reward = db.get(RewardRequestRedeem, request_id)
	if not reward:
		raise HTTPException(status_code=404, detail="Reward request not found")
	return RewardRequestRedeemOut.from_orm(reward)

def create_reward_request(db: Session, data: RewardRequestRedeemCreate, token: str = None) -> RewardRequestRedeemOut:
	from datetime import date
	new_request = RewardRequestRedeem(**data.dict(), request_date=date.today())
	db.add(new_request)
	db.commit()
	db.refresh(new_request)
	return RewardRequestRedeemOut.from_orm(new_request)

def update_reward_request(db: Session, request_id: int, data: RewardRequestRedeemUpdate, token: str = None) -> RewardRequestRedeemOut:
	from datetime import date
	reward = db.get(RewardRequestRedeem, request_id)
	if not reward:
		raise HTTPException(status_code=404, detail="Reward request not found")
	update_data = data.dict(exclude_unset=True)
	# Set redeem_date to today if not provided
	if "redeem_date" not in update_data or update_data["redeem_date"] is None:
		update_data["redeem_date"] = date.today()
	for field, value in update_data.items():
		setattr(reward, field, value)
	db.commit()
	db.refresh(reward)
	return RewardRequestRedeemOut.from_orm(reward)

def delete_reward_request(db: Session, request_id: int, token: str = None) -> dict:
	reward = db.get(RewardRequestRedeem, request_id)
	if not reward:
		raise HTTPException(status_code=404, detail="Reward request not found")
	db.delete(reward)
	db.commit()
	return {"status": True, "message": "Reward request deleted successfully"}

def get_all_redeemed_requests(db: Session, token: str = None) -> list:
	from ..admin_users.models import FamilyMember
	
	# Get user_id from token
	token_data = verify_token(token)
	user_id = int(token_data.get("id"))
	
	# Get all family members belonging to this parent (user_id)
	family_members = db.query(FamilyMember).filter(FamilyMember.user_id == user_id).all()
	family_member_ids = [member.id for member in family_members]
	
	if not family_member_ids:
		return []
	
	# Query redeemed requests only for this parent's family members
	query = select(RewardRequestRedeem).where(
		and_(
			RewardRequestRedeem.redeem_status == 1,
			RewardRequestRedeem.family_member_id.in_(family_member_ids)
		)
	).order_by(RewardRequestRedeem.created_at.desc())
	rewards = db.execute(query).scalars().all()
	result = []
	for r in rewards:
		member = db.query(FamilyMember).filter(FamilyMember.id == r.family_member_id).first()
		member_name = member.member_name if member else None
		reward_dict = RewardRequestRedeemOut.from_orm(r).dict()
		reward_dict["name"] = member_name
		reward_dict["family_member_name"] = member_name
		result.append(reward_dict)
	return result
