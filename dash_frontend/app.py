import os
import json
import requests
import pandas as pd
from datetime import datetime

import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.graph_objs as go

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "dev-token")

external_stylesheets = [
    {
        "href": "https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css",
        "rel": "stylesheet",
    },
    {
        "href": "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
        "rel": "stylesheet",
    }
]

# Add custom CSS
app_styles = """
.container { font-family: 'Inter', sans-serif; margin: 0; padding: 0; }
.header { background: #1f2937; color: white; padding: 1rem; display: flex; justify-content: space-between; align-items: center; }
.title { margin: 0; font-size: 1.5rem; font-weight: 600; }
.header-controls { display: flex; gap: 1rem; align-items: center; }
.body { display: flex; height: calc(100vh - 120px); }
.left-panel { width: 300px; padding: 1rem; background: #f9fafb; border-right: 1px solid #e5e7eb; overflow-y: auto; }
.main-panel { flex: 1; padding: 1rem; }
.chat-output { max-height: 200px; overflow-y: auto; padding: 0.5rem; background: white; border: 1px solid #d1d5db; border-radius: 0.375rem; margin: 0.5rem 0; }
.chat-controls { display: flex; gap: 0.5rem; align-items: center; margin: 0.5rem 0; }
.bottom-bar { background: #f3f4f6; padding: 0.5rem 1rem; border-top: 1px solid #e5e7eb; display: flex; justify-content: space-between; align-items: center; }
"""

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True, title="FloatChat")
server = app.server

suggested_prompts = [
    "Show floats active in the Indian Ocean last month",
    "Plot temperature vs depth for float 1234567",
    "Compare salinity profiles between two floats over time",
    "List top 10 floats by number of profiles",
]

app.layout = html.Div([
    # Header
    html.Div([
        html.H2("FloatChat — ARGO Ocean Data", className="title"),
        html.Div([
            html.Button("Light/Dark", id="theme-toggle", n_clicks=0),
            dcc.Dropdown(
                id="variable-select",
                options=[{"label": v, "value": v} for v in ["temperature", "salinity", "oxygen", "chlorophyll"]],
                value="temperature",
                clearable=False,
                style={"width": "220px"}
            ),
        ], className="header-controls")
    ], className="header"),

    # Body
    html.Div([
        # Left panel (controls & chat)
        html.Div([
            html.H4("Chat"),
            dcc.Textarea(id="chat-input", placeholder="Ask about floats, profiles, or visualizations...", style={"width":"100%", "height":"120px"}),
            html.Div([
                html.Button("Ask", id="ask-btn"),
                dcc.Checklist(options=[{"label": "Generate SQL", "value": "sql"}], value=[], id="gen-sql"),
            ], className="chat-controls"),
            html.Div(id="chat-output", className="chat-output"),
            html.Hr(),
            html.H4("Suggested"),
            html.Ul([html.Li(html.Button(p, id={"type": "suggest-btn", "index": i})) for i,p in enumerate(suggested_prompts)])
        ], className="left-panel"),

        # Main panel (map + profile viewer)
        html.Div([
            dcc.Graph(id="map-graph"),
            dcc.Graph(id="profile-graph"),
        ], className="main-panel"),
    ], className="body"),

    # Bottom bar
    html.Div([
        html.Div(id="status-bar", children="Ready."),
        html.A("Export CSV", href=f"{BACKEND_URL}/export?format=csv", target="_blank"),
        html.Span(" | "),
        html.A("Export ASCII", href=f"{BACKEND_URL}/export?format=ascii", target="_blank"),
    ], className="bottom-bar"),

    dcc.Store(id="theme", data="light"),
], className="container")

@app.callback(
    Output("chat-output", "children"),
    Output("map-graph", "figure"),
    Input("ask-btn", "n_clicks"),
    State("chat-input", "value"),
    State("gen-sql", "value"),
    prevent_initial_call=True,
)
def on_chat(n, text, gen_sql):
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    payload = {"message": text or "", "generate_sql": ("sql" in (gen_sql or [])), "visualize": True}
    try:
        r = requests.post(f"{BACKEND_URL}/chat", json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        msg = [html.P(data.get("text", ""))]
        if data.get("sql"):
            msg.append(html.Details([
                html.Summary("SQL Preview"),
                html.Pre(data.get("sql"))
            ]))
        fig = go.Figure(data=data.get("plot_spec", {}).get("data", []), layout=data.get("plot_spec", {}).get("layout", {}))
        return msg, fig
    except Exception as e:
        return [html.P(f"Error: {e}")], go.Figure()

@app.callback(
    Output("chat-input", "value"),
    Input({"type": "suggest-btn", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def fill_prompt(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
    try:
        idx = json.loads(prop_id)["index"]
        return suggested_prompts[idx]
    except Exception:
        return dash.no_update

@app.callback(
    Output("profile-graph", "figure"),
    Input("variable-select", "value")
)
def update_profile(var):
    # Fetch a latest profile and plot depth vs variable (mock depth)
    try:
        r = requests.post(f"{BACKEND_URL}/get_profile", json={"float_id": 1}, headers={"Authorization": f"Bearer {AUTH_TOKEN}"})
        p = r.json()
        # Mock vertical profile with synthetic depths
        depths = list(range(0, 2000, 50))
        if var == "temperature":
            vals = [max(0, p.get("temperature", 10) - 0.005*d) for d in depths]
        elif var == "salinity":
            vals = [p.get("salinity", 35) + 0.0005*d for d in depths]
        else:
            vals = [0 for _ in depths]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=vals, y=depths, mode="lines", name=var))
        fig.update_yaxes(autorange="reversed", title="Depth (m)")
        fig.update_xaxes(title=var.title())
        fig.update_layout(height=380, margin=dict(l=40, r=10, t=30, b=40))
        return fig
    except Exception:
        return go.Figure()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
