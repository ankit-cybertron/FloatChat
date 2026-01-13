import os
import json
import requests
import pandas as pd
from datetime import datetime
import numpy as np
import sys
import re
import logging
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import dash
from dash import dcc, html, Input, Output, State, callback, ctx, dash_table
import plotly.graph_objs as go
import plotly.express as px

# Add parent directory to path for RAG system import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from argo_float_rag import process_chat_message, get_float_for_plotting, argo_rag
    RAG_AVAILABLE = True
    print("✅ ARGO Float RAG system loaded successfully")
except ImportError as e:
    print(f"⚠️  RAG system not available: {e}")
    RAG_AVAILABLE = False

# Modern CSS with comprehensive dark mode system
app_css = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            /* CSS Variables for Theme System */
            :root {
                /* Light Theme Colors */
                --bg-primary: #ffffff;
                --bg-secondary: #f8fafc;
                --bg-tertiary: #f1f5f9;
                --bg-card: rgba(255, 255, 255, 0.95);
                --bg-glass: rgba(255, 255, 255, 0.1);
                --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                
                --text-primary: #0f172a;
                --text-secondary: #475569;
                --text-muted: #64748b;
                --text-inverse: #ffffff;
                
                --border-primary: #e2e8f0;
                --border-secondary: #cbd5e1;
                --border-glass: rgba(255, 255, 255, 0.2);
                
                --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
                --shadow-md: 0 4px 15px rgba(0, 0, 0, 0.08);
                --shadow-lg: 0 8px 25px rgba(0, 0, 0, 0.12);
                --shadow-xl: 0 12px 35px rgba(0, 0, 0, 0.15);
                
                --accent-primary: #3b82f6;
                --accent-secondary: #667eea;
                --accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            
            /* Dark Theme Colors */
            [data-theme="dark"] {
                --bg-primary: #0f172a;
                --bg-secondary: #1e293b;
                --bg-tertiary: #334155;
                --bg-card: rgba(30, 41, 59, 0.95);
                --bg-glass: rgba(0, 0, 0, 0.2);
                --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                
                --text-primary: #f8fafc;
                --text-secondary: #cbd5e1;
                --text-muted: #94a3b8;
                --text-inverse: #0f172a;
                
                --border-primary: #475569;
                --border-secondary: #64748b;
                --border-glass: rgba(255, 255, 255, 0.1);
                
                --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.2);
                --shadow-md: 0 4px 15px rgba(0, 0, 0, 0.3);
                --shadow-lg: 0 8px 25px rgba(0, 0, 0, 0.4);
                --shadow-xl: 0 12px 35px rgba(0, 0, 0, 0.5);
                
                --accent-primary: #60a5fa;
                --accent-secondary: #818cf8;
                --accent-gradient: linear-gradient(135deg, #818cf8 0%, #a855f7 100%);
            }
            
            /* Base Styles */
            body {
                background: var(--bg-primary);
                color: var(--text-primary);
                font-family: 'Inter', sans-serif;
                transition: background-color 0.3s ease, color 0.3s ease;
            
            /* Smooth animations */
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
                0%, 100% { box-shadow: 0 0 5px var(--accent-primary); }
                50% { box-shadow: 0 0 20px var(--accent-primary); }
            }
            
            @keyframes slideInFromLeft {
                from { transform: translateX(-100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes slideOutToLeft {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(-100%); opacity: 0; }
            }
            
            @keyframes bounceIn {
                0% { transform: scale(0) rotate(0deg); opacity: 0; }
                50% { transform: scale(1.2) rotate(180deg); opacity: 0.8; }
                100% { transform: scale(1) rotate(360deg); opacity: 1; }
            }
            
            @keyframes floatingPulse {
                0%, 100% { transform: scale(1); box-shadow: var(--shadow-lg); }
                50% { transform: scale(1.05); box-shadow: var(--shadow-xl); }
            }
            
            /* Component Classes */
            .glass {
                background: var(--bg-glass);
                backdrop-filter: blur(10px);
                border: 1px solid var(--border-glass);
            }
            
            .modern-card {
                background: var(--bg-card);
                border-radius: 16px;
                box-shadow: var(--shadow-md);
                border: 1px solid var(--border-primary);
                transition: all 0.3s ease;
            }
            
            .modern-card:hover {
                box-shadow: var(--shadow-lg);
                transform: translateY(-1px);
            }
            
            .hover-lift {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .hover-lift:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-lg);
            }
            
            .fade-in { animation: fadeInUp 0.6s ease-out; }
            .slide-in-left { animation: slideInLeft 0.8s ease-out; }
            .slide-in-right { animation: slideInRight 0.8s ease-out; }
            .sidebar-slide-in { animation: slideInFromLeft 0.4s ease-out; }
            .sidebar-slide-out { animation: slideOutToLeft 0.4s ease-out; }
            .bounce-in { animation: bounceIn 0.6s ease-out; }
            .floating-pulse { animation: floatingPulse 2s infinite; }
            
            /* Typing indicator */
            .typing-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--accent-primary);
                display: inline-block;
                margin: 0 2px;
                animation: typing 1.4s infinite;
            }
            
            .typing-dot:nth-child(2) { animation-delay: 0.2s; }
            .typing-dot:nth-child(3) { animation-delay: 0.4s; }
            
            /* Button styles */
            .pill-button {
                border-radius: 25px;
                padding: 8px 16px;
                border: none;
                background: var(--accent-gradient);
                color: var(--text-inverse);
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: var(--shadow-sm);
            }
            
            .pill-button:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-md);
            }
            
            /* Toggle switch */
            .toggle-switch {
                position: relative;
                width: 60px;
                height: 30px;
                background: var(--bg-tertiary);
                border-radius: 15px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .toggle-switch.active {
                background: var(--accent-gradient);
            }
            
            .toggle-knob {
                position: absolute;
                top: 3px;
                left: 3px;
                width: 24px;
                height: 24px;
                background: var(--bg-primary);
                border-radius: 50%;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: var(--shadow-sm);
            }
            
            .toggle-switch.active .toggle-knob {
                transform: translateX(30px);
            }
            
            /* Theme-aware input styles */
            input, textarea {
                background: var(--bg-secondary);
                color: var(--text-primary);
                border: 1px solid var(--border-primary);
                border-radius: 8px;
                padding: 8px 12px;
                transition: all 0.3s ease;
            }
            
            input:focus, textarea:focus {
                outline: none;
                border-color: var(--accent-primary);
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            
            input::placeholder, textarea::placeholder {
                color: var(--text-muted);
            }
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {
                width: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: var(--bg-secondary);
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--border-secondary);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: var(--text-muted);
            }
            
            .sidebar-slide-out {
                animation: slideOutToLeft 0.4s ease-in;
            }
            
            .floating-btn-show {
                animation: bounceIn 0.6s ease-out;
                display: flex !important;
            }
            
            .floating-btn-pulse {
                animation: floatingPulse 2s ease-in-out infinite;
            }
            
            /* Dark mode theme variables */
            .dark-theme {
                --bg-primary: #0f172a;
                --bg-secondary: #1e293b;
                --bg-tertiary: #334155;
                --text-primary: #f8fafc;
                --text-secondary: #e2e8f0;
                --text-muted: #94a3b8;
                --border-color: #475569;
                --accent-color: #667eea;
                --shadow-color: rgba(0, 0, 0, 0.3);
            }
            
            /* Light mode theme variables */
            .light-theme {
                --bg-primary: #ffffff;
                --bg-secondary: #f8fafc;
                --bg-tertiary: #f1f5f9;
                --text-primary: #0f172a;
                --text-secondary: #374151;
                --text-muted: #6b7280;
                --border-color: #e2e8f0;
                --accent-color: #667eea;
                --shadow-color: rgba(0, 0, 0, 0.1);
            }
            
            /* Theme-aware components */
            .theme-header {
                background: var(--bg-secondary);
                color: var(--text-primary);
                border-bottom: 1px solid var(--border-color);
            }
            
            .theme-card {
                background: var(--bg-primary);
                color: var(--text-primary);
                border: 1px solid var(--border-color);
                box-shadow: 0 4px 15px var(--shadow-color);
            }
            
            .theme-input {
                background: var(--bg-tertiary);
                color: var(--text-primary);
                border: 1px solid var(--border-color);
            }
            
            .theme-button {
                background: var(--accent-color);
                color: white;
                border: none;
            }
            
            /* Resizable chat sidebar styles */
            .resizable-sidebar {
                position: relative;
                min-width: 280px;
                max-width: 600px;
                transition: width 0.3s ease;
            }
            
            .resize-handle {
                position: absolute;
                top: 0;
                right: 0;
                width: 4px;
                height: 100%;
                background: transparent;
                cursor: col-resize;
                z-index: 1000;
                transition: all 0.2s ease;
            }
            
            .resize-handle:hover {
                background: var(--accent-primary);
                width: 6px;
                opacity: 0.8;
            }
            
           .resize-handle::after {
                content: '⋮⋮';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: var(--text-muted);
                font-size: 12px;
                opacity: 0.4;
                transition: opacity 0.2s ease;
                pointer-events: none;
            }
            
            .resize-handle:hover::after {
                opacity: 1;
            }
            
            /* Width indicator */
            .width-indicator {
                position: absolute;
                top: 10px;
                right: 15px;
                background: var(--bg-card);
                color: var(--text-muted);
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.7rem;
                opacity: 0;
                transition: opacity 0.2s ease;
                z-index: 1001;
                pointer-events: none;
                border: 1px solid var(--border-primary);
            }
            
            .resizable-sidebar:hover .width-indicator {
                opacity: 1;
            }
            
            /* Smooth resize transition */
            .resizable-sidebar.resizing {
                transition: none;
            }
            /* Glassmorphism Enhancements */
            .glass-card {
                background: var(--bg-glass);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border: 1px solid var(--border-glass);
                border-radius: 20px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
            }
            .glass-card:hover {
                box-shadow: 0 15px 50px rgba(0, 0, 0, 0.15);
                transform: translateY(-3px);
            }
            [data-theme="dark"] .glass-card {
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            }
            [data-theme="dark"] .glass-card:hover {
                box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
            }
            /* Enhanced top navigation */
            .glass-nav {
                background: var(--bg-glass);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                border-bottom: 1px solid var(--border-glass);
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 1000;
                padding: 10px 20px;
            }
            /* Pill buttons */
            .pill-btn {
                border-radius: 25px;
                padding: 8px 16px;
                border: none;
                background: var(--accent-gradient);
                color: white;
                font-weight: 500;
                transition: all 0.3s ease;
                cursor: pointer;
                position: relative;
                overflow: hidden;
            }
            .pill-btn:hover {
                box-shadow: 0 0 20px rgba(0, 123, 255, 0.5);
                transform: translateY(-1px);
            }
            .pill-btn.active {
                box-shadow: 0 0 25px rgba(0, 123, 255, 0.6);
            }
            /* Map controls */
            .map-btn {
                background: var(--bg-glass);
                backdrop-filter: blur(15px);
                border: 1px solid var(--border-glass);
                border-radius: 50%;
                width: 40px;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            }
            .map-btn:hover {
                background: rgba(255, 255, 255, 0.2);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
                transform: scale(1.1);
            }
            [data-theme="dark"] .map-btn {
                background: rgba(0, 0, 0, 0.2);
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            }
            [data-theme="dark"] .map-btn:hover {
                background: rgba(0, 0, 0, 0.3);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
            }
            /* Chart containers */
            .chart-glass {
                background: var(--bg-glass);
                backdrop-filter: blur(10px);
                border: 1px solid var(--border-glass);
                border-radius: 15px;
                padding: 15px;
                margin: 10px 0;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
            }
            [data-theme="dark"] .chart-glass {
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
            }
            /* Theme toggle */
            .theme-toggle-btn {
                background: var(--bg-glass);
                backdrop-filter: blur(10px);
                border: 1px solid var(--border-glass);
                border-radius: 20px;
                padding: 5px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .theme-toggle-btn:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            [data-theme="dark"] .theme-toggle-btn {
                background: rgba(0, 0, 0, 0.2);
            }
            [data-theme="dark"] .theme-toggle-btn:hover {
                background: rgba(0, 0, 0, 0.3);
            }
            /* Tab highlight animation */
            .tab-highlight {
                animation: tabGlow 2s ease-in-out;
            }
            @keyframes tabGlow {
                0% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0.7); }
                50% { box-shadow: 0 0 0 10px rgba(0, 123, 255, 0); }
                100% { box-shadow: 0 0 0 0 rgba(0, 123, 255, 0); }
            }
            /* Enhanced gradients */
            .blue-purple-gradient {
                background: linear-gradient(135deg, rgba(0, 123, 255, 0.1), rgba(138, 43, 226, 0.1), rgba(0, 255, 255, 0.1));
            }
            [data-theme="dark"] .blue-purple-gradient {
                background: linear-gradient(135deg, rgba(0, 123, 255, 0.2), rgba(138, 43, 226, 0.2), rgba(0, 255, 255, 0.2));
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "dev-token")

# Modern external stylesheets
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
        "rel": "stylesheet",
    },
    {
        "href": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
        "rel": "stylesheet",
    }
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True, title="FloatChat Research Dashboard")
server = app.server

# Set the custom CSS
app.index_string = app_css

# Quick action suggestions for research (removed as requested)
quick_actions = []

# Create interactive map with theme support
def create_interactive_map(dark_mode=False):
    """Create an enhanced interactive map with theme support"""
    
    # Use RAG system data if available, otherwise generate sample data
    if RAG_AVAILABLE:
        # Use actual RAG float database
        float_data_list = list(argo_rag.float_database.values())
        n_floats = len(float_data_list)
        
        # Extract data from RAG database
        lats = [float_data['latitude'] for float_data in float_data_list]
        lons = [float_data['longitude'] for float_data in float_data_list]
        temps = [float_data['surface_temperature'] for float_data in float_data_list]
        salinities = [float_data['surface_salinity'] for float_data in float_data_list]
        depths = [float_data['max_depth'] for float_data in float_data_list]
        float_ids = [float_data['float_id'] for float_data in float_data_list]
    else:
        # Fallback to sample data generation
        np.random.seed(42)  # For consistent results
        n_floats = 150  # More float points for better interactivity
        
        # Indian Ocean coordinates with more realistic distribution
        lats = np.random.uniform(-35, 15, n_floats)
        lons = np.random.uniform(45, 115, n_floats)
        
        # Temperature based on latitude (warmer near equator)
        temps = 28 - 0.4 * np.abs(lats) + np.random.normal(0, 2, n_floats)
        temps = np.clip(temps, 5, 32)  # Realistic ocean temperatures
        
        # Salinity data (realistic ocean values)
        salinities = 35 + np.random.normal(0, 0.5, n_floats)
        salinities = np.clip(salinities, 33, 37)
        
        # Depth data
        depths = np.random.uniform(10, 2000, n_floats)
        
        # Float IDs with more variety
        float_ids = [f"ARGO_{i+5000}" for i in range(n_floats)]
    
    # Enhanced hover text with more data
    hover_texts = [
        f"<b>{float_id}</b><br>" +
        f"🌡️ Temperature: {temp:.1f}°C<br>" +
        f"🧂 Salinity: {sal:.2f} PSU<br>" +
        f"📏 Depth: {depth:.0f}m<br>" +
        f"📍 Lat: {lat:.2f}°, Lon: {lon:.2f}°<br>" +
        f"<i>🖱️ Click to view detailed profile</i>"
        for float_id, temp, sal, depth, lat, lon in zip(float_ids, temps, salinities, depths, lats, lons)
    ]
    
    # Create the map
    fig = go.Figure()
    
    # Choose colorscale based on theme
    colorscale = 'Cividis' if dark_mode else 'Viridis'
    
    fig.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers',
        marker=dict(
            size=14,  # Larger markers for better interaction
            color=temps,
            colorscale=colorscale,
            showscale=True,
            colorbar=dict(
                title=dict(
                    text="Temperature (°C)",
                    font=dict(size=12, color='white' if dark_mode else 'black')
                ),
                thickness=15,
                len=0.4,
                x=0.98,  # Position at right edge
                y=0.15,  # Position at bottom
                xanchor="right",
                yanchor="bottom",
                bgcolor='rgba(0,0,0,0.7)' if dark_mode else 'rgba(255,255,255,0.9)',
                bordercolor='rgba(255,255,255,0.3)' if dark_mode else 'rgba(0,0,0,0.1)',
                borderwidth=1,
                tickfont=dict(size=10, color='white' if dark_mode else 'black'),
                # Add rounded corners effect
                outlinecolor='rgba(255,255,255,0.2)' if dark_mode else 'rgba(0,0,0,0.1)',
                outlinewidth=1
            ),
            opacity=0.9
        ),
        text=hover_texts,
        hovertemplate="<b>%{customdata[0]}</b><br>" +
                     "🌡️ <b>%{customdata[1]:.1f}°C</b><br>" +
                     "🧂 %{customdata[2]:.2f} PSU<br>" +
                     "📏 %{customdata[3]:.0f}m depth<br>" +
                     "📍 %{lat:.2f}°, %{lon:.2f}°<br>" +
                     "<i>Click for detailed profile</i>" +
                     "<extra></extra>",
        customdata=list(zip(float_ids, temps, salinities, depths)),
        name="ARGO Floats",
        # Enhanced hover effects
        hoverlabel=dict(
            bgcolor='rgba(0,0,0,0.8)' if dark_mode else 'rgba(255,255,255,0.95)',
            bordercolor='rgba(255,255,255,0.3)' if dark_mode else 'rgba(0,0,0,0.1)',
            font=dict(color='white' if dark_mode else 'black', size=12),
            namelength=0
        )
    ))
    
    # Modern map style based on theme
    map_style = "carto-darkmatter" if dark_mode else "carto-positron"
    
    fig.update_layout(
        mapbox=dict(
            style=map_style,
            center=dict(lat=-10, lon=80),
            zoom=3.2,
            # Enhanced map controls
            bearing=0,
            pitch=0
        ),
        # Remove all margins for full container usage
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        # Enhanced interactivity
        dragmode='pan',
        # Smooth transitions
        transition=dict(
            duration=500,
            easing="cubic-in-out"
        ),
        # Configure hover behavior
        hovermode='closest'
    )
    
    return fig

# Wrapper function for initial load
def create_float_map():
    """Wrapper for backward compatibility"""
    return create_interactive_map(dark_mode=False)

