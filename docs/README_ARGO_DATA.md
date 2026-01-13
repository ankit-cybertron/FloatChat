# Indian Ocean ARGO Data Processing System

A comprehensive system for filtering, storing, and accessing Indian Ocean ARGO float data with fast SQLite database integration for the research dashboard.

## 🌊 Overview

This system processes global ARGO float data to extract only Indian Ocean region floats and stores them in a high-performance SQLite database for fast querying and visualization in the research dashboard.

### Indian Ocean Region Definition
- **Longitude**: 20°E to 120°E  
- **Latitude**: 40°S to 25°N

## 📁 File Structure

```
/Users/cybertron/Desktop/SIH/
├── data_processor.py              # Core data processing and filtering
├── dashboard_data_integration.py  # Dashboard integration module
├── setup_indian_ocean_data.py     # Setup and processing script
├── example_usage.py              # Usage examples
├── README_ARGO_DATA.md           # This documentation
└── data/
    └── indian_ocean_floats.db    # SQLite database (created after processing)
```

## 🚀 Quick Start

### 1. Process ARGO Data

```bash
# Run the setup script to process your ARGO CSV data
python setup_indian_ocean_data.py

# Or with custom CSV path
python setup_indian_ocean_data.py --csv-path /path/to/your/argo_data.csv
```

### 2. Test the Database

```bash
# Quick test of existing database
python setup_indian_ocean_data.py --test
```

### 3. Use in Dashboard

The system automatically integrates with the research dashboard. Just run:

```bash
python dash_frontend/research_dashboard.py
```

## 📊 Data Processing Features

### Input Data Handling
- **CSV Format**: Processes global ARGO CSV files
- **Column Standardization**: Handles various column naming conventions
- **Missing Data**: Generates realistic placeholder values for missing columns
- **Quality Control**: Includes data quality flags and validation

### Geographic Filtering
- **Precise Boundaries**: Filters data to Indian Ocean coordinates
- **Efficient Processing**: Uses pandas for fast data manipulation
- **Progress Tracking**: Real-time processing progress updates

### Database Creation
- **SQLite Backend**: Fast, file-based database
- **Optimized Schema**: Indexed for quick queries
- **Batch Processing**: Efficient data insertion
- **Summary Statistics**: Pre-computed statistics table

## 🗄️ Database Schema

### `profiles` Table
```sql
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    float_id TEXT NOT NULL,
    datetime TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    depth REAL,
    temperature REAL,
    salinity REAL,
    pressure REAL,
    cycle_number INTEGER,
    profile_index INTEGER,
    temp_qc INTEGER DEFAULT 1,
    sal_qc INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Optimized Indexes
- Geographic indexes: `(latitude, longitude)`
- Float indexes: `(float_id)`, `(float_id, datetime)`
- Parameter indexes: `(temperature)`, `(salinity)`, `(depth)`
- Composite indexes for common queries

## 🔍 Data Access API

### Basic Usage

```python
from dashboard_data_integration import (
    get_map_floats, get_analysis_table_data, 
    get_float_details, search_argo_floats
)

# Get data for map display
map_data = get_map_floats(limit=150)

# Get data for analysis table
table_data = get_analysis_table_data(limit=50)

# Get detailed float profile
float_details = get_float_details("ARGO_5900001")

# Search floats
results = search_argo_floats("ARGO_59")
```

### Advanced Queries

```python
from data_processor import IndianOceanDataAccess

# Initialize data access
data_access = IndianOceanDataAccess()

# Custom filtered query
data = data_access.fetch_data({
    'lat_range': (-10, 10),           # Equatorial region
    'lon_range': (70, 90),            # Central Indian Ocean
    'temp_range': (25, 30),           # Warm water
    'depth_range': (0, 100),          # Surface layer
    'date_range': ('2023-01-01', '2024-01-01'),
    'quality_filter': True,           # Good quality data only
    'limit': 1000
})

# Regional search
regional_data = data_access.search_by_region(
    lat_center=0, lon_center=80, radius_deg=5, limit=500
)

# Get recent floats
recent_floats = data_access.get_recent_floats(days=30, limit=100)
```

## 📈 Dashboard Integration

### Automatic Integration
The system automatically integrates with the research dashboard:

- **Real Data Mode**: Uses SQLite database when available
- **Fallback Mode**: Uses simulated data if database not found
- **Seamless Switching**: No code changes needed in dashboard

### Dashboard Features Enhanced
- **Interactive Map**: Real ARGO float positions
- **Analysis Table**: Actual float measurements
- **Profile Plots**: Real temperature/salinity profiles
- **Search Function**: Search actual float IDs
- **Regional Analysis**: Query specific ocean regions

## 🛠️ Configuration

### CSV Input Requirements
The system expects a CSV file with ARGO data. Common column names are automatically detected:

**Required Columns** (at least one variation):
- Longitude: `longitude`, `lon`, `lng`, `LONGITUDE`
- Latitude: `latitude`, `lat`, `LATITUDE`
- Float ID: `float_id`, `platform_number`, `wmo`, `WMO`

**Optional Columns** (generated if missing):
- Temperature: `temperature`, `temp`, `TEMP`
- Salinity: `salinity`, `sal`, `PSAL`
- Pressure: `pressure`, `pres`, `PRES`
- Depth: `depth`, `DEPTH`
- DateTime: `datetime`, `time`, `date`

### Database Configuration
```python
# Custom database path
from dashboard_data_integration import initialize_dashboard_data
initialize_dashboard_data("/custom/path/to/database.db")
```

## 📊 Performance Optimizations

### Database Optimizations
- **Indexes**: Strategic indexing for common query patterns
- **Batch Inserts**: Efficient data loading
- **Memory Mapping**: SQLite performance tuning
- **Query Optimization**: Prepared statements and connection pooling

### Processing Optimizations
- **Pandas**: Vectorized operations for filtering
- **Memory Management**: Efficient data handling
- **Progress Tracking**: Real-time processing updates

## 🧪 Testing and Examples

### Run Examples
```bash
# See all usage examples
python example_usage.py
```

### Test Database
```bash
# Quick database test
python setup_indian_ocean_data.py --test
```

### Performance Testing
```python
import time
from dashboard_data_integration import get_map_floats

