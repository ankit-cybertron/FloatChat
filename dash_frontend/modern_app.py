import os
import json
import requests
import pandas as pd
from datetime import datetime
import uuid

import dash
from dash import dcc, html, Input, Output, State, callback, clientside_callback, ClientsideFunction
import plotly.graph_objs as go
import plotly.express as px

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

# Modern CSS with research-grade styling
modern_styles = """
:root {
    --primary-blue: #0ea5e9;
    --primary-teal: #14b8a6;
    --dark-bg: #0f172a;
    --dark-surface: #1e293b;
    --dark-border: #334155;
    --light-bg: #ffffff;
    --light-surface: #f8fafc;
    --light-border: #e2e8f0;
    --text-primary: #0f172a;
    --text-secondary: #64748b;
    --text-primary-dark: #f8fafc;
    --text-secondary-dark: #cbd5e1;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.theme-light {
    --bg-primary: var(--light-bg);
    --bg-secondary: var(--light-surface);
    --border-color: var(--light-border);
    --text-color: var(--text-primary);
    --text-muted: var(--text-secondary);
}

.theme-dark {
    --bg-primary: var(--dark-bg);
    --bg-secondary: var(--dark-surface);
    --border-color: var(--dark-border);
    --text-color: var(--text-primary-dark);
    --text-muted: var(--text-secondary-dark);
}

.dashboard-container {
    height: 100vh;
    background: var(--bg-primary);
    color: var(--text-color);
    display: flex;
    flex-direction: column;
    transition: all 0.3s ease;
}

/* Top Navigation */
.top-nav {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    padding: 0.75rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 50;
}

.nav-left {
    display: flex;
    align-items: center;
    gap: 1.5rem;
}

.nav-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--primary-blue);
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.nav-search {
    position: relative;
}

.nav-search input {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 0.5rem 1rem 0.5rem 2.5rem;
    width: 300px;
    color: var(--text-color);
    font-size: 0.875rem;
}

.nav-search i {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
}

.nav-right {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.theme-toggle {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 0.5rem;
    color: var(--text-color);
    cursor: pointer;
    transition: all 0.2s ease;
}

.theme-toggle:hover {
    background: var(--border-color);
}

.research-badge {
    background: var(--primary-teal);
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: 500;
}

/* Main Layout */
.main-layout {
    display: flex;
    flex: 1;
    overflow: hidden;
}

/* Chat Sidebar */
.chat-sidebar {
    width: 350px;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    transition: all 0.3s ease;
}

.chat-sidebar.collapsed {
    width: 60px;
}

.chat-header {
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.chat-title {
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.collapse-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 0.25rem;
    transition: all 0.2s ease;
}

.collapse-btn:hover {
    background: var(--border-color);
    color: var(--text-color);
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.message-card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    padding: 0.75rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.message-card.user {
    background: var(--primary-blue);
    color: white;
    margin-left: 2rem;
}

.message-card.assistant {
    margin-right: 2rem;
}

.quick-actions {
    padding: 1rem;
    border-top: 1px solid var(--border-color);
}

.quick-actions-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.quick-action-btn {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 1.5rem;
    padding: 0.5rem 0.75rem;
    font-size: 0.75rem;
    color: var(--text-color);
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.quick-action-btn:hover {
    background: var(--primary-blue);
    color: white;
    border-color: var(--primary-blue);
}

.chat-input-area {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.chat-input {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 0.75rem;
    color: var(--text-color);
    resize: vertical;
    min-height: 80px;
}

.chat-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.sql-toggle {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.75rem;
    color: var(--text-muted);
}

.send-btn {
    background: var(--primary-blue);
    color: white;
    border: none;
    border-radius: 0.5rem;
    padding: 0.5rem 1rem;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
}

.send-btn:hover {
    background: var(--primary-teal);
}

/* Content Area */
.content-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.content-tabs {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
    padding: 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.tab-btn {
    background: none;
    border: none;
    padding: 0.75rem 1rem;
    color: var(--text-muted);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.2s ease;
}

.tab-btn.active {
    color: var(--primary-blue);
    border-bottom-color: var(--primary-blue);
}

.tab-btn:hover {
    color: var(--text-color);
}

.content-main {
    flex: 1;
    display: flex;
    overflow: hidden;
}

/* Map Section */
.map-section {
    flex: 1;
    position: relative;
    background: var(--bg-primary);
}

.map-controls {
    position: absolute;
    top: 1rem;
    right: 1rem;
    z-index: 10;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.map-control-btn {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    padding: 0.5rem;
    color: var(--text-color);
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
}

.map-control-btn:hover {
    background: var(--primary-blue);
    color: white;
}

/* Visualization Panel */
.viz-panel {
    width: 400px;
    background: var(--bg-secondary);
    border-left: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
}

.viz-header {
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.viz-title {
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.viz-controls {
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
}

.control-group {
    margin-bottom: 1rem;
}

.control-label {
    display: block;
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.segmented-control {
    display: flex;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    overflow: hidden;
}

.segment-btn {
    flex: 1;
    background: none;
    border: none;
    padding: 0.5rem 0.75rem;
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.75rem;
}

.segment-btn.active {
    background: var(--primary-blue);
    color: white;
}

.segment-btn:hover:not(.active) {
    background: var(--border-color);
    color: var(--text-color);
}

.viz-content {
    flex: 1;
    padding: 1rem;
    overflow-y: auto;
}

.export-actions {
    padding: 1rem;
    border-top: 1px solid var(--border-color);
    display: flex;
    gap: 0.5rem;
}

.export-btn {
    flex: 1;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 0.375rem;
    padding: 0.5rem;
    color: var(--text-color);
    cursor: pointer;
    font-size: 0.75rem;
    transition: all 0.2s ease;
}

.export-btn:hover {
    background: var(--primary-teal);
    color: white;
    border-color: var(--primary-teal);
}

/* Loading States */
.loading-skeleton {
    background: linear-gradient(90deg, var(--border-color) 25%, transparent 50%, var(--border-color) 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
    border-radius: 0.5rem;
    height: 1rem;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

.typing-indicator {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    color: var(--text-muted);
    font-size: 0.875rem;
}

.typing-dot {
    width: 0.25rem;
    height: 0.25rem;
    background: var(--text-muted);
    border-radius: 50%;
    animation: typing 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
    0%, 80%, 100% { opacity: 0.3; }
    40% { opacity: 1; }
}

/* Responsive Design */
@media (max-width: 1024px) {
    .viz-panel {
        width: 300px;
    }
    
    .nav-search input {
        width: 200px;
    }
}

@media (max-width: 768px) {
    .main-layout {
        flex-direction: column;
    }
    
    .chat-sidebar {
        width: 100%;
        height: 200px;
    }
    
    .viz-panel {
        width: 100%;
        height: 300px;
        border-left: none;
        border-top: 1px solid var(--border-color);
    }
    
    .content-main {
        flex-direction: column;
    }
}

/* Utility Classes */
.hidden { display: none !important; }
.flex { display: flex; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-2 { gap: 0.5rem; }
.gap-4 { gap: 1rem; }
.p-2 { padding: 0.5rem; }
.p-4 { padding: 1rem; }
.rounded { border-radius: 0.375rem; }
.rounded-lg { border-radius: 0.5rem; }
.shadow { box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.transition { transition: all 0.2s ease; }
"""

