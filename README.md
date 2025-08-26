# ETL Fast Processing

A comprehensive ETL (Extract, Transform, Load) tool for onboarding data from multiple sources including API endpoints, Swift financial messages, and batch file processing. The system features an Angular frontend for client interaction, AI-powered schema detection, data cleaning and transformation, workflow management with approval processes, comprehensive logging for data lineage, and exception reporting.

## Features

### Data Ingestion
- **API Endpoints**: REST API for real-time data ingestion
- **Swift Messages**: Financial message processing with MT message support
- **Batch Processing**: File upload and processing (CSV, JSON, Excel)

### Schema Management
- **AI-Powered Detection**: Automatic schema detection using machine learning
- **Manual Override**: Manual schema definition and modification
- **Confidence Scoring**: Schema detection confidence metrics

### Data Processing
- **Cleaning Rules**: Remove duplicates, handle nulls, normalize text
- **Transformation Engine**: Configurable data aggregation and processing
- **Validation**: Data quality checks and validation rules

### Workflow Management
- **Job Scheduling**: Background job processing with Celery
- **Approval Workflows**: Role-based approval processes
- **Automated Retry**: Intelligent retry mechanisms for failed jobs
- **Notifications**: Email notifications for workflow events

### Monitoring & Lineage
- **Data Lineage**: Complete tracking of data flow and transformations
- **Exception Reporting**: Real-time exception detection and alerting
- **Audit Logging**: Comprehensive audit trail for all operations
- **Performance Metrics**: Job performance and system metrics

### Frontend
- **Angular GUI**: Modern web interface for all operations
- **Client Onboarding**: Streamlined data source onboarding process
- **Dashboard**: Real-time monitoring and management dashboard
- **Responsive Design**: Mobile-friendly interface

## Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **PostgreSQL**: Primary database for data storage
- **SQLAlchemy**: ORM for database operations
- **Celery**: Distributed task queue for background jobs
- **Redis**: Message broker and caching
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Machine learning for schema detection

### Frontend
- **Angular 17+**: Modern web framework
- **Angular Material**: UI component library
- **TypeScript**: Type-safe JavaScript
- **RxJS**: Reactive programming

### Infrastructure
- **Docker**: Containerization
- **Alembic**: Database migrations
- **Poetry**: Python dependency management
- **JWT**: Authentication and authorization

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/cw257900/etl_fastprocessing.git
cd etl_fastprocessing
```

2. Set up the backend:
```bash
cd backend
poetry install
cp .env.example .env
# Edit .env with your database and configuration settings
```

3. Run database migrations:
```bash
poetry run alembic upgrade head
```

4. Start the backend server:
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Set up the frontend:
```bash
cd frontend
npm install
```

2. Configure environment:
```bash
cp src/environments/environment.example.ts src/environments/environment.ts
# Edit environment.ts with your backend URL
```

3. Start the development server:
```bash
ng serve
```

### Access the Application

- Frontend: http://localhost:4200
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Documentation

The API documentation is automatically generated and available at `/docs` when running the backend server. Key endpoints include:

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/token` - User login

### Data Sources
- `POST /api/v1/data-sources/` - Create data source
- `GET /api/v1/data-sources/` - List data sources
- `GET /api/v1/data-sources/{id}` - Get data source details

### Data Ingestion
- `POST /api/v1/ingestion/api` - Ingest data via API
- `POST /api/v1/ingestion/swift` - Process Swift messages
- `POST /api/v1/ingestion/batch` - Upload batch files

### Processing
- `GET /api/v1/processing/jobs` - List processing jobs
- `POST /api/v1/processing/jobs/{id}/transform` - Apply transformations
- `POST /api/v1/processing/jobs/{id}/retry` - Retry failed jobs

### Workflow
- `GET /api/v1/workflow/approvals` - List pending approvals
- `POST /api/v1/workflow/approvals/{id}/approve` - Approve job
- `POST /api/v1/workflow/approvals/{id}/reject` - Reject job

### Lineage & Monitoring
- `GET /api/v1/lineage/job/{id}` - Get job lineage
- `GET /api/v1/exceptions/` - List exceptions
- `POST /api/v1/exceptions/{id}/resolve` - Resolve exception

## Architecture

The system follows a microservices architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Angular GUI   │    │   FastAPI       │    │   PostgreSQL    │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Celery        │◄──►│   Redis         │
                       │   Workers       │    │   Message Broker│
                       └─────────────────┘    └─────────────────┘
```

### Key Components

1. **Ingestion Layer**: Handles data from multiple sources
2. **Processing Engine**: Applies transformations and cleaning rules
3. **Schema Detection**: AI-powered schema inference
4. **Workflow Engine**: Manages job lifecycle and approvals
5. **Lineage Tracker**: Records data flow and transformations
6. **Exception Handler**: Monitors and reports data quality issues
7. **Notification System**: Sends alerts and updates

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and add tests
4. Run the test suite: `poetry run pytest`
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to the branch: `git push origin feature/new-feature`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the architecture documentation in `/docs`
