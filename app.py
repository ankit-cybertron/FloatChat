# app.py
import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import random
from datetime import datetime, timedelta

# Sample data generation
def generate_float_data():
    floats = []
    for i in range(10):
        float_id = 57000 + i
        lat = random.uniform(35, 50)
        lon = random.uniform(-30, -15)
        date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%b %d, %Y')
        temp = random.uniform(5, 20)
        floats.append({
            'id': float_id,
            'lat': lat,
            'lon': lon,
            'date': date,
            'temp': temp
        })
    return floats

def generate_profile_data():
    pressure = list(range(0, 101, 10))
    temperature = [18.5 - (p * 0.08) + random.uniform(-0.5, 0.5) for p in pressure]
    salinity = [35.0 + (p * 0.01) + random.uniform(-0.1, 0.1) for p in pressure]
    return pressure, temperature, salinity

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Sample data
float_data = generate_float_data()
pressure, temperature, salinity = generate_profile_data()

# App layout
app.layout = html.Div([
    # Top Navigation
    html.Nav(className='navbar', children=[
        html.Div(className='navbar-brand', children=[
            html.Div(className='logo', children='FDE'),
            html.Div(className='brand-text', children=[
                html.H1('Float Data Explorer'),
                html.P('Oceanographic Data Visualization')
            ])
        ]),
        html.Div(className='navbar-controls', children=[
            html.Div(className='search-bar', children=[
                html.Span(className='search-icon', children='🔍'),
                dcc.Input(
                    id='search-input',
                    type='text',
                    placeholder='Search floats or profiles...',
                    className='search-input'
                )
            ]),
            html.Button('🌙', id='theme-toggle', className='theme-toggle'),
            html.Button('⚙️', id='settings-btn', className='settings-btn')
        ])
    ]),
    
    # Main Content
    html.Div(className='main-content', children=[
        # Chat Assistant Panel
        html.Aside(className='chat-panel', id='chat-panel', children=[
            html.Div(className='chat-header', children=[
                html.Div(className='chat-title', children='Data Assistant'),
                html.Div(className='chat-controls', children=[
                    html.Button('🗑️', id='clear-chat', className='clear-chat'),
                    html.Button('◀', id='toggle-chat', className='toggle-chat')
                ])
            ]),
            html.Div(className='chat-messages', id='chat-messages', children=[
                html.Div(className='message assistant-message', children=[
                    html.P('Hello! I can help you explore float data. What would you like to know?')
                ])
            ]),
            html.Div(className='quick-actions', children=[
                html.Button('🌡️ Temperature', className='pill-btn', id='temp-btn'),
                html.Button('🧭 Profile Plot', className='pill-btn', id='profile-btn'),
                html.Button('📊 X-Y Plot', className='pill-btn', id='xy-btn'),
                html.Button('🌊 Salinity', className='pill-btn', id='salinity-btn')
            ]),
            html.Div(className='sql-toggle', children=[
                html.Span('SQL Mode'),
                dcc.Checklist(
                    id='sql-toggle',
                    options=[{'label': '', 'value': 'sql-mode'}],
                    value=[],
                    className='sql-checkbox'
                )
            ]),
            html.Div(className='chat-input', children=[
                dcc.Input(
                    id='chat-input',
                    type='text',
                    placeholder='Type a message...',
                    className='chat-input-field'
                ),
                html.Button('Send', id='send-btn', className='send-btn')
            ]),
            html.Div(className='typing-indicator', id='typing-indicator', children=[
                html.Span('Assistant is typing'),
                html.Span(className='typing-dots', children=[
                    html.Span('.'),
                    html.Span('.'),
                    html.Span('.')
                ])
            ])
        ]),
        
        # Map Section
        html.Section(className='map-section', children=[
            html.Div(className='map-container', children=[
                dcc.Graph(
                    id='map-plot',
                    config={'displayModeBar': False},
                    style={'height': '100%', 'width': '100%'}
                ),
                html.Div(className='map-controls', children=[
                    html.Button('🎬', className='map-btn', id='animation-btn'),
                    html.Button('⬜', className='map-btn', id='region-btn'),
                    html.Button('🔄', className='map-btn', id='reset-btn')
                ]),
                html.Div(className='map-legend', children=[
                    html.Div(className='legend-title', children='Temperature (°C)'),
                    html.Div(className='legend-scale'),
                    html.Div(className='legend-labels', children=[
                        html.Span('-2'),
                        html.Span('10'),
                        html.Span('22'),
                        html.Span('34')
                    ])
                ])
            ])
        ]),
        
        # Visualization Panel
        html.Aside(className='viz-panel', id='viz-panel', children=[
            html.Div(className='viz-header', children=[
                html.H3('Data Visualization')
            ]),
            html.Div(className='plot-tabs', children=[
                html.Button('Profile Plot', className='tab active', id='profile-tab'),
                html.Button('Time Series', className='tab', id='timeseries-tab'),
                html.Button('Comparison', className='tab', id='comparison-tab')
            ]),
            html.Div(className='viz-controls', children=[
                html.Div(className='control-group', children=[
                    html.Label('X-Axis', className='control-label'),
                    html.Div(className='segmented-control', children=[
                        html.Button('Pressure', className='segmented-btn active', id='x-pressure'),
                        html.Button('Depth', className='segmented-btn', id='x-depth'),
                        html.Button('Time', className='segmented-btn', id='x-time')
                    ])
                ]),
                html.Div(className='control-group', children=[
                    html.Label('Y-Axis', className='control-label'),
                    dcc.Dropdown(
                        id='y-axis-dropdown',
                        options=[
                            {'label': 'Temperature', 'value': 'temp'},
                            {'label': 'Salinity', 'value': 'salinity'},
                            {'label': 'Oxygen', 'value': 'oxygen'},
                            {'label': 'Chlorophyll', 'value': 'chlorophyll'}
                        ],
                        value='temp',
                        className='styled-dropdown'
                    )
                ]),
                html.Div(className='control-group', children=[
                    html.Label('View Mode', className='control-label'),
                    html.Div(className='segmented-control', children=[
                        html.Button('Lines', className='segmented-btn active', id='view-lines'),
                        html.Button('Scatter', className='segmented-btn', id='view-scatter'),
                        html.Button('Both', className='segmented-btn', id='view-both')
                    ])
                ])
            ]),
            html.Div(className='plot-container', children=[
                dcc.Graph(id='data-plot'),
                html.Div(className='loading-skeleton', id='plot-loading')
            ]),
            html.Div(className='viz-actions', children=[
                html.Button('📥 Export Data', className='action-btn', id='export-btn'),
                html.Button('📊 Add Annotation', className='action-btn', id='annotation-btn'),
                html.Button('🔗 Share Plot', className='action-btn', id='share-btn')
            ])
        ])
    ]),
    
    # Store components for state management
    dcc.Store(id='chat-history', data=[]),
    dcc.Store(id='theme-store', data='light'),
    dcc.Store(id='selected-float', data=None),
    
    # CSS
    html.Link(rel='stylesheet', href='https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap')
])

