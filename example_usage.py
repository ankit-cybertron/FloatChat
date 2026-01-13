#!/usr/bin/env python3
"""
Example Usage of Indian Ocean ARGO Data System
==============================================

This script demonstrates how to use the Indian Ocean ARGO data processing
and dashboard integration system.

Author: ARGO Research Dashboard Team
Date: September 2025
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def example_data_processing():
    """Example: Process ARGO data and create database"""
    print("📊 Example 1: Data Processing")
    print("-" * 40)
    
    from data_processor import IndianOceanArgoProcessor
    
    # Configuration
    csv_path = "/Users/cybertron/Desktop/Projects/FloatBot/Data/Latest_Data/cleaned_argo_data.csv"
    db_path = "/Users/cybertron/Desktop/SIH/data/example_indian_ocean.db"
    
    print(f"Input CSV: {csv_path}")
    print(f"Output DB: {db_path}")
    
    if os.path.exists(csv_path):
        # Create processor
        processor = IndianOceanArgoProcessor(csv_path, db_path)
        
        # Process data (this filters Indian Ocean region and creates SQLite DB)
        success = processor.process_data()
        
        if success:
            print("✅ Data processing completed successfully!")
        else:
            print("❌ Data processing failed!")
    else:
        print(f"⚠️  CSV file not found: {csv_path}")
        print("Using simulated data for demonstration...")
    
    print()


def example_data_access():
    """Example: Access data from the database"""
    print("🔍 Example 2: Data Access")
    print("-" * 40)
    
    from data_processor import IndianOceanDataAccess
    
    db_path = "/Users/cybertron/Desktop/SIH/data/indian_ocean_floats.db"
    
    try:
        # Create data access object
        data_access = IndianOceanDataAccess(db_path)
        
        # Get summary statistics
        stats = data_access.get_summary_stats()
        print("Database Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print()
        
        # Example queries
        print("Example Queries:")
        
        # 1. Get recent floats
        recent = data_access.get_recent_floats(days=30, limit=5)
        print(f"Recent floats (last 30 days): {len(recent)} records")
        
        # 2. Search by region
        regional = data_access.search_by_region(lat_center=0, lon_center=80, radius_deg=10, limit=10)
        print(f"Floats near equator (0°N, 80°E): {len(regional)} records")
        
        # 3. Custom filter query
        filtered = data_access.fetch_data({
            'temp_range': (20, 30),
            'depth_range': (0, 100),
            'limit': 10
        })
        print(f"Surface warm water (20-30°C, 0-100m): {len(filtered)} records")
        
        # 4. Get specific float profile
        float_list = data_access.get_float_list()
        if float_list:
            sample_float = float_list[0]
            profile = data_access.get_float_profile(sample_float)
            print(f"Profile for {sample_float}: {len(profile)} measurements")
        
    except FileNotFoundError:
        print(f"⚠️  Database not found: {db_path}")
        print("Run setup_indian_ocean_data.py first to create the database.")
    except Exception as e:
        print(f"❌ Error accessing data: {e}")
    
    print()


def example_dashboard_integration():
    """Example: Dashboard integration"""
    print("🎛️  Example 3: Dashboard Integration")
    print("-" * 40)
    
    from dashboard_data_integration import (
        get_map_floats, get_analysis_table_data, get_float_details,
        search_argo_floats, get_data_statistics
    )
    
    # Get data for map display
    map_data = get_map_floats(limit=10)
    print(f"Map data: {len(map_data['lats'])} floats")
    print(f"  Lat range: {min(map_data['lats']):.1f}° to {max(map_data['lats']):.1f}°")
    print(f"  Lon range: {min(map_data['lons']):.1f}° to {max(map_data['lons']):.1f}°")
    
    # Get data for analysis table
    table_data = get_analysis_table_data(limit=5)
    print(f"\nTable data: {len(table_data)} entries")
    if table_data:
        print("Sample entries:")
        for i, entry in enumerate(table_data[:3]):
            print(f"  {i+1}. {entry['argo_id']}: {entry['latitude']:.1f}°N, {entry['longitude']:.1f}°E")
    
    # Get detailed float profile
    if table_data:
        sample_float = table_data[0]['argo_id']
        details = get_float_details(sample_float)
        print(f"\nFloat details for {sample_float}:")
        print(f"  Location: {details['latitude']:.2f}°N, {details['longitude']:.2f}°E")
        print(f"  Surface temp: {details['surface_temp']:.1f}°C")
        print(f"  Max depth: {details['max_depth']:.0f}m")
        print(f"  Profile points: {len(details['profile_data']['depths'])}")
    
    # Search floats
    search_results = search_argo_floats("ARGO_59")
    print(f"\nSearch results for 'ARGO_59': {len(search_results)} matches")
    
    # Get statistics
    stats = get_data_statistics()
    print(f"\nData statistics:")
    print(f"  Source: {stats.get('data_source', 'Unknown')}")
    print(f"  Total profiles: {stats.get('total_profiles', 0):,}")
    print(f"  Unique floats: {stats.get('unique_floats', 0):,}")
    
    print()


def example_custom_analysis():
    """Example: Custom data analysis"""
    print("📈 Example 4: Custom Analysis")
    print("-" * 40)
    
    from dashboard_data_integration import get_region_floats
    
    # Define Indian Ocean sub-regions
    regions = {
        'Arabian Sea': ((10, 25), (50, 75)),
        'Bay of Bengal': ((5, 25), (80, 100)),
        'Southern Indian Ocean': ((-40, -10), (60, 120))
    }
    
    print("Regional analysis:")
    for region_name, (lat_range, lon_range) in regions.items():
        try:
            data = get_region_floats(lat_range, lon_range, limit=100)
            
            if not data.empty:
                avg_temp = data['temperature'].mean()
                avg_sal = data['salinity'].mean()
                print(f"  {region_name}:")
                print(f"    Floats: {len(data)}")
                print(f"    Avg temp: {avg_temp:.1f}°C")
                print(f"    Avg salinity: {avg_sal:.1f} PSU")
            else:
                print(f"  {region_name}: No data available")
        
        except Exception as e:
            print(f"  {region_name}: Error - {e}")
    
    print()


def main():
    """Run all examples"""
    print("🌊 Indian Ocean ARGO Data System Examples")
    print("=" * 60)
    print()
    
    # Run examples
    example_data_processing()
    example_data_access()
    example_dashboard_integration()
    example_custom_analysis()
    
    print("🎉 Examples completed!")
    print()
    print("Next steps:")
    print("1. Run 'python setup_indian_ocean_data.py' to process your ARGO data")
    print("2. Run 'python dash_frontend/research_dashboard.py' to start the dashboard")
    print("3. Use the dashboard_data_integration module in your own code")


if __name__ == "__main__":
    main()
