import pandas as pd
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.schema import DetectedSchema
import json
import numpy as np

class SchemaDetectionService:
    def __init__(self, db: Session):
        self.db = db
        self.confidence_threshold = 0.8

    async def detect_schema(self, data: Any, source_type: str, source_id: int = None) -> DetectedSchema:
        if source_type == "csv":
            return await self._detect_csv_schema(data, source_id)
        elif source_type == "json":
            return await self._detect_json_schema(data, source_id)
        elif source_type == "swift":
            return await self._detect_swift_schema(data, source_id)
        elif source_type in ["xlsx", "xls"]:
            return await self._detect_excel_schema(data, source_id)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    async def _detect_csv_schema(self, csv_data: Dict[str, Any], source_id: int) -> DetectedSchema:
        columns = csv_data.get("columns", [])
        data_rows = csv_data.get("data", [])
        
        if not data_rows:
            schema = {"columns": [], "row_count": 0, "confidence": 0.5}
        else:
            df = pd.DataFrame(data_rows)
            schema = await self._analyze_dataframe_schema(df)
        
        detected_schema = DetectedSchema(
            source_id=source_id,
            schema_data=schema,
            confidence_score=schema.get("confidence", 0.8),
            detection_method="pandas_profiling",
            sample_data=data_rows[:5] if data_rows else []
        )
        
        self.db.add(detected_schema)
        self.db.commit()
        self.db.refresh(detected_schema)
        
        return detected_schema

    async def _detect_json_schema(self, json_data: Dict[str, Any], source_id: int) -> DetectedSchema:
        schema = await self._analyze_json_structure(json_data)
        
        detected_schema = DetectedSchema(
            source_id=source_id,
            schema_data=schema,
            confidence_score=schema.get("confidence", 0.9),
            detection_method="json_structure_analysis",
            sample_data=json_data if isinstance(json_data, dict) else json_data[:5] if isinstance(json_data, list) else None
        )
        
        self.db.add(detected_schema)
        self.db.commit()
        self.db.refresh(detected_schema)
        
        return detected_schema

    async def _detect_swift_schema(self, swift_data: Dict[str, Any], source_id: int) -> DetectedSchema:
        schema = {
            "message_type": swift_data.get("message_type"),
            "fields": [],
            "confidence": 0.85
        }
        
        fields = swift_data.get("fields", {})
        for field_code, field_value in fields.items():
            field_info = {
                "field_code": field_code,
                "field_type": self._infer_swift_field_type(field_code, field_value),
                "sample_value": field_value,
                "required": True
            }
            schema["fields"].append(field_info)
        
        detected_schema = DetectedSchema(
            source_id=source_id,
            schema_data=schema,
            confidence_score=schema["confidence"],
            detection_method="swift_message_parsing",
            sample_data=swift_data
        )
        
        self.db.add(detected_schema)
        self.db.commit()
        self.db.refresh(detected_schema)
        
        return detected_schema

    async def _detect_excel_schema(self, excel_data: Dict[str, Any], source_id: int) -> DetectedSchema:
        columns = excel_data.get("columns", [])
        data_rows = excel_data.get("data", [])
        
        if data_rows:
            df = pd.DataFrame(data_rows)
            schema = await self._analyze_dataframe_schema(df)
        else:
            schema = {"columns": [], "row_count": 0, "confidence": 0.5}
        
        detected_schema = DetectedSchema(
            source_id=source_id,
            schema_data=schema,
            confidence_score=schema.get("confidence", 0.8),
            detection_method="excel_analysis",
            sample_data=data_rows[:5] if data_rows else []
        )
        
        self.db.add(detected_schema)
        self.db.commit()
        self.db.refresh(detected_schema)
        
        return detected_schema

    async def _analyze_dataframe_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        schema = {
            "columns": [],
            "row_count": len(df),
            "confidence": 0.9
        }
        
        for column in df.columns:
            col_data = df[column]
            col_info = {
                "name": column,
                "type": self._infer_column_type(col_data),
                "nullable": col_data.isnull().any(),
                "unique_values": col_data.nunique(),
                "sample_values": col_data.dropna().head(5).tolist(),
                "null_count": col_data.isnull().sum(),
                "null_percentage": (col_data.isnull().sum() / len(col_data)) * 100
            }
            
            if col_info["type"] in ["integer", "float"]:
                col_info["min_value"] = col_data.min()
                col_info["max_value"] = col_data.max()
                col_info["mean_value"] = col_data.mean()
            elif col_info["type"] == "string":
                col_info["avg_length"] = col_data.astype(str).str.len().mean()
                col_info["max_length"] = col_data.astype(str).str.len().max()
            
            schema["columns"].append(col_info)
        
        return schema

    async def _analyze_json_structure(self, json_data: Any) -> Dict[str, Any]:
        if isinstance(json_data, dict):
            return await self._analyze_json_object(json_data)
        elif isinstance(json_data, list):
            return await self._analyze_json_array(json_data)
        else:
            return {
                "type": "primitive",
                "data_type": type(json_data).__name__,
                "confidence": 0.9
            }

    async def _analyze_json_object(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        schema = {
            "type": "object",
            "properties": {},
            "confidence": 0.9
        }
        
        for key, value in obj.items():
            prop_schema = {
                "type": self._infer_json_type(value),
                "sample_value": value
            }
            
            if isinstance(value, dict):
                prop_schema["nested_schema"] = await self._analyze_json_object(value)
            elif isinstance(value, list) and value:
                prop_schema["array_item_type"] = self._infer_json_type(value[0])
                if isinstance(value[0], dict):
                    prop_schema["array_item_schema"] = await self._analyze_json_object(value[0])
            
            schema["properties"][key] = prop_schema
        
        return schema

    async def _analyze_json_array(self, arr: List[Any]) -> Dict[str, Any]:
        if not arr:
            return {"type": "array", "item_type": "unknown", "confidence": 0.5}
        
        first_item = arr[0]
        schema = {
            "type": "array",
            "item_type": self._infer_json_type(first_item),
            "length": len(arr),
            "confidence": 0.9
        }
        
        if isinstance(first_item, dict):
            schema["item_schema"] = await self._analyze_json_object(first_item)
        
        return schema

    def _infer_column_type(self, series: pd.Series) -> str:
        if pd.api.types.is_integer_dtype(series):
            return "integer"
        elif pd.api.types.is_float_dtype(series):
            return "float"
        elif pd.api.types.is_bool_dtype(series):
            return "boolean"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        else:
            return "string"

    def _infer_json_type(self, value: Any) -> str:
        if isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, dict):
            return "object"
        elif isinstance(value, list):
            return "array"
        elif value is None:
            return "null"
        else:
            return "unknown"

    def _infer_swift_field_type(self, field_code: str, field_value: str) -> str:
        if field_code in ["32A", "33B"]:
            return "currency_amount"
        elif field_code in ["30", "32"]:
            return "date"
        elif field_code in ["50", "59"]:
            return "party_identifier"
        elif field_code.startswith("7"):
            return "narrative"
        else:
            return "text"
