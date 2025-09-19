# Talend ETL Schema and Mapping Extraction

This project extracts input schema, output schema, and data mapping logic from a Talend XML file into separate JSON objects, creates a sample input file, and provides Python code to process the data according to the extracted mapping logic.

## Deliverables

### 1. Input Schema (`input_schema.json`)
Contains the input schema definition extracted from the Talend tMap component with 16 fields including:
- messageSourceIdentifier
- respAckDate, respAckTime
- Transaction leg information (txnLegSeqNo1/2, transactionStatusFlag1/2, etc.)
- Status information (status, statusCode, statusDesc)
- Success/Error information (successCode, successMsg, errorCode, errorMsg)

### 2. Output Schemas (`output_schemas.json`)
Contains 5 output table schemas extracted from the tMap component:
- **capri**: CAPRI table schema (11 fields) - processes CPR messages
- **swing**: SWING table schema (11 fields) - processes SWG messages  
- **item**: Item table schema (5 fields) - processes T messages
- **FPI**: FPI table schema (6 fields) - processes FPI messages
- **FCA**: FCA table schema (6 fields) - processes FPC messages

Each schema includes field definitions with types, lengths, constraints, and filter conditions.

### 3. Mapping Logic (`mapping_logic.json`)
Contains the complete data transformation logic including:
- **Variables**: 7 calculated variables (infoCode, infoMsg, status, messageID, etc.)
- **Output Mappings**: Field-by-field mapping expressions for each output table
- **Filter Conditions**: Logic to determine which records go to which output tables

### 4. Sample Input File (`sample_input.json`)
Contains 6 sample records representing different message types:
- CPR message (success case)
- SWG message (error case)
- T message (item processing)
- FPI message (FPI processing)
- FPC message (FCA processing)
- CPR message (duplicate transaction - filtered out)

### 5. Python Processor (`talend_processor.py`)
Complete Python implementation that:
- Loads the extracted schemas and mapping logic
- Processes input data according to Talend transformation rules
- Applies filters and routing logic
- Generates separate output files for each table
- Handles data type conversions and null value processing

## Key Features Extracted

### Data Routing Logic
- **CPR messages** → capri table
- **SWG messages** → swing table  
- **T messages** → item table
- **FPI messages** → FPI table
- **FPC messages** → FCA table

### Duplicate Detection
- Filters out records where transaction descriptions contain "duplicate transaction"
- Uses variable `Check_duplicates_trans` to implement this logic

### Data Transformations
- **Message ID extraction**: Removes prefixes (T, CPR, FPI, FPC, SWG) from messageSourceIdentifier
- **Status mapping**: Converts "OK"→3, "NOK"→4, other→0
- **Info code/message logic**: Uses success info if available, otherwise error info
- **Date/time concatenation**: Combines respAckDate + respAckTime
- **Fixed correspondent account numbers**: FPI=100022022, FCA=100026847

## Usage

### Running the Processor
```bash
python3 talend_processor.py
```

### Processing Custom Input
```python
from talend_processor import TalendProcessor

processor = TalendProcessor(
    'input_schema.json',
    'output_schemas.json', 
    'mapping_logic.json'
)

output_files = processor.process_file('your_input.json')
```

## Output Files Generated

When processing the sample input, the following output files are created:
- `capri_output.json` - 1 record (CPR message)
- `swing_output.json` - 1 record (SWG message)  
- `item_output.json` - 1 record (T message)
- `FPI_output.json` - 1 record (FPI message)
- `FCA_output.json` - 1 record (FCA message)

Note: The duplicate CPR message is correctly filtered out and does not appear in any output.

## Technical Implementation

### Schema Extraction
- Parsed Talend XML `<inputTables>` and `<outputTables>` sections
- Extracted field definitions, types, and constraints
- Captured metadata connector information

### Mapping Logic Extraction  
- Extracted `<varTables>` variable definitions and expressions
- Captured `<mapperTableEntries>` field mapping expressions
- Preserved filter conditions (`expressionFilter` attributes)

### Python Implementation
- Implements Talend expression evaluation logic
- Handles Talend-specific functions (Relational.ISNULL, TalendDate.parseDate)
- Supports BigDecimal conversions and conditional expressions
- Provides comprehensive error handling and logging

## Verification

The implementation has been tested and verified to:
✅ Successfully parse the Talend XML file  
✅ Extract accurate input/output schemas  
✅ Capture complete mapping logic  
✅ Process sample data correctly  
✅ Generate expected output files  
✅ Apply filters and transformations properly  
✅ Handle duplicate detection logic  

All deliverables are ready for production use.
