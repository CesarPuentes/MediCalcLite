from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the data once when the application starts
DATA_FILE = 'Clicsalud__Term_metro_de_Precios_de_Medicamentos_20250228.csv'
df = None

def load_data():
    global df
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, encoding='utf-8')
        # Convert price column to numeric, handling errors
        df['precio_por_tableta'] = pd.to_numeric(df['precio_por_tableta'], errors='coerce')
        # Drop rows with NaN prices
        df = df.dropna(subset=['precio_por_tableta'])
        print(f"Loaded {len(df)} records from {DATA_FILE}")
    else:
        print(f"Warning: {DATA_FILE} not found")
        df = pd.DataFrame()

# Load data at startup
load_data()

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """Return metadata about the dataset"""
    if df is None or df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
    
    return jsonify({
        'status': 'success',
        'total_records': len(df),
        'active_ingredients': df['principio_activo'].dropna().unique().tolist(),
        'manufacturers': df['fabricante'].dropna().unique().tolist(),
        'concentrations': df['concentracion'].dropna().unique().tolist(),
        'channels': df['canal'].dropna().unique().tolist(),
        'dispensing_units': df['unidad_de_dispensacion'].dropna().unique().tolist(),
        'price_range': {
            'min': float(df['precio_por_tableta'].min()),
            'max': float(df['precio_por_tableta'].max()),
            'avg': float(df['precio_por_tableta'].mean())
        },
        'columns': df.columns.tolist()
    })