# Quick action suggestions for research
quick_actions = [
    {"icon": "fas fa-map-marker-alt", "text": "Recent Floats", "query": "Show me the most recent float deployments"},
    {"icon": "fas fa-thermometer-half", "text": "Temperature", "query": "Plot temperature profiles for the Indian Ocean"},
    {"icon": "fas fa-tint", "text": "Salinity", "query": "Compare salinity data across different regions"},
    {"icon": "fas fa-chart-line", "text": "Trends", "query": "Show temperature trends over the last year"},
    {"icon": "fas fa-database", "text": "SQL Query", "query": "SELECT platform_number, COUNT(*) FROM profiles GROUP BY platform_number LIMIT 10"},
    {"icon": "fas fa-download", "text": "Export Data", "query": "Export recent profile data as CSV"},
]

# Sample chat history for demo
sample_messages = [
    {"type": "user", "content": "Show me temperature profiles for the Indian Ocean", "timestamp": "2 min ago"},
    {"type": "assistant", "content": "I found 1,247 temperature profiles in the Indian Ocean region. The data shows temperatures ranging from 2°C to 28°C across different depths. I've plotted the most recent profiles on the map.", "timestamp": "2 min ago"},
]

app.layout = html.Div([
    # Inject CSS
    html.Style(modern_styles),
    
    # Main container with theme class
    html.Div([
        # Top Navigation
        html.Div([
            html.Div([
                html.Div([
                    html.I(className="fas fa-water"),
                    "FLOAT DATA EXPLORER"
                ], className="nav-title"),
                
                html.Div([
                    html.I(className="fas fa-search"),
                    dcc.Input(
                        id="nav-search",
                        placeholder="Search floats, profiles...",
                        type="text",
                        style={"background": "transparent", "border": "none", "outline": "none", "width": "100%"}
                    )
                ], className="nav-search"),
            ], className="nav-left"),
            
            html.Div([
                html.Div("Research Lab", className="research-badge"),
                html.Button([
                    html.I(id="theme-icon", className="fas fa-moon")
                ], id="theme-toggle", className="theme-toggle"),
                html.Button([
                    html.I(className="fas fa-cog")
                ], className="theme-toggle"),
                html.Div("G", style={"width": "32px", "height": "32px", "background": "var(--primary-blue)", "color": "white", "border-radius": "50%", "display": "flex", "align-items": "center", "justify-content": "center", "font-weight": "600"})
            ], className="nav-right"),
        ], className="top-nav"),
        
        # Main Layout
        html.Div([
            # Chat Sidebar
            html.Div([
                # Chat Header
                html.Div([
                    html.Div([
                        html.I(className="fas fa-comments"),
                        html.Span("AI Assistant", id="chat-title-text")
                    ], className="chat-title"),
                    html.Button([
                        html.I(id="collapse-icon", className="fas fa-chevron-left")
                    ], id="collapse-btn", className="collapse-btn"),
                ], className="chat-header"),
                
                # Chat Messages
                html.Div([
                    # Sample messages
                    html.Div([
                        html.Div("Show me temperature profiles for the Indian Ocean", className="message-card user"),
                        html.Div([
                            html.Div("I found 1,247 temperature profiles in the Indian Ocean region. The data shows temperatures ranging from 2°C to 28°C across different depths."),
                            html.Div("✓ Plotted recent profiles on map", style={"margin-top": "0.5rem", "font-size": "0.75rem", "color": "var(--success)"})
                        ], className="message-card assistant"),
                    ], id="chat-messages-container")
                ], className="chat-messages"),
                
                # Quick Actions & Input
                html.Div([
                    html.Div([
                        html.Button([
                            html.I(className=action["icon"]),
                            html.Span(action["text"])
                        ], className="quick-action-btn", **{"data-query": action["query"]}) 
                        for action in quick_actions[:4]
                    ], className="quick-actions-grid"),
                    
                    html.Div([
                        dcc.Textarea(
                            id="chat-input",
                            placeholder="Ask about ocean data, request visualizations, or write SQL queries...",
                            className="chat-input"
                        ),
                        html.Div([
                            html.Label([
                                dcc.Checklist(
                                    id="sql-mode",
                                    options=[{"label": "SQL Mode", "value": "sql"}],
                                    value=[],
                                    style={"margin": "0"}
                                )
                            ], className="sql-toggle"),
                            html.Button([
                                html.I(className="fas fa-paper-plane"),
                                " Send"
                            ], id="send-btn", className="send-btn")
                        ], className="chat-controls")
                    ], className="chat-input-area")
                ], className="quick-actions"),
            ], id="chat-sidebar", className="chat-sidebar"),
            
            # Content Area
            html.Div([
                # Content Tabs
                html.Div([
                    html.Button([
                        html.I(className="fas fa-map"),
                        " Map View"
                    ], className="tab-btn active", id="map-tab"),
                    html.Button([
                        html.I(className="fas fa-chart-area"),
                        " Analysis"
                    ], className="tab-btn", id="analysis-tab"),
                    html.Button([
                        html.I(className="fas fa-history"),
                        " History"
                    ], className="tab-btn", id="history-tab"),
                ], className="content-tabs"),
                
                # Main Content
                html.Div([
                    # Map Section
                    html.Div([
                        dcc.Graph(
                            id="main-map",
                            style={"height": "100%"},
                            config={
                                "displayModeBar": True,
                                "displaylogo": False,
                                "modeBarButtonsToRemove": ["pan2d", "lasso2d"]
                            }
                        ),
                        
                        # Map Controls
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-play")
                            ], className="map-control-btn", title="Play Animation"),
                            html.Button([
                                html.I(className="fas fa-layer-group")
                            ], className="map-control-btn", title="Toggle Layers"),
                            html.Button([
                                html.I(className="fas fa-crosshairs")
                            ], className="map-control-btn", title="Center View"),
                        ], className="map-controls"),
                    ], className="map-section"),
                    
                    # Visualization Panel
                    html.Div([
                        # Viz Header
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-chart-line"),
                                "Data Visualization"
                            ], className="viz-title"),
                            html.Button([
                                html.I(className="fas fa-expand")
                            ], className="collapse-btn", title="Expand Panel")
                        ], className="viz-header"),
                        
                        # Viz Controls
                        html.Div([
                            html.Div([
                                html.Label("X-Axis Variable", className="control-label"),
                                html.Div([
                                    html.Button("Temperature", className="segment-btn active", id="x-temp"),
                                    html.Button("Salinity", className="segment-btn", id="x-sal"),
                                    html.Button("Pressure", className="segment-btn", id="x-pres"),
                                ], className="segmented-control")
                            ], className="control-group"),
                            
                            html.Div([
                                html.Label("Y-Axis Variable", className="control-label"),
                                html.Div([
                                    html.Button("Depth", className="segment-btn active", id="y-depth"),
                                    html.Button("Time", className="segment-btn", id="y-time"),
                                    html.Button("Latitude", className="segment-btn", id="y-lat"),
                                ], className="segmented-control")
                            ], className="control-group"),
                            
                            html.Div([
                                html.Label("View Mode", className="control-label"),
                                html.Div([
                                    html.Button("Profile", className="segment-btn active", id="view-profile"),
                                    html.Button("Scatter", className="segment-btn", id="view-scatter"),
                                    html.Button("Heatmap", className="segment-btn", id="view-heatmap"),
                                ], className="segmented-control")
                            ], className="control-group"),
                        ], className="viz-controls"),
                        
                        # Viz Content
                        html.Div([
                            dcc.Graph(
                                id="profile-plot",
                                style={"height": "300px"},
                                config={"displayModeBar": False}
                            )
                        ], className="viz-content"),
                        
                        # Export Actions
                        html.Div([
                            html.Button([
                                html.I(className="fas fa-download"),
                                " CSV"
                            ], className="export-btn"),
                            html.Button([
                                html.I(className="fas fa-file-image"),
                                " PNG"
                            ], className="export-btn"),
                            html.Button([
                                html.I(className="fas fa-share-alt"),
                                " Share"
                            ], className="export-btn"),
                        ], className="export-actions")
                    ], className="viz-panel"),
                ], className="content-main"),
            ], className="content-area"),
        ], className="main-layout"),
    ], id="dashboard-container", className="dashboard-container theme-light"),
    
    # Hidden stores for state management
    dcc.Store(id="theme-store", data="light"),
    dcc.Store(id="sidebar-collapsed", data=False),
    dcc.Store(id="chat-history", data=sample_messages),
    dcc.Store(id="selected-floats", data=[]),
])