# Add the same CSS as before (would be in a separate file in production)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Add all the CSS from the previous implementation here */
            :root {
                --primary: #0ea5e9;
                --primary-dark: #0284c7;
                --secondary: #14b8a6;
                --dark-bg: #0f172a;
                --dark-card: #1e293b;
                --dark-text: #f1f5f9;
                --light-bg: #f8fafc;
                --light-card: #ffffff;
                --light-text: #334155;
                --border-radius: 12px;
                --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                --transition: all 0.3s ease;
            }
            
            /* ... (include all the CSS from the previous implementation) ... */
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

# Callbacks for interactivity
@app.callback(
    Output('map-plot', 'figure'),
    Input('theme-store', 'data')
)
def update_map(theme):
    # Create map figure with sample data
    fig = px.scatter_mapbox(
        float_data,
        lat="lat",
        lon="lon",
        hover_name="id",
        hover_data={"lat": True, "lon": True, "date": True, "temp": True},
        color="temp",
        color_continuous_scale="Viridis",
        size_max=15,
        zoom=3
    )
    
    fig.update_layout(
        mapbox_style="carto-positron" if theme == "light" else "carto-darkmatter",
        margin={"r":0,"t":0,"l":0,"b":0},
        height=600
    )
    
    return fig

@app.callback(
    Output('data-plot', 'figure'),
    [Input('y-axis-dropdown', 'value'),
     Input('theme-store', 'data')]
)
def update_plot(y_axis, theme):
    # Create profile plot based on selection
    if y_axis == 'temp':
        y_data = temperature
        y_title = 'Temperature (°C)'
    else:  # salinity as default for other options
        y_data = salinity
        y_title = 'Salinity (PSU)'
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=y_data,
        y=pressure,
        mode='lines+markers',
        name='Profile',
        line=dict(color='#0ea5e9', width=3),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=f'{y_title} vs Pressure',
        xaxis_title=y_title,
        yaxis_title='Pressure (dbar)',
        yaxis=dict(autorange='reversed'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#334155' if theme == 'light' else '#f1f5f9')
    )
    
    return fig