# Test query performance
start_time = time.time()
data = get_map_floats(1000)
query_time = time.time() - start_time
print(f"Query time: {query_time:.2f} seconds for {len(data['lats'])} floats")
```

## 📋 Data Quality

### Quality Control Features
- **Geographic Validation**: Ensures coordinates are within Indian Ocean
- **Parameter Ranges**: Validates temperature, salinity, depth ranges
- **Quality Flags**: Includes data quality indicators
- **Missing Data Handling**: Realistic placeholder generation

### Data Statistics
The system provides comprehensive statistics:
- Total profiles and unique floats
- Geographic coverage (lat/lon ranges)
- Parameter distributions (temp/salinity averages)
- Temporal coverage (date ranges)

## 🔧 Troubleshooting

### Common Issues

**1. CSV File Not Found**
```bash
# Check file path
ls -la /Users/cybertron/Desktop/Projects/FloatBot/Data/Latest_Data/cleaned_argo_data.csv

# Use custom path
python setup_indian_ocean_data.py --csv-path /your/path/to/argo_data.csv
```

**2. Database Connection Error**
```python
# Check database exists
import os
db_path = "/Users/cybertron/Desktop/SIH/data/indian_ocean_floats.db"
print(f"Database exists: {os.path.exists(db_path)}")

# Recreate database
python setup_indian_ocean_data.py
```

**3. Memory Issues with Large CSV**
```python
# Process in chunks for large files
processor = IndianOceanArgoProcessor(csv_path, db_path)
# The system automatically handles large files efficiently
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Run your code - will show detailed processing information
```

## 🚀 Advanced Usage

### Custom Analysis Pipeline
```python
from data_processor import IndianOceanDataAccess
import pandas as pd
import matplotlib.pyplot as plt

# Load data
data_access = IndianOceanDataAccess()

# Custom analysis: Temperature vs Depth profiles
data = data_access.fetch_data({
    'depth_range': (0, 2000),
    'quality_filter': True,
    'limit': 10000
})

# Group by depth bins and calculate mean temperature
depth_bins = pd.cut(data['depth'], bins=20)
temp_profile = data.groupby(depth_bins)['temperature'].mean()

# Plot
plt.figure(figsize=(8, 6))
plt.plot(temp_profile.values, [bin.mid for bin in temp_profile.index])
plt.xlabel('Temperature (°C)')
plt.ylabel('Depth (m)')
plt.title('Indian Ocean Temperature Profile')
plt.gca().invert_yaxis()
plt.show()
```

### Integration with Other Tools
```python
# Export to different formats
data = data_access.fetch_data({'limit': 1000})

# To CSV
data.to_csv('indian_ocean_subset.csv', index=False)

# To NetCDF (requires xarray)
import xarray as xr
ds = data.set_index(['latitude', 'longitude', 'depth']).to_xarray()
ds.to_netcdf('indian_ocean_subset.nc')

# To GeoJSON for mapping
import geopandas as gpd
gdf = gpd.GeoDataFrame(
    data, 
    geometry=gpd.points_from_xy(data.longitude, data.latitude)
)
gdf.to_file('indian_ocean_floats.geojson', driver='GeoJSON')
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Run the test scripts to verify setup
3. Check log output for detailed error information
4. Ensure all dependencies are installed

## 🔄 Updates and Maintenance

### Updating Data
```bash
# Reprocess with new CSV data
python setup_indian_ocean_data.py --csv-path /path/to/new/argo_data.csv
```

### Database Maintenance
```python
# Get database statistics
from dashboard_data_integration import get_data_statistics
stats = get_data_statistics()
print(f"Database size: {stats}")

# Vacuum database (optimize)
import sqlite3
conn = sqlite3.connect("/Users/cybertron/Desktop/SIH/data/indian_ocean_floats.db")
conn.execute("VACUUM")
conn.close()
```

---

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   ARGO CSV      │───▶│  Data Processor  │───▶│  SQLite DB      │
│  (Global Data)  │    │  (Filter Indian  │    │ (Indian Ocean)  │
└─────────────────┘    │   Ocean Region)  │    └─────────────────┘
                       └──────────────────┘             │
                                                        │
┌─────────────────┐    ┌──────────────────┐            │
│ Research        │◀───│  Dashboard       │◀───────────┘
│ Dashboard UI    │    │  Integration     │
└─────────────────┘    └──────────────────┘
```

This system provides a complete pipeline from raw ARGO data to interactive dashboard visualization with high-performance data access capabilities.