# Callbacks for interactivity
@app.callback(
    [Output("dashboard-container", "className"),
     Output("theme-icon", "className")],
    Input("theme-toggle", "n_clicks"),
    State("theme-store", "data")
)
def toggle_theme(n_clicks, current_theme):
    if n_clicks and n_clicks > 0:
        new_theme = "dark" if current_theme == "light" else "light"
        icon_class = "fas fa-sun" if new_theme == "dark" else "fas fa-moon"
        return f"dashboard-container theme-{new_theme}", icon_class
    return f"dashboard-container theme-{current_theme}", "fas fa-moon"

@app.callback(
    [Output("chat-sidebar", "className"),
     Output("collapse-icon", "className"),
     Output("chat-title-text", "children")],
    Input("collapse-btn", "n_clicks"),
    State("sidebar-collapsed", "data")
)
def toggle_sidebar(n_clicks, collapsed):
    if n_clicks and n_clicks > 0:
        new_collapsed = not collapsed
        sidebar_class = "chat-sidebar collapsed" if new_collapsed else "chat-sidebar"
        icon_class = "fas fa-chevron-right" if new_collapsed else "fas fa-chevron-left"
        title_text = "" if new_collapsed else "AI Assistant"
        return sidebar_class, icon_class, title_text
    return "chat-sidebar", "fas fa-chevron-left", "AI Assistant"

