from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.workflow import WorkflowApproval, WorkflowState, ApprovalType
from app.models.processing_job import ProcessingJob, JobStatus
from app.models.user import User
from app.services.notification_service import NotificationService
from app.services.lineage_service import DataLineageService
from datetime import datetime

class WorkflowService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
        self.lineage_service = DataLineageService(db)

    async def submit_for_approval(
        self, 
        job_id: int, 
        submitted_by: int,
        approval_type: ApprovalType,
        comments: Optional[str] = None
    ) -> WorkflowApproval:
        job = self.db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not job:
            raise ValueError("Processing job not found")

        approval = WorkflowApproval(
            job_id=job_id,
            approval_type=approval_type,
            state=WorkflowState.PENDING,
            submitted_by=submitted_by,
            comments=comments,
            submitted_at=datetime.utcnow()
        )
        
        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)

        await self.lineage_service.track_workflow_event(
            job_id=job_id,
            event_type="approval_submitted",
            metadata={
                "approval_id": approval.id,
                "approval_type": approval_type.value,
                "submitted_by": submitted_by,
                "comments": comments
            }
        )

        await self.notification_service.notify_approvers(approval)
        
        return approval

    async def approve_job(
        self, 
        approval_id: int, 
        approver_id: int,
        comments: Optional[str] = None
    ) -> bool:
        approval = self.db.query(WorkflowApproval).filter(
            WorkflowApproval.id == approval_id
        ).first()
        
        if not approval or approval.state != WorkflowState.PENDING:
            return False

        approval.approved_by = approver_id
        approval.approved_at = datetime.utcnow()
        approval.state = WorkflowState.APPROVED
        if comments:
            approval.comments = f"{approval.comments}\n\nApprover comments: {comments}" if approval.comments else f"Approver comments: {comments}"
        
        self.db.commit()

        await self.lineage_service.track_workflow_event(
            job_id=approval.job_id,
            event_type="approval_approved",
            metadata={
                "approval_id": approval.id,
                "approved_by": approver_id,
                "comments": comments
            }
        )

        await self._execute_approved_job(approval.job_id, approval.approval_type)
        
        await self.notification_service.notify_approval_decision(approval, "approved")
        
        return True

    async def reject_job(
        self, 
        approval_id: int, 
        approver_id: int,
        comments: str
    ) -> bool:
        approval = self.db.query(WorkflowApproval).filter(
            WorkflowApproval.id == approval_id
        ).first()
        
        if not approval or approval.state != WorkflowState.PENDING:
            return False

        approval.approved_by = approver_id
        approval.approved_at = datetime.utcnow()
        approval.state = WorkflowState.REJECTED
        approval.comments = f"{approval.comments}\n\nRejection reason: {comments}" if approval.comments else f"Rejection reason: {comments}"
        
        self.db.commit()

        await self.lineage_service.track_workflow_event(
            job_id=approval.job_id,
            event_type="approval_rejected",
            metadata={
                "approval_id": approval.id,
                "rejected_by": approver_id,
                "rejection_reason": comments
            }
        )

        job = self.db.query(ProcessingJob).filter(ProcessingJob.id == approval.job_id).first()
        if job:
            job.status = JobStatus.CANCELLED
            self.db.commit()

        await self.notification_service.notify_approval_decision(approval, "rejected")
        
        return True

    async def _execute_approved_job(self, job_id: int, approval_type: ApprovalType):
        job = self.db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if not job:
            return

        if approval_type == ApprovalType.DATA_PROMOTION:
            await self._promote_data(job)
        elif approval_type == ApprovalType.JOB_EXECUTION:
            await self._execute_job(job)
        elif approval_type == ApprovalType.SCHEMA_CHANGE:
            await self._apply_schema_changes(job)

    async def _promote_data(self, job: ProcessingJob):
        job.status = JobStatus.RUNNING
        self.db.commit()

        try:
            await self.lineage_service.track_workflow_event(
                job_id=job.id,
                event_type="data_promotion_started",
                metadata={
                    "promotion_timestamp": datetime.utcnow().isoformat()
                }
            )

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            
            await self.lineage_service.track_workflow_event(
                job_id=job.id,
                event_type="data_promotion_completed",
                metadata={
                    "completion_timestamp": datetime.utcnow().isoformat()
                }
            )

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = f"Data promotion failed: {str(e)}"
            
            await self.lineage_service.track_workflow_event(
                job_id=job.id,
                event_type="data_promotion_failed",
                metadata={
                    "error": str(e),
                    "failure_timestamp": datetime.utcnow().isoformat()
                }
            )

        self.db.commit()

    async def _execute_job(self, job: ProcessingJob):
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        self.db.commit()

        try:
            from app.services.data_processing_service import DataProcessingService
            processing_service = DataProcessingService(self.db)
            
            if job.transformation_rules:
                rules = job.transformation_rules.get("rules", [])
                from app.schemas.processing import TransformationRuleCreate
                transformation_rules = [TransformationRuleCreate(**rule) for rule in rules]
                await processing_service.apply_transformation_rules(job, transformation_rules)

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = f"Job execution failed: {str(e)}"
            job.completed_at = datetime.utcnow()
            self.db.commit()

    async def _apply_schema_changes(self, job: ProcessingJob):
        await self.lineage_service.track_workflow_event(
            job_id=job.id,
            event_type="schema_change_applied",
            metadata={
                "schema_changes": job.input_data,
                "applied_timestamp": datetime.utcnow().isoformat()
            }
        )

    async def get_pending_approvals_for_user(self, user_id: int) -> List[WorkflowApproval]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        if user.role.value in ["admin", "data_engineer"]:
            return self.db.query(WorkflowApproval).filter(
                WorkflowApproval.state == WorkflowState.PENDING
            ).all()
        else:
            return []

    async def auto_retry_failed_jobs(self):
        failed_jobs = self.db.query(ProcessingJob).filter(
            ProcessingJob.status == JobStatus.FAILED
        ).all()

        for job in failed_jobs:
            retry_count = job.input_data.get("retry_count", 0) if job.input_data else 0
            if retry_count < 3:
                from app.services.data_processing_service import DataProcessingService
                processing_service = DataProcessingService(self.db)
                
                new_job = await processing_service.retry_job(job)
                new_job.input_data = new_job.input_data or {}
                new_job.input_data["retry_count"] = retry_count + 1
                new_job.input_data["auto_retry"] = True
                self.db.commit()

                await self.lineage_service.track_workflow_event(
                    job_id=new_job.id,
                    event_type="auto_retry_initiated",
                    metadata={
                        "original_job_id": job.id,
                        "retry_count": retry_count + 1,
                        "retry_reason": "automatic_retry_on_failure"
                    }
                )
