from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.data_lineage import DataLineage
from datetime import datetime

class DataLineageService:
    def __init__(self, db: Session):
        self.db = db

    async def track_data_ingestion(
        self, 
        source_id: int, 
        job_id: int, 
        metadata: Dict[str, Any]
    ) -> DataLineage:
        lineage = DataLineage(
            source_id=source_id,
            job_id=job_id,
            event_type="ingestion",
            metadata=metadata,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(lineage)
        self.db.commit()
        self.db.refresh(lineage)
        return lineage

    async def track_transformation(
        self, 
        job_id: int, 
        transformation_rules: List[str],
        input_schema: Dict,
        output_schema: Dict
    ) -> DataLineage:
        metadata = {
            "transformation_rules": transformation_rules,
            "transformation_timestamp": datetime.utcnow().isoformat(),
            "rules_count": len(transformation_rules)
        }
        
        lineage = DataLineage(
            job_id=job_id,
            event_type="transformation",
            metadata=metadata,
            input_schema=input_schema,
            output_schema=output_schema,
            transformation_details={
                "rules_applied": transformation_rules,
                "schema_changes": self._compare_schemas(input_schema, output_schema)
            },
            timestamp=datetime.utcnow()
        )
        
        self.db.add(lineage)
        self.db.commit()
        self.db.refresh(lineage)
        return lineage

    async def track_workflow_event(
        self,
        job_id: int,
        event_type: str,
        metadata: Dict[str, Any]
    ) -> DataLineage:
        lineage = DataLineage(
            job_id=job_id,
            event_type=event_type,
            metadata=metadata,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(lineage)
        self.db.commit()
        self.db.refresh(lineage)
        return lineage

    async def track_data_output(
        self,
        job_id: int,
        destination: str,
        output_metadata: Dict[str, Any]
    ) -> DataLineage:
        metadata = {
            "destination": destination,
            "output_timestamp": datetime.utcnow().isoformat(),
            **output_metadata
        }
        
        lineage = DataLineage(
            job_id=job_id,
            event_type="output",
            metadata=metadata,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(lineage)
        self.db.commit()
        self.db.refresh(lineage)
        return lineage

    async def trace_data_flow(self, job_id: int) -> Dict[str, Any]:
        lineage_records = self.db.query(DataLineage).filter(
            DataLineage.job_id == job_id
        ).order_by(DataLineage.timestamp).all()
        
        trace = {
            "job_id": job_id,
            "events": [],
            "data_flow": [],
            "transformations": [],
            "total_events": len(lineage_records)
        }
        
        for record in lineage_records:
            event = {
                "id": record.id,
                "event_type": record.event_type,
                "timestamp": record.timestamp.isoformat(),
                "metadata": record.metadata
            }
            
            if record.input_schema:
                event["input_schema"] = record.input_schema
            if record.output_schema:
                event["output_schema"] = record.output_schema
            if record.transformation_details:
                event["transformation_details"] = record.transformation_details
                trace["transformations"].append(event)
            
            trace["events"].append(event)
            
            trace["data_flow"].append({
                "step": len(trace["data_flow"]) + 1,
                "event_type": record.event_type,
                "timestamp": record.timestamp.isoformat(),
                "description": self._generate_event_description(record)
            })
        
        return trace

    async def get_lineage_by_source(self, source_id: int) -> List[Dict[str, Any]]:
        lineage_records = self.db.query(DataLineage).filter(
            DataLineage.source_id == source_id
        ).order_by(DataLineage.timestamp.desc()).all()
        
        return [
            {
                "id": record.id,
                "job_id": record.job_id,
                "event_type": record.event_type,
                "timestamp": record.timestamp.isoformat(),
                "metadata": record.metadata
            }
            for record in lineage_records
        ]

    async def get_downstream_dependencies(self, job_id: int) -> List[Dict[str, Any]]:
        dependencies = []
        
        lineage_records = self.db.query(DataLineage).filter(
            DataLineage.job_id == job_id,
            DataLineage.event_type == "output"
        ).all()
        
        for record in lineage_records:
            destination = record.metadata.get("destination")
            if destination:
                downstream_jobs = self.db.query(DataLineage).filter(
                    DataLineage.metadata.contains({"source": destination})
                ).all()
                
                for downstream in downstream_jobs:
                    dependencies.append({
                        "downstream_job_id": downstream.job_id,
                        "connection_type": "data_flow",
                        "destination": destination,
                        "timestamp": downstream.timestamp.isoformat()
                    })
        
        return dependencies

    async def generate_lineage_report(self, job_id: int) -> Dict[str, Any]:
        trace = await self.trace_data_flow(job_id)
        dependencies = await self.get_downstream_dependencies(job_id)
        
        report = {
            "job_id": job_id,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_events": trace["total_events"],
                "transformations_count": len(trace["transformations"]),
                "downstream_dependencies": len(dependencies)
            },
            "data_flow": trace["data_flow"],
            "transformations": trace["transformations"],
            "downstream_dependencies": dependencies,
            "full_trace": trace
        }
        
        return report

    def _compare_schemas(self, input_schema: Dict, output_schema: Dict) -> Dict[str, Any]:
        changes = {
            "columns_added": [],
            "columns_removed": [],
            "columns_modified": [],
            "row_count_change": 0
        }
        
        if input_schema and output_schema:
            input_columns = {col["name"]: col for col in input_schema.get("columns", [])}
            output_columns = {col["name"]: col for col in output_schema.get("columns", [])}
            
            changes["columns_added"] = list(set(output_columns.keys()) - set(input_columns.keys()))
            changes["columns_removed"] = list(set(input_columns.keys()) - set(output_columns.keys()))
            
            for col_name in set(input_columns.keys()) & set(output_columns.keys()):
                if input_columns[col_name].get("type") != output_columns[col_name].get("type"):
                    changes["columns_modified"].append({
                        "column": col_name,
                        "old_type": input_columns[col_name].get("type"),
                        "new_type": output_columns[col_name].get("type")
                    })
            
            input_rows = input_schema.get("row_count", 0)
            output_rows = output_schema.get("row_count", 0)
            changes["row_count_change"] = output_rows - input_rows
        
        return changes

    def _generate_event_description(self, record: DataLineage) -> str:
        event_type = record.event_type
        metadata = record.metadata or {}
        
        if event_type == "ingestion":
            ingestion_type = metadata.get("ingestion_type", "unknown")
            return f"Data ingested via {ingestion_type}"
        elif event_type == "transformation":
            rules_count = metadata.get("rules_count", 0)
            return f"Applied {rules_count} transformation rules"
        elif event_type == "output":
            destination = metadata.get("destination", "unknown")
            return f"Data output to {destination}"
        elif event_type == "approval_submitted":
            approval_type = metadata.get("approval_type", "unknown")
            return f"Submitted for {approval_type} approval"
        elif event_type == "approval_approved":
            return "Approval granted"
        elif event_type == "approval_rejected":
            return "Approval rejected"
        else:
            return f"Event: {event_type}"
