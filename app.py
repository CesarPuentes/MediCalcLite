from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import os
from data_service import DataService

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize data service
data_service = DataService()

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """Return metadata about the dataset"""
    if data_service.df is None or data_service.df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
    
    return jsonify({
        'status': 'success',
        'total_records': len(data_service.df),
        'active_ingredients': data_service.df['principio_activo'].dropna().unique().tolist(),
        'manufacturers': data_service.df['fabricante'].dropna().unique().tolist(),
        'concentrations': data_service.df['concentracion'].dropna().unique().tolist(),
        'channels': data_service.df['canal'].dropna().unique().tolist(),
        'dispensing_units': data_service.df['unidad_de_dispensacion'].dropna().unique().tolist(),
        'price_range': {
            'min': float(data_service.df['precio_por_tableta'].min()),
            'max': float(data_service.df['precio_por_tableta'].max()),
            'avg': float(data_service.df['precio_por_tableta'].mean())
        },
        'columns': data_service.df.columns.tolist()
    })

@app.route('/api/data', methods=['GET'])
def get_data():
    """Return filtered data based on query parameters"""
    if data_service.df is None or data_service.df.empty:
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
    filtered_df = data_service.filter_data(
        active_ingredient=active_ingredient,
        manufacturer=manufacturer,
        concentration=concentration,
        channel=channel,
        dispensing_unit=dispensing_unit,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit
    )
    
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
    if data_service.df is None or data_service.df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
        
    # Get filter parameters
    active_ingredient = request.args.get('active_ingredient')
    manufacturer = request.args.get('manufacturer')
    
    # Get stats
    stats = data_service.get_summary_stats(active_ingredient, manufacturer)
    
    return jsonify({
        'status': 'success',
        'summary': stats
    })

@app.route('/api/histogram', methods=['GET'])
def get_histogram():
    """Return histogram data for prices"""
    if data_service.df is None or data_service.df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
    
    # Get filter parameters
    active_ingredient = request.args.get('active_ingredient')
    manufacturer = request.args.get('manufacturer')
    bins = request.args.get('bins', 10, type=int)
    
    # Get histogram data
    histogram_data = data_service.get_histogram_data(active_ingredient, manufacturer, bins)
    
    return jsonify({
        'status': 'success',
        'histogram': histogram_data
    })

@app.route('/api/boxplot', methods=['GET'])
def get_boxplot():
    """Return boxplot data grouped by a specific column"""
    if data_service.df is None or data_service.df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
    
    # Get parameters
    group_by = request.args.get('group_by', 'fabricante')
    active_ingredient = request.args.get('active_ingredient')
    limit = request.args.get('limit', 10, type=int)
    
    # Get boxplot data
    boxplot_data = data_service.get_boxplot_data(group_by, active_ingredient, limit)
    
    if isinstance(boxplot_data, dict) and 'error' in boxplot_data:
        return jsonify({
            'status': 'error',
            'message': boxplot_data['error']
        }), 400
    
    return jsonify({
        'status': 'success',
        'boxplot': boxplot_data
    })

# Machine Learning Endpoints

@app.route('/api/ml/clusters', methods=['GET'])
def get_clusters():
    """Perform k-means clustering on the data"""
    if data_service.df is None or data_service.df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
    
    # Get parameters
    active_ingredient = request.args.get('active_ingredient')
    n_clusters = request.args.get('n_clusters', 3, type=int)
    
    # Get clustering results
    clustering_results = data_service.get_clustering(active_ingredient, n_clusters)
    
    return jsonify({
        'status': 'success',
        'clusters': clustering_results['cluster_stats'],
        'data_sample': clustering_results['data_sample']
    })

@app.route('/api/ml/anomalies', methods=['GET'])
def get_anomalies():
    """Detect price anomalies using Isolation Forest"""
    if data_service.df is None or data_service.df.empty:
        return jsonify({
            'status': 'error',
            'message': 'No data available'
        }), 500
    
    # Get parameters
    active_ingredient = request.args.get('active_ingredient')
    contamination = request.args.get('contamination', 0.05, type=float)
    
    # Get anomaly detection results
    anomaly_results = data_service.get_anomalies(active_ingredient, contamination)
    
    return jsonify({
        'status': 'success',
        'statistics': anomaly_results['stats'],
        'anomalies': anomaly_results['anomaly_data']
    })

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)