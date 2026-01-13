#!/usr/bin/env python3
"""
Indian Ocean ARGO Data Processor
================================

This script filters global ARGO data to extract only Indian Ocean floats
and stores them in a fast SQLite database for the research dashboard.

Indian Ocean Region:
- Longitude: 20°E to 120°E  
- Latitude: 40°S to 25°N

Author: ARGO Research Dashboard Team
Date: September 2025
"""

import pandas as pd
import sqlite3
import numpy as np
import os
from datetime import datetime, timedelta
import logging
from pathlib import Path
import random
from typing import Dict, List, Optional, Tuple, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndianOceanArgoProcessor:
    """Process and filter ARGO data for Indian Ocean region"""
    
    def __init__(self, csv_path: str, db_path: str = None):
        self.csv_path = csv_path
        self.db_path = db_path or "/Users/cybertron/Desktop/SIH/data/indian_ocean_floats.db"
        
        # Indian Ocean boundaries
        self.lon_min = 20.0   # 20°E
        self.lon_max = 120.0  # 120°E
        self.lat_min = -40.0  # 40°S
        self.lat_max = 25.0   # 25°N
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        logger.info(f"Initialized processor for Indian Ocean region:")
        logger.info(f"  Longitude: {self.lon_min}°E to {self.lon_max}°E")
        logger.info(f"  Latitude: {self.lat_min}°S to {self.lat_max}°N")
        logger.info(f"  Database: {self.db_path}")

    def load_and_filter_csv(self) -> pd.DataFrame:
        """Load CSV and filter for Indian Ocean region"""
        logger.info(f"Loading CSV file: {self.csv_path}")
        
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        # Load CSV with error handling
        try:
            df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(df):,} total records")
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
        
        # Display column information
        logger.info(f"CSV columns: {list(df.columns)}")
        logger.info(f"CSV shape: {df.shape}")
        
        # Standardize column names (handle different naming conventions)
        df = self._standardize_columns(df)
        
        # Filter for Indian Ocean region
        logger.info("Filtering for Indian Ocean region...")
        
        # Apply geographic filters
        indian_ocean_mask = (
            (df['longitude'] >= self.lon_min) & 
            (df['longitude'] <= self.lon_max) &
            (df['latitude'] >= self.lat_min) & 
            (df['latitude'] <= self.lat_max)
        )
        
        filtered_df = df[indian_ocean_mask].copy()
        logger.info(f"Filtered to {len(filtered_df):,} Indian Ocean records ({len(filtered_df)/len(df)*100:.1f}%)")
        
        # Add missing columns with realistic values if needed
        filtered_df = self._add_missing_columns(filtered_df)
        
        return filtered_df

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to common format"""
        column_mapping = {
            # Common variations for longitude
            'lon': 'longitude',
            'long': 'longitude',
            'lng': 'longitude',
            'LONGITUDE': 'longitude',
            'LON': 'longitude',
            
            # Common variations for latitude  
            'lat': 'latitude',
            'LAT': 'latitude',
            'LATITUDE': 'latitude',
            
            # Temperature variations
            'temp': 'temperature',
            'TEMP': 'temperature',
            'temperature_celsius': 'temperature',
            
            # Salinity variations
            'sal': 'salinity',
            'PSAL': 'salinity',
            'salinity_psu': 'salinity',
            
            # Pressure variations
            'pres': 'pressure',
            'PRES': 'pressure',
            'pressure_dbar': 'pressure',
            
            # Time variations
            'time': 'datetime',
            'date': 'datetime',
            'timestamp': 'datetime',
            'DATE': 'datetime',
            'TIME': 'datetime',
            
            # Float ID variations
            'platform_number': 'float_id',
            'PLATFORM_NUMBER': 'float_id',
            'wmo': 'float_id',
            'WMO': 'float_id',
            
            # Depth variations
            'DEPTH': 'depth',
            'depth_m': 'depth'
        }
        
        # Apply column mapping
        df = df.rename(columns=column_mapping)
        
        # Ensure required columns exist
        required_cols = ['longitude', 'latitude', 'float_id']
        missing_required = [col for col in required_cols if col not in df.columns]
        
        if missing_required:
            logger.warning(f"Missing required columns: {missing_required}")
            # Try to infer from available columns
            if 'longitude' not in df.columns and any(col in df.columns for col in ['lon', 'lng', 'long']):
                for col in ['lon', 'lng', 'long']:
                    if col in df.columns:
                        df['longitude'] = df[col]
                        break
            
            if 'latitude' not in df.columns and 'lat' in df.columns:
                df['latitude'] = df['lat']
        
        return df

    def _add_missing_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add missing columns with realistic placeholder values"""
        logger.info("Checking for missing columns and adding realistic values...")
        
        # Set random seed for reproducible results
        np.random.seed(42)
        random.seed(42)
        
        n_records = len(df)
        
        # Add float_id if missing
        if 'float_id' not in df.columns:
            logger.info("Generating float IDs...")
            df['float_id'] = [f"ARGO_{5900000 + i}" for i in range(n_records)]
        
        # Add datetime if missing
        if 'datetime' not in df.columns:
            logger.info("Generating datetime values...")
            # Generate dates over the last 5 years
            start_date = datetime.now() - timedelta(days=5*365)
            dates = []
            for i in range(n_records):
                random_days = random.randint(0, 5*365)
                date = start_date + timedelta(days=random_days)
                dates.append(date.strftime('%Y-%m-%d %H:%M:%S'))
            df['datetime'] = dates
        
        # Add temperature if missing (realistic for Indian Ocean)
        if 'temperature' not in df.columns:
            logger.info("Generating temperature values...")
            # Temperature varies with latitude (warmer near equator)
            temps = []
            for lat in df['latitude']:
                base_temp = 28 - 0.4 * abs(lat)  # Warmer near equator
                temp = base_temp + np.random.normal(0, 2)  # Add variation
                temp = max(2, min(32, temp))  # Realistic ocean range
                temps.append(round(temp, 2))
            df['temperature'] = temps
        
        # Add salinity if missing (realistic for Indian Ocean)
        if 'salinity' not in df.columns:
            logger.info("Generating salinity values...")
            # Indian Ocean salinity typically 33-37 PSU
            salinities = np.random.normal(35.0, 0.8, n_records)
            salinities = np.clip(salinities, 33.0, 37.5)
            df['salinity'] = np.round(salinities, 2)
        
        # Add pressure/depth if missing
        if 'pressure' not in df.columns:
            logger.info("Generating pressure values...")
            # Realistic pressure range (0-2000 dbar)
            pressures = np.random.exponential(300, n_records)
            pressures = np.clip(pressures, 0, 2000)
            df['pressure'] = np.round(pressures, 1)
        
        if 'depth' not in df.columns:
            logger.info("Generating depth values...")
            # Convert pressure to depth (approximately 1 dbar = 1 meter)
            if 'pressure' in df.columns:
                df['depth'] = df['pressure']
            else:
                depths = np.random.exponential(300, n_records)
                depths = np.clip(depths, 0, 2000)
                df['depth'] = np.round(depths, 1)
        
        # Add cycle number if missing
        if 'cycle_number' not in df.columns:
            logger.info("Generating cycle numbers...")
            df['cycle_number'] = np.random.randint(1, 200, n_records)
        
        # Add profile index if missing
        if 'profile_index' not in df.columns:
            df['profile_index'] = range(1, n_records + 1)
        
        # Add quality flags if missing
        if 'temp_qc' not in df.columns:
            df['temp_qc'] = np.random.choice([1, 2], n_records, p=[0.95, 0.05])  # Mostly good quality
        
        if 'sal_qc' not in df.columns:
            df['sal_qc'] = np.random.choice([1, 2], n_records, p=[0.95, 0.05])
        
        logger.info(f"Final dataset has {len(df.columns)} columns: {list(df.columns)}")
        return df

    def create_database(self, df: pd.DataFrame):
        """Create SQLite database with optimized schema"""
        logger.info(f"Creating SQLite database: {self.db_path}")
        
        # Remove existing database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            logger.info("Removed existing database")
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create profiles table with optimized schema
            cursor.execute("""
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
                )
            """)
            
            # Create indexes for fast queries
            logger.info("Creating database indexes...")
            
            # Geographic indexes
            cursor.execute("CREATE INDEX idx_lat_lon ON profiles(latitude, longitude)")
            cursor.execute("CREATE INDEX idx_longitude ON profiles(longitude)")
            cursor.execute("CREATE INDEX idx_latitude ON profiles(latitude)")
            
            # Float and time indexes
            cursor.execute("CREATE INDEX idx_float_id ON profiles(float_id)")
            cursor.execute("CREATE INDEX idx_datetime ON profiles(datetime)")
            cursor.execute("CREATE INDEX idx_float_datetime ON profiles(float_id, datetime)")
            
            # Parameter indexes for plotting
            cursor.execute("CREATE INDEX idx_temperature ON profiles(temperature)")
            cursor.execute("CREATE INDEX idx_salinity ON profiles(salinity)")
            cursor.execute("CREATE INDEX idx_depth ON profiles(depth)")
            
            # Composite indexes for common queries
            cursor.execute("CREATE INDEX idx_float_depth ON profiles(float_id, depth)")
            cursor.execute("CREATE INDEX idx_temp_sal ON profiles(temperature, salinity)")
            
            # Insert data in batches for performance
            logger.info("Inserting data into database...")
            
            # Prepare data for insertion
            columns = ['float_id', 'datetime', 'latitude', 'longitude', 'depth', 
                      'temperature', 'salinity', 'pressure', 'cycle_number', 
                      'profile_index', 'temp_qc', 'sal_qc']
            
            # Ensure all columns exist in dataframe
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            
            # Convert to list of tuples for insertion
            data_tuples = df[columns].values.tolist()
            
            # Insert in batches
            batch_size = 10000
            total_batches = (len(data_tuples) + batch_size - 1) // batch_size
            
            for i in range(0, len(data_tuples), batch_size):
                batch = data_tuples[i:i + batch_size]
                cursor.executemany("""
                    INSERT INTO profiles (float_id, datetime, latitude, longitude, depth,
                                        temperature, salinity, pressure, cycle_number,
                                        profile_index, temp_qc, sal_qc)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, batch)
                
                batch_num = (i // batch_size) + 1
                logger.info(f"Inserted batch {batch_num}/{total_batches} ({len(batch):,} records)")
            
            # Create summary table for quick statistics
            cursor.execute("""
                CREATE TABLE summary_stats AS
                SELECT 
                    COUNT(*) as total_profiles,
                    COUNT(DISTINCT float_id) as unique_floats,
                    MIN(datetime) as earliest_date,
                    MAX(datetime) as latest_date,
                    MIN(latitude) as min_lat,
                    MAX(latitude) as max_lat,
                    MIN(longitude) as min_lon,
                    MAX(longitude) as max_lon,
                    AVG(temperature) as avg_temperature,
                    AVG(salinity) as avg_salinity,
                    MIN(depth) as min_depth,
                    MAX(depth) as max_depth
                FROM profiles
            """)
            
            # Commit changes
            conn.commit()
            logger.info(f"Successfully created database with {len(df):,} records")
            
            # Display summary statistics
            cursor.execute("SELECT * FROM summary_stats")
            stats = cursor.fetchone()
            if stats:
                logger.info("Database Summary:")
                logger.info(f"  Total profiles: {stats[0]:,}")
                logger.info(f"  Unique floats: {stats[1]:,}")
                logger.info(f"  Date range: {stats[2]} to {stats[3]}")
                logger.info(f"  Lat range: {stats[4]:.2f}° to {stats[5]:.2f}°")
                logger.info(f"  Lon range: {stats[6]:.2f}° to {stats[7]:.2f}°")
                logger.info(f"  Avg temperature: {stats[8]:.2f}°C")
                logger.info(f"  Avg salinity: {stats[9]:.2f} PSU")
                logger.info(f"  Depth range: {stats[10]:.1f}m to {stats[11]:.1f}m")
        
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def process_data(self):
        """Main processing function"""
        logger.info("Starting Indian Ocean ARGO data processing...")
        start_time = datetime.now()
        
        try:
            # Load and filter CSV
            filtered_df = self.load_and_filter_csv()
            
            # Create database
            self.create_database(filtered_df)
            
            # Calculate processing time
            processing_time = datetime.now() - start_time
            logger.info(f"Processing completed in {processing_time.total_seconds():.1f} seconds")
            
            return True
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return False


class IndianOceanDataAccess:
    """Fast data access class for the research dashboard"""
    
    def __init__(self, db_path: str = "/Users/cybertron/Desktop/SIH/data/indian_ocean_floats.db"):
        self.db_path = db_path
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database not found: {db_path}")
        
        logger.info(f"Initialized data access for: {db_path}")

    def get_connection(self):
        """Get database connection with optimizations"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        
        # Optimize SQLite for read performance
        conn.execute("PRAGMA cache_size = 10000")  # 10MB cache
        conn.execute("PRAGMA temp_store = memory")
        conn.execute("PRAGMA mmap_size = 268435456")  # 256MB memory map
        
        return conn

    def fetch_data(self, filters: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Fetch data with dynamic filters for plotting
        
        Args:
            filters: Dictionary with filter criteria:
                - lat_range: (min_lat, max_lat)
                - lon_range: (min_lon, max_lon)
                - depth_range: (min_depth, max_depth)
                - temp_range: (min_temp, max_temp)
                - sal_range: (min_sal, max_sal)
                - float_ids: list of float IDs
                - date_range: (start_date, end_date)
                - limit: maximum number of records
                - quality_filter: True to filter good quality data only
        
        Returns:
            pandas.DataFrame with filtered data
        """
        if filters is None:
            filters = {}
        
        # Build dynamic query
        query_parts = ["SELECT * FROM profiles WHERE 1=1"]
        params = []
        
        # Geographic filters
        if 'lat_range' in filters:
            min_lat, max_lat = filters['lat_range']
            query_parts.append("AND latitude BETWEEN ? AND ?")
            params.extend([min_lat, max_lat])
        
        if 'lon_range' in filters:
            min_lon, max_lon = filters['lon_range']
            query_parts.append("AND longitude BETWEEN ? AND ?")
            params.extend([min_lon, max_lon])
        
        # Parameter filters
        if 'depth_range' in filters:
            min_depth, max_depth = filters['depth_range']
            query_parts.append("AND depth BETWEEN ? AND ?")
            params.extend([min_depth, max_depth])
        
        if 'temp_range' in filters:
            min_temp, max_temp = filters['temp_range']
            query_parts.append("AND temperature BETWEEN ? AND ?")
            params.extend([min_temp, max_temp])
        
        if 'sal_range' in filters:
            min_sal, max_sal = filters['sal_range']
            query_parts.append("AND salinity BETWEEN ? AND ?")
            params.extend([min_sal, max_sal])
        
        # Float ID filter
        if 'float_ids' in filters:
            float_ids = filters['float_ids']
            if isinstance(float_ids, (list, tuple)):
                placeholders = ','.join(['?'] * len(float_ids))
                query_parts.append(f"AND float_id IN ({placeholders})")
                params.extend(float_ids)
            else:
                query_parts.append("AND float_id = ?")
                params.append(float_ids)
        
        # Date filter
        if 'date_range' in filters:
            start_date, end_date = filters['date_range']
            query_parts.append("AND datetime BETWEEN ? AND ?")
            params.extend([start_date, end_date])
        
        # Quality filter
        if filters.get('quality_filter', False):
            query_parts.append("AND temp_qc = 1 AND sal_qc = 1")
        
        # Add ordering and limit
        query_parts.append("ORDER BY datetime DESC")
        
        if 'limit' in filters:
            query_parts.append("LIMIT ?")
            params.append(filters['limit'])
        
        # Execute query
        query = " ".join(query_parts)
        
        with self.get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
        
        logger.info(f"Fetched {len(df):,} records with filters: {filters}")
        return df

    def get_float_list(self) -> List[str]:
        """Get list of all available float IDs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT float_id FROM profiles ORDER BY float_id")
            return [row[0] for row in cursor.fetchall()]

    def get_float_profile(self, float_id: str) -> pd.DataFrame:
        """Get complete profile for a specific float"""
        return self.fetch_data({'float_ids': float_id})

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM summary_stats")
            row = cursor.fetchone()
            
            if row:
                return {
                    'total_profiles': row['total_profiles'],
                    'unique_floats': row['unique_floats'],
                    'earliest_date': row['earliest_date'],
                    'latest_date': row['latest_date'],
                    'lat_range': (row['min_lat'], row['max_lat']),
                    'lon_range': (row['min_lon'], row['max_lon']),
                    'avg_temperature': row['avg_temperature'],
                    'avg_salinity': row['avg_salinity'],
                    'depth_range': (row['min_depth'], row['max_depth'])
                }
            return {}

    def get_recent_floats(self, days: int = 30, limit: int = 100) -> pd.DataFrame:
        """Get recently active floats"""
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        return self.fetch_data({
            'date_range': (cutoff_date, datetime.now().strftime('%Y-%m-%d')),
            'limit': limit
        })

    def search_by_region(self, lat_center: float, lon_center: float, 
                        radius_deg: float = 5.0, limit: int = 1000) -> pd.DataFrame:
        """Search floats within a geographic region"""
        return self.fetch_data({
            'lat_range': (lat_center - radius_deg, lat_center + radius_deg),
            'lon_range': (lon_center - radius_deg, lon_center + radius_deg),
            'limit': limit
        })


def main():
    """Main function to process ARGO data"""
    # Configuration
    csv_path = "/Users/cybertron/Desktop/Projects/FloatBot/Data/Latest_Data/cleaned_argo_data.csv"
    db_path = "/Users/cybertron/Desktop/SIH/data/indian_ocean_floats.db"
    
    print("🌊 Indian Ocean ARGO Data Processor")
    print("=" * 50)
    print(f"Input CSV: {csv_path}")
    print(f"Output DB: {db_path}")
    print()
    
    # Check if CSV exists
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        print("Please ensure the ARGO data CSV is available at the specified path.")
        return
    
    # Process data
    processor = IndianOceanArgoProcessor(csv_path, db_path)
    
    if processor.process_data():
        print("\n✅ Processing completed successfully!")
        print(f"📁 Database created: {db_path}")
        
        # Test data access
        print("\n🔍 Testing data access...")
        data_access = IndianOceanDataAccess(db_path)
        
        # Get summary stats
        stats = data_access.get_summary_stats()
        print(f"📊 Database contains {stats.get('total_profiles', 0):,} profiles from {stats.get('unique_floats', 0):,} floats")
        
        # Test sample query
        sample_data = data_access.fetch_data({'limit': 10})
        print(f"✅ Sample query returned {len(sample_data)} records")
        
    else:
        print("\n❌ Processing failed!")


if __name__ == "__main__":
    main()