# Generate comprehensive ARGO data for table
def generate_argo_table_data():
    """Generate comprehensive ARGO float data for the analysis table"""
    np.random.seed(42)  # For consistent data
    
    # Generate 50 ARGO floats across Indian Ocean
    n_floats = 50
    
    data = []
    for i in range(n_floats):
        float_id = f"ARGO_{5900000 + i:04d}"
        lat = np.random.uniform(-30, 25)  # Indian Ocean latitudes
        lon = np.random.uniform(40, 120)  # Indian Ocean longitudes
        
        # Generate realistic oceanographic data
        temp = np.random.uniform(2, 30)  # Surface temperature
        salinity = np.random.uniform(33.5, 37.5)  # Typical salinity range
        depth = np.random.uniform(500, 2000)  # Max depth
        
        # Generate date (last 30 days)
        days_ago = np.random.randint(0, 30)
        date = (datetime.now() - pd.Timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Status based on recent data
        status = "Active" if days_ago < 7 else "Inactive" if days_ago > 20 else "Monitoring"
        
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

def classify_query(query: str) -> str:
    """Classify query type: 'argo' for our database, 'ocean_location' for location-based ocean data, 'ocean' for general ocean topics, 'unrelated' for others"""
    query_lower = query.lower().strip()
    
    # Check for ARGO float references
    argo_keywords = ['argo', 'float', 'wmo', 'platform', 'indian ocean', 'surface temperature', 'salinity', 'depth profile']
    if any(keyword in query_lower for keyword in argo_keywords):
        # Check if it's asking about our specific database
        database_keywords = ['our', 'this', 'here', 'dashboard', 'map', 'show', 'find', 'search', 'list']
        if any(keyword in query_lower for keyword in database_keywords):
            return 'argo'
        # Check for specific float IDs (ARGO_XXXX pattern)
        if 'argo_' in query_lower or re.search(r'\b\d{4,}\b', query_lower):
            return 'argo'
        # Check for region searches (e.g., "floats in Arabian Sea")
        region_keywords = ['arabian sea', 'bay of bengal', 'indian ocean', 'central indian', 'southern indian', 'western indian', 'region', 'area']
        if any(keyword in query_lower for keyword in region_keywords) and ('float' in query_lower or 'find' in query_lower or 'show' in query_lower):
            return 'argo'
    
    # Check for location-based ocean data queries
    location_ocean_keywords = [
        'ocean near', 'ocean around', 'ocean at', 'sea near', 'sea around', 'sea at', 
        'data near', 'data around', 'data at', 'ocean off', 'sea off',
        'ocean conditions', 'sea conditions', 'ocean data', 'sea data',
        'ocean profile', 'sea profile', 'ocean parameters', 'sea parameters',
        'ocean temperature', 'sea temperature', 'ocean salinity', 'sea salinity',
        'ocean pressure', 'sea pressure', 'ocean density', 'sea density'
    ]
    location_names = [
        # Major Indian coastal cities
        'mumbai', 'delhi', 'chennai', 'kolkata', 'goa', 'kochi', 'mangalore', 'visakhapatnam', 
        'paradip', 'pune', 'ahmedabad', 'surat', 'vadodara', 'rajkot', 'bhavnagar', 'jamnagar',
        
        # Gujarat coastal areas
        'diu', 'daman', 'porbandar', 'veraval', 'okha', 'jakhau', 'kutch', 'gujarat',
        
        # Karnataka coastal
        'karwar', 'honavar', 'kumta', 'murudeshwar', 'kundapur', 'udupi', 'malpe', 'mulki', 'sullia',
        
        # Kerala coastal
        'kannur', 'kozhi kode', 'calicut', 'thrissur', 'alleppey', 'alappuzha', 'kollam', 'quilon', 
        'trivandrum', 'thiruvananthapuram',
        
        # Tamil Nadu coastal
        'kanyakumari', 'nagercoil', 'tirunelveli', 'thoothukudi', 'tuticorin', 'ramanathapuram', 
        'pudukkottai', 'thanjavur', 'nagapattinam', 'cuddalore', 'puducherry', 'pondicherry', 
        'vellore', 'tiruvallur', 'kancheepuram',
        
        # Andhra Pradesh coastal
        'nellore', 'ongole', 'guntur', 'vijayawada', 'eluru', 'rajahmundry', 'kakinada', 'srikakulam',
        
        # Odisha coastal
        'berhampur', 'brahmapur', 'puri', 'bhubaneswar', 'cuttack', 'balasore', 'jajpur',
        
        # West Bengal coastal
        'kolkata', 'howrah', 'haldia', 'diamond harbour',
        
        # Maharashtra coastal
        'ratnagiri', 'sindhudurg', 'raigad', 'thane', 'palghar', 'dahanu',
        
        # States (coastal centers)
        'maharashtra', 'karnataka', 'kerala', 'tamil nadu', 'andhra pradesh', 'odisha', 'west bengal',
        
        # Ocean regions
        'arabian sea', 'bay of bengal', 'indian ocean', 'pacific ocean', 'atlantic ocean',
        
        # Additional global locations near Indian Ocean
        'colombo', 'male', 'victoria', 'port louis', 'antananarivo', 'dar es salaam', 
        'mogadishu', 'aden', 'salalah', 'muscat', 'karachi', 'gwadar', 'chittagong', 
        'yangon', 'jakarta', 'surabaya', 'perth', 'fremantle'
    ]
    
    if any(loc_kw in query_lower for loc_kw in location_ocean_keywords) or any(loc in query_lower for loc in location_names):
        # Additional check for oceanographic terms
        ocean_terms = [
            'temperature', 'salinity', 'pressure', 'density', 'current', 'wave', 'depth', 
            'profile', 'data', 'condition', 'water', 'marine', 'ocean', 'sea'
        ]
        if any(term in query_lower for term in ocean_terms) or 'ocean' in query_lower or 'sea' in query_lower:
            return 'ocean_location'
    
    # Check for general ocean topics (not about our ARGO database)
    ocean_keywords = ['ocean', 'sea', 'marine', 'atlantic', 'pacific', 'arctic', 'antarctic', 'coral', 'tide', 'wave', 'current', 'tsunami', 'climate', 'warming', 'ph', 'acidification', 'marine life', 'fish', 'plankton', 'whale', 'shark', 'kelp', 'mangrove', 'estuary', 'coastal', 'beach', 'dolphin', 'turtle', 'seahorse', 'jellyfish', 'octopus', 'squid', 'crab', 'lobster', 'shrimp', 'eel', 'salmon', 'tuna', 'cod', 'trout', 'bass', 'perch', 'catfish', 'carp', 'herring', 'sardine', 'anchovy', 'mackerel', 'swordfish', 'marlin', 'sailfish', 'tuna', 'eel', 'lamprey', 'hagfish', 'shark', 'ray', 'skate', 'chimaera', 'lungfish', 'coelacanth']
    if any(keyword in query_lower for keyword in ocean_keywords):
        return 'ocean'
    
    return 'unrelated'

def get_ocean_answer_with_groq(question: str) -> str:
    """Get brief answer for general ocean questions using Groq LLM"""
    try:
        from groq import Groq
        import os
        
        # Get API key from environment
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            return "🌊 Sorry, ocean knowledge service is currently unavailable."
        
        client = Groq(api_key=groq_api_key)
        
        system_prompt = """You are a marine science expert. Answer ocean-related questions in 1-2 sentences only. Keep responses under 50 words. Focus on facts, avoid speculation."""
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {question}\n\nProvide a very brief, factual answer:"}
            ],
            temperature=0.3,
            max_tokens=100,
        )
        
        answer = response.choices[0].message.content.strip()
        return f"🌊 {answer}"
        
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        return "🌊 Sorry, ocean knowledge service is temporarily unavailable."

def enhanced_chat_with_nlp_rag_llm(message: str, theme: str = "light") -> Dict[str, Any]:
    """Enhanced chat handler using NLP + Groq + RAG + LLM for comprehensive responses with tables and statistics"""
    try:
        from groq import Groq
        import os
        
        # Get API key from environment
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            return {
                'response': "🤖 Sorry, AI service is currently unavailable. Please set GROQ_API_KEY.",
                'table_data': None,
                'statistics': None,
                'plots_needed': False
            }
        
        client = Groq(api_key=groq_api_key)
        
        # Step 1: Use RAG to analyze query intent and gather relevant data
        intent = argo_rag.analyze_query_intent(message)
        
        # Step 2: Retrieve relevant ARGO float data if applicable
        float_data = []
        rag_context = ""
        
        if intent['float_ids']:
            for float_id in intent['float_ids']:
                data = argo_rag.get_float_data(float_id)
                if data:
                    float_data.append(data)
                    # Add float context for LLM
                    rag_context += f"Float {float_id}: {data['latitude']}°N, {data['longitude']}°E, Temp: {data['surface_temperature']}°C, Salinity: {data['surface_salinity']} PSU, Status: {data['status']}\n"
        
        if intent['region']:
            region_floats = argo_rag.search_floats_by_region(intent['region'])
            if region_floats:
                float_data.extend(region_floats[:3])  # Limit to 3 for context
                rag_context += f"Region {intent['region']}: {len(region_floats)} floats available\n"
        
        # Step 3: Create comprehensive system prompt for LLM
        system_prompt = f"""You are an advanced marine science AI assistant with access to ARGO float data.

CONTEXT DATA:
{rag_context}

INSTRUCTIONS:
- Answer any question using marine science knowledge in 1-2 sentences only
- When ARGO data is relevant, incorporate it naturally and briefly
- Provide statistical summaries when appropriate but keep them minimal
- Use approximate/random values when real data is missing (clearly indicate this)
- Prefer statistical data from oceanographic references
- Generate tables for comparative data, statistics, or lists when truly needed
- Explain oceanographic concepts in 1-2 concise sentences
- **CRITICAL: Keep ALL responses extremely brief and to the point - under 50 words when possible**

RESPONSE FORMAT:
- Start with direct answer to the question
- Include relevant statistics or data tables when helpful (but minimize)
- Use markdown for tables only when necessary
- End with key insights or additional context (keep very brief)
- If showing data, indicate if it's real or approximate

Current query: {message}
Intent analysis: {intent}
"""
        
        # Step 4: Get LLM response
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.4,
            max_tokens=200,
        )
        
        llm_response = response.choices[0].message.content.strip()
        
        # Step 5: Extract table data if present in response
        table_data = None
        statistics = None
        
        # Look for markdown tables in the response
        if '|' in llm_response and '\n' in llm_response:
            lines = llm_response.split('\n')
            table_start = -1
            for i, line in enumerate(lines):
                if '|' in line and ('---' in lines[i+1] if i+1 < len(lines) else False):
                    table_start = i
                    break
            
            if table_start >= 0:
                # Extract table
                table_lines = []
                for i in range(table_start, len(lines)):
                    if '|' in lines[i]:
                        table_lines.append(lines[i])
                    else:
                        break
                
                if table_lines:
                    # Convert to DataTable format
                    headers = [cell.strip() for cell in table_lines[0].split('|') if cell.strip()]
                    data = []
                    for line in table_lines[2:]:  # Skip header and separator
                        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                        if len(cells) == len(headers):
                            data.append(dict(zip(headers, cells)))
                    
                    if data:
                        table_data = {
                            'data': data,
                            'columns': [{'name': h, 'id': h} for h in headers]
                        }
        
        # Step 6: Generate statistics if relevant
        if any(keyword in message.lower() for keyword in ['statistics', 'stats', 'average', 'mean', 'summary', 'analysis']):
            if float_data:
                # Calculate statistics from available float data
                temps = [f['surface_temperature'] for f in float_data if 'surface_temperature' in f]
                salinities = [f['surface_salinity'] for f in float_data if 'surface_salinity' in f]
                
                statistics = {
                    'float_count': len(float_data),
                    'avg_temperature': round(np.mean(temps), 2) if temps else None,
                    'avg_salinity': round(np.mean(salinities), 2) if salinities else None,
                    'temp_range': f"{min(temps):.1f} - {max(temps):.1f}°C" if temps else None,
                    'salinity_range': f"{min(salinities):.2f} - {max(salinities):.2f} PSU" if salinities else None,
                    'active_floats': len([f for f in float_data if f.get('status') == 'Active'])
                }
            else:
                # Generate approximate statistics for demonstration
                statistics = {
                    'note': 'Approximate values based on typical Indian Ocean conditions',
                    'avg_surface_temp': '27.5°C',
                    'avg_surface_salinity': '35.2 PSU',
                    'typical_thermocline_depth': '50-100m',
                    'mixed_layer_depth': '20-80m'
                }
        
        # Step 7: Determine if plots are needed
        plots_needed = (
            intent['requires_plotting'] or 
            any(keyword in message.lower() for keyword in ['plot', 'graph', 'chart', 'visualize', 'show']) or
            len(float_data) > 0
        )
        
        return {
            'response': llm_response,
            'table_data': table_data,
            'statistics': statistics,
            'plots_needed': plots_needed,
            'float_data': float_data[:5],  # Limit for display
            'intent': intent
        }
        
    except Exception as e:
        logger.error(f"Enhanced chat error: {e}")
        return {
            'response': f"❌ Error processing your query: {str(e)[:100]}",
            'table_data': None,
            'statistics': None,
            'plots_needed': False
        }

def create_data_table(data: Dict[str, Any], table_id: str = "response-table", theme: str = "light") -> html.Div:
    """Create a styled DataTable component for displaying tabular data"""
    if not data or 'data' not in data or 'columns' not in data:
        return html.Div()
    
    # Theme-aware styling
    is_dark = theme == "dark"
    table_style = {
        'backgroundColor': 'var(--bg-card)' if not is_dark else '#1e293b',
        'color': 'var(--text-primary)' if not is_dark else '#f8fafc',
        'border': f'1px solid {"var(--border-primary)" if not is_dark else "#475569"}',
        'borderRadius': '8px',
        'overflow': 'hidden'
    }
    
    header_style = {
        'backgroundColor': 'var(--bg-secondary)' if not is_dark else '#334155',
        'color': 'var(--text-primary)' if not is_dark else '#f8fafc',
        'fontWeight': 'bold',
        'borderBottom': f'1px solid {"var(--border-primary)" if not is_dark else "#475569"}'
    }
    
    cell_style = {
        'backgroundColor': 'var(--bg-card)' if not is_dark else '#1e293b',
        'color': 'var(--text-primary)' if not is_dark else '#f8fafc',
        'borderBottom': f'1px solid {"var(--border-secondary)" if not is_dark else "#64748b"}'
    }
    
    return html.Div([
        html.H4("📊 Data Table", style={
            "color": "var(--accent-primary)",
            "margin-bottom": "1rem",
            "font-size": "1.1rem"
        }),
        dash_table.DataTable(
            id=table_id,
            columns=data['columns'],
            data=data['data'],
            style_table=table_style,
            style_header=header_style,
            style_cell=cell_style,
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'var(--bg-tertiary)' if not is_dark else '#374151',
                }
            ],
            page_size=10,
            style_as_list_view=True,
            css=[{
                'selector': '.dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table',
                'rule': 'border-collapse: separate; border-spacing: 0;'
            }]
        )
    ], style={"margin": "1rem 0"})

def generate_fallback_ocean_data(query: str) -> Dict[str, Any]:
    """Generate approximate/random ocean data when real data is missing"""
    query_lower = query.lower()
    
    # Generate approximate statistical data based on query type
    if 'temperature' in query_lower:
        return {
            'data': [
                {'Parameter': 'Surface Temperature', 'Average': '27.5°C', 'Range': '22-32°C', 'Source': 'Approximate'},
                {'Parameter': 'Deep Temperature', 'Average': '4.2°C', 'Range': '2-8°C', 'Source': 'Approximate'},
                {'Parameter': 'Thermocline Depth', 'Average': '75m', 'Range': '50-150m', 'Source': 'Approximate'}
            ],
            'columns': [
                {'name': 'Parameter', 'id': 'Parameter'},
                {'name': 'Average', 'id': 'Average'},
                {'name': 'Range', 'id': 'Range'},
                {'name': 'Source', 'id': 'Source'}
            ]
        }
    
    elif 'salinity' in query_lower:
        return {
            'data': [
                {'Region': 'Arabian Sea', 'Surface Salinity': '36.2 PSU', 'Deep Salinity': '34.8 PSU', 'Source': 'Approximate'},
                {'Region': 'Bay of Bengal', 'Surface Salinity': '32.5 PSU', 'Deep Salinity': '34.9 PSU', 'Source': 'Approximate'},
                {'Region': 'Indian Ocean', 'Surface Salinity': '35.2 PSU', 'Deep Salinity': '34.7 PSU', 'Source': 'Approximate'}
            ],
            'columns': [
                {'name': 'Region', 'id': 'Region'},
                {'name': 'Surface Salinity', 'id': 'Surface Salinity'},
                {'name': 'Deep Salinity', 'id': 'Deep Salinity'},
                {'name': 'Source', 'id': 'Source'}
            ]
        }
    
    elif 'depth' in query_lower or 'profile' in query_lower:
        return {
            'data': [
                {'Depth Range': '0-50m', 'Description': 'Mixed Layer', 'Typical Temp': '25-30°C', 'Source': 'Approximate'},
                {'Depth Range': '50-200m', 'Description': 'Thermocline', 'Typical Temp': '15-25°C', 'Source': 'Approximate'},
                {'Depth Range': '200-2000m', 'Description': 'Deep Water', 'Typical Temp': '2-10°C', 'Source': 'Approximate'}
            ],
            'columns': [
                {'name': 'Depth Range', 'id': 'Depth Range'},
                {'name': 'Description', 'id': 'Description'},
                {'name': 'Typical Temp', 'id': 'Typical Temp'},
                {'name': 'Source', 'id': 'Source'}
            ]
        }
    
    else:
        # General ocean statistics
        return {
            'data': [
                {'Ocean Parameter': 'Average Depth', 'Value': '3,800m', 'Global Range': '2,000-11,000m', 'Source': 'Approximate'},
                {'Ocean Parameter': 'Surface Area', 'Value': '361 million km²', 'Percentage': '71% of Earth', 'Source': 'Approximate'},
                {'Ocean Parameter': 'Volume', 'Value': '1.3 billion km³', 'Deepest Point': '11,034m (Mariana Trench)', 'Source': 'Approximate'},
                {'Ocean Parameter': 'Average Temperature', 'Value': '3.9°C', 'Surface Average': '17°C', 'Source': 'Approximate'}
            ],
            'columns': [
                {'name': 'Ocean Parameter', 'id': 'Ocean Parameter'},
                {'name': 'Value', 'id': 'Value'},
                {'name': 'Global Range/Percentage', 'id': 'Global Range'},
                {'name': 'Source', 'id': 'Source'}
            ]
        }

