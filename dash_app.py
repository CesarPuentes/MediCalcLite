import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data_service import DataService

# Initialize data service
data_service = DataService()
df = data_service.df

# Get unique values for dropdowns
active_ingredients = sorted(df['principio_activo'].dropna().unique())
manufacturers = sorted(df['fabricante'].dropna().unique())
concentrations = sorted(df['concentracion'].dropna().unique())
channels = sorted(df['canal'].dropna().unique())
dispensing_units = sorted(df['unidad_de_dispensacion'].dropna().unique())

# Initialize the Dash app
app = dash.Dash(__name__, 
                title='PharmaLens',
                external_stylesheets=[
                    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css'
                ])

# Define the layout
app.layout = html.Div([
    # Navigation bar
    html.Nav([
        html.Div([
            html.A([
                html.I(className="bi bi-capsule me-2"),
                "PharmaLens"
            ], className="navbar-brand", href="#"),
            html.Button([
                html.Span(className="navbar-toggler-icon")
            ], className="navbar-toggler", **{
                'data-bs-toggle': 'collapse',
                'data-bs-target': '#navbarNav',
                'aria-controls': 'navbarNav',
                'aria-expanded': 'false',
                'aria-label': 'Toggle navigation'
            }),
            html.Div([
                html.Ul([
                    html.Li([
                        html.A("Dashboard", className="nav-link", href="#")
                    ], className="nav-item"),
                    html.Li([
                        html.A("Anomaly Detection", className="nav-link", href="#anomaly-tab")
                    ], className="nav-item"),
                    html.Li([
                        html.A("Clustering", className="nav-link", href="#clustering-tab")
                    ], className="nav-item")
                ], className="navbar-nav"),
            ], className="collapse navbar-collapse", id="navbarNav")
        ], className="container-fluid")
    ], className="navbar navbar-expand-lg navbar-light bg-white shadow-sm"),
    
    # Main container
    html.Div([
        # Dashboard header
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H4("Drug Price Analysis Dashboard", className="mb-0")
                    ], className="card-header bg-primary text-white"),
                    html.Div([
                        # Summary statistics cards
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.H6("Total Records", className="card-title text-muted"),
                                        html.H2(f"{len(df)}", className="card-text")
                                    ], className="card-body text-center")
                                ], className="card bg-light mb-3")
                            ], className="col-md-3"),
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.H6("Average Price", className="card-title text-muted"),
                                        html.H2(f"${df['precio_por_tableta'].mean():.2f}", className="card-text")
                                    ], className="card-body text-center")
                                ], className="card bg-light mb-3")
                            ], className="col-md-3"),
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.H6("Price Range", className="card-title text-muted"),
                                        html.H2(f"${df['precio_por_tableta'].min():.2f} - ${df['precio_por_tableta'].max():.2f}", className="card-text")
                                    ], className="card-body text-center")
                                ], className="card bg-light mb-3")
                            ], className="col-md-3"),
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.H6("Active Ingredients", className="card-title text-muted"),
                                        html.H2(f"{len(active_ingredients)}", className="card-text")
                                    ], className="card-body text-center")
                                ], className="card bg-light mb-3")
                            ], className="col-md-3")
                        ], className="row")
                    ], className="card-body")
                ], className="card shadow")
            ], className="col-12")
        ], className="row mb-3"),
        
        # Filters
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H5("Filters", className="mb-0")
                    ], className="card-header"),
                    html.Div([
                        html.Div([
                            # First row of filters
                            html.Div([
                                html.Div([
                                    html.Label("Active Ingredient", className="form-label"),
                                    dcc.Dropdown(
                                        id='active-ingredient',
                                        options=[{'label': 'All Active Ingredients', 'value': 'all'}] + 
                                                [{'label': i, 'value': i} for i in active_ingredients],
                                        value='all',
                                        className="form-select"
                                    )
                                ], className="col-md-4"),
                                html.Div([
                                    html.Label("Manufacturer", className="form-label"),
                                    dcc.Dropdown(
                                        id='manufacturer',
                                        options=[{'label': 'All Manufacturers', 'value': 'all'}] + 
                                                [{'label': m, 'value': m} for m in manufacturers],
                                        value='all',
                                        className="form-select"
                                    )
                                ], className="col-md-4"),
                                html.Div([
                                    html.Label("Concentration", className="form-label"),
                                    dcc.Dropdown(
                                        id='concentration',
                                        options=[{'label': 'All Concentrations', 'value': 'all'}] + 
                                                [{'label': c, 'value': c} for c in concentrations],
                                        value='all',
                                        className="form-select"
                                    )
                                ], className="col-md-4")
                            ], className="row g-3 mb-3"),
                            
                            # Second row of filters
                            html.Div([
                                html.Div([
                                    html.Label("Distribution Channel", className="form-label"),
                                    dcc.Dropdown(
                                        id='channel',
                                        options=[{'label': 'All Channels', 'value': 'all'}] + 
                                                [{'label': c, 'value': c} for c in channels],
                                        value='all',
                                        className="form-select"
                                    )
                                ], className="col-md-4"),
                                html.Div([
                                    html.Label("Price Range", className="form-label"),
                                    dcc.RangeSlider(
                                        id='price-range',
                                        min=0,
                                        max=df['precio_por_tableta'].max(),
                                        value=[0, df['precio_por_tableta'].max()],
                                        marks={0: '$0', int(df['precio_por_tableta'].max()): f'${int(df["precio_por_tableta"].max())}'},
                                        tooltip={"placement": "bottom", "always_visible": True}
                                    )
                                ], className="col-md-4"),
                                html.Div([
                                    html.Label("Visualization Type", className="form-label"),
                                    dcc.RadioItems(
                                        id='viz-type',
                                        options=[
                                            {'label': 'Bar Chart', 'value': 'bar'},
                                            {'label': 'Histogram', 'value': 'histogram'},
                                            {'label': 'Box Plot', 'value': 'box'},
                                            {'label': 'Scatter', 'value': 'scatter'},
                                            {'label': 'Pie Chart', 'value': 'pie'}
                                        ],
                                        value='bar',
                                        className="btn-group",
                                        inputClassName="btn-check",
                                        labelClassName="btn btn-outline-primary",
                                        labelStyle={'display': 'inline-block', 'marginRight': '10px'}
                                    )
                                ], className="col-md-4")
                            ], className="row g-3 mb-3"),
                            
                            # Buttons
                            html.Div([
                                html.Button("Apply Filters", id="apply-filters", className="btn btn-primary me-2"),
                                html.Button("Reset Filters", id="reset-filters", className="btn btn-secondary")
                            ], className="col-12")
                        ], className="row g-3")
                    ], className="card-body")
                ], className="card shadow")
            ], className="col-12")
        ], className="row mb-3"),
        
        # Main visualization and data table
        html.Div([
            # Visualization card
            html.Div([
                html.Div([
                    html.Div([
                        html.H5("Data Visualization", className="mb-0"),
                        html.Div([
                            html.A([
                                html.I(className="bi bi-download"),
                                " Download"
                            ], id="download-chart", className="btn btn-sm btn-outline-primary me-2"),
                            dcc.Download(id="download-chart-file")
                        ], className="btn-group")
                    ], className="card-header d-flex justify-content-between align-items-center"),
                    html.Div([
                        dcc.Loading(
                            id="loading-visualization",
                            type="circle",
                            children=html.Div(id="visualization-container", style={"height": "400px"})
                        )
                    ], className="card-body")
                ], className="card shadow mb-3")
            ], className="col-md-8"),
            
            # Advanced analytics card
            html.Div([
                html.Div([
                    html.Div([
                        html.H5("Advanced Analytics", className="mb-0")
                    ], className="card-header"),
                    html.Div([
                        html.Div([
                            html.A([
                                html.Div([
                                    html.H6("Price Anomaly Detection", className="mb-1"),
                                    html.Small("Find unusually priced medications", className="text-muted"),
                                ]),
                                html.Span("ML", className="badge bg-primary rounded-pill")
                            ], href="#anomaly-section", id="show-anomaly", className="list-group-item list-group-item-action d-flex justify-content-between align-items-center"),
                            html.A([
                                html.Div([
                                    html.H6("Price Clustering", className="mb-1"),
                                    html.Small("Group medications by price segments", className="text-muted"),
                                ]),
                                html.Span("ML", className="badge bg-primary rounded-pill")
                            ], href="#clustering-section", id="show-clustering", className="list-group-item list-group-item-action d-flex justify-content-between align-items-center")
                        ], className="list-group")
                    ], className="card-body")
                ], className="card shadow mb-3"),
                
                # Summary statistics card
                html.Div([
                    html.Div([
                        html.H5("Summary Statistics", className="mb-0")
                    ], className="card-header"),
                    html.Div([
                        html.Div(id="summary-stats", children="Select filters and apply to see statistics.")
                    ], className="card-body")
                ], className="card shadow")
            ], className="col-md-4")
        ], className="row mb-3"),
        
        # Data table
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.H5("Data Table", className="mb-0"),
                        html.Div([
                            html.A([
                                html.I(className="bi bi-download"),
                                " Export"
                            ], id="download-data", className="btn btn-sm btn-outline-primary"),
                            dcc.Download(id="download-data-file")
                        ], className="btn-group")
                    ], className="card-header d-flex justify-content-between align-items-center"),
                    html.Div([
                        dcc.Loading(
                            id="loading-table",
                            type="circle",
                            children=html.Div(id="data-table")
                        )
                    ], className="card-body")
                ], className="card shadow")
            ], className="col-12")
        ], className="row mb-3"),
        
        # ML sections (initially hidden)
        html.Div(id="anomaly-section", style={'display': 'none'}),
        html.Div(id="clustering-section", style={'display': 'none'})
        
    ], className="container-fluid py-3")
])

