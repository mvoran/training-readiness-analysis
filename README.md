# Training Readiness Dashboard

A comprehensive training analytics platform that combines DuckDB for data processing with Metabase for visualization. This project helps athletes track and analyze their training stress, readiness, and performance metrics.

## Project Overview

This project provides:
- **Data Processing**: DuckDB-based data pipeline for TrainingPeaks exports
- **Analytics**: Automated calculation of training stress ratios and readiness metrics
- **Visualization**: Metabase dashboard for interactive data exploration
- **Export Capabilities**: Standardized CSV exports for further analysis

## Project Structure

```
TrainingReadiness/
├── database/
│   ├── training_readiness.duckdb    # Main DuckDB database
│   ├── queries/                     # Data processing scripts
│   │   ├── load_trainingpeaks_data.py
│   │   ├── load_trainingpeaks_data.sql
│   │   ├── clean_trainingpeaks_data.py
│   │   ├── calculate_1wk_4wk_ratio_training_stress.py
│   │   ├── calculate_1wk_training_stress.py
│   │   ├── calculate_48hr_training_stress.py
│   │   └── append_to_duckdb.sql
│   └── data/                        # Generated CSV exports
├── visualization/
│   └── docker/                      # Metabase Docker setup
│       ├── docker-compose.yaml
│       ├── run_docker.sh
│       ├── metabase-setup.sh
│       ├── env.template
│       └── init-training.sql
├── source_data/                     # Raw TrainingPeaks exports
└── project_docs/                    # Detailed documentation
```

## DuckDB Configuration & Setup

### Prerequisites

1. **Python Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install pandas duckdb duckdb-extensions
   ```

2. **DuckDB CLI** (optional but recommended):
   ```bash
   brew install duckdb
   ```

3. **Install DuckDB Extensions**:
   ```bash
   duckdb
   INSTALL excel;
   LOAD excel;
   .quit
   ```

### Loading Data to DuckDB

The project includes automated scripts for loading TrainingPeaks export data:

#### Basic Data Loading
```bash
cd database/queries
python3 load_trainingpeaks_data.py <path/to/your/data.xlsx>
```

**Supported Formats**:
- Excel files (`.xlsx`, `.xls`)
- CSV files (`.csv`)

**Loading Modes**:
- **Append** (default): Adds new data to existing database
- **Replace**: Replaces all existing data with new data
  ```bash
  python3 load_trainingpeaks_data.py <path/to/your/data.xlsx> -r
  ```

#### Data Cleaning
Before loading, you may need to clean your TrainingPeaks data:
```bash
python3 clean_trainingpeaks_data.py
```

*Note: This tool requires standardized RPE (Rate of Perceived Exertion) tracking over time to create actionable reports.*

## Standard Export Queries

The project includes several automated export scripts for common training metrics:

### 1. 1-Week to 4-Week Training Stress Ratio
```bash
python3 calculate_1wk_4wk_ratio_training_stress.py
```
**Output**: `rolling_1wk_4wk_stress_ratio_YYYYMMDD_HHMMSS.csv`

**Metrics**:
- Daily training stress
- 7-day rolling average stress
- 28-day rolling average stress
- Stress ratio (7-day / 28-day)

### 2. 1-Week Training Stress
```bash
python3 calculate_1wk_training_stress.py
```
**Output**: `rolling_1wk_stress_YYYYMMDD_HHMMSS.csv`

### 3. 48-Hour Training Stress
```bash
python3 calculate_48hr_training_stress.py
```
**Output**: `rolling_48hr_stress_YYYYMMDD_HHMMSS.csv`

## Metabase Docker Setup

### Prerequisites

1. **Docker Desktop**: Install from [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/)
2. **Docker Login**: May require `docker logout` followed by `docker login` to resolve 401 errors

### Setup Instructions

1. **Configure Environment**:
   - Copy `visualization/docker/env.template` to `visualization/docker/.env`
   - Update the `.env` file with your configuration:
     ```bash
     # Metabase admin credentials
     MB_SETUP_EMAIL=your-email@example.com
     MB_SETUP_PASSWORD=your-password
     MB_SETUP_FIRST_NAME=Your
     MB_SETUP_LAST_NAME=Name
     MB_SITE_NAME=Training Readiness
     
     # Path configuration
     ICLOUD_DIR=/path/to/your/iCloud/project/directory
     LOCAL_DIR=/Users/yourusername/Docker/Training_Readiness
     ```

2. **Setup Local Directory**:
   ```bash
   mkdir -p /Users/yourusername/Docker/Training_Readiness
   cp visualization/docker/run_docker.sh /Users/yourusername/Docker/Training_Readiness/
   cp visualization/docker/.env /Users/yourusername/Docker/Training_Readiness/
   ```

3. **Start Metabase**:
   ```bash
   cd /Users/yourusername/Docker/Training_Readiness
   ./run_docker.sh up -d
   ```

4. **Access Metabase**:
   - Open browser to `http://localhost:3000`
   - Login with your configured credentials
   - The external database connection will be automatically configured

### Docker Management

- **Start in background**: `./run_docker.sh up -d`
- **Start with logs**: `./run_docker.sh up`
- **Stop containers**: `./run_docker.sh down`
- **Stop and remove volumes**: `./run_docker.sh down -v`

### Logging

The setup automatically captures logs to the `logs/` directory:
- `docker-compose.log`: Overall Docker Compose logs
- `postgres_db.log`: PostgreSQL database logs
- `metabase.log`: Metabase application logs
- `metabase_setup.log`: Setup script logs

View logs in real-time:
```bash
tail -f logs/metabase_setup.log
```

## Data Flow

1. **Export** training data from TrainingPeaks
2. **Load** data into DuckDB using the provided scripts
3. **Calculate** training metrics using the export queries
4. **Visualize** results in Metabase dashboard
5. **Export** standardized CSV files for further analysis

## Key Features

- **Automated Data Processing**: Streamlined pipeline from TrainingPeaks to analytics
- **Training Stress Analysis**: Rolling averages and stress ratios for readiness assessment
- **Interactive Dashboards**: Metabase-based visualization with drill-down capabilities
- **Standardized Exports**: Consistent CSV format for external analysis
- **Docker-Based Deployment**: Easy setup and management of the visualization layer

## Troubleshooting

### Common Issues

1. **Docker 401 Error**: Run `docker logout` then `docker login`
2. **Metabase Not Starting**: Check logs with `docker logs metabase`
3. **Data Loading Errors**: Ensure Excel extension is installed in DuckDB
4. **Permission Issues**: Make sure log files are writable

### Getting Help

- Check the `project_docs/` directory for detailed setup guides
- Review container logs in the `logs/` directory
- Ensure all prerequisites are installed and configured

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the terms specified in the LICENSE file.