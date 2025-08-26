from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.workflow import WorkflowApproval
from app.schemas.workflow import WorkflowApprovalResponse, ApprovalRequest
from app.services.workflow_service import WorkflowService
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/approvals", response_model=List[WorkflowApprovalResponse])
async def list_pending_approvals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    approvals = db.query(WorkflowApproval).offset(skip).limit(limit).all()
    return [
        WorkflowApprovalResponse(
            id=approval.id,
            job_id=approval.job_id,
            approval_type=approval.approval_type,
            state=approval.state,
            submitted_by=approval.submitted_by,
            approved_by=approval.approved_by,
            comments=approval.comments,
            submitted_at=approval.submitted_at,
            approved_at=approval.approved_at
        )
        for approval in approvals
    ]

@router.post("/approvals/{job_id}/submit")
async def submit_for_approval(
    job_id: int,
    approval_request: ApprovalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = WorkflowService(db)
        approval = await service.submit_for_approval(
            job_id=job_id,
            submitted_by=current_user.id,
            approval_type=approval_request.approval_type,
            comments=approval_request.comments
        )
        return {
            "status": "success",
            "approval_id": approval.id,
            "message": "Job submitted for approval"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/approvals/{approval_id}/approve")
async def approve_job(
    approval_id: int,
    comments: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = WorkflowService(db)
        success = await service.approve_job(
            approval_id=approval_id,
            approver_id=current_user.id,
            comments=comments
        )
        if success:
            return {"status": "success", "message": "Job approved successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to approve job")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/approvals/{approval_id}/reject")
async def reject_job(
    approval_id: int,
    comments: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        service = WorkflowService(db)
        success = await service.reject_job(
            approval_id=approval_id,
            approver_id=current_user.id,
            comments=comments
        )
        if success:
            return {"status": "success", "message": "Job rejected"}
        else:
            raise HTTPException(status_code=400, detail="Failed to reject job")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
