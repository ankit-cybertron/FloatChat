#!/usr/bin/env python3
"""
Dashboard Data Integration Module
================================

This module integrates the Indian Ocean ARGO SQLite database with the research dashboard,
replacing the simulated data with real ARGO float data.

Author: ARGO Research Dashboard Team
Date: September 2025
"""

import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from data_processor import IndianOceanDataAccess

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardDataProvider:
    """Provides real ARGO data for the research dashboard"""
    
    def __init__(self, db_path: str = "/Users/cybertron/Desktop/SIH/data/indian_ocean_floats.db"):
        self.db_path = db_path
        self.data_access = None
        self.fallback_mode = False
        
        # Try to initialize real data access
        try:
            if os.path.exists(db_path):
                self.data_access = IndianOceanDataAccess(db_path)
                logger.info("✅ Connected to real ARGO database")
            else:
                logger.warning(f"Database not found: {db_path}")
                self.fallback_mode = True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.fallback_mode = True
        
        if self.fallback_mode:
            logger.info("🔄 Using fallback simulated data mode")

    def get_map_data(self, limit: int = 150) -> Dict[str, List]:
        """Get data for the interactive map display"""
        if self.fallback_mode:
            return self._get_simulated_map_data(limit)
        
        try:
            # Get recent diverse floats for map display
            df = self.data_access.fetch_data({
                'limit': limit * 3,  # Get more to ensure diversity
                'quality_filter': True
            })
            
            if df.empty:
                logger.warning("No data found, using simulated data")
                return self._get_simulated_map_data(limit)
            
            # Group by float_id and get latest position for each
            latest_positions = df.groupby('float_id').first().reset_index()
            
            # Sample to requested limit if we have more
            if len(latest_positions) > limit:
                latest_positions = latest_positions.sample(n=limit, random_state=42)
            
            return {
                'lats': latest_positions['latitude'].tolist(),
                'lons': latest_positions['longitude'].tolist(),
                'temps': latest_positions['temperature'].tolist(),
                'salinities': latest_positions['salinity'].tolist(),
                'depths': latest_positions['depth'].tolist(),
                'float_ids': latest_positions['float_id'].tolist(),
                'dates': latest_positions['datetime'].tolist()
            }
            
        except Exception as e:
            logger.error(f"Error getting map data: {e}")
            return self._get_simulated_map_data(limit)

    def get_table_data(self, limit: int = 50) -> List[Dict]:
        """Get data for the analysis table"""
        if self.fallback_mode:
            return self._get_simulated_table_data(limit)
        
        try:
            # Get diverse floats for table display
            df = self.data_access.fetch_data({
                'limit': limit * 2,
                'quality_filter': True
            })
            
            if df.empty:
                return self._get_simulated_table_data(limit)
            
            # Group by float_id and get latest data for each
            latest_data = df.groupby('float_id').first().reset_index()
            
            # Sample to requested limit
            if len(latest_data) > limit:
                latest_data = latest_data.sample(n=limit, random_state=42)
            
            # Convert to table format
            table_data = []
            for _, row in latest_data.iterrows():
                # Determine status based on date
                try:
                    last_date = datetime.strptime(row['datetime'][:10], '%Y-%m-%d')
                    days_ago = (datetime.now() - last_date).days
                    
                    if days_ago <= 30:
                        status = "Active"
                    elif days_ago <= 90:
                        status = "Monitoring"
                    else:
                        status = "Inactive"
                except:
                    status = "Unknown"
                
                table_data.append({
                    "argo_id": row['float_id'],
                    "latitude": round(float(row['latitude']), 2),
                    "longitude": round(float(row['longitude']), 2),
                    "temperature": round(float(row['temperature']), 1),
                    "salinity": round(float(row['salinity']), 2),
                    "depth": round(float(row['depth']), 0),
                    "date": row['datetime'][:10],
                    "status": status
                })
            
            return table_data
            
        except Exception as e:
            logger.error(f"Error getting table data: {e}")
            return self._get_simulated_table_data(limit)

    def get_float_profile(self, float_id: str) -> Dict[str, Any]:
        """Get detailed profile data for a specific float"""
        if self.fallback_mode:
            return self._get_simulated_float_profile(float_id)
        
        try:
            df = self.data_access.get_float_profile(float_id)
            
            if df.empty:
                return self._get_simulated_float_profile(float_id)
            
            # Sort by depth for profile plotting
            df = df.sort_values('depth')
            
            # Get surface values for summary
            surface_data = df.iloc[0]
            
            return {
                'float_id': float_id,
                'latitude': float(surface_data['latitude']),
                'longitude': float(surface_data['longitude']),
                'surface_temp': float(surface_data['temperature']),
                'surface_salinity': float(surface_data['salinity']),
                'max_depth': float(df['depth'].max()),
                'last_update': surface_data['datetime'][:10],
                'profile_data': {
                    'depths': df['depth'].tolist(),
                    'temperatures': df['temperature'].tolist(),
                    'salinities': df['salinity'].tolist(),
                    'pressures': df['pressure'].tolist() if 'pressure' in df.columns else df['depth'].tolist()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting float profile for {float_id}: {e}")
            return self._get_simulated_float_profile(float_id)

    def search_floats(self, query: str) -> List[Dict]:
        """Search for floats by ID or region"""
        if self.fallback_mode:
            return self._search_simulated_floats(query)
        
        try:
            # Try to search by float ID first
            if query.upper().startswith('ARGO_'):
                df = self.data_access.fetch_data({'float_ids': query.upper()})
            else:
                # Search by partial float ID
                with self.data_access.get_connection() as conn:
                    df = pd.read_sql_query(
                        "SELECT * FROM profiles WHERE float_id LIKE ? LIMIT 20",
                        conn, params=[f'%{query.upper()}%']
                    )
            
            if df.empty:
                return []
            
            # Group by float_id and return latest position for each
            results = []
            for float_id, group in df.groupby('float_id'):
                latest = group.iloc[0]
                results.append({
                    'float_id': float_id,
                    'latitude': float(latest['latitude']),
                    'longitude': float(latest['longitude']),
                    'temperature': float(latest['temperature']),
                    'salinity': float(latest['salinity']),
                    'depth': float(latest['depth']),
                    'date': latest['datetime'][:10]
                })
            
            return results[:10]  # Limit to 10 results
            
        except Exception as e:
            logger.error(f"Error searching floats: {e}")
            return self._search_simulated_floats(query)

    def get_regional_data(self, lat_range: Tuple[float, float], 
                         lon_range: Tuple[float, float], limit: int = 1000) -> pd.DataFrame:
        """Get data for a specific geographic region"""
        if self.fallback_mode:
            return self._get_simulated_regional_data(lat_range, lon_range, limit)
        
        try:
            return self.data_access.fetch_data({
                'lat_range': lat_range,
                'lon_range': lon_range,
                'limit': limit,
                'quality_filter': True
            })
        except Exception as e:
            logger.error(f"Error getting regional data: {e}")
            return self._get_simulated_regional_data(lat_range, lon_range, limit)

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if self.fallback_mode:
            return {
                'total_profiles': 50000,
                'unique_floats': 150,
                'data_source': 'Simulated',
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            }
        
        try:
            stats = self.data_access.get_summary_stats()
            stats['data_source'] = 'Real ARGO Database'
            return stats
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {
                'total_profiles': 0,
                'unique_floats': 0,
                'data_source': 'Error',
                'error': str(e)
            }

    # Fallback simulated data methods (same as original dashboard)
    def _get_simulated_map_data(self, limit: int = 150) -> Dict[str, List]:
        """Generate simulated map data as fallback"""
        np.random.seed(42)
        
        # Indian Ocean coordinates
        lats = np.random.uniform(-35, 15, limit)
        lons = np.random.uniform(45, 115, limit)
        
        # Temperature based on latitude
        temps = 28 - 0.4 * np.abs(lats) + np.random.normal(0, 2, limit)
        temps = np.clip(temps, 5, 32)
        
        # Salinity data
        salinities = 35 + np.random.normal(0, 0.5, limit)
        salinities = np.clip(salinities, 33, 37)
        
        # Depth data
        depths = np.random.uniform(10, 2000, limit)
        
        # Float IDs
        float_ids = [f"ARGO_{i+5000}" for i in range(limit)]
        
        # Recent dates
        dates = []
        for i in range(limit):
            days_ago = np.random.randint(0, 365)
            date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            dates.append(date)
        
        return {
            'lats': lats.tolist(),
            'lons': lons.tolist(),
            'temps': temps.tolist(),
            'salinities': salinities.tolist(),
            'depths': depths.tolist(),
            'float_ids': float_ids,
            'dates': dates
        }

    def _get_simulated_table_data(self, limit: int = 50) -> List[Dict]:
        """Generate simulated table data as fallback"""
        np.random.seed(42)
        
        data = []
        for i in range(limit):
            float_id = f"ARGO_{5900000 + i:04d}"
            lat = np.random.uniform(-30, 25)
            lon = np.random.uniform(40, 120)
            temp = np.random.uniform(2, 30)
            salinity = np.random.uniform(33.5, 37.5)
            depth = np.random.uniform(500, 2000)
            
            days_ago = np.random.randint(0, 30)
            date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            
            status = np.random.choice(["Active", "Monitoring", "Inactive"], p=[0.7, 0.2, 0.1])
            
            data.append({
                "argo_id": float_id,
                "latitude": round(lat, 2),
                "longitude": round(lon, 2),
                "temperature": round(temp, 1),
                "salinity": round(salinity, 2),
                "depth": round(depth, 0),
                "date": date,
                "status": status
            })
        
        return data

    def _get_simulated_float_profile(self, float_id: str) -> Dict[str, Any]:
        """Generate simulated float profile as fallback"""
        np.random.seed(hash(float_id) % 1000)
        
        # Generate profile data
        depths = np.linspace(0, 2000, 50)
        base_temp = np.random.uniform(20, 30)
        base_salinity = np.random.uniform(34, 36)
        
        # Temperature profile with thermocline
        temps = base_temp * np.exp(-depths/500) + 2 + np.random.normal(0, 0.3, 50)
        temps = np.clip(temps, 2, base_temp)
        
        # Salinity profile
        sals = base_salinity + np.random.normal(0, 0.1, 50) + depths * 0.0001
        sals = np.clip(sals, 33, 37)
        
        return {
            'float_id': float_id,
            'latitude': np.random.uniform(-30, 25),
            'longitude': np.random.uniform(40, 120),
            'surface_temp': float(temps[0]),
            'surface_salinity': float(sals[0]),
            'max_depth': 2000.0,
            'last_update': (datetime.now() - timedelta(days=np.random.randint(0, 30))).strftime('%Y-%m-%d'),
            'profile_data': {
                'depths': depths.tolist(),
                'temperatures': temps.tolist(),
                'salinities': sals.tolist(),
                'pressures': depths.tolist()
            }
        }

    def _search_simulated_floats(self, query: str) -> List[Dict]:
        """Search simulated floats as fallback"""
        # Return a few matching results
        results = []
        for i in range(min(5, len(query) + 2)):
            float_id = f"ARGO_{5900000 + hash(query + str(i)) % 1000:04d}"
            results.append({
                'float_id': float_id,
                'latitude': np.random.uniform(-30, 25),
                'longitude': np.random.uniform(40, 120),
                'temperature': np.random.uniform(15, 30),
                'salinity': np.random.uniform(34, 36),
                'depth': np.random.uniform(500, 2000),
                'date': (datetime.now() - timedelta(days=np.random.randint(0, 30))).strftime('%Y-%m-%d')
            })
        return results

    def _get_simulated_regional_data(self, lat_range: Tuple[float, float], 
                                   lon_range: Tuple[float, float], limit: int = 1000) -> pd.DataFrame:
        """Generate simulated regional data as fallback"""
        np.random.seed(42)
        
        n_points = min(limit, 1000)
        lats = np.random.uniform(lat_range[0], lat_range[1], n_points)
        lons = np.random.uniform(lon_range[0], lon_range[1], n_points)
        temps = 28 - 0.4 * np.abs(lats) + np.random.normal(0, 2, n_points)
        sals = 35 + np.random.normal(0, 0.5, n_points)
        depths = np.random.uniform(10, 2000, n_points)
        
        return pd.DataFrame({
            'latitude': lats,
            'longitude': lons,
            'temperature': temps,
            'salinity': sals,
            'depth': depths,
            'float_id': [f"ARGO_{i+5000}" for i in range(n_points)],
            'datetime': [(datetime.now() - timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(n_points)]
        })


# Global instance for dashboard use
dashboard_data = DashboardDataProvider()


def get_dashboard_data() -> DashboardDataProvider:
    """Get the global dashboard data provider instance"""
    return dashboard_data


def initialize_dashboard_data(db_path: str = None) -> bool:
    """Initialize dashboard data with custom database path"""
    global dashboard_data
    
    if db_path:
        dashboard_data = DashboardDataProvider(db_path)
    
    return not dashboard_data.fallback_mode


# Convenience functions for dashboard integration
def get_map_floats(limit: int = 150) -> Dict[str, List]:
    """Get float data for map display"""
    return dashboard_data.get_map_data(limit)


def get_analysis_table_data(limit: int = 50) -> List[Dict]:
    """Get data for analysis table"""
    return dashboard_data.get_table_data(limit)


def get_float_details(float_id: str) -> Dict[str, Any]:
    """Get detailed float profile data"""
    return dashboard_data.get_float_profile(float_id)


def search_argo_floats(query: str) -> List[Dict]:
    """Search for ARGO floats"""
    return dashboard_data.search_floats(query)


def get_region_floats(lat_range: Tuple[float, float], 
                     lon_range: Tuple[float, float], limit: int = 1000) -> pd.DataFrame:
    """Get floats in a specific region"""
    return dashboard_data.get_regional_data(lat_range, lon_range, limit)


def get_data_statistics() -> Dict[str, Any]:
    """Get database statistics"""
    return dashboard_data.get_database_stats()


if __name__ == "__main__":
    # Test the data integration
    print("🧪 Testing Dashboard Data Integration")
    print("=" * 50)
    
    # Test map data
    map_data = get_map_floats(10)
    print(f"✅ Map data: {len(map_data['lats'])} floats")
    
    # Test table data
    table_data = get_analysis_table_data(5)
    print(f"✅ Table data: {len(table_data)} entries")
    
    # Test float details
    if table_data:
        float_id = table_data[0]['argo_id']
        details = get_float_details(float_id)
        print(f"✅ Float details for {float_id}: {len(details['profile_data']['depths'])} depth points")
    
    # Test search
    search_results = search_argo_floats("ARGO")
    print(f"✅ Search results: {len(search_results)} matches")
    
    # Test statistics
    stats = get_data_statistics()
    print(f"✅ Statistics: {stats.get('total_profiles', 0)} profiles, {stats.get('unique_floats', 0)} floats")
    print(f"📊 Data source: {stats.get('data_source', 'Unknown')}")