# Callback to filter and display data
@app.callback(
    [Output('visualization-container', 'children'),
     Output('data-table', 'children'),
     Output('summary-stats', 'children')],
    [Input('apply-filters', 'n_clicks'),
     Input('reset-filters', 'n_clicks')],
    [State('active-ingredient', 'value'),
     State('manufacturer', 'value'),
     State('concentration', 'value'),
     State('channel', 'value'),
     State('price-range', 'value'),
     State('viz-type', 'value')]
)
def update_data(apply_clicks, reset_clicks, active_ingredient, manufacturer, concentration, channel, price_range, viz_type):
    # Get triggered button
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Reset filters if reset button clicked
    if trigger_id == 'reset-filters':
        active_ingredient = 'all'
        manufacturer = 'all'
        concentration = 'all'
        channel = 'all'
        price_range = [0, df['precio_por_tableta'].max()]
        viz_type = 'bar'
    
    # Filter data using data service
    if active_ingredient == 'all':
        active_ingredient = None
    if manufacturer == 'all':
        manufacturer = None
    if concentration == 'all':
        concentration = None
    if channel == 'all':
        channel = None
    
    filtered_df = data_service.filter_data(
        active_ingredient=active_ingredient,
        manufacturer=manufacturer,
        concentration=concentration,
        channel=channel,
        min_price=price_range[0],
        max_price=price_range[1],
        limit=1000
    )
    
    # Create visualization based on type
    visualization = create_visualization(filtered_df, viz_type, active_ingredient)
    
    # Create data table
    table = create_data_table(filtered_df.head(50))
    
    # Create summary statistics
    stats = create_summary_stats(filtered_df)
    
    return visualization, table, stats