def extract_location_from_query(query: str) -> tuple:
    """Extract location information from ocean data queries"""
    query_lower = query.lower().strip()
    
    # Define location coordinates (lat, lon, name) - expanded database
    locations = {
        # Major Indian coastal cities
        'mumbai': (19.0760, 72.8777, 'Mumbai'),
        'delhi': (28.7041, 77.1025, 'Delhi'),  # Though inland, for completeness
        'chennai': (13.0827, 80.2707, 'Chennai'),
        'kolkata': (22.5726, 88.3639, 'Kolkata'),
        'goa': (15.2993, 74.1240, 'Goa'),
        'kochi': (9.9312, 76.2673, 'Kochi'),
        'mangalore': (12.9141, 74.8560, 'Mangalore'),
        'visakhapatnam': (17.6868, 83.2185, 'Visakhapatnam'),
        'paradip': (20.3161, 86.6114, 'Paradip'),
        'pune': (18.5204, 73.8567, 'Pune'),
        'ahmedabad': (23.0225, 72.5714, 'Ahmedabad'),
        'surat': (21.1702, 72.8311, 'Surat'),
        'vadodara': (22.3072, 73.1812, 'Vadodara'),
        'rajkot': (22.3039, 70.8022, 'Rajkot'),
        'bhavnagar': (21.7645, 72.1519, 'Bhavnagar'),
        'jamnagar': (22.4707, 70.0577, 'Jamnagar'),
        
        # Gujarat coastal areas
        'diu': (20.7144, 70.9879, 'Diu'),
        'daman': (20.3974, 72.8328, 'Daman'),
        'porbandar': (21.6417, 69.6293, 'Porbandar'),
        'veraval': (20.9159, 70.3629, 'Veraval'),
        'okha': (22.4677, 69.0724, 'Okha'),
        'jakhau': (23.2183, 68.7177, 'Jakhau'),
        'kutch': (23.7337, 68.9167, 'Kutch'),
        'gujarat': (22.2587, 71.1924, 'Gujarat Coast'),
        
        # Karnataka coastal
        'karwar': (14.8136, 74.1319, 'Karwar'),
        'honavar': (14.2809, 74.4450, 'Honavar'),
        'kumta': (14.4280, 74.4189, 'Kumta'),
        'murudeshwar': (14.0943, 74.4848, 'Murudeshwar'),
        'kundapur': (13.6230, 74.6908, 'Kundapur'),
        'udupi': (13.3409, 74.7421, 'Udupi'),
        'malpe': (13.3496, 74.7036, 'Malpe'),
        'mulki': (13.0911, 74.7935, 'Mulki'),
        'sullia': (12.5625, 75.3869, 'Sullia'),
        
        # Kerala coastal
        'kannur': (11.8745, 75.3704, 'Kannur'),
        'kozhi kode': (11.2588, 75.7804, 'Kozhikode'),
        'calicut': (11.2588, 75.7804, 'Calicut'),
        'thrissur': (10.5276, 76.2144, 'Thrissur'),
        'alleppey': (9.4981, 76.3388, 'Alleppey'),
        'alappuzha': (9.4981, 76.3388, 'Alappuzha'),
        'kollam': (8.8932, 76.6141, 'Kollam'),
        'quilon': (8.8932, 76.6141, 'Quilon'),
        'trivandrum': (8.5241, 76.9366, 'Trivandrum'),
        'thiruvananthapuram': (8.5241, 76.9366, 'Thiruvananthapuram'),
        
        # Tamil Nadu coastal
        'kanyakumari': (8.0883, 77.5385, 'Kanyakumari'),
        'nagercoil': (8.1784, 77.4343, 'Nagercoil'),
        'tirunelveli': (8.7139, 77.7567, 'Tirunelveli'),
        'thoothukudi': (8.7642, 78.1348, 'Thoothukudi'),
        'tuticorin': (8.7642, 78.1348, 'Tuticorin'),
        'ramanathapuram': (9.3639, 78.8395, 'Ramanathapuram'),
        'pudukkottai': (10.3833, 78.8001, 'Pudukkottai'),
        'thanjavur': (10.7870, 79.1378, 'Thanjavur'),
        'nagapattinam': (10.7656, 79.8424, 'Nagapattinam'),
        'cuddalore': (11.7447, 79.7680, 'Cuddalore'),
        'puducherry': (11.9416, 79.8083, 'Puducherry'),
        'pondicherry': (11.9416, 79.8083, 'Pondicherry'),
        'vellore': (12.9165, 79.1325, 'Vellore'),
        'tiruvallur': (13.1457, 79.9083, 'Tiruvallur'),
        'kancheepuram': (12.8342, 79.7036, 'Kancheepuram'),
        
        # Andhra Pradesh coastal
        'nellore': (14.4426, 79.9865, 'Nellore'),
        'ongole': (15.5057, 80.0499, 'Ongole'),
        'guntur': (16.3067, 80.4365, 'Guntur'),
        'vijayawada': (16.5062, 80.6480, 'Vijayawada'),
        'eluru': (16.7107, 81.0952, 'Eluru'),
        'rajahmundry': (17.0005, 81.8040, 'Rajahmundry'),
        'kakinada': (16.9891, 82.2475, 'Kakinada'),
        'srikakulam': (18.2960, 83.8968, 'Srikakulam'),
        
        # Odisha coastal
        'berhampur': (19.3149, 84.7941, 'Berhampur'),
        'brahmapur': (19.3149, 84.7941, 'Brahmapur'),
        'puri': (19.8135, 85.8312, 'Puri'),
        'bhubaneswar': (20.2961, 85.8245, 'Bhubaneswar'),
        'cuttack': (20.4625, 85.8830, 'Cuttack'),
        'balasore': (21.4927, 86.9335, 'Balasore'),
        'jajpur': (20.8529, 86.3334, 'Jajpur'),
        
        # West Bengal coastal
        'kolkata': (22.5726, 88.3639, 'Kolkata'),
        'howrah': (22.5958, 88.2636, 'Howrah'),
        'haldia': (22.0667, 88.0698, 'Haldia'),
        'diamond harbour': (22.1911, 88.1909, 'Diamond Harbour'),
        
        # Maharashtra coastal
        'ratnagiri': (16.9944, 73.3000, 'Ratnagiri'),
        'sindhudurg': (16.0467, 73.5333, 'Sindhudurg'),
        'raigad': (18.2314, 73.4400, 'Raigad'),
        'thane': (19.2183, 72.9781, 'Thane'),
        'palghar': (19.6972, 72.7699, 'Palghar'),
        'dahanu': (19.9678, 72.7126, 'Dahanu'),
        
        # States (coastal centers)
        'maharashtra': (18.5204, 73.8567, 'Maharashtra Coast'),
        'karnataka': (15.3173, 75.7139, 'Karnataka Coast'),
        'kerala': (10.8505, 76.2711, 'Kerala Coast'),
        'tamil nadu': (11.1271, 78.6569, 'Tamil Nadu Coast'),
        'andhra pradesh': (15.9129, 79.7400, 'Andhra Pradesh Coast'),
        'odisha': (20.9517, 85.0985, 'Odisha Coast'),
        'west bengal': (22.9868, 87.8550, 'West Bengal Coast'),
        
        # Ocean regions
        'arabian sea': (15.0, 65.0, 'Arabian Sea'),
        'bay of bengal': (15.0, 85.0, 'Bay of Bengal'),
        'indian ocean': (0.0, 75.0, 'Indian Ocean'),
        'pacific ocean': (0.0, -170.0, 'Pacific Ocean'),
        'atlantic ocean': (0.0, -30.0, 'Atlantic Ocean'),
        
        # Additional global locations near Indian Ocean
        'colombo': (6.9271, 79.8612, 'Colombo'),
        'male': (4.1755, 73.5093, 'Malé'),
        'victoria': (-4.6191, 55.4513, 'Victoria'),
        'port louis': (-20.1609, 57.5012, 'Port Louis'),
        'antananarivo': (-18.8792, 47.5079, 'Antananarivo'),
        'dar es salaam': (-6.7924, 39.2083, 'Dar es Salaam'),
        'mogadishu': (2.0469, 45.3182, 'Mogadishu'),
        'aden': (12.7855, 45.0187, 'Aden'),
        'salalah': (17.0151, 54.0924, 'Salalah'),
        'muscat': (23.5880, 58.3829, 'Muscat'),
        'karachi': (24.8607, 67.0011, 'Karachi'),
        'gwadar': (25.1216, 62.3254, 'Gwadar'),
        'chittagong': (22.3569, 91.7832, 'Chittagong'),
        'yangon': (16.8661, 96.1951, 'Yangon'),
        'jakarta': (-6.2088, 106.8456, 'Jakarta'),
        'surabaya': (-7.2575, 112.7521, 'Surabaya'),
        'perth': (-31.9505, 115.8605, 'Perth'),
        'fremantle': (-32.0569, 115.7439, 'Fremantle'),
    }
    
    # Find location in query
    for loc_key, (lat, lon, name) in locations.items():
        if loc_key in query_lower:
            return lat, lon, name
    
    # If no specific location found, check if it's asking about Indian Ocean or nearby
    if any(word in query_lower for word in ['indian ocean', 'arabian sea', 'bay of bengal']):
        if 'indian ocean' in query_lower:
            return 0.0, 75.0, 'Indian Ocean'
        elif 'arabian sea' in query_lower:
            return 15.0, 65.0, 'Arabian Sea'
        elif 'bay of bengal' in query_lower:
            return 15.0, 85.0, 'Bay of Bengal'
    
    # Default to Arabian Sea if no specific location found
    return 15.0, 65.0, 'Arabian Sea'

def generate_location_ocean_data(lat: float, lon: float, location_name: str, theme: str = "light") -> dict:
    """Generate synthetic oceanographic data for a specific location"""
    import numpy as np
    
    # Seed for reproducible results based on location
    np.random.seed(hash(location_name) % 1000)
    
    # Adjust baseline conditions based on location
    # Arabian Sea (warmer, saltier)
    if 'arabian' in location_name.lower():
        base_temp = 28.0
        base_salinity = 36.5
        temp_variation = 3.0
        salinity_variation = 0.8
    # Bay of Bengal (slightly cooler, fresher due to rivers)
    elif 'bengal' in location_name.lower():
        base_temp = 26.0
        base_salinity = 33.8
        temp_variation = 2.5
        salinity_variation = 1.2
    # Indian Ocean (moderate)
    elif 'indian ocean' in location_name.lower():
        base_temp = 27.0
        base_salinity = 35.0
        temp_variation = 4.0
        salinity_variation = 1.0
    # Coastal cities (influenced by land)
    else:
        base_temp = 25.0
        base_salinity = 34.5
        temp_variation = 5.0
        salinity_variation = 1.5
    
    # Generate depth profile (0-2000m)
    depths = np.linspace(0, 2000, 50)
    
    # Temperature profile with thermocline
    temp_profile = base_temp - depths * 0.01  # Temperature decreases with depth
    temp_profile += np.random.normal(0, temp_variation * 0.1, len(depths))  # Add variation
    # Add thermocline effect (rapid temperature change around 200-500m)
    thermocline_mask = (depths >= 200) & (depths <= 500)
    temp_profile[thermocline_mask] -= np.sin((depths[thermocline_mask] - 200) * np.pi / 300) * 2
    temp_profile = np.clip(temp_profile, 2, base_temp + 2)
    
    # Salinity profile
    sal_profile = base_salinity + depths * 0.0005  # Slight increase with depth
    sal_profile += np.random.normal(0, salinity_variation * 0.1, len(depths))
    sal_profile = np.clip(sal_profile, 32, 38)
    
    # Pressure calculation (simplified)
    pressure_profile = depths * 0.1  # Approximate pressure in dbar
    
    # Density calculation (simplified UNESCO formula approximation)
    density_profile = 1000 + (sal_profile - 35) * 0.8 - (temp_profile - 10) * 0.2 + pressure_profile * 0.0004
    
    # Add some realistic variation
    density_profile += np.random.normal(0, 0.5, len(depths))
    
    # Calculate statistics
    stats = {
        'surface_temp': float(temp_profile[0]),
        'deep_temp': float(temp_profile[-1]),
        'temp_range': float(temp_profile[0] - temp_profile[-1]),
        'surface_salinity': float(sal_profile[0]),
        'deep_salinity': float(sal_profile[-1]),
        'salinity_range': float(sal_profile[-1] - sal_profile[0]),
        'mixed_layer_depth': float(depths[np.where(temp_profile < temp_profile[0] - 0.5)[0][0]] if len(np.where(temp_profile < temp_profile[0] - 0.5)[0]) > 0 else 100),
        'thermocline_depth': float(depths[np.argmin(np.gradient(temp_profile))]),
        'max_pressure': float(pressure_profile[-1]),
        'avg_density': float(np.mean(density_profile))
    }
    
    # Theme colors
    is_dark = theme == "dark"
    colors = {
        'bg': '#1e293b' if is_dark else 'white',
        'text': 'white' if is_dark else 'black',
        'grid': '#374151' if is_dark else '#e5e7eb'
    }
    
    return {
        'location': location_name,
        'coordinates': (lat, lon),
        'depths': depths,
        'temperature': temp_profile,
        'salinity': sal_profile,
        'pressure': pressure_profile,
        'density': density_profile,
        'statistics': stats,
        'colors': colors
    }

def create_region_bounding_box(lat: float, lon: float, location_name: str, theme: str = "light") -> dict:
    """Create a map figure with a red bounding box around the specified region"""
    
    # Create a bounding box around the location (approximately 2° x 2°)
    box_size = 1.5  # degrees
    
    # Define the four corners of the bounding box
    lons = [lon - box_size, lon + box_size, lon + box_size, lon - box_size, lon - box_size]
    lats = [lat - box_size, lat - box_size, lat + box_size, lat + box_size, lat - box_size]
    
    # Create the map figure
    fig = go.Figure()
    
    # Add the bounding box as a scatter trace with lines
    fig.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='lines',
        line=dict(color='red', width=3),
        fill='none',
        name=f'{location_name} Region',
        hovertemplate=f'<b>{location_name} Analysis Region</b><br>' +
                     f'Lat: {lat:.2f}°, Lon: {lon:.2f}°<br>' +
                     '<i>Red box shows data collection area</i><extra></extra>'
    ))
    
    # Add a marker at the center point
    fig.add_trace(go.Scattermapbox(
        lat=[lat],
        lon=[lon],
        mode='markers',
        marker=dict(
            size=12,
            color='red',
            symbol='circle'
        ),
        text=[f"<b>{location_name}</b><br>📍 {lat:.2f}°, {lon:.2f}°<br>🔴 Analysis Center"],
        hovertemplate='%{text}<extra></extra>',
        name='Analysis Center'
    ))
    
    # Theme-aware styling
    is_dark = theme == "dark"
    map_style = "carto-darkmatter" if is_dark else "carto-positron"
    bg_color = 'rgba(30, 41, 59, 0)' if is_dark else 'rgba(255, 255, 255, 0)'
    
    # Update layout with appropriate zoom to show the bounding box
    fig.update_layout(
        mapbox=dict(
            style=map_style,
            center=dict(lat=lat, lon=lon),
            zoom=6,  # Zoom out to show the bounding box
            bearing=0,
            pitch=0
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255, 255, 255, 0.8)' if not is_dark else 'rgba(0, 0, 0, 0.8)',
            bordercolor='red',
            borderwidth=1
        )
    )
    
    return fig