@app.route('/api/data', methods=['GET'])
def get_data():
    """Return filtered data based on query parameters"""
    if df is None or df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
    
    # Get filter parameters
    active_ingredient = request.args.get('active_ingredient')
    manufacturer = request.args.get('manufacturer')
    concentration = request.args.get('concentration')
    channel = request.args.get('channel')
    dispensing_unit = request.args.get('dispensing_unit')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort_by', 'precio_por_tableta')
    sort_order = request.args.get('sort_order', 'asc')
    limit = request.args.get('limit', 50, type=int)
    
    # Apply filters
    filtered_df = df.copy()
    
    if active_ingredient:
        filtered_df = filtered_df[filtered_df['principio_activo'] == active_ingredient]
    
    if manufacturer:
        filtered_df = filtered_df[filtered_df['fabricante'] == manufacturer]
    
    if concentration:
        filtered_df = filtered_df[filtered_df['concentracion'] == concentration]
    
    if channel:
        filtered_df = filtered_df[filtered_df['canal'] == channel]
    
    if dispensing_unit:
        filtered_df = filtered_df[filtered_df['unidad_de_dispensacion'] == dispensing_unit]
    
    if min_price is not None:
        filtered_df = filtered_df[filtered_df['precio_por_tableta'] >= min_price]
    
    if max_price is not None:
        filtered_df = filtered_df[filtered_df['precio_por_tableta'] <= max_price]
    
    # Apply sorting
    if sort_by in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=(sort_order.lower() == 'asc'))
    
    # Apply limit
    if limit:
        filtered_df = filtered_df.head(limit)
    
    # Convert to JSON-compatible format
    result = filtered_df.to_dict(orient='records')
    
    return jsonify({
        'status': 'success',
        'count': len(result),
        'data': result
    })

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Return summary statistics based on filters"""
    if df is None or df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
        
    # Get filter parameters
    active_ingredient = request.args.get('active_ingredient')
    manufacturer = request.args.get('manufacturer')
    
    # Apply filters
    filtered_df = df.copy()
    
    if active_ingredient:
        filtered_df = filtered_df[filtered_df['principio_activo'] == active_ingredient]
    
    if manufacturer:
        filtered_df = filtered_df[filtered_df['fabricante'] == manufacturer]
    
    # Calculate statistics
    stats = {
        'count': len(filtered_df),
        'price_stats': {
            'min': float(filtered_df['precio_por_tableta'].min()),
            'max': float(filtered_df['precio_por_tableta'].max()),
            'mean': float(filtered_df['precio_por_tableta'].mean()),
            'median': float(filtered_df['precio_por_tableta'].median()),
            'std': float(filtered_df['precio_por_tableta'].std())
        }
    }
    
    # Add manufacturer breakdown if active ingredient is specified
    if active_ingredient:
        manufacturer_stats = filtered_df.groupby('fabricante').agg({
            'precio_por_tableta': ['count', 'min', 'max', 'mean']
        }).reset_index()
        
        manufacturer_stats.columns = ['manufacturer', 'count', 'min_price', 'max_price', 'avg_price']
        stats['manufacturers'] = manufacturer_stats.to_dict(orient='records')
    
    # Add active ingredient breakdown if manufacturer is specified
    if manufacturer:
        ingredient_stats = filtered_df.groupby('principio_activo').agg({
            'precio_por_tableta': ['count', 'min', 'max', 'mean']
        }).reset_index()
        
        ingredient_stats.columns = ['active_ingredient', 'count', 'min_price', 'max_price', 'avg_price']
        stats['active_ingredients'] = ingredient_stats.to_dict(orient='records')
    
    return jsonify({
        'status': 'success',
        'summary': stats
    })

@app.route('/api/histogram', methods=['GET'])
def get_histogram():
    """Return histogram data for prices"""
    if df is None or df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
    
    # Get filter parameters
    active_ingredient = request.args.get('active_ingredient')
    manufacturer = request.args.get('manufacturer')
    bins = request.args.get('bins', 10, type=int)
    
    # Apply filters
    filtered_df = df.copy()
    
    if active_ingredient:
        filtered_df = filtered_df[filtered_df['principio_activo'] == active_ingredient]
    
    if manufacturer:
        filtered_df = filtered_df[filtered_df['fabricante'] == manufacturer]
    
    # Calculate histogram
    hist, bin_edges = np.histogram(filtered_df['precio_por_tableta'], bins=bins)
    
    # Format histogram data
    histogram_data = []
    for i in range(len(hist)):
        histogram_data.append({
            'bin': f"{bin_edges[i]:.2f} - {bin_edges[i+1]:.2f}",
            'binStart': float(bin_edges[i]),
            'binEnd': float(bin_edges[i+1]),
            'count': int(hist[i]),
            'normalizedCount': float(hist[i] / len(filtered_df)) if len(filtered_df) > 0 else 0
        })
    
    return jsonify({
        'status': 'success',
        'histogram': histogram_data
    })

@app.route('/api/boxplot', methods=['GET'])
def get_boxplot():
    """Return boxplot data grouped by a specific column"""
    if df is None or df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
    
    # Get parameters
    group_by = request.args.get('group_by', 'fabricante')
    active_ingredient = request.args.get('active_ingredient')
    limit = request.args.get('limit', 10, type=int)
    
    # Apply filters
    filtered_df = df.copy()
    
    if active_ingredient and group_by != 'principio_activo':
        filtered_df = filtered_df[filtered_df['principio_activo'] == active_ingredient]
    
    # Group by the specified column
    if group_by in filtered_df.columns:
        # Calculate boxplot statistics for each group
        boxplot_data = []
        
        # Group by the specified column
        groups = filtered_df.groupby(group_by)
        
        # Process each group
        for name, group in groups:
            # Skip groups with too few data points
            if len(group) < 5:
                continue
                
            prices = group['precio_por_tableta'].sort_values()
            
            boxplot_data.append({
                'name': name,
                'min': float(prices.min()),
                'q1': float(prices.quantile(0.25)),
                'median': float(prices.median()),
                'q3': float(prices.quantile(0.75)),
                'max': float(prices.max()),
                'count': len(group)
            })
        
        # Sort by median and limit results
        boxplot_data.sort(key=lambda x: x['median'], reverse=True)
        boxplot_data = boxplot_data[:limit]
        
        return jsonify({
            'status': 'success',
            'boxplot': boxplot_data
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Column {group_by} not found'
        }), 400

# Machine Learning Endpoints

@app.route('/api/ml/clusters', methods=['GET'])
def get_clusters():
    """Perform k-means clustering on the data"""
    if df is None or df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
    
    # Get parameters
    active_ingredient = request.args.get('active_ingredient')
    n_clusters = request.args.get('n_clusters', 3, type=int)
    
    # Apply filters
    filtered_df = df.copy()
    
    if active_ingredient:
        filtered_df = filtered_df[filtered_df['principio_activo'] == active_ingredient]
    
    # Prepare data for clustering
    X = filtered_df[['precio_por_tableta']].copy()
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Perform clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    filtered_df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Calculate cluster statistics
    cluster_stats = []
    for i in range(n_clusters):
        cluster_df = filtered_df[filtered_df['cluster'] == i]
        cluster_stats.append({
            'cluster_id': int(i),
            'count': int(len(cluster_df)),
            'min_price': float(cluster_df['precio_por_tableta'].min()),
            'max_price': float(cluster_df['precio_por_tableta'].max()),
            'avg_price': float(cluster_df['precio_por_tableta'].mean()),
            'center': float(kmeans.cluster_centers_[i][0] * scaler.scale_[0] + scaler.mean_[0])
        })
    
    # Add cluster information to the dataset
    result = []
    for _, row in filtered_df.head(100).iterrows():
        result.append({
            'id': int(row.name),
            'nombre_comercial': row['nombre_comercial'],
            'principio_activo': row['principio_activo'],
            'fabricante': row['fabricante'],
            'precio_por_tableta': float(row['precio_por_tableta']),
            'cluster': int(row['cluster'])
        })
    
    return jsonify({
        'status': 'success',
        'clusters': cluster_stats,
        'data_sample': result
    })

@app.route('/api/ml/anomalies', methods=['GET'])
def get_anomalies():
    """Detect price anomalies using Isolation Forest"""
    if df is None or df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
    
    # Get parameters
    active_ingredient = request.args.get('active_ingredient')
    contamination = request.args.get('contamination', 0.05, type=float)
    
    # Apply filters
    filtered_df = df.copy()
    
    if active_ingredient:
        filtered_df = filtered_df[filtered_df['principio_activo'] == active_ingredient]
    
    # Prepare data for anomaly detection
    X = filtered_df[['precio_por_tableta']].copy()
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Perform anomaly detection
    isolation_forest = IsolationForest(contamination=contamination, random_state=42)
    filtered_df['anomaly'] = isolation_forest.fit_predict(X_scaled)
    
    # -1 indicates anomaly, 1 indicates normal
    filtered_df['anomaly'] = filtered_df['anomaly'].map({1: 0, -1: 1})
    
    # Get anomalies
    anomalies = filtered_df[filtered_df['anomaly'] == 1].sort_values('precio_por_tableta', ascending=False)
    
    # Format anomalies
    anomaly_data = []
    for _, row in anomalies.iterrows():
        anomaly_data.append({
            'id': int(row.name),
            'nombre_comercial': row['nombre_comercial'],
            'principio_activo': row['principio_activo'],
            'fabricante': row['fabricante'],
            'precio_por_tableta': float(row['precio_por_tableta']),
            'is_anomaly': bool(row['anomaly'])
        })
    
    # Calculate statistics
    normal_prices = filtered_df[filtered_df['anomaly'] == 0]['precio_por_tableta']
    anomaly_prices = filtered_df[filtered_df['anomaly'] == 1]['precio_por_tableta']
    
    stats = {
        'normal_count': int(len(normal_prices)),
        'anomaly_count': int(len(anomaly_prices)),
        'normal_avg_price': float(normal_prices.mean()) if len(normal_prices) > 0 else 0,
        'anomaly_avg_price': float(anomaly_prices.mean()) if len(anomaly_prices) > 0 else 0,
        'price_threshold_upper': float(normal_prices.mean() + 2 * normal_prices.std()) if len(normal_prices) > 0 else 0,
        'price_threshold_lower': float(normal_prices.mean() - 2 * normal_prices.std()) if len(normal_prices) > 0 else 0
    }
    
    return jsonify({
        'status': 'success',
        'statistics': stats,
        'anomalies': anomaly_data
    })

# Run the app
if __name__ == '__main__':
    app.run(debug=True)