@app.callback(
    [Output('chat-messages', 'children'),
     Output('chat-input', 'value')],
    [Input('send-btn', 'n_clicks'),
     Input('temp-btn', 'n_clicks'),
     Input('profile-btn', 'n_clicks'),
     Input('xy-btn', 'n_clicks'),
     Input('salinity-btn', 'n_clicks')],
    [State('chat-input', 'value'),
     State('chat-messages', 'children')]
)
def update_chat(send_clicks, temp_clicks, profile_clicks, xy_clicks, salinity_clicks, input_value, current_messages):
    triggered_id = ctx.triggered_id if ctx.triggered_id else None
    
    if not current_messages:
        current_messages = []
    
    if triggered_id == 'send-btn' and input_value:
        # Add user message
        user_message = html.Div(className='message user-message', children=[
            html.P(input_value)
        ])
        current_messages.append(user_message)
        
        # Add assistant response (simulated)
        assistant_response = f"I've processed your request: '{input_value}'. Here are the results."
        assistant_message = html.Div(className='message assistant-message', children=[
            html.P(assistant_response)
        ])
        current_messages.append(assistant_message)
        
        return current_messages, ''
    
    elif triggered_id and triggered_id.endswith('-btn') and triggered_id != 'send-btn':
        # Handle quick action buttons
        action_map = {
            'temp-btn': 'temperature data',
            'profile-btn': 'profile plot',
            'xy-btn': 'X-Y plot',
            'salinity-btn': 'salinity data'
        }
        
        action = action_map.get(triggered_id, 'data')
        user_message = html.Div(className='message user-message', children=[
            html.P(f"Show me {action}")
        ])
        current_messages.append(user_message)
        
        assistant_message = html.Div(className='message assistant-message', children=[
            html.P(f"Displaying {action} in the visualization panel.")
        ])
        current_messages.append(assistant_message)
        
        return current_messages, ''
    
    return current_messages, input_value

@app.callback(
    Output('theme-store', 'data'),
    Input('theme-toggle', 'n_clicks'),
    State('theme-store', 'data')
)
def toggle_theme(clicks, current_theme):
    if clicks:
        return 'dark' if current_theme == 'light' else 'light'
    return current_theme

@app.callback(
    Output('chat-panel', 'className'),
    Input('toggle-chat', 'n_clicks'),
    State('chat-panel', 'className')
)
def toggle_chat_panel(clicks, current_class):
    if clicks:
        if 'collapsed' in current_class:
            return current_class.replace('collapsed', '').strip()
        else:
            return current_class + ' collapsed'
    return current_class

if __name__ == '__main__':
    app.run(debug=True)