@app.callback(
    Output("main-map", "figure"),
    Input("dashboard-container", "id")  # Trigger on load
)
def update_map(_):
    # Create sample map with ARGO float locations
    try:
        # Try to get real data from backend
        response = requests.get(f"{BACKEND_URL}/list_floats", 
                              headers={"Authorization": f"Bearer {AUTH_TOKEN}"}, 
                              timeout=5)
        if response.status_code == 200:
            floats_data = response.json()
            if floats_data:
                # Get some profile data for mapping
                profile_response = requests.post(f"{BACKEND_URL}/chat", 
                                               json={"message": "show map", "visualize": True},
                                               headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
                                               timeout=10)
                if profile_response.status_code == 200:
                    chat_data = profile_response.json()
                    if chat_data.get("plot_spec"):
                        return chat_data["plot_spec"]
    except:
        pass
    
    # Fallback to sample data
    import numpy as np
    n_floats = 150
    
    # Generate sample float positions in Indian Ocean
    lats = np.random.normal(-20, 15, n_floats)
    lons = np.random.normal(75, 20, n_floats)
    temps = np.random.normal(15, 8, n_floats)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers',
        marker=dict(
            size=8,
            color=temps,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Temperature (°C)",
                titleside="right",
                thickness=15,
                len=0.7
            )
        ),
        text=[f"Float #{i+1000}<br>Temp: {temp:.1f}°C<br>Last: 2 hrs ago" 
              for i, temp in enumerate(temps)],
        hovertemplate="<b>%{text}</b><br>Lat: %{lat:.2f}<br>Lon: %{lon:.2f}<extra></extra>",
        name="ARGO Floats"
    ))
    
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=-20, lon=75),
            zoom=3
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        showlegend=False
    )
    
    return fig

@app.callback(
    Output("profile-plot", "figure"),
    [Input("x-temp", "n_clicks"), Input("x-sal", "n_clicks"), Input("x-pres", "n_clicks"),
     Input("y-depth", "n_clicks"), Input("y-time", "n_clicks"), Input("y-lat", "n_clicks")]
)
def update_profile_plot(*args):
    # Generate sample profile data
    depths = np.linspace(0, 2000, 50)
    temp_profile = 25 * np.exp(-depths/500) + 2
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=temp_profile,
        y=depths,
        mode='lines+markers',
        name='Temperature Profile',
        line=dict(color='#0ea5e9', width=3),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        xaxis_title="Temperature (°C)",
        yaxis_title="Depth (m)",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=40, r=20, t=20, b=40),
        height=300,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8051, debug=True)