def create_location_ocean_plots(data: dict, theme: str = "light") -> tuple:
    """Create comprehensive plots for location-based ocean data with all 4 parameters"""
    
    # Temperature vs Depth
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(
        x=data['temperature'],
        y=data['depths'],
        mode='lines+markers',
        line=dict(color='#ef4444', width=3),
        marker=dict(size=4, color='#ef4444'),
        name='Temperature',
        hovertemplate='<b>Depth:</b> %{y:.0f}m<br><b>Temperature:</b> %{x:.1f}°C<extra></extra>'
    ))
    temp_fig.update_layout(
        title=f"Temperature Profile - {data['location']}",
        xaxis_title="Temperature (°C)",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed", gridcolor=data['colors']['grid']),
        xaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=300
    )
    
    # Salinity vs Depth
    sal_fig = go.Figure()
    sal_fig.add_trace(go.Scatter(
        x=data['salinity'],
        y=data['depths'],
        mode='lines+markers',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=4, color='#3b82f6'),
        name='Salinity',
        hovertemplate='<b>Depth:</b> %{y:.0f}m<br><b>Salinity:</b> %{x:.2f} PSU<extra></extra>'
    ))
    sal_fig.update_layout(
        title=f"Salinity Profile - {data['location']}",
        xaxis_title="Salinity (PSU)",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed", gridcolor=data['colors']['grid']),
        xaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=300
    )
    
    # Pressure vs Depth
    pressure_fig = go.Figure()
    pressure_fig.add_trace(go.Scatter(
        x=data['pressure'],
        y=data['depths'],
        mode='lines+markers',
        line=dict(color='#8b5cf6', width=3),
        marker=dict(size=4, color='#8b5cf6'),
        name='Pressure',
        hovertemplate='<b>Depth:</b> %{y:.0f}m<br><b>Pressure:</b> %{x:.1f} dbar<extra></extra>'
    ))
    pressure_fig.update_layout(
        title=f"Pressure Profile - {data['location']}",
        xaxis_title="Pressure (dbar)",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed", gridcolor=data['colors']['grid']),
        xaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=300
    )
    
    # T-S Diagram
    ts_fig = go.Figure()
    ts_fig.add_trace(go.Scatter(
        x=data['salinity'],
        y=data['temperature'],
        mode='markers',
        marker=dict(
            size=6,
            color=data['depths'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Depth (m)", thickness=10, len=0.5)
        ),
        name='T-S Relationship',
        hovertemplate='<b>Salinity:</b> %{x:.2f} PSU<br><b>Temperature:</b> %{y:.1f}°C<extra></extra>'
    ))
    ts_fig.update_layout(
        title=f"T-S Diagram - {data['location']}",
        xaxis_title="Salinity (PSU)",
        yaxis_title="Temperature (°C)",
        xaxis=dict(gridcolor=data['colors']['grid']),
        yaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=300
    )
    
    # Density vs Depth
    density_fig = go.Figure()
    density_fig.add_trace(go.Scatter(
        x=data['density'],
        y=data['depths'],
        mode='lines+markers',
        line=dict(color='#10b981', width=3),
        marker=dict(size=4, color='#10b981'),
        name='Density',
        hovertemplate='<b>Depth:</b> %{y:.0f}m<br><b>Density:</b> %{x:.1f} kg/m³<extra></extra>'
    ))
    density_fig.update_layout(
        title=f"Density Profile - {data['location']}",
        xaxis_title="Density (kg/m³)",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed", gridcolor=data['colors']['grid']),
        xaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=300
    )
    
def create_location_ocean_plots(data: dict, theme: str = "light") -> tuple:
    """Create comprehensive plots for location-based ocean data with all 4 parameters"""
    
    # Temperature vs Depth
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(
        x=data['temperature'],
        y=data['depths'],
        mode='lines+markers',
        line=dict(color='#ef4444', width=3),
        marker=dict(size=4, color='#ef4444'),
        name='Temperature',
        hovertemplate='<b>Depth:</b> %{y:.0f}m<br><b>Temperature:</b> %{x:.1f}°C<extra></extra>'
    ))
    temp_fig.update_layout(
        title=f"Temperature Profile - {data['location']}",
        xaxis_title="Temperature (°C)",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed", gridcolor=data['colors']['grid']),
        xaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=300
    )
    
    # Salinity vs Depth
    sal_fig = go.Figure()
    sal_fig.add_trace(go.Scatter(
        x=data['salinity'],
        y=data['depths'],
        mode='lines+markers',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=4, color='#3b82f6'),
        name='Salinity',
        hovertemplate='<b>Depth:</b> %{y:.0f}m<br><b>Salinity:</b> %{x:.2f} PSU<extra></extra>'
    ))
    sal_fig.update_layout(
        title=f"Salinity Profile - {data['location']}",
        xaxis_title="Salinity (PSU)",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed", gridcolor=data['colors']['grid']),
        xaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=300
    )
    
    # Pressure vs Depth
    pressure_fig = go.Figure()
    pressure_fig.add_trace(go.Scatter(
        x=data['pressure'],
        y=data['depths'],
        mode='lines+markers',
        line=dict(color='#8b5cf6', width=3),
        marker=dict(size=4, color='#8b5cf6'),
        name='Pressure',
        hovertemplate='<b>Depth:</b> %{y:.0f}m<br><b>Pressure:</b> %{x:.1f} dbar<extra></extra>'
    ))
    pressure_fig.update_layout(
        title=f"Pressure Profile - {data['location']}",
        xaxis_title="Pressure (dbar)",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed", gridcolor=data['colors']['grid']),
        xaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=300
    )
    
    # T-S Diagram
    ts_fig = go.Figure()
    ts_fig.add_trace(go.Scatter(
        x=data['salinity'],
        y=data['temperature'],
        mode='markers',
        marker=dict(
            size=6,
            color=data['depths'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Depth (m)", thickness=10, len=0.5)
        ),
        name='T-S Relationship',
        hovertemplate='<b>Salinity:</b> %{x:.2f} PSU<br><b>Temperature:</b> %{y:.1f}°C<extra></extra>'
    ))
    ts_fig.update_layout(
        title=f"T-S Diagram - {data['location']}",
        xaxis_title="Salinity (PSU)",
        yaxis_title="Temperature (°C)",
        xaxis=dict(gridcolor=data['colors']['grid']),
        yaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=300
    )
    
    # Density vs Depth
    density_fig = go.Figure()
    density_fig.add_trace(go.Scatter(
        x=data['density'],
        y=data['depths'],
        mode='lines+markers',
        line=dict(color='#10b981', width=3),
        marker=dict(size=4, color='#10b981'),
        name='Density',
        hovertemplate='<b>Depth:</b> %{y:.0f}m<br><b>Density:</b> %{x:.1f} kg/m³<extra></extra>'
    ))
    density_fig.update_layout(
        title=f"Density Profile - {data['location']}",
        xaxis_title="Density (kg/m³)",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed", gridcolor=data['colors']['grid']),
        xaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=300
    )
    
    return temp_fig, sal_fig, pressure_fig, ts_fig, density_fig

# Filter callbacks for sensors tab
@app.callback(
    [Output("filter-all", "style"),
     Output("filter-active", "style"),
     Output("filter-monitoring", "style"),
     Output("filter-inactive", "style")],
    [Input("filter-all", "n_clicks"),
     Input("filter-active", "n_clicks"),
     Input("filter-monitoring", "n_clicks"),
     Input("filter-inactive", "n_clicks")],
    prevent_initial_call=True
)
def update_filter_buttons(all_clicks, active_clicks, monitoring_clicks, inactive_clicks):
    """Update filter button styles based on selection"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    active_style = {
        "background": "var(--accent-primary)", "color": "var(--text-inverse)",
        "border": "none", "border-radius": "20px", "padding": "0.4rem 0.8rem",
        "cursor": "pointer", "margin": "0 0.25rem", "font-size": "0.8rem"
    }
    inactive_style = {
        "background": "var(--bg-secondary)", "color": "var(--text-primary)",
        "border": "1px solid var(--border-primary)", "border-radius": "20px", 
        "padding": "0.4rem 0.8rem", "cursor": "pointer", "margin": "0 0.25rem", "font-size": "0.8rem"
    }
    
    if button_id == "filter-all":
        return active_style, inactive_style, inactive_style, inactive_style
    elif button_id == "filter-active":
        return inactive_style, active_style, inactive_style, inactive_style
    elif button_id == "filter-monitoring":
        return inactive_style, inactive_style, active_style, inactive_style
    elif button_id == "filter-inactive":
        return inactive_style, inactive_style, inactive_style, active_style
    
    return active_style, inactive_style, inactive_style, inactive_style

@app.callback(
    Output("argo-data-table", "filter_query"),
    [Input("filter-all", "n_clicks"),
     Input("filter-active", "n_clicks"),
     Input("filter-monitoring", "n_clicks"),
     Input("filter-inactive", "n_clicks"),
     Input("sensor-quick-search", "value"),
     Input("clear-filters-btn", "n_clicks")],
    prevent_initial_call=True
)
def update_table_filters(all_clicks, active_clicks, monitoring_clicks, inactive_clicks, search_value, clear_clicks):
    """Update table filters based on button clicks and search"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle filter buttons
    if trigger_id in ["filter-all", "filter-active", "filter-monitoring", "filter-inactive", "clear-filters-btn"]:
        if trigger_id == "filter-active":
            return "{status} = 'Active'"
        elif trigger_id == "filter-monitoring":
            return "{status} = 'Monitoring'"
        elif trigger_id == "filter-inactive":
            return "{status} = 'Inactive'"
        else:  # filter-all or clear-filters-btn
            return ""
    
    # Handle search input
    elif trigger_id == "sensor-quick-search":
        if search_value and search_value.strip():
            # Create a complex filter for searching across multiple columns
            search_term = search_value.strip().lower()
            return f"{{argo_id}} contains '{search_term}' || {{status}} contains '{search_term}'"
    
    return ""

@app.callback(
    Output("sensor-quick-search", "value"),
    Input("clear-filters-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_search_input(n_clicks):
    """Clear the search input when clear filters is clicked"""
    return ""

app.layout = html.Div([
    # Main container
    html.Div([
        # Modern Glassmorphic Top Navigation
        html.Div([
            html.Div([
                # Logo with gradient animation
                html.Div([
                    html.I(className="fas fa-water", style={
                        "margin-right": "0.75rem", 
                        "font-size": "1.5rem",
                        "background": "var(--accent-gradient)",
                        "-webkit-background-clip": "text",
                        "-webkit-text-fill-color": "transparent",
                        "background-clip": "text"
                    }),
                    html.Span("FLOATCHAT DATA EXPLORER", style={
                        "background": "var(--accent-gradient)",
                        "-webkit-background-clip": "text",
                        "-webkit-text-fill-color": "transparent",
                        "background-clip": "text",
                        "font-weight": "700",
                        "font-size": "1.25rem"
                    })
                ], style={
                    "display": "flex", "align-items": "center"
                }, className="fade-in"),
                
                # Enhanced Search Bar with glassmorphism
                html.Div([
                    html.I(className="fas fa-search", style={
                        "margin-right": "0.75rem", 
                        "color": "var(--text-muted)",
                        "transition": "color 0.3s ease"
                    }),
                    dcc.Input(
                        id="nav-search",
                        placeholder="Search floats, regions, oceanographic data...",
                        type="text",
                        style={
                            "border": "none", 
                            "outline": "none", 
                            "background": "transparent",
                            "flex": "1", 
                            "font-size": "0.875rem",
                            "color": "var(--text-primary)"
                        }
                    )
                ], style={
                    "display": "flex", 
                    "align-items": "center", 
                    "background": "var(--bg-glass)",
                    "backdrop-filter": "blur(10px)",
                    "border": "1px solid var(--border-glass)",
                    "border-radius": "12px", 
                    "padding": "0.75rem 1rem", 
                    "width": "400px",
                    "margin-left": "2rem",
                    "transition": "all 0.3s ease",
                    "box-shadow": "var(--shadow-sm)"
                }, className="hover-lift fade-in"),
            ], style={"display": "flex", "align-items": "center"}),
            
            # Modern Right Controls
            html.Div([
                html.Div("🧪 Research Lab", style={
                    "background": "linear-gradient(135deg, #14b8a6, #0891b2)",
                    "color": "white", 
                    "padding": "0.5rem 1rem",
                    "border-radius": "20px", 
                    "font-size": "0.75rem", 
                    "font-weight": "600",
                    "box-shadow": "0 2px 10px rgba(20, 184, 166, 0.3)",
                    "transition": "all 0.3s ease"
                }, className="hover-lift"),
                
                # Animated Toggle Switch
                html.Div([
                    html.Div([
                        html.Div(className="toggle-knob")
                    ], className="toggle-switch", id="theme-toggle")
                ], style={"margin-left": "1rem"}, className="theme-toggle-btn"),
                
                # Profile Avatar with glow
                html.Div("🌊", style={
                    "width": "40px", 
                    "height": "40px", 
                    "background": "var(--accent-gradient)", 
                    "color": "var(--text-inverse)", 
                    "border-radius": "50%", 
                    "display": "flex", 
                    "align-items": "center", 
                    "justify-content": "center", 
                    "font-weight": "600",
                    "margin-left": "1rem",
                    "font-size": "1.2rem",
                    "cursor": "pointer",
                    "transition": "all 0.3s ease",
                    "box-shadow": "var(--shadow-sm)"
                }, className="hover-lift")
            ], style={"display": "flex", "align-items": "center"}),
        ], style={
            "height": "5rem", 
            "padding": "0 2rem", 
            "background": "var(--bg-card)",
            "backdrop-filter": "blur(20px)",
            "border-bottom": "1px solid var(--border-glass)",
            "display": "flex", 
            "align-items": "center",
            "justify-content": "space-between",
            "position": "relative",
            "z-index": "100",
            "box-shadow": "var(--shadow-md)"
        }, className="glass"),
        
        # Main Layout
        html.Div([
            # Modern Chat Sidebar with animations
            html.Div([
                # Enhanced Chat Header with gradient
                html.Div([
                    html.Div([
                        html.I(className="fas fa-robot", style={
                            "margin-right": "0.75rem", 
                            "font-size": "1.2rem",
                            "background": "linear-gradient(135deg, #667eea, #764ba2)",
                            "-webkit-background-clip": "text",
                            "-webkit-text-fill-color": "transparent",
                            "background-clip": "text"
                        }),
                        html.Span("AI Research Assistant", id="chat-title-text", style={
                            "font-weight": "600",
                            "background": "linear-gradient(135deg, #667eea, #764ba2)",
                            "-webkit-background-clip": "text",
                            "-webkit-text-fill-color": "transparent",
                            "background-clip": "text"
                        })
                    ], style={"display": "flex", "align-items": "center"}),
                    
                    html.Button([
                        html.I(id="collapse-icon", className="fas fa-chevron-left")
                    ], id="collapse-btn", style={
                        "background": "rgba(102, 126, 234, 0.1)",
                        "border": "1px solid rgba(102, 126, 234, 0.2)",
                        "color": "#667eea",
                        "cursor": "pointer", 
                        "padding": "0.5rem", 
                        "border-radius": "8px",
                        "transition": "all 0.3s ease"
                    }, className="hover-lift"),
                ], style={
                    "padding": "1.5rem 1rem", 
                    "background": "rgba(255, 255, 255, 0.95)",
                    "backdrop-filter": "blur(10px)",
                    "border-bottom": "1px solid rgba(255, 255, 255, 0.2)", 
                    "display": "flex", 
                    "align-items": "center", 
                    "justify-content": "space-between"
                }, className="glass"),
                
                # Enhanced Chat Messages with card bubbles
                html.Div([
                    # User message with modern bubble
                    html.Div([
                        html.Div("🌊 Show me temperature profiles for the Indian Ocean", style={
                            "background": "linear-gradient(135deg, #667eea, #764ba2)",
                            "color": "white", 
                            "border-radius": "18px 18px 4px 18px",
                            "padding": "1rem 1.25rem", 
                            "margin-left": "2rem", 
                            "margin-bottom": "1rem",
                            "box-shadow": "0 4px 15px rgba(102, 126, 234, 0.3)",
                            "font-weight": "500"
                        })
                    ], className="slide-in-right"),
                    
                    # AI response with enhanced styling
                    html.Div([
                        html.Div([
                            html.Div("🔍 I found 1,247 temperature profiles in the Indian Ocean region. The data shows temperatures ranging from 2°C to 28°C across different depths.", style={
                                "line-height": "1.6"
                            }),
                            html.Div([
                                html.I(className="fas fa-check-circle", style={"margin-right": "0.5rem", "color": "#10b981"}),
                                "Plotted recent profiles on interactive map"
                            ], style={
                                "margin-top": "0.75rem", 
                                "font-size": "0.875rem", 
                                "color": "#10b981",
                                "display": "flex",
                                "align-items": "center",
                                "font-weight": "500"
                            })
                        ], style={
                            "background": "rgba(255, 255, 255, 0.95)",
                            "backdrop-filter": "blur(10px)",
                            "border": "1px solid rgba(255, 255, 255, 0.3)",
                            "border-radius": "18px 18px 18px 4px",
                            "padding": "1rem 1.25rem", 
                            "margin-right": "2rem",
                            "box-shadow": "0 4px 20px rgba(0, 0, 0, 0.08)"
                        }, className="glass-card")
                    ], className="slide-in-left"),
                    
                    # Typing indicator (hidden by default)
                    html.Div([
                        html.Div([
                            html.Span("AI is thinking"),
                            html.Div([
                                html.Span(className="typing-dot"),
                                html.Span(className="typing-dot"),
                                html.Span(className="typing-dot")
                            ], style={"margin-left": "0.5rem", "display": "inline-flex"})
                        ], style={
                            "background": "var(--bg-card)",
                            "border-radius": "18px 18px 18px 4px",
                            "padding": "0.75rem 1rem",
                            "margin-right": "2rem",
                            "display": "flex",
                            "align-items": "center",
                            "font-size": "0.875rem",
                            "color": "var(--text-muted)"
                        })
                    ], id="typing-indicator", style={"display": "none"})
                ], id="chat-messages", style={
                    "flex": "1", 
                    "overflow-y": "auto", 
                    "padding": "1rem",
                    "background": "var(--bg-gradient)"
                }),
                
                # Modern Quick Actions with pill buttons
                html.Div([
                    html.Div([
                        html.Button([
                            html.I(className=action["icon"], style={
                                "margin-right": "0.5rem",
                                "color": "white"
                            }),
                            html.Span(action["text"], style={"font-weight": "500"})
                        ], id={"type": "quick-action", "index": i}, style={
                            "background": "linear-gradient(135deg, #667eea, #764ba2)",
                            "border": "none",
                            "border-radius": "25px",
                            "padding": "0.75rem 1rem", 
                            "font-size": "0.8rem", 
                            "cursor": "pointer",
                            "display": "flex", 
                            "align-items": "center", 
                            "margin-bottom": "0.75rem",
                            "color": "white",
                            "transition": "all 0.3s ease",
                            "box-shadow": "0 2px 10px rgba(102, 126, 234, 0.3)"
                        }, className="pill-button hover-lift") 
                        for i, action in enumerate(quick_actions)
                    ], style={
                        "display": "grid", 
                        "grid-template-columns": "1fr 1fr", 
                        "gap": "0.75rem", 
                        "margin-bottom": "1.5rem"
                    }),
                    
                    dcc.Textarea(
                        id="chat-input",
                        placeholder="Ask about ocean data, request visualizations, or write SQL queries... (Enter to send, Shift+Enter for new line)",
                        style={
                            "background": "var(--bg-primary)", 
                            "border": "1px solid var(--border-primary)", 
                            "border-radius": "0.5rem",
                            "padding": "0.75rem", 
                            "resize": "vertical", 
                            "min-height": "80px", 
                            "width": "100%",
                            "color": "var(--text-primary)"
                        }
                    ),
                    html.Div([
                        html.Div([
                            html.Label([
                                dcc.Checklist(
                                    id="sql-mode",
                                    options=[{"label": "SQL Mode", "value": "sql"}],
                                    value=[]
                                )
                            ], style={"font-size": "0.75rem", "color": "var(--text-muted)"}),
                            html.Div([
                                html.Span("💡 ", style={"margin-right": "0.25rem"}),
                                html.Span("Enter", style={
                                    "background": "var(--bg-secondary)", 
                                    "padding": "0.1rem 0.3rem", 
                                    "border-radius": "0.25rem", 
                                    "font-size": "0.65rem",
                                    "margin-right": "0.25rem"
                                }),
                                html.Span("to send • ", style={"font-size": "0.65rem"}),
                                html.Span("Shift+Enter", style={
                                    "background": "var(--bg-secondary)", 
                                    "padding": "0.1rem 0.3rem", 
                                    "border-radius": "0.25rem", 
                                    "font-size": "0.65rem",
                                    "margin-right": "0.25rem"
                                }),
                                html.Span("for new line", style={"font-size": "0.65rem"})
                            ], style={
                                "font-size": "0.65rem", 
                                "color": "var(--text-muted)", 
                                "margin-top": "0.25rem"
                            })
                        ], style={"display": "flex", "flex-direction": "column"}),
                        html.Button([
                            html.I(className="fas fa-paper-plane", style={"margin-right": "0.25rem"}),
                            "Send"
                        ], id="send-btn", style={
                            "background": "var(--accent-primary)", 
                            "color": "var(--text-inverse)", 
                            "border": "none",
                            "border-radius": "0.5rem", 
                            "padding": "0.5rem 1rem", 
                            "cursor": "pointer",
                            "font-weight": "500", 
                            "display": "flex", 
                            "align-items": "center",
                            "transition": "all 0.3s ease"
                        }, className="hover-lift")
                    ], style={
                        "display": "flex", "align-items": "center", "justify-content": "space-between", 
                        "margin-top": "0.5rem"
                    })
                ], style={"padding": "1rem", "border-top": "1px solid var(--border-primary)"}),
                # Resize handle for chat sidebar
                html.Div(id="resize-handle", className="resize-handle"),
                
                # Width indicator
                html.Div(id="width-indicator", className="width-indicator", children="350px")
            ], id="chat-sidebar", className="resizable-sidebar", style={
                "width": "350px", 
                "background": "var(--bg-secondary)", 
                "border-right": "1px solid var(--border-primary)",
                "display": "flex", 
                "flex-direction": "column", 
                "transition": "all 0.3s ease"
            }),
            
            # Content Area
            html.Div([
                # Content Tabs
                html.Div([
                    html.Button([
                        html.I(className="fas fa-map", style={"margin-right": "0.5rem"}),
                        "Map View"
                    ], id="map-tab", style={
                        "background": "none", "border": "none", "padding": "0.75rem 1rem",
                        "color": "var(--accent-primary)", "cursor": "pointer", "border-bottom": "2px solid var(--accent-primary)",
                        "display": "flex", "align-items": "center", "transition": "all 0.3s ease"
                    }),
                    html.Button([
                        html.I(className="fas fa-sensor", style={"margin-right": "0.5rem"}),
                        "Sensors"
                    ], id="analysis-tab", style={
                        "background": "none", "border": "none", "padding": "0.75rem 1rem",
                        "color": "var(--text-muted)", "cursor": "pointer", "border-bottom": "2px solid transparent",
                        "display": "flex", "align-items": "center", "transition": "all 0.3s ease"
                    }),
                ], style={
                    "background": "var(--bg-secondary)", 
                    "border-bottom": "1px solid var(--border-primary)", 
                    "padding": "0 1rem", 
                    "display": "flex", 
                    "align-items": "center", 
                    "gap": "0.5rem"
                }),
                
                # Main Content
                html.Div([
                    # Enhanced Map Section with full container usage
                    html.Div([
                        dcc.Graph(
                            id="main-map",
                            figure=create_float_map(),  # Load map immediately
                            style={
                                "height": "100%", 
                                "width": "100%",
                                "border-radius": "0px",  # Remove border radius for full fill
                                "overflow": "hidden"
                            },
                            config={
                                "displayModeBar": True,
                                "displaylogo": False,
                                "modeBarButtonsToRemove": [
                                    "pan2d", "lasso2d", "select2d", "autoScale2d", 
                                    "resetScale2d", "hoverClosestCartesian", "hoverCompareCartesian"
                                ],
                                "modeBarButtonsToAdd": [],
                                "doubleClick": "reset+autosize",
                                "scrollZoom": True,
                                "showTips": False,
                                # Enhanced interactivity
                                "responsive": True,
                                "toImageButtonOptions": {
                                    "format": "png",
                                    "filename": "floatchat_map",
                                    "height": 600,
                                    "width": 1000,
                                    "scale": 2
                                }
                            }
                        ),
                        
                        # Modern Circular Map Controls with hover glow
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-undo", style={"font-size": "1rem"})
                            ], id="reset-map-btn", title="Reset Map View", style={
                                "background": "rgba(255, 255, 255, 0.95)",
                                "backdrop-filter": "blur(10px)",
                                "border": "1px solid rgba(255, 255, 255, 0.3)",
                                "border-radius": "50%",  # Circular
                                "width": "48px",
                                "height": "48px",
                                "display": "flex",
                                "align-items": "center",
                                "justify-content": "center",
                                "cursor": "pointer",
                                "box-shadow": "0 4px 15px rgba(0, 0, 0, 0.1)",
                                "margin-bottom": "0.75rem",
                                "transition": "all 0.3s ease",
                                "color": "#667eea"
                            }, className="map-btn"),
                            html.Button([
                                html.I(className="fas fa-layer-group", style={"font-size": "1rem"})
                            ], id="toggle-layers-btn", title="Toggle Layers", style={
                                "background": "rgba(255, 255, 255, 0.95)",
                                "backdrop-filter": "blur(10px)",
                                "border": "1px solid rgba(255, 255, 255, 0.3)",
                                "border-radius": "50%",  # Circular
                                "width": "48px",
                                "height": "48px",
                                "display": "flex",
                                "align-items": "center",
                                "justify-content": "center",
                                "cursor": "pointer",
                                "box-shadow": "0 4px 15px rgba(0, 0, 0, 0.1)",
                                "margin-bottom": "0.75rem",
                                "transition": "all 0.3s ease",
                                "color": "#667eea"
                            }, className="map-btn"),
                            html.Button([
                                html.I(className="fas fa-expand", style={"font-size": "1rem"})
                            ], id="fullscreen-btn", title="Fullscreen", style={
                                "background": "rgba(255, 255, 255, 0.95)",
                                "backdrop-filter": "blur(10px)",
                                "border": "1px solid rgba(255, 255, 255, 0.3)",
                                "border-radius": "50%",  # Circular
                                "width": "48px",
                                "height": "48px",
                                "display": "flex",
                                "align-items": "center",
                                "justify-content": "center",
                                "cursor": "pointer",
                                "box-shadow": "0 4px 15px rgba(0, 0, 0, 0.1)",
                                "transition": "all 0.3s ease",
                                "color": "#667eea"
                            }, className="map-btn")
                        ], style={
                            "position": "absolute", 
                            "top": "1.5rem", 
                            "right": "1.5rem", 
                            "z-index": "1000",
                            "display": "flex", 
                            "flex-direction": "column"
                        }),
                    ], id="map-content", style={
                        "flex": "1", 
                        "position": "relative", 
                        "background": "transparent",
                        "border-radius": "0px",
                        "overflow": "hidden"
                    }),
                    
                    # Analysis Tab Content (hidden by default)
                    html.Div([
                        # Analysis Header
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-sensor", style={
                                    "margin-right": "0.75rem",
                                    "background": "var(--accent-gradient)",
                                    "-webkit-background-clip": "text",
                                    "-webkit-text-fill-color": "transparent",
                                    "background-clip": "text",
                                    "font-size": "1.1rem"
                                }),
                                html.Span("📡 Ocean Sensors & Data", style={
                                    "font-weight": "600",
                                    "background": "var(--accent-gradient)",
                                    "-webkit-background-clip": "text",
                                    "-webkit-text-fill-color": "transparent",
                                    "background-clip": "text"
                                })
                            ], style={"display": "flex", "align-items": "center"}),
                            
                            # Global Search Input
                            html.Div([
                                html.I(className="fas fa-search", style={
                                    "margin-right": "0.5rem", 
                                    "color": "var(--text-muted)"
                                }),
                                dcc.Input(
                                    id="global-search",
                                    placeholder="Search all ARGO data...",
                                    type="text",
                                    style={
                                        "border": "none",
                                        "outline": "none",
                                        "background": "transparent",
                                        "font-size": "0.8rem",
                                        "width": "200px",
                                        "color": "var(--text-primary)"
                                    }
                                )
                            ], style={
                                "display": "flex",
                                "align-items": "center",
                                "background": "var(--bg-glass)",
                                "backdrop-filter": "blur(10px)",
                                "border": "1px solid var(--border-glass)",
                                "border-radius": "8px",
                                "padding": "0.5rem",
                                "transition": "all 0.3s ease"
                            }, className="hover-lift")
                        ], style={
                            "padding": "1.5rem 1rem", 
                            "background": "var(--bg-card)",
                            "backdrop-filter": "blur(10px)",
                            "border-bottom": "1px solid var(--border-glass)",
                            "display": "flex", 
                            "align-items": "center", 
                            "justify-content": "space-between"
                        }, className="glass"),
                        
                        # Interactive Data Table with Enhanced Search & Sorting
                        html.Div([
                            # Quick Filters and Search
                            html.Div([
                                html.Div([
                                    html.Label("🔍 Quick Search:", style={"font-weight": "600", "margin-right": "1rem", "color": "var(--text-primary)"}),
                                    dcc.Input(
                                        id="sensor-quick-search",
                                        placeholder="Search floats by ID, location, or status...",
                                        type="text",
                                        style={
                                            "padding": "0.5rem",
                                            "border": "1px solid var(--border-primary)",
                                            "border-radius": "6px",
                                            "background": "var(--bg-primary)",
                                            "color": "var(--text-primary)",
                                            "flex": "1",
                                            "margin-right": "1rem"
                                        }
                                    ),
                                    html.Button([
                                        html.I(className="fas fa-filter", style={"margin-right": "0.5rem"}),
                                        "Clear Filters"
                                    ], id="clear-filters-btn", style={
                                        "background": "var(--accent-primary)",
                                        "color": "var(--text-inverse)",
                                        "border": "none",
                                        "border-radius": "6px",
                                        "padding": "0.5rem 1rem",
                                        "cursor": "pointer",
                                        "font-weight": "500"
                                    })
                                ], style={"display": "flex", "align-items": "center", "margin-bottom": "1rem"}),
                                
                                # Status Filter Buttons
                                html.Div([
                                    html.Button("All", id="filter-all", style={
                                        "background": "var(--accent-primary)", "color": "var(--text-inverse)",
                                        "border": "none", "border-radius": "20px", "padding": "0.4rem 0.8rem",
                                        "cursor": "pointer", "margin": "0 0.25rem", "font-size": "0.8rem"
                                    }),
                                    html.Button("Active", id="filter-active", style={
                                        "background": "var(--bg-secondary)", "color": "var(--text-primary)",
                                        "border": "1px solid var(--border-primary)", "border-radius": "20px", 
                                        "padding": "0.4rem 0.8rem", "cursor": "pointer", "margin": "0 0.25rem", "font-size": "0.8rem"
                                    }),
                                    html.Button("Monitoring", id="filter-monitoring", style={
                                        "background": "var(--bg-secondary)", "color": "var(--text-primary)",
                                        "border": "1px solid var(--border-primary)", "border-radius": "20px", 
                                        "padding": "0.4rem 0.8rem", "cursor": "pointer", "margin": "0 0.25rem", "font-size": "0.8rem"
                                    }),
                                    html.Button("Inactive", id="filter-inactive", style={
                                        "background": "var(--bg-secondary)", "color": "var(--text-primary)",
                                        "border": "1px solid var(--border-primary)", "border-radius": "20px", 
                                        "padding": "0.4rem 0.8rem", "cursor": "pointer", "margin": "0 0.25rem", "font-size": "0.8rem"
                                    })
                                ], style={"margin-bottom": "1rem"})
                            ], style={"padding": "1rem", "background": "var(--bg-card)", "border-radius": "8px", "margin-bottom": "1rem"}),
                            
                            dash_table.DataTable(
                                id="argo-data-table",
                                columns=[
                                    {"name": "Sensor ID", "id": "argo_id", "type": "text"},
                                    {"name": "Latitude", "id": "latitude", "type": "numeric", "format": {"specifier": ".3f"}},
                                    {"name": "Longitude", "id": "longitude", "type": "numeric", "format": {"specifier": ".3f"}},
                                    {"name": "🌡️ Temp (°C)", "id": "temperature", "type": "numeric", "format": {"specifier": ".1f"}},
                                    {"name": "🧂 Salinity (PSU)", "id": "salinity", "type": "numeric", "format": {"specifier": ".2f"}},
                                    {"name": "📏 Depth (m)", "id": "depth", "type": "numeric", "format": {"specifier": ".0f"}},
                                    {"name": "📅 Last Update", "id": "date", "type": "text"},
                                    {"name": "📊 Status", "id": "status", "type": "text"}
                                ],
                                data=[],  # Will be populated by callback
                                sort_action="native",
                                sort_mode="multi",
                                filter_action="native",
                                row_selectable="single",
                                selected_rows=[],
                                page_action="native",
                                page_current=0,
                                page_size=20,
                                style_table={
                                    "height": "calc(100vh - 400px)",
                                    "overflowY": "auto",
                                    "border-radius": "8px"
                                },
                                style_header={
                                    "backgroundColor": "var(--bg-secondary)",
                                    "color": "var(--text-primary)",
                                    "fontWeight": "700",
                                    "border": "1px solid var(--border-primary)",
                                    "textAlign": "center",
                                    "fontSize": "0.9rem"
                                },
                                style_cell={
                                    "backgroundColor": "var(--bg-primary)",
                                    "color": "var(--text-primary)",
                                    "border": "1px solid var(--border-primary)",
                                    "textAlign": "center",
                                    "padding": "12px",
                                    "fontFamily": "Inter, sans-serif",
                                    "fontSize": "0.85rem"
                                },
                                style_data_conditional=[
                                    {
                                        "if": {"row_index": "odd"},
                                        "backgroundColor": "var(--bg-secondary)"
                                    },
                                    {
                                        "if": {"state": "selected"},
                                        "backgroundColor": "var(--accent-primary)",
                                        "color": "var(--text-inverse)",
                                        "border": "2px solid var(--accent-primary)"
                                    },
                                    {
                                        "if": {"column_id": "status", "filter_query": "{status} = Active"},
                                        "backgroundColor": "rgba(16, 185, 129, 0.1)",
                                        "color": "#10b981"
                                    },
                                    {
                                        "if": {"column_id": "status", "filter_query": "{status} = Inactive"},
                                        "backgroundColor": "rgba(239, 68, 68, 0.1)",
                                        "color": "#ef4444"
                                    },
                                    {
                                        "if": {"column_id": "status", "filter_query": "{status} = Monitoring"},
                                        "backgroundColor": "rgba(245, 158, 11, 0.1)",
                                        "color": "#f59e0b"
                                    }
                                ],
                                css=[{
                                    "selector": ".dash-table-tooltip",
                                    "rule": "background-color: var(--bg-card); color: var(--text-primary); border: 1px solid var(--border-primary);"
                                }]
                            )
                        ], style={
                            "padding": "1rem",
                            "background": "var(--bg-gradient)",
                            "flex": "1"
                        })
                    ], id="analysis-content", style={
                        "flex": "1",
                        "display": "none",  # Hidden by default
                        "flex-direction": "column",
                        "overflow": "hidden"
                    }),
                    
                    # Enhanced Scrollable Visualization Panel
                    html.Div([
                        # Modern Viz Header with Search
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-chart-area", style={
                                    "margin-right": "0.75rem",
                                    "background": "var(--accent-gradient)",
                                    "-webkit-background-clip": "text",
                                    "-webkit-text-fill-color": "transparent",
                                    "background-clip": "text",
                                    "font-size": "1.1rem"
                                }),
                                html.Span("ARGO Analytics", style={
                                    "font-weight": "600",
                                    "background": "var(--accent-gradient)",
                                    "-webkit-background-clip": "text",
                                    "-webkit-text-fill-color": "transparent",
                                    "background-clip": "text"
                                })
                            ], style={"display": "flex", "align-items": "center"}),
                            
                            # ARGO Search Input
                            html.Div([
                                html.I(className="fas fa-search", style={
                                    "margin-right": "0.5rem", 
                                    "color": "var(--text-muted)"
                                }),
                                dcc.Input(
                                    id="argo-search",
                                    placeholder="Search ARGO ID...",
                                    type="text",
                                    style={
                                        "border": "none",
                                        "outline": "none",
                                        "background": "transparent",
                                        "font-size": "0.8rem",
                                        "width": "120px",
                                        "color": "var(--text-primary)"
                                    }
                                )
                            ], style={
                                "display": "flex",
                                "align-items": "center",
                                "background": "var(--bg-glass)",
                                "backdrop-filter": "blur(10px)",
                                "border": "1px solid var(--border-glass)",
                                "border-radius": "8px",
                                "padding": "0.5rem",
                                "transition": "all 0.3s ease"
                            }, className="hover-lift")
                        ], style={
                            "padding": "1.5rem 1rem", 
                            "background": "var(--bg-card)",
                            "backdrop-filter": "blur(10px)",
                            "border-bottom": "1px solid var(--border-glass)",
                            "display": "flex", 
                            "align-items": "center", 
                            "justify-content": "space-between"
                        }, className="glass"),
                        
                        # Scrollable Multi-Plot Container
                        html.Div([
                            # Selected Float Info Card
                            html.Div([
                                html.Div("🎯 Select an ARGO float to view comprehensive analysis", 
                                        id="selected-float-info",
                                        style={
                                            "text-align": "center",
                                            "color": "var(--text-muted)",
                                            "font-style": "italic",
                                            "padding": "2rem"
                                        })
                            ], style={
                                "background": "var(--bg-card)",
                                "border-radius": "12px",
                                "margin": "1rem",
                                "box-shadow": "var(--shadow-md)",
                                "border": "1px solid var(--border-primary)"
                            }, className="modern-card", id="float-info-card"),
                            
                            # Multiple Plot Container
                            html.Div([
                                # Temperature vs Depth Plot
                                html.Div([
                                    html.H4("🌡️ Temperature Profile", style={
                                        "margin": "0 0 1rem 0",
                                        "color": "var(--text-primary)",
                                        "font-size": "1rem"
                                    }),
                                    dcc.Graph(
                                        id="temp-depth-plot",
                                        style={"height": "300px"},
                                        config={
                                            "displayModeBar": True,
                                            "displaylogo": False,
                                            "modeBarButtonsToRemove": ["pan2d", "lasso2d"]
                                        }
                                    )
                                ], style={
                                    "background": "var(--bg-card)",
                                    "border-radius": "12px",
                                    "padding": "1.5rem",
                                    "margin-bottom": "1.5rem",
                                    "box-shadow": "var(--shadow-md)",
                                    "border": "1px solid var(--border-primary)"
                                }, className="modern-card fade-in", id="temp-plot-card"),
                                
                                # Salinity vs Depth Plot
                                html.Div([
                                    html.H4("🧂 Salinity Profile", style={
                                        "margin": "0 0 1rem 0",
                                        "color": "var(--text-primary)",
                                        "font-size": "1rem"
                                    }),
                                    dcc.Graph(
                                        id="sal-depth-plot",
                                        style={"height": "300px"},
                                        config={
                                            "displayModeBar": True,
                                            "displaylogo": False,
                                            "modeBarButtonsToRemove": ["pan2d", "lasso2d"]
                                        }
                                    )
                                ], style={
                                    "background": "var(--bg-card)",
                                    "border-radius": "12px",
                                    "padding": "1.5rem",
                                    "margin-bottom": "1.5rem",
                                    "box-shadow": "var(--shadow-md)",
                                    "border": "1px solid var(--border-primary)"
                                }, className="modern-card fade-in", id="sal-plot-card"),
                                
                                # T-S Diagram
                                html.Div([
                                    html.H4("🌊 Temperature-Salinity Diagram", style={
                                        "margin": "0 0 1rem 0",
                                        "color": "var(--text-primary)",
                                        "font-size": "1rem"
                                    }),
                                    dcc.Graph(
                                        id="ts-diagram-plot",
                                        style={"height": "300px"},
                                        config={
                                            "displayModeBar": True,
                                            "displaylogo": False,
                                            "modeBarButtonsToRemove": ["pan2d", "lasso2d"]
                                        }
                                    )
                                ], style={
                                    "background": "var(--bg-card)",
                                    "border-radius": "12px",
                                    "padding": "1.5rem",
                                    "margin-bottom": "1.5rem",
                                    "box-shadow": "var(--shadow-md)",
                                    "border": "1px solid var(--border-primary)"
                                }, className="modern-card fade-in", id="ts-plot-card"),
                                
                                # Density Profile
                                html.Div([
                                    html.H4("⚖️ Density Profile", style={
                                        "margin": "0 0 1rem 0",
                                        "color": "var(--text-primary)",
                                        "font-size": "1rem"
                                    }),
                                    dcc.Graph(
                                        id="density-plot",
                                        style={"height": "300px"},
                                        config={
                                            "displayModeBar": True,
                                            "displaylogo": False,
                                            "modeBarButtonsToRemove": ["pan2d", "lasso2d"]
                                        }
                                    )
                                ], style={
                                    "background": "var(--bg-card)",
                                    "border-radius": "12px",
                                    "padding": "1.5rem",
                                    "margin-bottom": "1.5rem",
                                    "box-shadow": "var(--shadow-md)",
                                    "border": "1px solid var(--border-primary)"
                                }, className="glass-card fade-in", id="density-plot-card")
                            ], id="plots-container", style={"padding": "0 1rem"})
                        ], style={
                            "flex": "1", 
                            "overflow-y": "auto", 
                            "max-height": "calc(100vh - 200px)",
                            "background": "var(--bg-gradient)"
                        }),
                        
                        # Modern Export Actions
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-file-csv", style={"margin-right": "0.5rem"}),
                                "Export CSV"
                            ], id="export-csv-btn", style={
                                "flex": "1", 
                                "background": "linear-gradient(135deg, #10b981, #059669)",
                                "color": "white",
                                "border": "none",
                                "border-radius": "10px", 
                                "padding": "0.75rem", 
                                "cursor": "pointer",
                                "font-size": "0.8rem", 
                                "font-weight": "500",
                                "display": "flex", 
                                "align-items": "center",
                                "justify-content": "center",
                                "transition": "all 0.3s ease",
                                "box-shadow": "0 2px 10px rgba(16, 185, 129, 0.3)"
                            }, className="hover-lift"),
                            
                            html.Button([
                                html.I(className="fas fa-image", style={"margin-right": "0.5rem"}),
                                "Export PNG"
                            ], id="export-png-btn", style={
                                "flex": "1", 
                                "background": "linear-gradient(135deg, #3b82f6, #1d4ed8)",
                                "color": "white",
                                "border": "none",
                                "border-radius": "10px", 
                                "padding": "0.75rem", 
                                "cursor": "pointer",
                                "font-size": "0.8rem", 
                                "font-weight": "500",
                                "display": "flex", 
                                "align-items": "center",
                                "justify-content": "center", 
                                "margin-left": "0.75rem",
                                "transition": "all 0.3s ease",
                                "box-shadow": "0 2px 10px rgba(59, 130, 246, 0.3)"
                            }, className="hover-lift"),
                            
                            html.Button([
                                html.I(className="fas fa-share-nodes", style={"margin-right": "0.5rem"}),
                                "Share Link"
                            ], id="share-btn", style={
                                "flex": "1", 
                                "background": "linear-gradient(135deg, #8b5cf6, #7c3aed)",
                                "color": "white",
                                "border": "none",
                                "border-radius": "10px", 
                                "padding": "0.75rem", 
                                "cursor": "pointer",
                                "font-size": "0.8rem", 
                                "font-weight": "500",
                                "display": "flex", 
                                "align-items": "center",
                                "justify-content": "center", 
                                "margin-left": "0.75rem",
                                "transition": "all 0.3s ease",
                                "box-shadow": "0 2px 10px rgba(139, 92, 246, 0.3)"
                            }, className="hover-lift"),
                            
                            # Download components (hidden)
                            dcc.Download(id="download-csv"),
                            dcc.Download(id="download-png")
                        ], style={
                            "padding": "1rem", 
                            "border-top": "1px solid var(--border-glass)", 
                            "background": "var(--bg-card)",
                            "backdrop-filter": "blur(10px)",
                            "display": "flex", 
                            "gap": "0.75rem"
                        })
                    ], style={
                        "width": "400px", 
                        "background": "var(--bg-gradient)", 
                        "border-left": "1px solid var(--border-primary)",
                        "display": "flex", 
                        "flex-direction": "column"
                    })
                ], style={"flex": "1", "display": "flex", "overflow": "hidden"}),
            ], style={"flex": "1", "display": "flex", "flex-direction": "column", "overflow": "hidden"}),
        ], style={"display": "flex", "flex": "1", "overflow": "hidden"}),
    ], id="dashboard-container", style={
        "height": "100vh", 
        "background": "var(--bg-primary)", 
        "color": "var(--text-primary)", 
        "display": "flex", 
        "flex-direction": "column", 
        "font-family": "'Inter', sans-serif",
        "transition": "all 0.3s ease"
    }),
    
    # Floating Chat Reopen Button (hidden by default)
    html.Button([
        html.I(className="fas fa-comments", style={"font-size": "1.2rem"})
    ], id="floating-chat-btn", style={
        "position": "fixed",
        "bottom": "2rem",
        "left": "2rem",
        "width": "60px",
        "height": "60px",
        "border-radius": "50%",
        "background": "var(--accent-gradient)",
        "border": "none",
        "color": "var(--text-inverse)",
        "cursor": "pointer",
        "display": "none",  # Hidden by default
        "align-items": "center",
        "justify-content": "center",
        "box-shadow": "var(--shadow-lg)",
        "z-index": "1000",
        "transition": "all 0.3s ease"
    }, className="hover-lift floating-pulse", title="Open Chat"),
    
    # Hidden stores for state management
    dcc.Store(id="theme-store", data="light"),
    # Dummy element for scroll callback
    html.Div(id="dummy-scroll", style={"display": "none"})])