# Function to create visualization based on type
def create_visualization(df, viz_type, active_ingredient):
    if df.empty:
        return html.Div("No data available for the selected filters.", className="text-center p-5")
    
    if viz_type == 'bar':
        # Determine what to group by
        if active_ingredient:
            # If active ingredient selected, group by manufacturer
            group_col = 'fabricante'
        else:
            # Otherwise group by active ingredient
            group_col = 'principio_activo'
        
        # Group and calculate mean price
        group_df = df.groupby(group_col)['precio_por_tableta'].mean().reset_index()
        group_df = group_df.sort_values('precio_por_tableta', ascending=False).head(20)
        
        fig = px.bar(
            group_df, 
            x=group_col, 
            y='precio_por_tableta',
            labels={'precio_por_tableta': 'Price per Tablet ($)', group_col: group_col.capitalize()},
            title=f'Average Price by {group_col.capitalize()}',
            color='precio_por_tableta',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=400,
            margin=dict(l=50, r=20, t=50, b=100)
        )
        
        return dcc.Graph(figure=fig, style={'height': '100%'})
    
    elif viz_type == 'histogram':
        fig = px.histogram(
            df, 
            x='precio_por_tableta', 
            nbins=20,
            labels={'precio_por_tableta': 'Price per Tablet ($)', 'count': 'Number of Products'},
            title='Price Distribution Histogram',
            color_discrete_sequence=['#3498db']
        )
        
        fig.update_layout(
            height=400,
            margin=dict(l=50, r=20, t=50, b=50)
        )
        
        return dcc.Graph(figure=fig, style={'height': '100%'})
    
    elif viz_type == 'box':
        # Determine what to group by
        if active_ingredient:
            # If active ingredient selected, group by manufacturer
            group_col = 'fabricante'
        else:
            # Otherwise group by active ingredient
            group_col = 'principio_activo'
        
        # Limit to top groups by count for readability
        top_groups = df[group_col].value_counts().head(10).index.tolist()
        box_df = df[df[group_col].isin(top_groups)]
        
        fig = px.box(
            box_df, 
            x='precio_por_tableta', 
            y=group_col,
            labels={'precio_por_tableta': 'Price per Tablet ($)', group_col: group_col.capitalize()},
            title=f'Price Distribution by {group_col.capitalize()}',
            color_discrete_sequence=['#3498db']
        )
        
        fig.update_layout(
            height=400,
            margin=dict(l=150, r=20, t=50, b=50)
        )
        
        return dcc.Graph(figure=fig, style={'height': '100%'})
    
    elif viz_type == 'scatter':
        # Create scatter plot
        fig = px.scatter(
            df, 
            x='fabricante', 
            y='precio_por_tableta',
            labels={'precio_por_tableta': 'Price per Tablet ($)', 'fabricante': 'Manufacturer'},
            title='Price Scatter Plot',
            color='precio_por_tableta',
            color_continuous_scale='Blues',
            hover_data=['nombre_comercial', 'principio_activo', 'concentracion']
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=400,
            margin=dict(l=50, r=20, t=50, b=100)
        )
        
        return dcc.Graph(figure=fig, style={'height': '100%'})
    
    elif viz_type == 'pie':
        # Determine what to group by
        if active_ingredient:
            # If active ingredient selected, group by manufacturer
            group_col = 'fabricante'
        else:
            # Otherwise group by active ingredient
            group_col = 'principio_activo'
        
        # Group and count
        group_counts = df[group_col].value_counts().reset_index()
        group_counts.columns = [group_col, 'count']
        
        # Limit to top 10 groups for readability
        group_counts = group_counts.head(10)
        
        fig = px.pie(
            group_counts, 
            values='count', 
            names=group_col,
            title=f'Distribution by {group_col.capitalize()}',
        )
        
        fig.update_layout(
            height=400,
            margin=dict(l=50, r=20, t=50, b=50)
        )
        
        return dcc.Graph(figure=fig, style={'height': '100%'})
    
    # Default if no visualization type matches
    return html.Div("Select a visualization type", className="text-center p-5")

