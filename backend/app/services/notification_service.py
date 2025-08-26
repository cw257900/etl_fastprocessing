import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from sqlalchemy.orm import Session
from app.models.workflow import WorkflowApproval
from app.models.exception import DataException
from app.models.user import User, UserRole
from app.core.config import settings

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    async def notify_approvers(self, approval: WorkflowApproval):
        approvers = self.db.query(User).filter(
            User.role.in_([UserRole.ADMIN, UserRole.DATA_ENGINEER]),
            User.is_active == True
        ).all()

        subject = f"Approval Required: {approval.approval_type.value}"
        message = f"""
        A new approval request has been submitted.
        
        Job ID: {approval.job_id}
        Approval Type: {approval.approval_type.value}
        Submitted By: {approval.submitted_by}
        Comments: {approval.comments or 'No comments'}
        
        Please review and approve/reject this request.
        """

        for approver in approvers:
            await self._send_email(approver.email, subject, message)

    async def notify_approval_decision(self, approval: WorkflowApproval, decision: str):
        submitter = self.db.query(User).filter(User.id == approval.submitted_by).first()
        if not submitter:
            return

        subject = f"Approval {decision.title()}: Job {approval.job_id}"
        message = f"""
        Your approval request has been {decision}.
        
        Job ID: {approval.job_id}
        Approval Type: {approval.approval_type.value}
        Decision: {decision.title()}
        Approver Comments: {approval.comments or 'No comments'}
        """

        await self._send_email(submitter.email, subject, message)

    async def send_exception_alert(self, exception: DataException):
        admins = self.db.query(User).filter(
            User.role == UserRole.ADMIN,
            User.is_active == True
        ).all()

        subject = f"Data Exception Alert: {exception.severity.value.upper()}"
        message = f"""
        A {exception.severity.value} severity exception has occurred.
        
        Job ID: {exception.job_id}
        Exception Type: {exception.exception_type}
        Message: {exception.message}
        Timestamp: {exception.timestamp}
        
        Please investigate and resolve this issue.
        """

        for admin in admins:
            await self._send_email(admin.email, subject, message)

    async def send_exception_resolution_notification(self, exception: DataException):
        resolver = self.db.query(User).filter(User.id == exception.resolved_by).first()
        admins = self.db.query(User).filter(
            User.role == UserRole.ADMIN,
            User.is_active == True
        ).all()

        subject = f"Exception Resolved: {exception.exception_type}"
        message = f"""
        An exception has been resolved.
        
        Job ID: {exception.job_id}
        Exception Type: {exception.exception_type}
        Resolved By: {resolver.full_name if resolver else 'Unknown'}
        Resolution Notes: {exception.resolution_notes}
        Resolved At: {exception.resolved_at}
        """

        for admin in admins:
            await self._send_email(admin.email, subject, message)

    async def send_job_completion_notification(self, job_id: int, status: str, user_email: str):
        subject = f"Job {status.title()}: {job_id}"
        message = f"""
        Your processing job has {status}.
        
        Job ID: {job_id}
        Status: {status.title()}
        
        You can view the details in the ETL dashboard.
        """

        await self._send_email(user_email, subject, message)

    async def _send_email(self, to_email: str, subject: str, message: str):
        if not all([settings.smtp_server, settings.smtp_username, settings.smtp_password]):
            print(f"Email notification (would send to {to_email}): {subject}")
            print(f"Message: {message}")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = settings.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            text = msg.as_string()
            server.sendmail(settings.smtp_username, to_email, text)
            server.quit()

        except Exception as e:
            print(f"Failed to send email to {to_email}: {str(e)}")