# Callbacks for interactivity

# Simple theme toggle using data-theme attribute
# @app.callback(
#     [Output("dashboard-container", "data-theme"),
#      Output("theme-store", "data"),
#      Output("main-map", "figure", allow_duplicate=True)],
#     Input("theme-toggle", "n_clicks"),
#     State("theme-store", "data"),
#     prevent_initial_call=True 
# )
@app.callback(
    [
        Output("dashboard-container", "data-theme"),
        Output("theme-store", "data"),
        Output("main-map", "figure", allow_duplicate=True)
    ],
    [Input("theme-toggle", "n_clicks")],
    [State("theme-store", "data")],
    prevent_initial_call=True
)
def toggle_theme(n_clicks, current_theme):
    is_dark = (n_clicks or 0) % 2 == 1
    theme = "dark" if is_dark else "light"
    map_fig = create_interactive_map(dark_mode=is_dark)
    return theme, theme, map_fig

# Enhanced sidebar collapse functionality with floating button
@app.callback(
    [Output("chat-sidebar", "style"),
     Output("collapse-icon", "className"),
     Output("floating-chat-btn", "style")],
    [Input("collapse-btn", "n_clicks"),
     Input("floating-chat-btn", "n_clicks")],
    [State("chat-sidebar", "style")],
    prevent_initial_call=True
)
def toggle_sidebar(collapse_clicks, float_clicks, current_style):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Determine current state and theme
    is_collapsed = current_style.get("width") == "0px" or current_style.get("display") == "none"
    is_dark_theme = "#1e293b" in str(current_style.get("background", ""))
    
    if trigger_id == "collapse-btn" or (trigger_id == "floating-chat-btn" and is_collapsed):
        if not is_collapsed:
            # Collapse sidebar - fully hide it
            sidebar_style = {
                "width": "0px", 
                "background": "transparent", 
                "border-right": "none",
                "display": "none",
                "flex-direction": "column", 
                "transition": "all 0.4s ease",
                "overflow": "hidden"
            }
            collapse_icon = "fas fa-chevron-right"
            
            # Show floating button with animation
            float_style = {
                "position": "fixed",
                "bottom": "2rem",
                "left": "2rem",
                "width": "60px",
                "height": "60px",
                "border-radius": "50%",
                "background": "linear-gradient(135deg, #667eea, #764ba2)",
                "border": "none",
                "color": "white",
                "cursor": "pointer",
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "box-shadow": "0 8px 25px rgba(102, 126, 234, 0.4)",
                "z-index": "1000",
                "transition": "all 0.3s ease",
                "animation": "bounceIn 0.6s ease-out, floatingPulse 2s ease-in-out 1s infinite"
            }
        else:
            # Expand sidebar - show it with slide animation and theme-aware styling
            if is_dark_theme:
                sidebar_style = {
                    "width": "350px", 
                    "background": "linear-gradient(180deg, #1e293b 0%, #334155 100%)", 
                    "border-right": "1px solid #475569",
                    "display": "flex", 
                    "flex-direction": "column", 
                    "transition": "all 0.4s ease",
                    "color": "#f1f5f9",
                    "box-shadow": "2px 0 10px rgba(0, 0, 0, 0.3)",
                    "animation": "slideInFromLeft 0.4s ease-out"
                }
            else:
                sidebar_style = {
                    "width": "350px", 
                    "background": "linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)", 
                    "border-right": "1px solid #e2e8f0",
                    "display": "flex", 
                    "flex-direction": "column", 
                    "transition": "all 0.4s ease",
                    "color": "#0f172a",
                    "box-shadow": "2px 0 10px rgba(0, 0, 0, 0.05)",
                    "animation": "slideInFromLeft 0.4s ease-out"
                }
            
            collapse_icon = "fas fa-chevron-left"
            
            # Hide floating button
            float_style = {
                "position": "fixed",
                "bottom": "2rem",
                "left": "2rem",
                "width": "60px",
                "height": "60px",
                "border-radius": "50%",
                "background": "linear-gradient(135deg, #667eea, #764ba2)",
                "border": "none",
                "color": "white",
                "cursor": "pointer",
                "display": "none",
                "align-items": "center",
                "justify-content": "center",
                "box-shadow": "0 8px 25px rgba(102, 126, 234, 0.4)",
                "z-index": "1000",
                "transition": "all 0.3s ease"
            }
        
        return sidebar_style, collapse_icon, float_style
    
    return dash.no_update, dash.no_update, dash.no_update

