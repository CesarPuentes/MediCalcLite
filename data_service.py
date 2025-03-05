import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import os

class DataService:
    """
    Service to handle data operations for the drug price analysis application
    """
    
    def __init__(self, data_file='./Clicsalud_-_Term_metro_de_Precios_de_Medicamentos_20250228.csv'):
        """Initialize the data service and load the data"""
        self.DATA_FILE = data_file
        self.df = self.load_data()
    
    def load_data(self):
        """Load data from CSV file"""
        if os.path.exists(self.DATA_FILE):
            df = pd.read_csv(self.DATA_FILE, encoding='utf-8')
            # Convert price column to numeric, handling errors
            df['precio_por_tableta'] = pd.to_numeric(df['precio_por_tableta'], errors='coerce')
            # Drop rows with NaN prices
            df = df.dropna(subset=['precio_por_tableta'])
            print(f"Loaded {len(df)} records from {self.DATA_FILE}")
            return df
        else:
            print(f"Warning: {self.DATA_FILE} not found")
            return pd.DataFrame()
    
    def filter_data(self, active_ingredient=None, manufacturer=None, concentration=None, 
                   channel=None, dispensing_unit=None, min_price=None, max_price=None,
                   sort_by='precio_por_tableta', sort_order='asc', limit=50):
        """Filter the dataset based on parameters"""
        filtered_df = self.df.copy()
        
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
            
        return filtered_df
    
    def get_summary_stats(self, active_ingredient=None, manufacturer=None):
        """Get summary statistics based on filters"""
        filtered_df = self.filter_data(active_ingredient=active_ingredient, manufacturer=manufacturer)
        
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
            
        return stats
    
    def get_histogram_data(self, active_ingredient=None, manufacturer=None, bins=10):
        """Get histogram data for prices"""
        filtered_df = self.filter_data(active_ingredient=active_ingredient, manufacturer=manufacturer)
        
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
            
        return histogram_data
    
    def get_boxplot_data(self, group_by='fabricante', active_ingredient=None, limit=10):
        """Get boxplot data grouped by a specific column"""
        filtered_df = self.filter_data(active_ingredient=active_ingredient)
        
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
            
            return boxplot_data
        else:
            return {'error': f'Column {group_by} not found'}
    
    def get_clustering(self, active_ingredient=None, n_clusters=3):
        """Perform k-means clustering on the data"""
        filtered_df = self.filter_data(active_ingredient=active_ingredient)
        
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
        data_sample = []
        for _, row in filtered_df.head(100).iterrows():
            data_sample.append({
                'id': int(row.name),
                'nombre_comercial': row['nombre_comercial'],
                'principio_activo': row['principio_activo'],
                'fabricante': row['fabricante'],
                'precio_por_tableta': float(row['precio_por_tableta']),
                'cluster': int(row['cluster'])
            })
            
        return {
            'cluster_stats': cluster_stats,
            'data_sample': data_sample
        }
    
    def get_anomalies(self, active_ingredient=None, contamination=0.05):
        """Detect price anomalies using Isolation Forest"""
        filtered_df = self.filter_data(active_ingredient=active_ingredient)
        
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
        
        return {
            'stats': stats,
            'anomaly_data': anomaly_data
        }