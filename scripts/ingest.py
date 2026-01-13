import argparse
import os
import glob
from datetime import datetime
import pandas as pd
import numpy as np

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.db import engine, SessionLocal
from backend.models import Base, Float, Profile, ProfileSummary

# Optional: embeddings
try:
    from sentence_transformers import SentenceTransformer
    _embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
except Exception:
    _embedder = None

from backend.vectorstore import VectorStore

Base.metadata.create_all(bind=engine)


def parse_args():
    p = argparse.ArgumentParser(description="Ingest ARGO CSV to Parquet/SQL and Vector DB")
    p.add_argument("--input", required=False, default="/Users/cybertron/Desktop/Projects/FloatBot/Data/Latest_Data/cleaned_argo_data.csv", help="Path to CSV file")
    p.add_argument("--parquet_out", default="data/processed/profiles.parquet")
    p.add_argument("--sample_size", type=int, default=10000, help="Number of rows to sample for PoC")
    return p.parse_args()


def ingest():
    args = parse_args()
    os.makedirs(os.path.dirname(args.parquet_out), exist_ok=True)
    db = SessionLocal()

    print(f"Loading CSV from: {args.input}")
    
    if not os.path.exists(args.input):
        print(f"CSV file not found: {args.input}")
        return
    
    # Load CSV data
    print("Reading CSV file...")
    df = pd.read_csv(args.input)
    
    # Sample data for PoC performance
    if len(df) > args.sample_size:
        print(f"Sampling {args.sample_size} rows from {len(df)} total rows")
        df = df.sample(n=args.sample_size, random_state=42)
    
    print(f"Processing {len(df)} rows...")
    
    # Get unique platforms and create Float records
    unique_platforms = df['platform_number'].unique()
    float_id_map = {}
    
    for i, platform_num in enumerate(unique_platforms):
        float_id = i + 1
        float_record = Float(
            float_id=float_id,
            platform_number=int(platform_num),
            region="Indian Ocean"  # Default region
        )
        db.merge(float_record)
        float_id_map[platform_num] = float_id
    
    db.commit()
    print(f"Created {len(unique_platforms)} float records")
    
    # Process profiles in batches
    batch_size = 1000
    records = []
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(df)-1)//batch_size + 1}")
        
        for _, row in batch.iterrows():
            try:
                # Parse datetime
                dt = pd.to_datetime(row['datetime'], errors='coerce')
                
                profile = Profile(
                    float_id=float_id_map[row['platform_number']],
                    platform_number=int(row['platform_number']),
                    cycle_number=int(row['cycle_number']) if pd.notna(row['cycle_number']) else 0,
                    profile_index=int(row['profile_index']) if pd.notna(row['profile_index']) else 0,
                    datetime=dt.to_pydatetime() if pd.notna(dt) else None,
                    julian_day=float(row['julian_day']) if pd.notna(row['julian_day']) else None,
                    latitude=float(row['latitude']) if pd.notna(row['latitude']) else None,
                    longitude=float(row['longitude']) if pd.notna(row['longitude']) else None,
                    pressure=float(row['pressure']) if pd.notna(row['pressure']) else None,
                    temperature=float(row['temperature']) if pd.notna(row['temperature']) else None,
                    salinity=float(row['salinity']) if pd.notna(row['salinity']) else None,
                    depth=float(row['depth']) if pd.notna(row['depth']) else None,
                    pres_error=float(row['pres_error']) if pd.notna(row['pres_error']) else None,
                    temp_error=float(row['temp_error']) if pd.notna(row['temp_error']) else None,
                    sal_error=float(row['sal_error']) if pd.notna(row['sal_error']) else None,
                    year=int(row['year']) if pd.notna(row['year']) else None,
                    month=int(row['month']) if pd.notna(row['month']) else None,
                    day=int(row['day']) if pd.notna(row['day']) else None,
                    salinity_bin=str(row['salinity_bin']) if pd.notna(row['salinity_bin']) else None,
                    source_file=str(row['source_file']) if pd.notna(row['source_file']) else None,
                )
                db.add(profile)
                
                records.append({
                    "profile_id": None,  # Will be set after flush
                    "float_id": float_id_map[row['platform_number']],
                    "platform_number": int(row['platform_number']),
                    "datetime": dt.to_pydatetime() if pd.notna(dt) else None,
                    "latitude": float(row['latitude']) if pd.notna(row['latitude']) else None,
                    "longitude": float(row['longitude']) if pd.notna(row['longitude']) else None,
                    "pressure": float(row['pressure']) if pd.notna(row['pressure']) else None,
                    "temperature": float(row['temperature']) if pd.notna(row['temperature']) else None,
                    "salinity": float(row['salinity']) if pd.notna(row['salinity']) else None,
                    "depth": float(row['depth']) if pd.notna(row['depth']) else None,
                })
            except Exception as e:
                print(f"Error processing row: {e}")
                continue
        
        # Commit batch
        db.commit()
    
    print(f"Inserted {len(records)} profile records")
    
    # Write Parquet
    df_out = pd.DataFrame(records)
    if len(df_out) > 0:
        df_out.to_parquet(args.parquet_out, index=False)
        print(f"Saved Parquet to: {args.parquet_out}")

    # Create embeddings from summaries (sample subset for performance)
    print("Creating embeddings...")
    vstore = VectorStore()
    
    # Get recent profiles for embedding
    recent_profiles = db.query(Profile).order_by(Profile.profile_id.desc()).limit(1000).all()
    
    ids, embeds, metas = [], [], []
    for p in recent_profiles:
        if p.latitude and p.longitude and p.temperature and p.salinity:
            text = f"Platform {p.platform_number} at {p.datetime} lat={p.latitude:.3f} lon={p.longitude:.3f} T={p.temperature:.2f}°C S={p.salinity:.2f} depth={p.depth}m"
            emb = (_embedder.encode([text])[0].tolist() if _embedder else [0.0]*384)
            
            ps = ProfileSummary(profile_id=p.profile_id, summary_text=text, embedding=emb)
            db.merge(ps)
            
            ids.append(str(p.profile_id))
            embeds.append(emb)
            metas.append({
                "profile_id": p.profile_id, 
                "float_id": p.float_id, 
                "platform_number": p.platform_number,
                "text": text
            })
    
    if ids:
        vstore.upsert_embeddings(ids, embeds, metas)
        print(f"Created {len(ids)} embeddings")

    db.commit()
    db.close()
    print(f"Ingestion complete! Processed {len(records)} profiles.")

if __name__ == "__main__":
    ingest()