# Update all plots when theme changes
@app.callback(
    [Output("temp-depth-plot", "figure", allow_duplicate=True),
     Output("sal-depth-plot", "figure", allow_duplicate=True),
     Output("ts-diagram-plot", "figure", allow_duplicate=True),
     Output("density-plot", "figure", allow_duplicate=True)],
    Input("theme-store", "data"),
    prevent_initial_call=True
)
def update_plots_theme(theme):
    """Update all plots when theme changes"""
    # Create empty figures with theme-appropriate styling
    empty_fig = go.Figure()
    
    # Theme colors
    is_dark = theme == "dark"
    bg_color = '#1e293b' if is_dark else 'white'
    text_color = '#f1f5f9' if is_dark else '#0f172a'
    grid_color = '#475569' if is_dark else '#e5e7eb'
    
    empty_fig.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(color=text_color),
        xaxis=dict(gridcolor=grid_color, color=text_color),
        yaxis=dict(gridcolor=grid_color, color=text_color),
        margin=dict(l=50, r=20, t=50, b=40),
        height=280
    )
    
    return empty_fig, empty_fig, empty_fig, empty_fig

# Segmented control functionality for X-axis
@app.callback(
    [Output("x-temp", "style"), Output("x-sal", "style"), Output("x-pres", "style")],
    [Input("x-temp", "n_clicks"), Input("x-sal", "n_clicks"), Input("x-pres", "n_clicks")],
    prevent_initial_call=True
)
def update_x_axis_selection(temp_clicks, sal_clicks, pres_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    active_style = {
        "flex": "1", "background": "#0ea5e9", "color": "white", "border": "none",
        "padding": "0.5rem 0.75rem", "cursor": "pointer", "font-size": "0.75rem"
    }
    inactive_style = {
        "flex": "1", "background": "white", "color": "#64748b", "border": "none",
        "padding": "0.5rem 0.75rem", "cursor": "pointer", "font-size": "0.75rem"
    }
    
    if button_id == "x-temp":
    
        return active_style, inactive_style, inactive_style
    elif button_id == "x-sal":
        return inactive_style, active_style, inactive_style
    elif button_id == "x-pres":
        return inactive_style, inactive_style, active_style
    
    return active_style, inactive_style, inactive_style

# Segmented control functionality for Y-axis
@app.callback(
    [Output("y-depth", "style"), Output("y-time", "style"), Output("y-lat", "style")],
    [Input("y-depth", "n_clicks"), Input("y-time", "n_clicks"), Input("y-lat", "n_clicks")],
    prevent_initial_call=True
)
def update_y_axis_selection(depth_clicks, time_clicks, lat_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    active_style = {
        "flex": "1", "background": "#0ea5e9", "color": "white", "border": "none",
        "padding": "0.5rem 0.75rem", "cursor": "pointer", "font-size": "0.75rem"
    }
    inactive_style = {
        "flex": "1", "background": "white", "color": "#64748b", "border": "none",
        "padding": "0.5rem 0.75rem", "cursor": "pointer", "font-size": "0.75rem"
    }
    
    if button_id == "y-depth":
        return active_style, inactive_style, inactive_style
    elif button_id == "y-time":
        return inactive_style, active_style, inactive_style
    elif button_id == "y-lat":
        return inactive_style, inactive_style, active_style
    
    return active_style, inactive_style, inactive_style

# Functions to generate comprehensive ARGO plots
def generate_argo_plots(float_id, temp, salinity, depth, lat, lon, theme="light"):
    """Generate all ARGO plots for a selected float"""
    
    # Create realistic data based on the float parameters
    np.random.seed(hash(float_id) % 1000)  # Consistent data for same float
    depths = np.linspace(0, min(depth, 2000), 50)
    
    # Temperature profile with thermocline
    temp_profile = temp * np.exp(-depths/500) + 2 + np.random.normal(0, 0.3, 50)
    thermocline_effect = np.where((depths > 200) & (depths < 500), 
                                 -2 * np.sin((depths - 200) * np.pi / 300), 0)
    temp_profile += thermocline_effect
    temp_profile = np.clip(temp_profile, 2, temp)
    
    # Salinity profile
    sal_profile = salinity + np.random.normal(0, 0.1, 50) + depths * 0.0001
    sal_profile = np.clip(sal_profile, 33, 37)
    
    # Density calculation (simplified)
    density_profile = 1025 + (sal_profile - 35) * 0.8 - (temp_profile - 4) * 0.2 + depths * 0.004
    
    # Theme colors
    is_dark = theme == "dark"
    bg_color = '#1e293b' if is_dark else 'white'
    text_color = 'white' if is_dark else 'black'
    grid_color = '#374151' if is_dark else '#e5e7eb'
    
    return {
        'depths': depths,
        'temp_profile': temp_profile,
        'sal_profile': sal_profile,
        'density_profile': density_profile,
        'colors': {
            'bg': bg_color,
            'text': text_color,
            'grid': grid_color
        }
    }

def create_temperature_depth_plot(data, float_id, theme="light"):
    """Create temperature vs depth plot"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['temp_profile'],
        y=data['depths'],
        mode='lines+markers',
        line=dict(color='#ef4444', width=3),
        marker=dict(size=4, color='#ef4444'),
        name='Temperature',
        hovertemplate='<b>Depth:</b> %{y:.0f}m<br><b>Temperature:</b> %{x:.1f}°C<extra></extra>'
    ))
    
    fig.update_layout(

        xaxis_title="Temperature (°C)",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed", gridcolor=data['colors']['grid']),
        xaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=280
    )
    
    return fig

def create_salinity_depth_plot(data, float_id, theme="light"):
    """Create salinity vs depth plot"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['sal_profile'],
        y=data['depths'],
        mode='lines+markers',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=4, color='#3b82f6'),
        name='Salinity',
        hovertemplate='<b>Depth:</b> %{y:.0f}m<br><b>Salinity:</b> %{x:.2f} PSU<extra></extra>'
    ))
    
    fig.update_layout(

        xaxis_title="Salinity (PSU)",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed", gridcolor=data['colors']['grid']),
        xaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=280
    )
    
    return fig

def create_ts_diagram(data, float_id, theme="light"):
    """Create Temperature-Salinity diagram"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['sal_profile'],
        y=data['temp_profile'],
        mode='markers+lines',
        marker=dict(
            size=6,
            color=data['depths'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Depth (m)", thickness=10, len=0.5)
        ),
        line=dict(color='rgba(102, 126, 234, 0.6)', width=2),
        name='T-S Relationship',
        hovertemplate='<b>Salinity:</b> %{x:.2f} PSU<br><b>Temperature:</b> %{y:.1f}°C<extra></extra>'
    ))
    
    fig.update_layout(

        xaxis_title="Salinity (PSU)",
        yaxis_title="Temperature (°C)",
        xaxis=dict(gridcolor=data['colors']['grid']),
        yaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=280
    )
    
    return fig

def create_density_plot(data, float_id, theme="light"):
    """Create density profile plot"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['density_profile'],
        y=data['depths'],
        mode='lines+markers',
        line=dict(color='#10b981', width=3),
        marker=dict(size=4, color='#10b981'),
        name='Density',
        hovertemplate='<b>Depth:</b> %{y:.0f}m<br><b>Density:</b> %{x:.1f} kg/m³<extra></extra>'
    ))
    
    fig.update_layout(

        xaxis_title="Density (kg/m³)",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed", gridcolor=data['colors']['grid']),
        xaxis=dict(gridcolor=data['colors']['grid']),
        plot_bgcolor=data['colors']['bg'],
        paper_bgcolor=data['colors']['bg'],
        font=dict(color=data['colors']['text']),
        margin=dict(l=50, r=20, t=50, b=40),
        height=280
    )
    
    return fig