# Function to create data table
def create_data_table(df):
    if df.empty:
        return html.Div("No data available for the selected filters.", className="text-center p-5")
    
    # Create a Dash DataTable
    table = dash_table.DataTable(
        id='table',
        columns=[
            {"name": "Name", "id": "nombre_comercial"},
            {"name": "Active Ingredient", "id": "principio_activo"},
            {"name": "Manufacturer", "id": "fabricante"},
            {"name": "Concentration", "id": "concentracion"},
            {"name": "Price", "id": "precio_por_tableta", "type": "numeric", "format": {"specifier": "$.2f"}}
        ],
        data=df.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ]
    )
    
    return table

# Function to create summary statistics
def create_summary_stats(df):
    if df.empty:
        return html.Div("No data available for the selected filters.", className="text-center p-5")
    
    # Calculate statistics
    count = len(df)
    min_price = df['precio_por_tableta'].min()
    max_price = df['precio_por_tableta'].max()
    avg_price = df['precio_por_tableta'].mean()
    median_price = df['precio_por_tableta'].median()
    
    # Create HTML table for statistics
    stats = html.Div([
        html.Table([
            html.Tbody([
                html.Tr([html.Th("Records:"), html.Td(f"{count}")]),
                html.Tr([html.Th("Min Price:"), html.Td(f"${min_price:.2f}")]),
                html.Tr([html.Th("Max Price:"), html.Td(f"${max_price:.2f}")]),
                html.Tr([html.Th("Average Price:"), html.Td(f"${avg_price:.2f}")]),
                html.Tr([html.Th("Median Price:"), html.Td(f"${median_price:.2f}")])
            ])
        ], className="table table-sm")
    ])
    
    return stats

