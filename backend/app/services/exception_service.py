from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.exception import DataException, ExceptionSeverity
from app.models.processing_job import ProcessingJob
from app.services.notification_service import NotificationService
from datetime import datetime

class ExceptionService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)

    async def report_exception(
        self, 
        job_id: int,
        exception_type: str,
        message: str,
        severity: ExceptionSeverity,
        metadata: Dict[str, Any] = None,
        stack_trace: str = None
    ) -> DataException:
        exception = DataException(
            job_id=job_id,
            exception_type=exception_type,
            message=message,
            severity=severity,
            metadata=metadata or {},
            stack_trace=stack_trace,
            timestamp=datetime.utcnow(),
            resolved=False
        )
        
        self.db.add(exception)
        self.db.commit()
        self.db.refresh(exception)

        if severity in [ExceptionSeverity.HIGH, ExceptionSeverity.CRITICAL]:
            await self.notification_service.send_exception_alert(exception)

        await self._suggest_auto_correction(exception)
        
        return exception

    async def resolve_exception(
        self,
        exception_id: int,
        resolved_by: int,
        resolution_notes: str
    ) -> bool:
        exception = self.db.query(DataException).filter(
            DataException.id == exception_id
        ).first()
        
        if not exception:
            return False

        exception.resolved = True
        exception.resolved_by = resolved_by
        exception.resolution_notes = resolution_notes
        exception.resolved_at = datetime.utcnow()
        
        self.db.commit()

        await self.notification_service.send_exception_resolution_notification(exception)
        
        return True

    async def get_exception_statistics(self) -> Dict[str, Any]:
        total_exceptions = self.db.query(DataException).count()
        resolved_exceptions = self.db.query(DataException).filter(
            DataException.resolved == True
        ).count()
        
        severity_counts = {}
        for severity in ExceptionSeverity:
            count = self.db.query(DataException).filter(
                DataException.severity == severity
            ).count()
            severity_counts[severity.value] = count

        exception_types = self.db.query(
            DataException.exception_type,
            self.db.func.count(DataException.id).label('count')
        ).group_by(DataException.exception_type).all()

        return {
            "total_exceptions": total_exceptions,
            "resolved_exceptions": resolved_exceptions,
            "unresolved_exceptions": total_exceptions - resolved_exceptions,
            "resolution_rate": (resolved_exceptions / total_exceptions * 100) if total_exceptions > 0 else 0,
            "severity_breakdown": severity_counts,
            "exception_types": [{"type": et.exception_type, "count": et.count} for et in exception_types]
        }

    async def get_job_exceptions(self, job_id: int) -> List[DataException]:
        return self.db.query(DataException).filter(
            DataException.job_id == job_id
        ).order_by(DataException.timestamp.desc()).all()

    async def get_recent_exceptions(self, limit: int = 50) -> List[DataException]:
        return self.db.query(DataException).order_by(
            DataException.timestamp.desc()
        ).limit(limit).all()

    async def _suggest_auto_correction(self, exception: DataException):
        suggestions = []
        
        if exception.exception_type == "data_type_mismatch":
            suggestions.append({
                "type": "data_type_conversion",
                "description": "Apply automatic data type conversion",
                "confidence": 0.8,
                "action": "convert_data_types"
            })
        
        elif exception.exception_type == "missing_required_field":
            suggestions.append({
                "type": "default_value_assignment",
                "description": "Assign default values to missing fields",
                "confidence": 0.7,
                "action": "fill_missing_values"
            })
        
        elif exception.exception_type == "duplicate_records":
            suggestions.append({
                "type": "deduplication",
                "description": "Remove duplicate records automatically",
                "confidence": 0.9,
                "action": "remove_duplicates"
            })
        
        elif exception.exception_type == "invalid_date_format":
            suggestions.append({
                "type": "date_parsing",
                "description": "Apply intelligent date parsing",
                "confidence": 0.8,
                "action": "parse_dates"
            })
        
        elif exception.exception_type == "encoding_error":
            suggestions.append({
                "type": "encoding_detection",
                "description": "Auto-detect and convert file encoding",
                "confidence": 0.7,
                "action": "fix_encoding"
            })

        if suggestions:
            exception.metadata = exception.metadata or {}
            exception.metadata["auto_correction_suggestions"] = suggestions
            self.db.commit()

            for suggestion in suggestions:
                if suggestion["confidence"] > 0.8:
                    await self._attempt_auto_correction(exception, suggestion)

    async def _attempt_auto_correction(self, exception: DataException, suggestion: Dict[str, Any]):
        try:
            job = self.db.query(ProcessingJob).filter(
                ProcessingJob.id == exception.job_id
            ).first()
            
            if not job:
                return

            correction_metadata = {
                "original_exception_id": exception.id,
                "correction_type": suggestion["type"],
                "correction_action": suggestion["action"],
                "auto_correction": True,
                "timestamp": datetime.utcnow().isoformat()
            }

            if suggestion["action"] == "convert_data_types":
                await self._auto_convert_data_types(job, correction_metadata)
            elif suggestion["action"] == "fill_missing_values":
                await self._auto_fill_missing_values(job, correction_metadata)
            elif suggestion["action"] == "remove_duplicates":
                await self._auto_remove_duplicates(job, correction_metadata)
            elif suggestion["action"] == "parse_dates":
                await self._auto_parse_dates(job, correction_metadata)

            await self.report_exception(
                job_id=job.id,
                exception_type="auto_correction_applied",
                message=f"Auto-correction applied: {suggestion['description']}",
                severity=ExceptionSeverity.LOW,
                metadata=correction_metadata
            )

        except Exception as e:
            await self.report_exception(
                job_id=exception.job_id,
                exception_type="auto_correction_failed",
                message=f"Auto-correction failed: {str(e)}",
                severity=ExceptionSeverity.MEDIUM,
                metadata={
                    "original_exception_id": exception.id,
                    "failed_correction": suggestion["type"],
                    "error": str(e)
                }
            )

    async def _auto_convert_data_types(self, job: ProcessingJob, metadata: Dict[str, Any]):
        from app.services.data_processing_service import DataProcessingService
        from app.schemas.processing import TransformationRuleCreate
        
        processing_service = DataProcessingService(self.db)
        
        rule = TransformationRuleCreate(
            rule_type="validate_data_types",
            parameters={
                "type_mappings": {
                    "numeric_columns": "float",
                    "date_columns": "datetime"
                }
            },
            description="Auto data type conversion"
        )
        
        await processing_service.apply_transformation_rules(job, [rule])

    async def _auto_fill_missing_values(self, job: ProcessingJob, metadata: Dict[str, Any]):
        from app.services.data_processing_service import DataProcessingService
        from app.schemas.processing import TransformationRuleCreate
        
        processing_service = DataProcessingService(self.db)
        
        rule = TransformationRuleCreate(
            rule_type="handle_nulls",
            parameters={
                "strategy": "fill",
                "fill_value": "N/A"
            },
            description="Auto fill missing values"
        )
        
        await processing_service.apply_transformation_rules(job, [rule])

    async def _auto_remove_duplicates(self, job: ProcessingJob, metadata: Dict[str, Any]):
        from app.services.data_processing_service import DataProcessingService
        from app.schemas.processing import TransformationRuleCreate
        
        processing_service = DataProcessingService(self.db)
        
        rule = TransformationRuleCreate(
            rule_type="remove_duplicates",
            parameters={
                "keep": "first"
            },
            description="Auto remove duplicates"
        )
        
        await processing_service.apply_transformation_rules(job, [rule])

    async def _auto_parse_dates(self, job: ProcessingJob, metadata: Dict[str, Any]):
        from app.services.data_processing_service import DataProcessingService
        from app.schemas.processing import TransformationRuleCreate
        
        processing_service = DataProcessingService(self.db)
        
        rule = TransformationRuleCreate(
            rule_type="validate_data_types",
            parameters={
                "type_mappings": {
                    "date_columns": "datetime"
                }
            },
            description="Auto parse dates"
        )
        
        await processing_service.apply_transformation_rules(job, [rule])