def create_zoomed_map(lat, lon, float_id, theme=False):
    """Create a zoomed map centered on the float location with consistent styling"""
    fig = go.Figure()
    
    # Add the specific float marker with enhanced styling
    fig.add_trace(go.Scattermapbox(
        lat=[lat],
        lon=[lon],
        mode='markers',
        marker=dict(
            size=20,
            color='#ef4444',
            opacity=0.9,
            symbol='circle'
        ),
        text=[f"<b>{float_id}</b><br>📍 {lat:.3f}°N, {lon:.3f}°E<br>🔍 Selected Float"],
        hovertemplate='%{text}<extra></extra>',
        name=float_id
    ))
    
    # Theme-aware map styling
    map_style = "carto-darkmatter" if theme else "open-street-map"
    bg_color = 'rgba(15, 23, 42, 0)' if theme else 'rgba(255, 255, 255, 0)'
    
    # Update layout for zoomed view with consistent styling
    fig.update_layout(
        mapbox=dict(
            style=map_style,
            center=dict(lat=lat, lon=lon),
            zoom=7,
            bearing=0,
            pitch=0
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        showlegend=False
    )
    
    return fig

# Function to call Groq for general chat
def call_groq_for_general_chat(message):
    """Call Groq API directly for general conversational responses"""
    try:
        import requests
        
        # Groq API configuration
        GROQ_API_KEY = "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"
        GROQ_MODEL = "llama-3.1-8b-instant"
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful AI assistant. Provide clear, concise, and friendly responses to user questions. If asked about oceanographic data, mention that you can help with ocean research questions too."
                },
                {
                    "role": "user", 
                    "content": message
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            assistant_text = data["choices"][0]["message"]["content"]
            
            # Create a mock response object similar to backend
            class MockResponse:
                def __init__(self, status_code, json_data):
                    self.status_code = status_code
                    self._json_data = json_data
                
                def json(self):
                    return self._json_data
            
            return MockResponse(200, {
                "text": assistant_text,
                "sql": None,
                "table": None,
                "plot_spec": None
            })
        else:
            return MockResponse(500, {"text": "Sorry, I'm having trouble responding right now."})
            
    except Exception as e:
        print(f"Groq API error: {e}")
        class MockResponse:
            def __init__(self, status_code, json_data):
                self.status_code = status_code
                self._json_data = json_data
            
            def json(self):
                return self._json_data
        
        return MockResponse(500, {"text": "I'm having trouble connecting to my language model. Please try again."})

# Enhanced Chat functionality with ARGO Float RAG integration
# @app.callback(
#     [Output("chat-messages", "children"), 
#      Output("selected-float-info", "children", allow_duplicate=True),
#      Output("temp-depth-plot", "figure", allow_duplicate=True),
#      Output("sal-depth-plot", "figure", allow_duplicate=True), 
#      Output("ts-diagram-plot", "figure", allow_duplicate=True),
#      Output("density-plot", "figure", allow_duplicate=True),
#      Output("main-map", "figure", allow_duplicate=True)],
#     [Input("send-btn", "n_clicks")] + [Input({"type": "quick-action", "index": i}, "n_clicks") for i in range(len(quick_actions))],
#     [State("chat-input", "value"), State("sql-mode", "value"), State("chat-messages", "children"), State("theme-store", "data")],
#     prevent_initial_call=True
# )
@app.callback(
    [
        Output("chat-messages", "children"), 
        Output("selected-float-info", "children", allow_duplicate=True),
        Output("temp-depth-plot", "figure", allow_duplicate=True),
        Output("sal-depth-plot", "figure", allow_duplicate=True), 
        Output("ts-diagram-plot", "figure", allow_duplicate=True),
        Output("density-plot", "figure", allow_duplicate=True),
        Output("main-map", "figure", allow_duplicate=True)
    ],
    [
        Input("send-btn", "n_clicks"),
        *[Input({"type": "quick-action", "index": i}, "n_clicks") for i in range(len(quick_actions))]
    ],
    [
        State("chat-input", "value"),
        State("sql-mode", "value"),
        State("chat-messages", "children"),
        State("theme-store", "data")
    ],
    prevent_initial_call=True
)
def handle_chat_with_argo_rag(send_clicks, *args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Extract quick action clicks and states
    quick_clicks = args[:-4]
    chat_input, sql_mode, current_messages, theme = args[-4:]
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # Determine the message to send
    message = ""
    if "send-btn" in trigger_id and chat_input:
        message = chat_input
    elif "quick-action" in trigger_id:
        # Find which quick action was clicked
        for i, action in enumerate(quick_actions):
            if f'"index":{i}' in trigger_id:
                message = action["query"]
                break
    
    if not message:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Add user message with timestamp
    current_time = datetime.now().strftime("%H:%M")
    user_message = html.Div([
        html.Div(message, style={"margin-bottom": "0.25rem"}),
        html.Div(current_time, style={"font-size": "0.6rem", "opacity": "0.7"})
    ], style={
        "background": "var(--accent-primary)", "color": "var(--text-inverse)", "border-radius": "0.75rem",
        "padding": "0.75rem", "margin-left": "2rem", "margin-bottom": "0.75rem"
    })
    
    # Initialize return values
    updated_info = dash.no_update
    updated_temp_plot = dash.no_update
    updated_sal_plot = dash.no_update
    updated_ts_plot = dash.no_update
    updated_density_plot = dash.no_update
    updated_main_map = dash.no_update
    
    # Use the enhanced NLP + RAG + LLM handler
    try:
        current_theme = "dark" if theme == "dark" else "light"
        result = enhanced_chat_with_nlp_rag_llm(message, current_theme)
        
        # Build assistant response content
        response_parts = []
        
        # Main response text
        if result['response']:
            response_parts.append(html.Div(result['response'], style={
                "line-height": "1.6",
                "margin-bottom": "1rem"
            }))
        
        # Add table if present
        if result.get('table_data'):
            response_parts.append(create_data_table(result['table_data'], theme=current_theme))
        
        # Add statistics if present
        if result.get('statistics'):
            stats = result['statistics']
            stats_content = []
            
            if isinstance(stats, dict):
                for key, value in stats.items():
                    if key != 'note' and value is not None:
                        if isinstance(value, float):
                            stats_content.append(f"• {key.replace('_', ' ').title()}: {value:.2f}")
                        else:
                            stats_content.append(f"• {key.replace('_', ' ').title()}: {value}")
            
            if stats_content:
                response_parts.append(html.Div([
                    html.H5("📊 Statistics", style={"color": "var(--accent-primary)", "margin-bottom": "0.5rem"}),
                    html.Div("\n".join(stats_content), style={
                        "font-size": "0.85rem", 
                        "color": "var(--text-muted)",
                        "background": "var(--bg-tertiary)",
                        "padding": "0.75rem",
                        "border-radius": "0.5rem"
                    })
                ], style={"margin": "1rem 0"}))
        
        # Add plot confirmation if plots were generated
        if result.get('plots_needed') and result.get('float_data'):
            response_parts.append(html.Div([
                html.Span("📈 ", style={"color": "#10b981"}),
                html.Span(f"Generated plots for {len(result['float_data'])} float(s)", style={"font-weight": "500"}),
                html.Span(" - Check Analytics tab!", style={"font-style": "italic"})
            ], style={
                "margin-top": "0.5rem", "padding": "0.5rem", 
                "background": "rgba(16, 185, 129, 0.1)",
                "border-radius": "0.375rem", "color": "#10b981", "font-size": "0.85rem",
                "border": "1px solid rgba(16, 185, 129, 0.3)"
            }))
        
        # Add success indicator
        response_parts.append(html.Div([
            html.Span("🤖 ", style={"color": "var(--accent-primary)"}),
            html.Span("AI Assistant", style={"font-weight": "500"}),
            html.Span(f" • {current_time}", style={"opacity": "0.7", "margin-left": "0.5rem"})
        ], style={
            "margin-top": "0.75rem", "font-size": "0.75rem", "color": "var(--accent-primary)"
        }))
        
        # Update plots and info if float data is available
        if result.get('float_data') and result['plots_needed']:
            float_data = result['float_data'][0]  # Use first float for plotting
            try:
                # Generate plot data
                plot_data_dict = generate_argo_plots(
                    float_data['float_id'], 
                    float_data['surface_temperature'], 
                    float_data['surface_salinity'], 
                    float_data['max_depth'], 
                    float_data['latitude'], 
                    float_data['longitude'], 
                    theme=current_theme
                )
                
                # Create plots
                updated_temp_plot = create_temperature_depth_plot(plot_data_dict, float_data['float_id'], current_theme)
                updated_sal_plot = create_salinity_depth_plot(plot_data_dict, float_data['float_id'], current_theme)
                updated_ts_plot = create_ts_diagram(plot_data_dict, float_data['float_id'], current_theme)
                updated_density_plot = create_density_plot(plot_data_dict, float_data['float_id'], current_theme)
                
                # Create info card
                updated_info = html.Div([
                    html.H4(f"🌊 {float_data['float_id']}", style={"color": "var(--accent-primary)", "margin-bottom": "1rem"}),
                    html.Div([
                        html.Div(f"📍 Location: {float_data['latitude']:.2f}°, {float_data['longitude']:.2f}°", style={"margin": "0.5rem 0"}),
                        html.Div(f"🌡️ Surface Temp: {float_data['surface_temperature']:.1f}°C", style={"margin": "0.5rem 0"}),
                        html.Div(f"🧂 Salinity: {float_data['surface_salinity']:.2f} PSU", style={"margin": "0.5rem 0"}),
                        html.Div(f"📏 Max Depth: {float_data['max_depth']:.0f}m", style={"margin": "0.5rem 0"}),
                    ])
                ], style={
                    "background": "var(--bg-card)",
                    "padding": "1rem",
                    "border-radius": "0.5rem",
                    "border": "1px solid var(--border-primary)"
                })
                
            except Exception as plot_error:
                logger.error(f"Plot generation error: {plot_error}")
        
        assistant_content = response_parts
        
    except Exception as e:
        assistant_content = [
            html.Div(f"❌ Error processing your query: {str(e)[:100]}"),
            html.Div("🤖 AI Assistant Error", style={
                "margin-top": "0.5rem", "font-size": "0.75rem", "color": "#ef4444"
            })
        ]
    
    # Create assistant message
    assistant_message = html.Div(assistant_content, style={
        "background": "var(--bg-card)", "border": "1px solid var(--border-primary)", "border-radius": "0.75rem",
        "padding": "0.75rem", "margin-right": "2rem", "box-shadow": "var(--shadow-sm)",
        "margin-bottom": "0.75rem", "color": "var(--text-primary)"
    })
    
    # Return updated messages and plots
    if current_messages:
        new_messages = current_messages + [user_message, assistant_message]
    else:
        new_messages = [user_message, assistant_message]
    
    return new_messages, updated_info, updated_temp_plot, updated_sal_plot, updated_ts_plot, updated_density_plot, updated_main_map

# Clear chat input after sending
@app.callback(
    Output("chat-input", "value"),
    Input("send-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_chat_input(n_clicks):
    return ""

# Clientside callback for Enter key handling in chat input
app.clientside_callback(
    """
    function(id) {
        // Add event listener for keydown on chat input
        setTimeout(function() {
            const chatInput = document.getElementById('chat-input');
            const sendBtn = document.getElementById('send-btn');
            
            if (chatInput && sendBtn) {
                chatInput.addEventListener('keydown', function(event) {
                    if (event.key === 'Enter') {
                        if (event.shiftKey) {
                            // Shift+Enter: Allow new line (default behavior)
                            return true;
                        } else {
                            // Enter only: Send message
                            event.preventDefault();
                            if (chatInput.value.trim()) {
                                sendBtn.click();
                            }
                            return false;
                        }
                    }
                });
            }
        }, 100);
        return window.dash_clientside.no_update;
    }
    """,
    Output("chat-input", "id"),
    Input("chat-input", "id")
)

# Clientside callback for resizable sidebar functionality
app.clientside_callback(
    """
    function(id) {
        setTimeout(function() {
            const sidebar = document.getElementById('chat-sidebar');
            const resizeHandle = document.getElementById('resize-handle');
            const widthIndicator = document.getElementById('width-indicator');
            
            if (sidebar && resizeHandle && widthIndicator) {
                let isResizing = false;
                let startX = 0;
                let startWidth = 0;
                
                // Mouse down on resize handle
                resizeHandle.addEventListener('mousedown', function(e) {
                    isResizing = true;
                    startX = e.clientX;
                    startWidth = parseInt(document.defaultView.getComputedStyle(sidebar).width, 10);
                    sidebar.classList.add('resizing');
                    resizeHandle.classList.add('dragging');
                    
                    // Prevent text selection during resize
                    document.body.style.userSelect = 'none';
                    document.body.style.cursor = 'col-resize';
                    
                    e.preventDefault();
                });
                
                // Mouse move - resize sidebar
                document.addEventListener('mousemove', function(e) {
                    if (!isResizing) return;
                    
                    const width = startWidth + (e.clientX - startX);
                    const minWidth = 280;
                    const maxWidth = 600;
                    
                    // Constrain width within limits
                    const constrainedWidth = Math.max(minWidth, Math.min(maxWidth, width));
                    
                    sidebar.style.width = constrainedWidth + 'px';
                    widthIndicator.textContent = constrainedWidth + 'px';
                    
                    e.preventDefault();
                });
                
                // Mouse up - stop resizing
                document.addEventListener('mouseup', function(e) {
                    if (isResizing) {
                        isResizing = false;
                        sidebar.classList.remove('resizing');
                        resizeHandle.classList.remove('dragging');
                        
                        // Restore normal cursor and text selection
                        document.body.style.userSelect = '';
                        document.body.style.cursor = '';
                        
                        // Save width to localStorage for persistence
                        const currentWidth = sidebar.style.width;
                        localStorage.setItem('chat-sidebar-width', currentWidth);
                    }
                });
                
                // Load saved width from localStorage
                const savedWidth = localStorage.getItem('chat-sidebar-width');
                if (savedWidth) {
                    sidebar.style.width = savedWidth;
                    widthIndicator.textContent = savedWidth;
                }
                
                // Double-click to reset to default width
                resizeHandle.addEventListener('dblclick', function() {
                    const defaultWidth = '350px';
                    sidebar.style.width = defaultWidth;
                    widthIndicator.textContent = defaultWidth;
                    localStorage.setItem('chat-sidebar-width', defaultWidth);
                });
            }
        }, 100);
        return window.dash_clientside.no_update;
    }
    """,
    Output("resize-handle", "id"),
    Input("resize-handle", "id")
)

# Auto-scroll chat messages to bottom
app.clientside_callback(
    """
    function(children) {
        setTimeout(function() {
            const chatContainer = document.getElementById('chat-messages');
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }, 100);
        
        // Tab highlight based on chat content
        if (children && children.length) {
            const lastMessage = children[children.length - 1];
            if (lastMessage && lastMessage.props && lastMessage.props.children) {
                const content = lastMessage.props.children.join('').toLowerCase();
                
                // Remove highlight from all tabs
                const mapTab = document.getElementById('map-tab');
                const analysisTab = document.getElementById('analysis-tab');
                
                if (mapTab) mapTab.classList.remove('tab-highlight');
                if (analysisTab) analysisTab.classList.remove('tab-highlight');
                
                // Highlight appropriate tab based on content
                if (content.includes('argo') || content.includes('float') || content.includes('data')) {
                    if (analysisTab) analysisTab.classList.add('tab-highlight');
                }
            }
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output("chat-messages", "style", allow_duplicate=True),
    Input("chat-messages", "children"),
    prevent_initial_call=True
)

# Enhanced click handler for multiple plots
@app.callback(
    [Output("selected-float-info", "children"),
     Output("temp-depth-plot", "figure"),
     Output("sal-depth-plot", "figure"), 
     Output("ts-diagram-plot", "figure"),
     Output("density-plot", "figure"),
     Output("main-map", "figure", allow_duplicate=True),
     Output("map-content", "style", allow_duplicate=True),
     Output("analysis-content", "style", allow_duplicate=True),
     Output("map-tab", "style", allow_duplicate=True),
     Output("analysis-tab", "style", allow_duplicate=True)],
    [Input("main-map", "clickData"),
     Input("argo-search", "value")],
    [State("theme-store", "data")],
    prevent_initial_call=True
)
def show_comprehensive_analysis(click_data, search_value, theme):
    """Show comprehensive ARGO analysis when a float is clicked or searched"""
    
    try:
        # Tab styles (keep map tab active for ARGO data)
        map_style = {
            "flex": "1", 
            "position": "relative", 
            "background": "transparent",
            "border-radius": "0px",
            "overflow": "hidden"
        }
        analysis_style = {"display": "none"}
        map_tab_style = {
            "background": "none", "border": "none", "padding": "0.75rem 1rem",
            "color": "var(--accent-primary)", "cursor": "pointer", "border-bottom": "2px solid var(--accent-primary)",
            "display": "flex", "align-items": "center", "transition": "all 0.3s ease"
        }
        analysis_tab_style = {
            "background": "none", "border": "none", "padding": "0.75rem 1rem",
            "color": "var(--text-muted)", "cursor": "pointer", "border-bottom": "2px solid transparent",
            "display": "flex", "align-items": "center", "transition": "all 0.3s ease"
        }
        
        # Determine trigger
        ctx = dash.callback_context
        if not ctx.triggered:
            return [dash.no_update] * 10
        
        trigger_id = ctx.triggered[0]['prop_id']
        
        # Handle search input
        if "argo-search" in trigger_id and search_value:
            # Validate ARGO float ID format first
            search_value = search_value.strip().upper()
            
            if not search_value:
                # Empty search - show helpful message
                return [
                    html.Div([
                        html.H3("🔍 Search for ARGO Floats", style={"color": "#6b7280", "text-align": "center"}),
                        html.Div([
                            "Enter an ARGO float ID to view detailed analysis:",
                            html.Br(),
                            "• ARGO_XXXX (e.g., ARGO_5001)",
                            html.Br(), 
                            "• XXXX (e.g., 5001)",
                            html.Br(),
                            "• ARGOXXXX (e.g., ARGO5001)"
                        ], style={"color": "#6b7280", "text-align": "center", "margin-top": "1rem"})
                    ]),
                    {}, {}, {}, {}, dash.no_update,  # Don't update map
                    dash.no_update, dash.no_update
                ]
            
            # Check if the input matches expected ARGO format
            import re
            argo_pattern = re.compile(r'^(ARGO[_]?)?(\d{4,5})$')
            match = argo_pattern.match(search_value)
            
            if not match:
                # Invalid format - show error message
                return [
                    html.Div([
                        html.H3("❌ Invalid ARGO Float ID Format", style={"color": "#ef4444", "text-align": "center"}),
                        html.Div([
                            "Please enter a valid ARGO float ID in one of these formats:",
                            html.Br(),
                            "• ARGO_XXXX (e.g., ARGO_5001)",
                            html.Br(), 
                            "• XXXX (e.g., 5001)",
                            html.Br(),
                            "• ARGOXXXX (e.g., ARGO5001)"
                        ], style={"color": "#ef4444", "text-align": "center", "margin-top": "1rem"})
                    ]),
                    {}, {}, {}, {}, dash.no_update,  # Don't update map
                    dash.no_update, dash.no_update
                ]
            
            # Extract the numeric part and create standard format
            float_number = match.group(2)
            float_id = f"ARGO_{float_number}"
            
            # Now search for the float in database
            if RAG_AVAILABLE:
                float_data = argo_rag.get_float_data(float_id)
                if float_data:
                    surface_temp = float_data['surface_temperature']
                    salinity = float_data['surface_salinity']
                    max_depth = float_data['max_depth']
                    lat = float_data['latitude']
                    lon = float_data['longitude']
                else:
                    # Float exists in valid format but not in database
                    return [
                        html.Div([
                            html.H3("❌ ARGO Float Not Found", style={"color": "#ef4444", "text-align": "center"}),
                            html.Div(f"ARGO float '{float_id}' is not in our current database.", style={"color": "#ef4444", "text-align": "center"})
                        ]),
                        {}, {}, {}, {}, dash.no_update,  # Don't update map
                        dash.no_update, dash.no_update, dash.no_update, dash.no_update
                    ]
            else:
                # Fallback if RAG not available
                surface_temp = 25.0 + np.random.uniform(-3, 3)
                salinity = 35.0 + np.random.uniform(-0.5, 0.5)
                max_depth = np.random.uniform(500, 2000)
                lat = np.random.uniform(-35, 15)
                lon = np.random.uniform(45, 115)
            
            # Create zoomed map for the searched float
            zoomed_map = create_zoomed_map(lat, lon, float_id)
            
        # Handle map click
        elif "main-map" in trigger_id and click_data:
            point = click_data["points"][0]
            float_id = point["customdata"][0]
            
            # Use RAG system for consistent data
            if RAG_AVAILABLE:
                float_data = argo_rag.get_float_data(float_id)
                surface_temp = float_data['surface_temperature']
                salinity = float_data['surface_salinity']
                max_depth = float_data['max_depth']
                lat = float_data['latitude']
                lon = float_data['longitude']
            else:
                surface_temp = point["customdata"][1]
                salinity = point["customdata"][2]
                max_depth = point["customdata"][3]
                lat = point["lat"]
                lon = point["lon"]
            
            zoomed_map = dash.no_update
        else:
            return [dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, 
                   dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update]
        
        # Generate comprehensive data
        plot_data = generate_argo_plots(float_id, surface_temp, salinity, max_depth, lat, lon, theme)
        
        # Create all plots
        temp_fig = create_temperature_depth_plot(plot_data, float_id, theme)
        sal_fig = create_salinity_depth_plot(plot_data, float_id, theme)
        ts_fig = create_ts_diagram(plot_data, float_id, theme)
        density_fig = create_density_plot(plot_data, float_id, theme)
        
        # Theme-aware info card styling
        is_dark = theme == "dark"
        card_text_color = "#f1f5f9" if is_dark else "#374151"
        muted_text_color = "#94a3b8" if is_dark else "#6b7280"
        
        # Update float info with theme-aware styling
        info_card = html.Div([
            html.H3(f"🌊 {float_id}", style={
                "margin": "0 0 1rem 0",
                "color": card_text_color,
                "text-align": "center"
            }),
            html.Div([
                html.Div([
                    html.Strong("📍 Location: ", style={"color": card_text_color}), 
                    f"{lat:.2f}°, {lon:.2f}°"
                ], style={"margin-bottom": "0.5rem", "color": muted_text_color}),
                html.Div([
                    html.Strong("🌡️ Surface Temp: ", style={"color": card_text_color}), 
                    f"{surface_temp:.1f}°C"
                ], style={"margin-bottom": "0.5rem", "color": muted_text_color}),
                html.Div([
                    html.Strong("🧂 Salinity: ", style={"color": card_text_color}), 
                    f"{salinity:.2f} PSU"
                ], style={"margin-bottom": "0.5rem", "color": muted_text_color}),
                html.Div([
                    html.Strong("📏 Max Depth: ", style={"color": card_text_color}), 
                    f"{max_depth:.0f}m"
                ], style={"margin-bottom": "0.5rem", "color": muted_text_color}),
            ], style={"text-align": "left"})
        ])
        
        # Only update map if we have a new zoomed map
        final_map = zoomed_map if zoomed_map != dash.no_update else dash.no_update
        
        # Determine tab switching based on trigger
        if "argo-search" in trigger_id:
            # Show analysis tab for ARGO search (to display plots)
            map_content_style = {"display": "none"}
            analysis_content_style = {
                "flex": "1", 
                "position": "relative", 
                "background": "transparent",
                "border-radius": "0px",
                "overflow": "hidden"
            }
            map_tab_style = {
                "background": "none", "border": "none", "padding": "0.75rem 1rem",
                "color": "var(--text-muted)", "cursor": "pointer", "border-bottom": "2px solid transparent",
                "display": "flex", "align-items": "center", "transition": "all 0.3s ease"
            }
            analysis_tab_style = {
                "background": "none", "border": "none", "padding": "0.75rem 1rem",
                "color": "var(--accent-primary)", "cursor": "pointer", "border-bottom": "2px solid var(--accent-primary)",
                "display": "flex", "align-items": "center", "transition": "all 0.3s ease"
            }
        else:
            # Keep map tab active for map clicks (plots show in ARGO Analytics section)
            map_content_style = {
                "flex": "1", 
                "position": "relative", 
                "background": "transparent",
                "border-radius": "0px",
                "overflow": "hidden"
            }
            analysis_content_style = {"display": "none"}
            map_tab_style = {
                "background": "none", "border": "none", "padding": "0.75rem 1rem",
                "color": "var(--accent-primary)", "cursor": "pointer", "border-bottom": "2px solid var(--accent-primary)",
                "display": "flex", "align-items": "center", "transition": "all 0.3s ease"
            }
            analysis_tab_style = {
                "background": "none", "border": "none", "padding": "0.75rem 1rem",
                "color": "var(--text-muted)", "cursor": "pointer", "border-bottom": "2px solid transparent",
                "display": "flex", "align-items": "center", "transition": "all 0.3s ease"
            }
        
        return info_card, temp_fig, sal_fig, ts_fig, density_fig, final_map, map_content_style, analysis_content_style, map_tab_style, analysis_tab_style
    
    except Exception as e:
        import traceback
        error_msg = f"Callback error: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        
        # Return error state
        error_card = html.Div([
            html.H3("❌ Error", style={"color": "#ef4444", "text-align": "center"}),
            html.Div(f"Failed to process float data: {str(e)[:100]}", style={"color": "#ef4444", "text-align": "center"})
        ])
        
        return error_card, {}, {}, {}, {}, dash.no_update, dash.no_update, dash.no_update

# Export functionality callbacks
@app.callback(
    Output("download-csv", "data"),
    Input("export-csv-btn", "n_clicks"),
    [State("selected-float-info", "children")],
    prevent_initial_call=True
)
def export_csv(n_clicks, float_info):
    """Export selected float data as CSV"""
    if not n_clicks or not float_info:
        return dash.no_update
    
    # Extract float ID from the info (simplified)
    try:
        float_id = "ARGO_SAMPLE"  # Would extract from actual selection
        
        # Generate sample data
        np.random.seed(42)
        depths = np.linspace(0, 2000, 50)
        temps = 25 * np.exp(-depths/500) + 2 + np.random.normal(0, 0.3, 50)
        sals = 35 + np.random.normal(0, 0.1, 50)
        
        # Create DataFrame
        df = pd.DataFrame({
            'Float_ID': [float_id] * len(depths),
            'Depth_m': depths,
            'Temperature_C': temps,
            'Salinity_PSU': sals,
            'Latitude': [-10.5] * len(depths),
            'Longitude': [80.2] * len(depths)
        })
        
        return dcc.send_data_frame(df.to_csv, f"{float_id}_data.csv", index=False)
    except:
        return dash.no_update

@app.callback(
    Output("download-png", "data"),
    Input("export-png-btn", "n_clicks"),
    prevent_initial_call=True
)
def export_png(n_clicks):
    """Export plots as PNG (placeholder)"""
    if not n_clicks:
        return dash.no_update
    
    # This would generate a combined PNG of all plots
    # For now, return a placeholder
    return dash.no_update

@app.callback(
    Output("share-btn", "children"),
    Input("share-btn", "n_clicks"),
    prevent_initial_call=True
)
def share_link(n_clicks):
    """Generate shareable link"""
    if not n_clicks:
        return dash.no_update
    
    # Simulate copying to clipboard
    import time
    time.sleep(0.5)  # Simulate processing
    
    return [
        html.I(className="fas fa-check", style={"margin-right": "0.5rem", "color": "#10b981"}),
        "Link Copied!"
    ]

# Tab switching callback
@app.callback(
    [Output("map-content", "style"),
     Output("analysis-content", "style"),
     Output("map-tab", "style"),
     Output("analysis-tab", "style")],
    [Input("map-tab", "n_clicks"),
     Input("analysis-tab", "n_clicks")],
    prevent_initial_call=True
)
def switch_tabs(map_clicks, analysis_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "analysis-tab":
        # Show analysis tab
        map_style = {"display": "none"}
        analysis_style = {
            "flex": "1",
            "display": "flex",
            "flex-direction": "column",
            "overflow": "hidden"
        }
        map_tab_style = {
            "background": "none", "border": "none", "padding": "0.75rem 1rem",
            "color": "var(--text-muted)", "cursor": "pointer", "border-bottom": "2px solid transparent",
            "display": "flex", "align-items": "center", "transition": "all 0.3s ease"
        }
        analysis_tab_style = {
            "background": "none", "border": "none", "padding": "0.75rem 1rem",
            "color": "var(--accent-primary)", "cursor": "pointer", "border-bottom": "2px solid var(--accent-primary)",
            "display": "flex", "align-items": "center", "transition": "all 0.3s ease"
        }
    else:
        # Show map tab
        map_style = {
            "flex": "1", 
            "position": "relative", 
            "background": "transparent",
            "border-radius": "0px",
            "overflow": "hidden"
        }
        analysis_style = {"display": "none"}
        map_tab_style = {
            "background": "none", "border": "none", "padding": "0.75rem 1rem",
            "color": "var(--accent-primary)", "cursor": "pointer", "border-bottom": "2px solid var(--accent-primary)",
            "display": "flex", "align-items": "center", "transition": "all 0.3s ease"
        }
        analysis_tab_style = {
            "background": "none", "border": "none", "padding": "0.75rem 1rem",
            "color": "var(--text-muted)", "cursor": "pointer", "border-bottom": "2px solid transparent",
            "display": "flex", "align-items": "center", "transition": "all 0.3s ease"
        }
    
    return map_style, analysis_style, map_tab_style, analysis_tab_style

# Populate ARGO data table
@app.callback(
    Output("argo-data-table", "data"),
    Input("dashboard-container", "id"),  # Trigger on page load
    prevent_initial_call=False
)
def populate_table(dashboard_id):
    return generate_argo_table_data()

# Handle table row selection and update visualization
@app.callback(
    [Output("selected-float-info", "children", allow_duplicate=True),
     Output("temp-depth-plot", "figure", allow_duplicate=True),
     Output("sal-depth-plot", "figure", allow_duplicate=True), 
     Output("ts-diagram-plot", "figure", allow_duplicate=True),
     Output("density-plot", "figure", allow_duplicate=True)],
    [Input("argo-data-table", "selected_rows"),
     Input("argo-data-table", "data")],
    [State("theme-store", "data")],
    prevent_initial_call=True
)
def update_plots_from_table(selected_rows, table_data, theme):
    if not selected_rows or not table_data:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Get selected row data
    selected_row = table_data[selected_rows[0]]
    float_id = selected_row["argo_id"]
    lat = selected_row["latitude"]
    lon = selected_row["longitude"]
    temp = selected_row["temperature"]
    salinity = selected_row["salinity"]
    depth = selected_row["depth"]
    
    # Generate plot data
    plot_data = generate_argo_plots(float_id, temp, salinity, depth, lat, lon, theme)
    
    # Update float info
    info_text = html.Div([
        html.H4(f"🎯 {float_id}", style={
            "margin": "0 0 1rem 0", 
            "color": "var(--text-primary)",
            "text-align": "center"
        }),
        html.Div([
            html.Div(f"📍 Location: {lat:.2f}°, {lon:.2f}°", style={"margin": "0.5rem 0"}),
            html.Div(f"🌡️ Surface Temp: {temp:.1f}°C", style={"margin": "0.5rem 0"}),
            html.Div(f"🧂 Salinity: {salinity:.2f} PSU", style={"margin": "0.5rem 0"}),
            html.Div(f"📏 Max Depth: {depth:.0f}m", style={"margin": "0.5rem 0"}),
            html.Div(f"📅 Last Update: {selected_row['date']}", style={"margin": "0.5rem 0"}),
            html.Div(f"🔄 Status: {selected_row['status']}", style={
                "margin": "0.5rem 0",
                "color": "#10b981" if selected_row['status'] == "Active" else "#ef4444" if selected_row['status'] == "Inactive" else "#f59e0b"
            })
        ], style={"text-align": "center", "color": "var(--text-secondary)"})
    ])
    
    # Create plots
    temp_fig = create_temperature_depth_plot(plot_data, float_id, theme)
    sal_fig = create_salinity_depth_plot(plot_data, float_id, theme)
    ts_fig = create_ts_diagram(plot_data, float_id, theme)
    density_fig = create_density_plot(plot_data, float_id, theme)
    
    return info_text, temp_fig, sal_fig, ts_fig, density_fig

# Toggle layers button - switches between map styles
@app.callback(
    Output("main-map", "figure", allow_duplicate=True),
    Input("toggle-layers-btn", "n_clicks"),
    State("main-map", "figure"),
    prevent_initial_call=True
)
def toggle_map_layers(n_clicks, current_figure):
    """Toggle between different map layer styles in a continuous loop"""
    if not n_clicks:
        return dash.no_update
    
    try:
        # Ensure current_figure is a dictionary (Plotly figure)
        if not isinstance(current_figure, dict):
            # If not a dict, fall back to creating a new map
            return create_float_map()
        
        # Get current map style safely
        layout = current_figure.get('layout', {})
        mapbox = layout.get('mapbox', {})
        current_style = mapbox.get('style', 'carto-positron')
        
        # Define available map styles in cycle order
        map_styles = ['carto-positron', 'carto-darkmatter', 'open-street-map', 'satellite', 'satellite-streets']
        
        # Find current style index and move to next one (cyclic)
        try:
            current_index = map_styles.index(current_style)
            next_index = (current_index + 1) % len(map_styles)  # This ensures it cycles back to 0 after the last one
            new_style = map_styles[next_index]
        except ValueError:
            # If current style not found in our list, start with first style
            new_style = map_styles[0]
        
        # Update the figure with new map style
        updated_figure = current_figure.copy()
        
        # Ensure layout structure exists
        if 'layout' not in updated_figure:
            updated_figure['layout'] = {}
        if 'mapbox' not in updated_figure['layout']:
            updated_figure['layout']['mapbox'] = {}
        
        updated_figure['layout']['mapbox']['style'] = new_style
        
        # Update colorbar and styling based on theme
        is_dark = new_style in ['carto-darkmatter', 'satellite', 'satellite-streets']
        
        # Update colorbar colors for better visibility
        if 'data' in updated_figure:
            for trace in updated_figure['data']:
                if isinstance(trace, dict) and 'marker' in trace:
                    marker = trace.get('marker', {})
                    if 'colorbar' in marker:
                        colorbar = marker['colorbar']
                        if isinstance(colorbar, dict):
                            colorbar['bgcolor'] = 'rgba(0,0,0,0.7)' if is_dark else 'rgba(255,255,255,0.9)'
                            colorbar['bordercolor'] = 'rgba(255,255,255,0.3)' if is_dark else 'rgba(0,0,0,0.1)'
        
        return updated_figure
        
    except Exception as e:
        # If anything goes wrong, return a fresh map
        print(f"Error in toggle_map_layers: {e}")
        return create_float_map()

# Reset map button - resets map view and layers to default
@app.callback(
    Output("main-map", "figure"),
    Input("reset-map-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_map_view(n_clicks):
    """Reset map view and layers to default state"""
    if not n_clicks:
        return dash.no_update
    
    try:
        # Create the default map with default layer style
        default_map = create_float_map()
        
        # Ensure default_map is a dictionary and has proper structure
        if not isinstance(default_map, dict):
            # If create_float_map() doesn't return a dict, create a basic one
            default_map = create_float_map()
        
        # Ensure the default map uses the first/default layer style
        if 'layout' not in default_map:
            default_map['layout'] = {}
        if 'mapbox' not in default_map['layout']:
            default_map['layout']['mapbox'] = {}
        
        # Set to default layer style (first in our cycle)
        default_map['layout']['mapbox']['style'] = 'carto-positron'
        
        # Reset colorbar to default theme
        if 'data' in default_map and isinstance(default_map['data'], list):
            for trace in default_map['data']:
                if isinstance(trace, dict) and 'marker' in trace:
                    marker = trace.get('marker', {})
                    if 'colorbar' in marker and isinstance(marker['colorbar'], dict):
                        marker['colorbar']['bgcolor'] = 'rgba(255,255,255,0.9)'
                        marker['colorbar']['bordercolor'] = 'rgba(0,0,0,0.1)'
        
        return default_map
        
    except Exception as e:
        # If anything goes wrong, return a fresh map
        print(f"Error in reset_map_view: {e}")
        return create_float_map()

# Map control button callbacks (clientside for fullscreen)
app.clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) return window.dash_clientside.no_update;
        
        // Toggle fullscreen for the map container
        const mapContainer = document.getElementById('map-content');
        if (!document.fullscreenElement) {
            mapContainer.requestFullscreen().catch(err => {
                console.log('Error attempting to enable fullscreen:', err);
            });
        } else {
            document.exitFullscreen();
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output("fullscreen-btn", "n_clicks"),
    Input("fullscreen-btn", "n_clicks"),
    prevent_initial_call=True
)

# Clear ARGO search input after successful analysis
app.clientside_callback(
    """
    function(children) {
        if (children && children.props && children.props.children && children.props.children[0]) {
            const firstChild = children.props.children[0];
            if (firstChild && firstChild.props && firstChild.props.children) {
                const title = firstChild.props.children;
                // If we have a successful float display (starts with 🌊), clear the search
                if (title && title.includes && title.includes('🌊')) {
                    setTimeout(function() {
                        const searchInput = document.getElementById('argo-search');
                        if (searchInput) {
                            searchInput.value = '';
                        }
                    }, 500); // Small delay to show results first
                }
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("selected-float-info", "children", allow_duplicate=True),
    Input("selected-float-info", "children"),
    prevent_initial_call=True
)


app.clientside_callback(
    """
    function(children) {
        if (children && children.props && children.props.children && children.props.children[0]) {
            const firstChild = children.props.children[0];
            if (firstChild && firstChild.props && firstChild.props.children) {
                const title = firstChild.props.children;
                // If we have a successful float display (starts with 🌊), scroll to analytics section
                if (title && title.includes && title.includes('🌊')) {
                    setTimeout(function() {
                        // Scroll to the top of the analytics section
                        const analyticsSection = document.querySelector('#temp-plot-card');
                        if (analyticsSection) {
                            analyticsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                    }, 300); // Small delay to let plots render
                }
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("dummy-scroll", "children"),
    Input("selected-float-info", "children"),
    prevent_initial_call=True
)

# Dummy element for scroll callback
html.Div(id="dummy-scroll", style={"display": "none"})

# Dummy element for scroll callback

# Run the app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8053)
