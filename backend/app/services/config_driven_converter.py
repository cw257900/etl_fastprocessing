#!/usr/bin/env python3
"""
Configuration-driven ETL Converter
Supports multiple conversion scenarios using JSON configuration files
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import re
from fastapi import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigDrivenETLConverter:
    """
    Configuration-driven ETL converter that can handle multiple transformation scenarios
    """
    
    def __init__(self, input_schema_path: str, output_schema_path: str, processing_rules_path: str):
        """
        Initialize converter with configuration files
        """
        self.input_schema = self.load_json_config(input_schema_path)
        self.output_schema = self.load_json_config(output_schema_path)
        self.processing_rules = self.load_json_config(processing_rules_path)
        
        logger.info(f"Loaded configuration for: {self.processing_rules['processing_name']}")
        
    def load_json_config(self, file_path: str) -> Dict[str, Any]:
        """
        Load JSON configuration file
        """
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config file {file_path}: {e}")
            raise
    
    def read_dat_file(self, file_path: str) -> pd.DataFrame:
        """
        Read .dat file based on input schema specifications
        """
        logger.info(f"Reading .dat file: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            records = []
            for line_num, line in enumerate(lines, 1):
                line = line.rstrip('\n\r')
                if not line.strip():
                    continue
                
                record = self.parse_dat_line(line, line_num)
                if record:
                    records.append(record)
            
            df = pd.DataFrame(records)
            logger.info(f"Successfully parsed {len(df)} records from .dat file")
            return df
            
        except Exception as e:
            logger.error(f"Error reading .dat file {file_path}: {e}")
            raise
    
    def parse_dat_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """
        Parse a single line from .dat file based on input schema field specifications
        """
        record = {}
        position = 0
        
        try:
            for column in self.input_schema['columns']:
                field_name = column['name']
                field_length = column.get('length', 1)
                data_type = column.get('data_type', 'string')
                required = column.get('required', False)
                
                if position + field_length > len(line):
                    if required:
                        logger.warning(f"Line {line_num}: Required field '{field_name}' extends beyond line length")
                    field_value = ''
                else:
                    field_value = line[position:position + field_length].strip()
                
                if required and not field_value:
                    logger.warning(f"Line {line_num}: Required field '{field_name}' is empty")
                
                if data_type == 'string':
                    record[field_name] = field_value
                elif data_type == 'numeric':
                    try:
                        record[field_name] = float(field_value) if field_value else 0.0
                    except ValueError:
                        logger.warning(f"Line {line_num}: Invalid numeric value for field '{field_name}': {field_value}")
                        record[field_name] = 0.0
                else:
                    record[field_name] = field_value
                
                position += field_length
            
            return record
            
        except Exception as e:
            logger.error(f"Error parsing line {line_num}: {e}")
            return None
    
    def validate_input_data(self, df: pd.DataFrame) -> bool:
        """
        Validate input data against input schema
        """
        logger.info("Validating input data...")
        
        required_columns = [col['name'] for col in self.input_schema['columns'] if col.get('required', False)]
        missing_columns = set(required_columns) - set(df.columns)
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        for rule in self.input_schema.get('validation_rules', []):
            if not self.apply_validation_rule(df, rule):
                return False
        
        logger.info("Input data validation passed")
        return True
    
    def apply_validation_rule(self, df: pd.DataFrame, rule: Dict[str, Any]) -> bool:
        """
        Apply a specific validation rule
        """
        rule_type = rule['rule_type']
        
        if rule_type == 'required_fields':
            missing_fields = set(rule['fields']) - set(df.columns)
            if missing_fields:
                logger.error(f"Missing required fields: {missing_fields}")
                return False
                
        elif rule_type == 'currency_validation':
            field = rule['field']
            valid_values = rule['valid_values']
            if field in df.columns:
                invalid_values = set(df[field].dropna().unique()) - set(valid_values)
                if invalid_values:
                    logger.warning(f"Invalid currency values found: {invalid_values}")
        
        elif rule_type == 'product_type_validation':
            field = rule['field']
            valid_values = rule['valid_values']
            if field in df.columns:
                invalid_values = set(df[field].dropna().unique()) - set(valid_values)
                if invalid_values:
                    logger.warning(f"Invalid product type values found: {invalid_values}")
        
        return True
    
    def apply_transformation_rule(self, row: pd.Series, rule: Dict[str, Any]) -> Any:
        """
        Apply a specific transformation rule to a row
        """
        rule_id = rule['rule_id']
        
        if rule_id == 'LEAF_GL_CALCULATION':
            return self.calculate_leaf_gl_from_config(row, rule)
        elif rule_id == 'ACCRUAL_ACCOUNT_LOGIC':
            return self.calculate_accrual_account_from_config(row, rule)
        elif rule_id == 'DRORCR_CALCULATION':
            return self.calculate_drorcr_from_config(row, rule)
        elif rule_id == 'BALANCE_SIGN_CALCULATION':
            return self.calculate_balance_sign_from_config(row, rule)
        elif rule_id == 'DATE_FORMATTING':
            return self.format_dates_from_config(row, rule)
        elif rule_id == 'AMOUNT_CALCULATION':
            return self.calculate_amounts_from_config(row, rule)
        
        return None
    
    def calculate_leaf_gl_from_config(self, row: pd.Series, rule: Dict[str, Any]) -> str:
        """
        Calculate LEAF_GL based on configuration rules
        """
        currency = row.get('CURRENCY_Cosmos', '')
        product_type = row.get('PRODUCT_TYPE', '')
        leaf_gl = row.get('LEAF_GL', '')
        
        for condition in rule['logic']['conditions']:
            if self.evaluate_condition(row, condition['condition']):
                if 'JPY_D_G' in condition['action']:
                    return f"{leaf_gl}_JPY_D_G"
                elif 'JPY_OTHER' in condition['action']:
                    return f"{leaf_gl}_JPY_OTHER"
                elif 'NOJPY_D_G' in condition['action']:
                    return f"{leaf_gl}_NOJPY_D_G"
                elif 'NOJPY_OTHER' in condition['action']:
                    return f"{leaf_gl}_NOJPY_OTHER"
        
        return leaf_gl
    
    def calculate_accrual_account_from_config(self, row: pd.Series, rule: Dict[str, Any]) -> str:
        """
        Calculate accrual account based on configuration rules
        """
        for condition in rule['logic']['conditions']:
            if self.evaluate_condition(row, condition['condition']):
                source_field = condition['source_field']
                return str(row.get(source_field, ''))
        
        return ''
    
    def calculate_drorcr_from_config(self, row: pd.Series, rule: Dict[str, Any]) -> str:
        """
        Calculate DRORCR based on configuration rules
        """
        for condition in rule['logic']['conditions']:
            if self.evaluate_condition(row, condition['condition']):
                return condition['value']
        
        default_action = rule['logic'].get('default_action', {})
        if default_action:
            face_value = self.safe_float_conversion(row.get('FACE_VALUE', 0))
            return 'C' if face_value >= 0 else 'D'
        
        return 'C'
    
    def calculate_balance_sign_from_config(self, row: pd.Series, rule: Dict[str, Any]) -> Dict[str, str]:
        """
        Calculate balance signs based on configuration rules
        """
        currency_flex = row.get('Currency_Flex', '')
        
        if currency_flex == 'JPY':
            amount = self.safe_float_conversion(row.get('LCY_FACE_VALUE', 0))
        else:
            amount = self.safe_float_conversion(row.get('FACE_VALUE', 0))
        
        sign = 'D' if amount < 0 else 'C'
        
        return {
            'OPBALSIGN': sign,
            'CLBALSIGN': sign
        }
    
    def format_dates_from_config(self, row: pd.Series, rule: Dict[str, Any]) -> Dict[str, str]:
        """
        Format dates based on configuration rules
        """
        formatted_dates = {}
        
        date_mappings = {
            'VALUEDATE': 'VALUE_DATE',
            'ENTRYDATE': 'DEAL_DATE',
            'OPBALDATE': 'VALUE_DATE',
            'CLBALDATE': 'VALUE_DATE'
        }
        
        for output_field, input_field in date_mappings.items():
            date_value = row.get(input_field, '')
            formatted_dates[output_field] = self.format_date(date_value)
        
        return formatted_dates
    
    def calculate_amounts_from_config(self, row: pd.Series, rule: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate amounts based on configuration rules
        """
        currency_flex = row.get('Currency_Flex', '')
        
        if currency_flex == 'JPY':
            amount = self.safe_float_conversion(row.get('LCY_FACE_VALUE', 0))
        else:
            amount = self.safe_float_conversion(row.get('FACE_VALUE', 0))
        
        return {
            'AMOUNT': abs(amount),
            'OPBAL': amount,
            'CLBAL': amount
        }
    
    def evaluate_condition(self, row: pd.Series, condition: str) -> bool:
        """
        Evaluate a condition string against a row
        """
        try:
            currency_cosmos = row.get('CURRENCY_Cosmos', '')
            currency_flex = row.get('Currency_Flex', '')
            product_type = row.get('PRODUCT_TYPE', '')
            contract_status = row.get('CONTRACT_STATUS', '')
            face_value = self.safe_float_conversion(row.get('FACE_VALUE', 0))
            
            if "CURRENCY_Cosmos == 'JPY' AND PRODUCT_TYPE IN ['D', 'G']" in condition:
                return currency_cosmos == 'JPY' and product_type in ['D', 'G']
            elif "CURRENCY_Cosmos == 'JPY' AND PRODUCT_TYPE NOT IN ['D', 'G']" in condition:
                return currency_cosmos == 'JPY' and product_type not in ['D', 'G']
            elif "CURRENCY_Cosmos != 'JPY' AND PRODUCT_TYPE IN ['D', 'G']" in condition:
                return currency_cosmos != 'JPY' and product_type in ['D', 'G']
            elif "CURRENCY_Cosmos != 'JPY' AND PRODUCT_TYPE NOT IN ['D', 'G']" in condition:
                return currency_cosmos != 'JPY' and product_type not in ['D', 'G']
            elif "Currency_Flex == 'JPY'" in condition:
                return currency_flex == 'JPY'
            elif "Currency_Flex != 'JPY'" in condition:
                return currency_flex != 'JPY'
            elif "CONTRACT_STATUS == 'Y' AND FACE_VALUE >= 0" in condition:
                return contract_status == 'Y' and face_value >= 0
            elif "CONTRACT_STATUS == 'Y' AND FACE_VALUE < 0" in condition:
                return contract_status == 'Y' and face_value < 0
            elif "CONTRACT_STATUS == 'A' AND FACE_VALUE >= 0" in condition:
                return contract_status == 'A' and face_value >= 0
            elif "CONTRACT_STATUS == 'A' AND FACE_VALUE < 0" in condition:
                return contract_status == 'A' and face_value < 0
            
            return False
        except Exception as e:
            logger.warning(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def safe_float_conversion(self, value: Any) -> float:
        """
        Safely convert value to float
        """
        try:
            return float(value) if value else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def format_date(self, date_str: str) -> str:
        """
        Format date to YYYYMMDD format
        """
        if not date_str or pd.isna(date_str):
            return ''
        
        try:
            for fmt in ['%Y-%m-%d', '%Y%m%d', '%d/%m/%Y', '%m/%d/%Y']:
                try:
                    dt = datetime.strptime(str(date_str), fmt)
                    return dt.strftime('%Y%m%d')
                except ValueError:
                    continue
            return str(date_str)[:8]  # Fallback
        except Exception:
            return ''
    
    def apply_field_mapping(self, row: pd.Series, mapping: Dict[str, Any]) -> Any:
        """
        Apply field mapping based on configuration
        """
        transformation = mapping['transformation']
        input_field = mapping['input_field']
        
        if transformation == 'DIRECT_COPY':
            return row.get(input_field, '')
        elif transformation == 'DEFAULT_VALUE':
            return mapping['default_value']
        elif transformation == 'STRING_CONVERSION':
            return str(row.get(input_field, ''))
        
        return ''
    
    def transform_row(self, row: pd.Series) -> Dict[str, Any]:
        """
        Transform a single row based on configuration
        """
        transformed = {}
        
        for rule in self.processing_rules['transformation_rules']:
            result = self.apply_transformation_rule(row, rule)
            
            if isinstance(result, dict):
                transformed.update(result)
            elif result is not None:
                output_field = rule.get('output_field')
                if output_field:
                    transformed[output_field] = result
        
        for mapping in self.processing_rules['field_mappings']:
            output_field = mapping['output_field']
            transformed[output_field] = self.apply_field_mapping(row, mapping)
        
        output_columns = [col['name'] for col in self.output_schema['columns']]
        additional_fields = self.output_schema.get('additional_fields', {}).get('fields', [])
        all_output_fields = output_columns + additional_fields
        
        for field in all_output_fields:
            if field not in transformed:
                transformed[field] = ''
        
        return transformed
    
    def convert_data(self, input_data) -> pd.DataFrame:
        """
        Convert input data based on configuration
        Accepts DataFrame, file path to .dat file, or CSV file path
        """
        if isinstance(input_data, str):
            if input_data.endswith('.dat'):
                input_df = self.read_dat_file(input_data)
            elif input_data.endswith('.csv'):
                input_df = pd.read_csv(input_data)
            else:
                raise ValueError(f"Unsupported file format: {input_data}")
        elif isinstance(input_data, pd.DataFrame):
            input_df = input_data
        else:
            raise ValueError("Input data must be DataFrame or file path")
        
        logger.info(f"Converting {len(input_df)} input records using {self.processing_rules['processing_name']}")
        
        if not self.validate_input_data(input_df):
            raise ValueError("Input data validation failed")
        
        transformed_rows = []
        for idx, row in input_df.iterrows():
            try:
                transformed_row = self.transform_row(row)
                transformed_rows.append(transformed_row)
            except Exception as e:
                logger.error(f"Error transforming row {idx}: {e}")
                continue
        
        output_columns = [col['name'] for col in self.output_schema['columns']]
        additional_fields = self.output_schema.get('additional_fields', {}).get('fields', [])
        all_columns = output_columns + additional_fields
        
        output_df = pd.DataFrame(transformed_rows, columns=all_columns)
        
        logger.info(f"Converted to {len(output_df)} output records")
        return output_df
    
    def save_output(self, df: pd.DataFrame, filename: str, format_type: str = 'csv'):
        """
        Save output DataFrame to file
        """
        if format_type.lower() == 'csv':
            df.to_csv(filename, index=False)
        elif format_type.lower() == 'excel':
            df.to_excel(filename, index=False)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        logger.info(f"Output saved to {filename}")


def main():
    """
    Example usage of configuration-driven converter
    """
    try:
        converter = ConfigDrivenETLConverter(
            input_schema_path='input_schema.json',
            output_schema_path='output_schema.json',
            processing_rules_path='processing_rules.json'
        )
        
        print(f"Configuration-driven ETL Converter initialized for: {converter.processing_rules['processing_name']}")
        print(f"Input schema: {converter.input_schema['schema_name']} v{converter.input_schema['version']}")
        print(f"Output schema: {converter.output_schema['schema_name']} v{converter.output_schema['version']}")
        
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    main()
