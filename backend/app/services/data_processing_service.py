from typing import Dict, Any, List
import pandas as pd
from sqlalchemy.orm import Session
from app.models.processing_job import ProcessingJob, JobStatus
from app.schemas.processing import TransformationRuleCreate
from app.services.lineage_service import DataLineageService
from app.services.exception_service import ExceptionService
from datetime import datetime

class DataProcessingService:
    def __init__(self, db: Session):
        self.db = db
        self.lineage_service = DataLineageService(db)
        self.exception_service = ExceptionService(db)
        self.cleaning_rules = {
            'remove_duplicates': self._remove_duplicates,
            'handle_nulls': self._handle_nulls,
            'normalize_text': self._normalize_text,
            'validate_data_types': self._validate_data_types,
            'filter_rows': self._filter_rows,
            'aggregate_data': self._aggregate_data
        }

    async def apply_transformation_rules(
        self, 
        job: ProcessingJob, 
        transformation_rules: List[TransformationRuleCreate]
    ) -> Dict[str, Any]:
        try:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            self.db.commit()

            input_data = job.input_data
            if isinstance(input_data, dict) and "data" in input_data:
                df = pd.DataFrame(input_data["data"])
            else:
                df = pd.DataFrame(input_data)

            original_schema = await self._get_dataframe_schema(df)

            for rule in transformation_rules:
                if rule.rule_type in self.cleaning_rules:
                    df = await self.cleaning_rules[rule.rule_type](df, rule.parameters)
                else:
                    await self.exception_service.report_exception(
                        job_id=job.id,
                        exception_type="unknown_transformation_rule",
                        message=f"Unknown transformation rule: {rule.rule_type}",
                        severity="medium"
                    )

            processed_schema = await self._get_dataframe_schema(df)
            
            validation_results = await self._validate_processed_data(df)

            await self.lineage_service.track_transformation(
                job_id=job.id,
                transformation_rules=[rule.rule_type for rule in transformation_rules],
                input_schema=original_schema,
                output_schema=processed_schema
            )

            result = {
                "processed_data": df.to_dict('records'),
                "validation_results": validation_results,
                "row_count": len(df),
                "original_row_count": len(pd.DataFrame(input_data.get("data", input_data))),
                "transformation_summary": {
                    "rules_applied": len(transformation_rules),
                    "rules_list": [rule.rule_type for rule in transformation_rules]
                }
            }

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.output_data = result
            job.transformation_rules = {
                "rules": [rule.dict() for rule in transformation_rules],
                "applied_at": datetime.utcnow().isoformat()
            }
            
            self.db.commit()

            return result

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()

            await self.exception_service.report_exception(
                job_id=job.id,
                exception_type="transformation_error",
                message=str(e),
                severity="high"
            )

            return {
                "status": "failed",
                "error": str(e)
            }

    async def retry_job(self, job: ProcessingJob) -> ProcessingJob:
        new_job = ProcessingJob(
            name=f"Retry - {job.name}",
            description=f"Retry of job {job.id}",
            source_id=job.source_id,
            status=JobStatus.PENDING,
            input_data=job.input_data,
            transformation_rules=job.transformation_rules,
            created_by=job.created_by
        )
        
        self.db.add(new_job)
        self.db.commit()
        self.db.refresh(new_job)

        await self.lineage_service.track_data_ingestion(
            source_id=job.source_id,
            job_id=new_job.id,
            metadata={
                "retry_of_job": job.id,
                "retry_reason": "manual_retry",
                "original_error": job.error_message
            }
        )

        return new_job

    async def _remove_duplicates(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        subset_columns = parameters.get("subset_columns")
        keep = parameters.get("keep", "first")
        
        if subset_columns:
            return df.drop_duplicates(subset=subset_columns, keep=keep)
        else:
            return df.drop_duplicates(keep=keep)

    async def _handle_nulls(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        strategy = parameters.get("strategy", "drop")
        columns = parameters.get("columns")
        fill_value = parameters.get("fill_value")

        if columns:
            target_df = df[columns]
        else:
            target_df = df

        if strategy == "drop":
            return df.dropna(subset=columns) if columns else df.dropna()
        elif strategy == "fill":
            if columns:
                df[columns] = df[columns].fillna(fill_value)
                return df
            else:
                return df.fillna(fill_value)
        elif strategy == "forward_fill":
            if columns:
                df[columns] = df[columns].fillna(method='ffill')
                return df
            else:
                return df.fillna(method='ffill')
        else:
            return df

    async def _normalize_text(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        columns = parameters.get("columns", [])
        operations = parameters.get("operations", ["lower", "strip"])

        for column in columns:
            if column in df.columns:
                if "lower" in operations:
                    df[column] = df[column].astype(str).str.lower()
                if "upper" in operations:
                    df[column] = df[column].astype(str).str.upper()
                if "strip" in operations:
                    df[column] = df[column].astype(str).str.strip()
                if "remove_special_chars" in operations:
                    df[column] = df[column].astype(str).str.replace(r'[^a-zA-Z0-9\s]', '', regex=True)

        return df

    async def _validate_data_types(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        type_mappings = parameters.get("type_mappings", {})
        
        for column, target_type in type_mappings.items():
            if column in df.columns:
                try:
                    if target_type == "int":
                        df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
                    elif target_type == "float":
                        df[column] = pd.to_numeric(df[column], errors='coerce')
                    elif target_type == "datetime":
                        df[column] = pd.to_datetime(df[column], errors='coerce')
                    elif target_type == "string":
                        df[column] = df[column].astype(str)
                except Exception:
                    pass

        return df

    async def _filter_rows(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        conditions = parameters.get("conditions", [])
        
        for condition in conditions:
            column = condition.get("column")
            operator = condition.get("operator")
            value = condition.get("value")
            
            if column in df.columns:
                if operator == "equals":
                    df = df[df[column] == value]
                elif operator == "not_equals":
                    df = df[df[column] != value]
                elif operator == "greater_than":
                    df = df[df[column] > value]
                elif operator == "less_than":
                    df = df[df[column] < value]
                elif operator == "contains":
                    df = df[df[column].astype(str).str.contains(str(value), na=False)]
                elif operator == "not_null":
                    df = df[df[column].notna()]
                elif operator == "is_null":
                    df = df[df[column].isna()]

        return df

    async def _aggregate_data(self, df: pd.DataFrame, parameters: Dict[str, Any]) -> pd.DataFrame:
        group_by = parameters.get("group_by", [])
        aggregations = parameters.get("aggregations", {})
        
        if group_by and aggregations:
            return df.groupby(group_by).agg(aggregations).reset_index()
        else:
            return df

    async def _get_dataframe_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        schema = {
            "columns": [],
            "row_count": len(df)
        }
        
        for column in df.columns:
            col_info = {
                "name": column,
                "type": str(df[column].dtype),
                "null_count": df[column].isnull().sum(),
                "unique_count": df[column].nunique()
            }
            schema["columns"].append(col_info)
        
        return schema

    async def _validate_processed_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        validation_results = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "null_counts": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict(),
            "duplicate_rows": df.duplicated().sum(),
            "validation_passed": True,
            "issues": []
        }
        
        if validation_results["duplicate_rows"] > 0:
            validation_results["issues"].append(f"Found {validation_results['duplicate_rows']} duplicate rows")
        
        high_null_columns = [col for col, count in validation_results["null_counts"].items() 
                           if count > len(df) * 0.5]
        if high_null_columns:
            validation_results["issues"].append(f"High null percentage in columns: {high_null_columns}")
        
        if validation_results["issues"]:
            validation_results["validation_passed"] = False
        
        return validation_results
