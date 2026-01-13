#!/usr/bin/env python3
"""
Setup Indian Ocean ARGO Data
============================

This script processes the global ARGO CSV data, filters for Indian Ocean region,
and sets up the SQLite database for the research dashboard.

Usage:
    python setup_indian_ocean_data.py

Author: ARGO Research Dashboard Team
Date: September 2025
"""

import os
import sys
import time
from pathlib import Path

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_processor import IndianOceanArgoProcessor, IndianOceanDataAccess
from dashboard_data_integration import initialize_dashboard_data, get_data_statistics

def main():
    """Main setup function"""
    print("🌊 Indian Ocean ARGO Data Setup")
    print("=" * 60)
    print()
    
    # Configuration
    csv_path = "/Users/cybertron/Desktop/Projects/FloatBot/Data/Latest_Data/cleaned_argo_data.csv"
    db_path = "/Users/cybertron/Desktop/SIH/data/indian_ocean_floats.db"
    
    print(f"📁 Input CSV: {csv_path}")
    print(f"📁 Output DB: {db_path}")
    print()
    
    # Step 1: Check if CSV exists
    print("Step 1: Checking input data...")
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        print()
        print("Please ensure the ARGO data CSV is available at:")
        print(f"  {csv_path}")
        print()
        print("Alternative: You can modify the csv_path variable in this script")
        print("to point to your ARGO data file location.")
        return False
    
    file_size = os.path.getsize(csv_path) / (1024 * 1024)  # MB
    print(f"✅ Found CSV file ({file_size:.1f} MB)")
    print()
    
    # Step 2: Process data
    print("Step 2: Processing ARGO data...")
    print("This may take a few minutes depending on file size...")
    print()
    
    start_time = time.time()
    
    try:
        processor = IndianOceanArgoProcessor(csv_path, db_path)
        success = processor.process_data()
        
        if not success:
            print("❌ Data processing failed!")
            return False
        
        processing_time = time.time() - start_time
        print(f"✅ Processing completed in {processing_time:.1f} seconds")
        print()
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return False
    
    # Step 3: Verify database
    print("Step 3: Verifying database...")
    
    try:
        data_access = IndianOceanDataAccess(db_path)
        stats = data_access.get_summary_stats()
        
        print("📊 Database Statistics:")
        print(f"  • Total profiles: {stats.get('total_profiles', 0):,}")
        print(f"  • Unique floats: {stats.get('unique_floats', 0):,}")
        print(f"  • Date range: {stats.get('earliest_date', 'N/A')} to {stats.get('latest_date', 'N/A')}")
        print(f"  • Latitude range: {stats.get('lat_range', (0, 0))[0]:.1f}° to {stats.get('lat_range', (0, 0))[1]:.1f}°")
        print(f"  • Longitude range: {stats.get('lon_range', (0, 0))[0]:.1f}° to {stats.get('lon_range', (0, 0))[1]:.1f}°")
        print(f"  • Avg temperature: {stats.get('avg_temperature', 0):.1f}°C")
        print(f"  • Avg salinity: {stats.get('avg_salinity', 0):.1f} PSU")
        print()
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False
    
    # Step 4: Test dashboard integration
    print("Step 4: Testing dashboard integration...")
    
    try:
        # Initialize dashboard data
        success = initialize_dashboard_data(db_path)
        
        if success:
            print("✅ Dashboard integration successful (using real data)")
            
            # Test some queries
            from dashboard_data_integration import get_map_floats, get_analysis_table_data, get_float_details
            
            # Test map data
            map_data = get_map_floats(10)
            print(f"  • Map data test: {len(map_data['lats'])} floats loaded")
            
            # Test table data
            table_data = get_analysis_table_data(5)
            print(f"  • Table data test: {len(table_data)} entries loaded")
            
            # Test float details
            if table_data:
                float_id = table_data[0]['argo_id']
                details = get_float_details(float_id)
                print(f"  • Float profile test: {len(details['profile_data']['depths'])} depth points for {float_id}")
            
        else:
            print("⚠️  Dashboard integration using fallback mode (simulated data)")
        
        print()
        
    except Exception as e:
        print(f"❌ Error testing dashboard integration: {e}")
        return False
    
    # Step 5: Success summary
    print("🎉 Setup Complete!")
    print("=" * 60)
    print()
    print("Your Indian Ocean ARGO database is ready!")
    print()
    print("Next steps:")
    print("1. Run the research dashboard:")
    print("   python dash_frontend/research_dashboard.py")
    print()
    print("2. The dashboard will now use real ARGO data instead of simulated data")
    print()
    print("3. Database location:")
    print(f"   {db_path}")
    print()
    print("4. You can also use the data programmatically:")
    print("   from dashboard_data_integration import get_map_floats, get_analysis_table_data")
    print()
    
    return True


def quick_test():
    """Quick test of existing database"""
    db_path = "/Users/cybertron/Desktop/SIH/data/indian_ocean_floats.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("Run the full setup first.")
        return
    
    print("🧪 Quick Database Test")
    print("=" * 30)
    
    try:
        from dashboard_data_integration import get_data_statistics, get_map_floats
        
        # Get statistics
        stats = get_data_statistics()
        print(f"📊 Total profiles: {stats.get('total_profiles', 0):,}")
        print(f"📊 Unique floats: {stats.get('unique_floats', 0):,}")
        print(f"📊 Data source: {stats.get('data_source', 'Unknown')}")
        
        # Test data retrieval
        map_data = get_map_floats(5)
        print(f"✅ Successfully loaded {len(map_data['lats'])} floats for testing")
        
        print("\n🎉 Database is working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing database: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Indian Ocean ARGO data")
    parser.add_argument("--test", action="store_true", help="Quick test of existing database")
    parser.add_argument("--csv-path", help="Path to ARGO CSV file")
    
    args = parser.parse_args()
    
    if args.test:
        quick_test()
    else:
        if args.csv_path:
            # Update the CSV path if provided
            csv_path = args.csv_path
            print(f"Using custom CSV path: {csv_path}")
        
        success = main()
        
        if success:
            print("✅ Setup completed successfully!")
            sys.exit(0)
        else:
            print("❌ Setup failed!")
            sys.exit(1)
