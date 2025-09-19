#!/usr/bin/env python3
"""
Talend ETL Processor
Processes input data according to the mapping logic extracted from Talend tMap component.
"""

import json
import re
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any, Optional


class TalendProcessor:
    """Processes data according to Talend tMap mapping logic."""
    
    def __init__(self, input_schema_file: str, output_schemas_file: str, mapping_logic_file: str):
        """Initialize processor with schema and mapping files."""
        with open(input_schema_file, 'r') as f:
            self.input_schema = json.load(f)
        
        with open(output_schemas_file, 'r') as f:
            self.output_schemas = json.load(f)
        
        with open(mapping_logic_file, 'r') as f:
            self.mapping_logic = json.load(f)
    
    def is_null(self, value: Any) -> bool:
        """Check if value is null or None (Relational.ISNULL equivalent)."""
        return value is None or value == "null" or value == ""
    
    def parse_date(self, pattern: str, date_str: str) -> Optional[str]:
        """Parse date string according to pattern (TalendDate.parseDate equivalent)."""
        if self.is_null(date_str):
            return None
        try:
            if pattern == "yyyy-MM-dd":
                return date_str  # Assuming input is already in correct format
            return date_str
        except:
            return None
    
    def evaluate_variable(self, var_name: str, row: Dict[str, Any], variables: Dict[str, Any]) -> Any:
        """Evaluate a variable expression."""
        var_def = self.mapping_logic['mapping_logic']['variables'][var_name]
        expression = var_def['expression']
        
        if var_name == 'infoCode':
            if self.is_null(row.get('successCode')) or str(row.get('successCode', '')).lower() == 'null':
                return row.get('errorCode')
            return row.get('successCode')
        
        elif var_name == 'infoMsg':
            if self.is_null(row.get('successMsg')) or str(row.get('successMsg', '')).lower() == 'null':
                return row.get('errorMsg')
            return row.get('successMsg')
        
        elif var_name == 'status':
            status = str(row.get('status', '')).strip().upper()
            if status == 'OK':
                return 3
            elif status == 'NOK':
                return 4
            else:
                return 0
        
        elif var_name == 'messageID':
            msg_id = str(row.get('messageSourceIdentifier', ''))
            for prefix in ['T', 'CPR', 'FPI', 'FPC', 'SWG']:
                msg_id = msg_id.replace(prefix, '')
            return msg_id
        
        elif var_name == 'FPI_CORR_ACC_NO':
            return Decimal('100022022')
        
        elif var_name == 'FCA_CORR_ACC_NO':
            return Decimal('100026847')
        
        elif var_name == 'Check_duplicates_trans':
            desc1 = str(row.get('transactionStatusFlagDescription1', '')).lower()
            desc2 = str(row.get('transactionStatusFlagDescription2', '')).lower()
            
            if (not self.is_null(row.get('transactionStatusFlagDescription1')) and 
                'duplicate transaction' in desc1) or \
               (not self.is_null(row.get('transactionStatusFlagDescription2')) and 
                'duplicate transaction' in desc2):
                return 'Y'
            return 'N'
        
        return None
    
    def evaluate_expression(self, expression: str, row: Dict[str, Any], variables: Dict[str, Any]) -> Any:
        """Evaluate a mapping expression."""
        if expression.startswith('Var.'):
            var_name = expression.replace('Var.', '')
            return variables.get(var_name)
        
        if expression.startswith('row1.'):
            field_name = expression.replace('row1.', '')
            return row.get(field_name)
        
        if '(row1.respAckDate + row1.respAckTime)' in expression:
            date_part = str(row.get('respAckDate', ''))
            time_part = str(row.get('respAckTime', ''))
            result = date_part + time_part
            if '.replaceAll("null", "")' in expression:
                result = result.replace('null', '')
            return result
        
        if expression.startswith('new BigDecimal('):
            if 'Var.messageID' in expression:
                return Decimal(str(variables.get('messageID', '0')))
            elif '"100022022"' in expression:
                return Decimal('100022022')
            elif '"100026847"' in expression:
                return Decimal('100026847')
        
        if 'TalendDate.parseDate' in expression:
            if 'yyyy-MM-dd' in expression and 'row1.respAckDate' in expression:
                return self.parse_date('yyyy-MM-dd', row.get('respAckDate', ''))
        
        if 'Relational.ISNULL(row1.statusDesc) ? row1.statusCode : row1.statusDesc' in expression:
            if self.is_null(row.get('statusDesc')):
                return row.get('statusCode')
            return row.get('statusDesc')
        
        if '.' not in expression and expression in row:
            return row[expression]
        
        return expression
    
    def evaluate_filter(self, filter_expr: str, row: Dict[str, Any], variables: Dict[str, Any]) -> bool:
        """Evaluate filter expression to determine if row should be processed."""
        msg_id = row.get('messageSourceIdentifier', '')
        check_duplicates = variables.get('Check_duplicates_trans', 'N')
        
        if 'CPR' in filter_expr:
            return 'CPR' in msg_id and check_duplicates == 'N'
        elif 'SWG' in filter_expr:
            return 'SWG' in msg_id and check_duplicates == 'N'
        elif 'FPI' in filter_expr:
            return 'FPI' in msg_id and check_duplicates == 'N'
        elif 'FPC' in filter_expr:
            return 'FPC' in msg_id and check_duplicates == 'N'
        elif '.contains("T")' in filter_expr:
            return 'T' in msg_id and check_duplicates == 'N'
        
        return False
    
    def process_row(self, row: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Process a single input row and generate outputs for all applicable tables."""
        results = {
            'capri': [],
            'swing': [],
            'item': [],
            'FPI': [],
            'FCA': []
        }
        
        variables = {}
        for var_name in self.mapping_logic['mapping_logic']['variables']:
            variables[var_name] = self.evaluate_variable(var_name, row, variables)
        
        for table_name, mapping in self.mapping_logic['mapping_logic']['output_mappings'].items():
            if self.evaluate_filter(mapping['filter'], row, variables):
                output_row = {}
                
                for output_field, expression in mapping['field_mappings'].items():
                    output_row[output_field] = self.evaluate_expression(expression, row, variables)
                
                results[table_name].append(output_row)
        
        return results
    
    def process_file(self, input_file: str, output_dir: str = '.') -> Dict[str, str]:
        """Process input file and generate output files for each table."""
        import pandas as pd
        
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
            input_data = df.to_dict('records')
        elif input_file.endswith('.xlsx') or input_file.endswith('.xls'):
            df = pd.read_excel(input_file)
            input_data = df.to_dict('records')
        elif input_file.endswith('.json'):
            with open(input_file, 'r') as f:
                input_data = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {input_file}. Supported formats: CSV, Excel (.xlsx/.xls), JSON")
        
        all_results = {
            'capri': [],
            'swing': [],
            'item': [],
            'FPI': [],
            'FCA': []
        }
        
        for row in input_data:
            row_results = self.process_row(row)
            for table_name, records in row_results.items():
                all_results[table_name].extend(records)
        
        output_files = {}
        for table_name, records in all_results.items():
            if records:  # Only create file if there are records
                output_file = f"{output_dir}/{table_name}_output.json"
                with open(output_file, 'w') as f:
                    json.dump(records, f, indent=2, default=str)
                output_files[table_name] = output_file
                print(f"Generated {len(records)} records for {table_name} -> {output_file}")
        
        return output_files
    
    def print_summary(self, input_file: str):
        """Print processing summary."""
        import pandas as pd
        
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
            input_data = df.to_dict('records')
        elif input_file.endswith('.xlsx') or input_file.endswith('.xls'):
            df = pd.read_excel(input_file)
            input_data = df.to_dict('records')
        elif input_file.endswith('.json'):
            with open(input_file, 'r') as f:
                input_data = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {input_file}. Supported formats: CSV, Excel (.xlsx/.xls), JSON")
        
        print(f"\nProcessing Summary:")
        print(f"Input records: {len(input_data)}")
        
        for row in input_data:
            variables = {}
            for var_name in self.mapping_logic['mapping_logic']['variables']:
                variables[var_name] = self.evaluate_variable(var_name, row, variables)
            
            msg_id = row.get('messageSourceIdentifier', '')
            check_dup = variables.get('Check_duplicates_trans', 'N')
            
            print(f"\nRecord: {msg_id}")
            print(f"  Duplicate check: {check_dup}")
            
            for table_name, mapping in self.mapping_logic['mapping_logic']['output_mappings'].items():
                if self.evaluate_filter(mapping['filter'], row, variables):
                    print(f"  -> Will output to {table_name}")


def main():
    """Main function to run the processor."""
    import sys
    import os
    
    processor = TalendProcessor(
        'input_schema.json',
        'output_schemas.json', 
        'mapping_logic.json'
    )
    
    print("Talend ETL Processor")
    print("===================")
    
    sample_files = ['sample_input.csv', 'sample_input.xlsx', 'sample_input.json']
    input_file = None
    
    for file in sample_files:
        if os.path.exists(file):
            input_file = file
            break
    
    if not input_file:
        print("Error: No sample input file found. Expected: sample_input.csv, sample_input.xlsx, or sample_input.json")
        sys.exit(1)
    
    print(f"Processing input file: {input_file}")
    
    output_files = processor.process_file(input_file)
    
    processor.print_summary(input_file)
    
    print(f"\nOutput files generated:")
    for table, file_path in output_files.items():
        print(f"  {table}: {file_path}")


if __name__ == "__main__":
    main()