# Callback for showing anomaly detection section
@app.callback(
    Output('anomaly-section', 'style'),
    Input('show-anomaly', 'n_clicks'),
    prevent_initial_call=True
)
def show_anomaly_section(n_clicks):
    if n_clicks:
        return {'display': 'block'}
    return {'display': 'none'}

# Callback for showing clustering section
@app.callback(
    Output('clustering-section', 'style'),
    Input('show-clustering', 'n_clicks'),
    prevent_initial_call=True
)
def show_clustering_section(n_clicks):
    if n_clicks:
        return {'display': 'block'}
    return {'display': 'none'}

# Callback for downloading chart
@app.callback(
    Output('download-chart-file', 'data'),
    Input('download-chart', 'n_clicks'),
    prevent_initial_call=True
)
def download_chart(n_clicks):
    return dict(
        content="Chart download not implemented in this example",
        filename="chart.txt"
    )

# Callback for downloading data
@app.callback(
    Output('download-data-file', 'data'),
    Input('download-data', 'n_clicks'),
    [State('active-ingredient', 'value'),
     State('manufacturer', 'value'),
     State('concentration', 'value'),
     State('channel', 'value'),
     State('price-range', 'value')],
    prevent_initial_call=True
)
def download_data(n_clicks, active_ingredient, manufacturer, concentration, channel, price_range):
    # Convert 'all' to None for data service
    if active_ingredient == 'all':
        active_ingredient = None
    if manufacturer == 'all':
        manufacturer = None
    if concentration == 'all':
        concentration = None
    if channel == 'all':
        channel = None
    
    # Filter data using data service
    filtered_df = data_service.filter_data(
        active_ingredient=active_ingredient,
        manufacturer=manufacturer,
        concentration=concentration,
        channel=channel,
        min_price=price_range[0],
        max_price=price_range[1]
    )
    
    # Return CSV download
    return dcc.send_data_frame(filtered_df.to_csv, "drug_prices_filtered.csv")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)