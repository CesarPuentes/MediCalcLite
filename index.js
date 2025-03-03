import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ScatterChart, Scatter, Cell, PieChart, Pie, ComposedChart, Rectangle,
  AreaChart, Area
} from 'recharts';
import _ from 'lodash';

// API base URL - replace with your Flask server URL
const API_BASE_URL = 'http://localhost:5000/api';

const DrugPriceVisualizer = () => {
  // State for data and filters
  const [data, setData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [activeIngredients, setActiveIngredients] = useState([]);
  const [manufacturers, setManufacturers] = useState([]);
  const [concentrations, setConcentrations] = useState([]);
  const [channels, setChannels] = useState([]);
  const [dispensingUnits, setDispensingUnits] = useState([]);
  const [histogramData, setHistogramData] = useState([]);
  const [boxplotData, setBoxplotData] = useState([]);
  const [anomalyData, setAnomalyData] = useState(null);
  const [clusterData, setClusterData] = useState(null);
  
  // State for selected filters
  const [selectedActiveIngredient, setSelectedActiveIngredient] = useState('');
  const [selectedManufacturer, setSelectedManufacturer] = useState('');
  const [selectedConcentration, setSelectedConcentration] = useState('');
  const [selectedChannel, setSelectedChannel] = useState('');
  const [selectedDispensingUnit, setSelectedDispensingUnit] = useState('');
  const [sortBy, setSortBy] = useState('precio_por_tableta');
  const [sortOrder, setSortOrder] = useState('asc');
  const [viewType, setViewType] = useState('bar');
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(1000);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Load metadata on component mount
  useEffect(() => {
    fetchMetadata();
  }, []);
  
  // Fetch filtered data when filters change
  useEffect(() => {
    fetchFilteredData();
    
    // Fetch specific visualization data based on view type
    if (viewType === 'histogram') {
      fetchHistogramData();
    } else if (viewType === 'boxplot') {
      fetchBoxplotData();
    } else if (viewType === 'anomalies') {
      fetchAnomalyData();
    } else if (viewType === 'clusters') {
      fetchClusterData();
    }
  }, [selectedActiveIngredient, selectedManufacturer, selectedConcentration, 
      selectedChannel, selectedDispensingUnit, sortBy, sortOrder, minPrice, maxPrice, viewType]);
  
  // Fetch metadata from backend
  const fetchMetadata = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/metadata`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setActiveIngredients(data.active_ingredients || []);
        setManufacturers(data.manufacturers || []);
        setConcentrations(data.concentrations || []);
        setChannels(data.channels || []);
        setDispensingUnits(data.dispensing_units || []);
        
        // Set initial price range
        if (data.price_range) {
          setMinPrice(0);
          setMaxPrice(Math.ceil(data.price_range.max));
        }
      } else {
        setError(data.message || 'Failed to fetch metadata');
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching metadata:', error);
      setError('Failed to connect to the server. Please try again later.');
      setLoading(false);
    }
  };
  
  // Fetch filtered data from backend
  const fetchFilteredData = async () => {
    try {
      setLoading(true);
      
      // Build query string
      const params = new URLSearchParams();
      if (selectedActiveIngredient) params.append('active_ingredient', selectedActiveIngredient);
      if (selectedManufacturer) params.append('manufacturer', selectedManufacturer);
      if (selectedConcentration) params.append('concentration', selectedConcentration);
      if (selectedChannel) params.append('channel', selectedChannel);
      if (selectedDispensingUnit) params.append('dispensing_unit', selectedDispensingUnit);
      if (minPrice !== undefined) params.append('min_price', minPrice);
      if (maxPrice !== undefined) params.append('max_price', maxPrice);
      params.append('sort_by', sortBy);
      params.append('sort_order', sortOrder);
      params.append('limit', 50);
      
      const response = await fetch(`${API_BASE_URL}/data?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.status === 'success') {
        setFilteredData(result.data || []);
      } else {
        setError(result.message || 'Failed to fetch data');
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching filtered data:', error);
      setError('Failed to connect to the server. Please try again later.');
      setLoading(false);
    }
  };
  
  // Fetch histogram data
  const fetchHistogramData = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedActiveIngredient) params.append('active_ingredient', selectedActiveIngredient);
      if (selectedManufacturer) params.append('manufacturer', selectedManufacturer);
      params.append('bins', 10);
      
      const response = await fetch(`${API_BASE_URL}/histogram?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.status === 'success') {
        setHistogramData(result.histogram || []);
      }
    } catch (error) {
      console.error('Error fetching histogram data:', error);
    }
  };
  
  // Fetch boxplot data
  const fetchBoxplotData = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedActiveIngredient) params.append('active_ingredient', selectedActiveIngredient);
      
      // Group by manufacturer if active ingredient is selected, otherwise by active ingredient
      const groupBy = selectedActiveIngredient ? 'fabricante' : 'principio_activo';
      params.append('group_by', groupBy);
      params.append('limit', 10);
      
      const response = await fetch(`${API_BASE_URL}/boxplot?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.status === 'success') {
        setBoxplotData(result.boxplot || []);
      }
    } catch (error) {
      console.error('Error fetching boxplot data:', error);
    }
  };
  
  // Fetch anomaly data
  const fetchAnomalyData = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedActiveIngredient) params.append('active_ingredient', selectedActiveIngredient);
      params.append('contamination', 0.05);
      
      const response = await fetch(`${API_BASE_URL}/ml/anomalies?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.status === 'success') {
        setAnomalyData(result);
      }
    } catch (error) {
      console.error('Error fetching anomaly data:', error);
    }
  };
  
  // Fetch cluster data
  const fetchClusterData = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedActiveIngredient) params.append('active_ingredient', selectedActiveIngredient);
      params.append('n_clusters', 3);
      
      const response = await fetch(`${API_BASE_URL}/ml/clusters?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.status === 'success') {
        setClusterData(result);
      }
    } catch (error) {
      console.error('Error fetching cluster data:', error);
    }
  };
  
  // Get pie chart data for manufacturer distribution
  const getPieChartData = () => {
    if (filteredData.length === 0) return [];
    
    const groupBy = selectedActiveIngredient ? 'fabricante' : 'principio_activo';
    
    const grouped = _.chain(filteredData)
      .groupBy(groupBy)
      .map((items, name) => ({
        name: name,
        value: items.length
      }))
      .orderBy(['value'], ['desc'])
      .value();
    
    return grouped;
  };
  
  // Get color based on price value
  const getColor = (value, min, max) => {
    const normalized = (value - min) / (max - min);
    if (normalized < 0.33) {
      return '#3498db'; // Blue for low prices
    } else if (normalized < 0.66) {
      return '#2ecc71'; // Green for medium prices
    } else {
      return '#e74c3c'; // Red for high prices
    }
  };
  
  // Random colors for pie chart
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FF6B6B', '#6B66FF'];
  
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h1 className="text-2xl font-bold mb-4">Drug Price Visualization Dashboard</h1>
      
      {error && (
        <div className="p-4 mb-4 bg-red-100 text-red-700 rounded">
          <p><strong>Error:</strong> {error}</p>
        </div>
      )}
      
      {loading && filteredData.length === 0 ? (
        <div className="flex items-center justify-center h-64">
          <p className="text-lg">Loading data...</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {/* Active Ingredient Filter */}
            <div>
              <label className="block text-sm font-medium mb-1">Active Ingredient</label>
              <select
                className="w-full p-2 border rounded"
                value={selectedActiveIngredient}
                onChange={(e) => setSelectedActiveIngredient(e.target.value)}
              >
                <option value="">All Active Ingredients</option>
                {activeIngredients.map(ingredient => (
                  <option key={ingredient} value={ingredient}>
                    {ingredient}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Manufacturer Filter */}
            <div>
              <label className="block text-sm font-medium mb-1">Manufacturer</label>
              <select
                className="w-full p-2 border rounded"
                value={selectedManufacturer}
                onChange={(e) => setSelectedManufacturer(e.target.value)}
              >
                <option value="">All Manufacturers</option>
                {manufacturers.map(manufacturer => (
                  <option key={manufacturer} value={manufacturer}>
                    {manufacturer}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Concentration Filter */}
            <div>
              <label className="block text-sm font-medium mb-1">Concentration</label>
              <select
                className="w-full p-2 border rounded"
                value={selectedConcentration}
                onChange={(e) => setSelectedConcentration(e.target.value)}
              >
                <option value="">All Concentrations</option>
                {concentrations.map(concentration => (
                  <option key={concentration} value={concentration}>
                    {concentration}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {/* Distribution Channel Filter */}
            <div>
              <label className="block text-sm font-medium mb-1">Distribution Channel</label>
              <select
                className="w-full p-2 border rounded"
                value={selectedChannel}
                onChange={(e) => setSelectedChannel(e.target.value)}
              >
                <option value="">All Channels</option>
                {channels.map(channel => (
                  <option key={channel} value={channel}>
                    {channel}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Dispensing Unit Filter */}
            <div>
              <label className="block text-sm font-medium mb-1">Dispensing Unit</label>
              <select
                className="w-full p-2 border rounded"
                value={selectedDispensingUnit}
                onChange={(e) => setSelectedDispensingUnit(e.target.value)}
              >
                <option value="">All Dispensing Units</option>
                {dispensingUnits.map(unit => (
                  <option key={unit} value={unit}>
                    {unit}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            {/* Sorting Options */}
            <div>
              <label className="block text-sm font-medium mb-1">Sort By</label>
              <div className="flex space-x-2">
                <select
                  className="w-1/2 p-2 border rounded"
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <option value="precio_por_tableta">Price</option>
                  <option value="nombre_comercial">Name</option>
                </select>
                
                <select
                  className="w-1/2 p-2 border rounded"
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value)}
                >
                  <option value="asc">Ascending</option>
                  <option value="desc">Descending</option>
                </select>
              </div>
            </div>
            
            {/* View Type */}
            <div>
              <label className="block text-sm font-medium mb-1">Chart Type</label>
              <div className="flex flex-wrap">
                <button
                  className={`px-3 py-2 border rounded-l text-sm ${viewType === 'bar' ? 'bg-blue-500 text-white' : 'bg-white'}`}
                  onClick={() => setViewType('bar')}
                >
                  Bar
                </button>
                <button
                  className={`px-3 py-2 border-t border-b border-r text-sm ${viewType === 'scatter' ? 'bg-blue-500 text-white' : 'bg-white'}`}
                  onClick={() => setViewType('scatter')}
                >
                  Scatter
                </button>
                <button
                  className={`px-3 py-2 border-t border-b border-r text-sm ${viewType === 'pie' ? 'bg-blue-500 text-white' : 'bg-white'}`}
                  onClick={() => setViewType('pie')}
                >
                  Pie
                </button>
                <button
                  className={`px-3 py-2 border-t border-b border-r text-sm ${viewType === 'histogram' ? 'bg-blue-500 text-white' : 'bg-white'}`}
                  onClick={() => setViewType('histogram')}
                >
                  Histogram
                </button>
                <button
                  className={`px-3 py-2 border-t border-b border-r text-sm ${viewType === 'boxplot' ? 'bg-blue-500 text-white' : 'bg-white'}`}
                  onClick={() => setViewType('boxplot')}
                >
                  Box Plot
                </button>
                <button
                  className={`px-3 py-2 border-t border-b border-r text-sm ${viewType === 'anomalies' ? 'bg-blue-500 text-white' : 'bg-white'}`}
                  onClick={() => setViewType('anomalies')}
                >
                  Anomalies
                </button>
                <button
                  className={`px-3 py-2 border-t border-b border-r rounded-r text-sm ${viewType === 'clusters' ? 'bg-blue-500 text-white' : 'bg-white'}`}
                  onClick={() => setViewType('clusters')}
                >
                  Clusters
                </button>
              </div>
            </div>
            
            {/* Price Range */}
            <div>
              <label className="block text-sm font-medium mb-1">Price Range</label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  min="0"
                  value={minPrice}
                  onChange={(e) => setMinPrice(Number(e.target.value))}
                  placeholder="Min"
                  className="w-1/2 p-2 border rounded"
                />
                <input
                  type="number"
                  min="0"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(Number(e.target.value))}
                  placeholder="Max"
                  className="w-1/2 p-2 border rounded"
                />
              </div>
            </div>
          </div>
          
          {/* Charts */}
          <div className="bg-gray-50 p-4 rounded-lg mt-4">
            {viewType === 'bar' && (
              // Bar Chart View
              <div className="h-96">
                {filteredData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={filteredData}
                      margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey={selectedActiveIngredient ? "fabricante" : "nombre_comercial"} 
                        angle={-45} 
                        textAnchor="end"
                        height={100} 
                        interval={0}
                      />
                      <YAxis label={{ value: 'Price per Tablet', angle: -90, position: 'insideLeft' }} />
                      <Tooltip 
                        formatter={(value) => [`$${value.toFixed(2)}`, 'Price per Tablet']}
                        labelFormatter={(label) => `${selectedActiveIngredient ? "Manufacturer" : "Product"}: ${label}`}
                      />
                      <Legend />
                      <Bar dataKey="precio_por_tableta" name="Price per Tablet">
                        {filteredData.map((entry, index) => {
                          const min = Math.min(...filteredData.map(d => d.precio_por_tableta));
                          const max = Math.max(...filteredData.map(d => d.precio_por_tableta));
                          return <Cell key={`cell-${index}`} fill={getColor(entry.precio_por_tableta, min, max)} />;
                        })}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-500">No data available for the selected filters</p>
                  </div>
                )}
              </div>
            )}
            
            {viewType === 'scatter' && (
              // Scatter Plot View
              <div className="h-96">
                {filteredData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart
                      margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                    >
                      <CartesianGrid />
                      <XAxis 
                        type="category"
                        dataKey="fabricante" 
                        name="Manufacturer"
                        angle={-45} 
                        textAnchor="end"
                        height={100} 
                      />
                      <YAxis 
                        type="number"
                        dataKey="precio_por_tableta" 
                        name="Price"
                        label={{ value: 'Price per Tablet', angle: -90, position: 'insideLeft' }} 
                      />
                      <Tooltip 
                        cursor={{ strokeDasharray: '3 3' }}
                        formatter={(value) => {
                          if (typeof value === 'number') {
                            return [`$${value.toFixed(2)}`, 'Price per Tablet'];
                          }
                          return [value, 'Value'];
                        }}
                        labelFormatter={(label) => {
                          return `Product: ${filteredData.find(item => item.fabricante === label)?.nombre_comercial || label}`;
                        }}
                      />
                      <Legend />
                      <Scatter 
                        name="Drug Products" 
                        data={filteredData} 
                      >
                        {filteredData.map((entry, index) => {
                          const min = Math.min(...filteredData.map(d => d.precio_por_tableta));
                          const max = Math.max(...filteredData.map(d => d.precio_por_tableta));
                          return <Cell key={`cell-${index}`} fill={getColor(entry.precio_por_tableta, min, max)} />;
                        })}
                      </Scatter>
                    </ScatterChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-500">No data available for the selected filters</p>
                  </div>
                )}
              </div>
            )}
            
            {viewType === 'pie' && (
              // Pie Chart View
              <div className="h-96">
                {filteredData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={getPieChartData()}
                        cx="50%"
                        cy="50%"
                        labelLine={true}
                        label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={120}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {getPieChartData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [value, 'Products']} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-500">No data available for the selected filters</p>
                  </div>
                )}
              </div>
            )}
            
            {viewType === 'histogram' && (
              // Histogram View
              <div className="h-96">
                {histogramData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={histogramData}
                      margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="bin" 
                        angle={-45} 
                        textAnchor="end"
                        height={100} 
                        interval={0}
                      />
                      <YAxis label={{ value: 'Number of Products', angle: -90, position: 'insideLeft' }} />
                      <Tooltip 
                        formatter={(value) => [value, 'Products']}
                        labelFormatter={(label) => `Price Range: ${label}`}
                      />
                      <Legend />
                      <Bar dataKey="count" name="Number of Products" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-500">No histogram data available for the selected filters</p>
                  </div>
                )}
              </div>
            )}
            
            {viewType === 'boxplot' && (
              // Box Plot View
              <div className="h-96">
                {boxplotData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart 
                      layout="vertical"
                      data={boxplotData}
                      margin={{ top: 20, right: 30, left: 150, bottom: 10 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" domain={['dataMin', 'dataMax']} />
                      <YAxis 
                        type="category" 
                        dataKey="name" 
                        width={150}
                        tick={{ fontSize: 12 }}
                      />
                      <Tooltip 
                        formatter={(value) => [`$${value.toFixed(2)}`, 'Price']}
                        labelFormatter={(label) => `${selectedActiveIngredient ? 'Manufacturer' : 'Active Ingredient'}: ${label}`}
                      />
                      <Legend />
                      
                      {/* Min to Max line */}
                      {boxplotData.map((entry, index) => (
                        <React.Fragment key={`boxplot-${index}`}>
                          {/* Min to Q1 */}
                          <Bar 
                            dataKey="min" 
                            stackId={`stack-${index}`} 
                            fill="transparent" 
                            stroke="#8884d8"
                            name={index === 0 ? "Min-Max Range" : ""} 
                            isAnimationActive={false}
                          />
                          
                          {/* Q1 to Q3 (IQR) */}
                          <Bar 
                            dataKey="q1" 
                            stackId={`stack-${index}`} 
                            fill="#8884d8" 
                            name={index === 0 ? "Interquartile Range" : ""}
                            isAnimationActive={false}
                          />
                          
                          {/* Median */}
                          <Bar 
                            dataKey="median" 
                            fill="#ff7300" 
                            name={index === 0 ? "Median" : ""} 
                            isAnimationActive={false}
                          />
                        </React.Fragment>
                      ))}
                    </ComposedChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-500">Not enough data for box plots. Try selecting an active ingredient.</p>
                  </div>
                )}
              </div>
            )}
            
            {viewType === 'anomalies' && (
              // Anomaly Detection View
              <div className="h-96">
                {anomalyData && anomalyData.anomalies ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
                    <div className="bg-white p-4 rounded shadow">
                      <h3 className="text-lg font-medium mb-2">Anomaly Detection Results</h3>
                      <div className="space-y-2">
                        <p>Normal data points: {anomalyData.statistics.normal_count}</p>
                        <p>Anomalies detected: {anomalyData.statistics.anomaly_count}</p>
                        <p>Average normal price: ${anomalyData.statistics.normal_avg_price.toFixed(2)}</p>
                        <p>Average anomaly price: ${anomalyData.statistics.anomaly_avg_price.toFixed(2)}</p>
                        <p>Upper threshold: ${anomalyData.statistics.price_threshold_upper.toFixed(2)}</p>
                        <p>Lower threshold: ${anomalyData.statistics.price_threshold_lower.toFixed(2)}</p>
                      </div>
                    </div>
                    
                    <div className="bg-white p-4 rounded shadow overflow-y-auto h-full">
                      <h3 className="text-lg font-medium mb-2">Anomalous Prices</h3>
                      {anomalyData.anomalies.length > 0 ? (
                        <table className="min-w-full">
                          <thead>
                            <tr>
                              <th className="border px-2 py-1 text-left">Product</th>
                              <th className="border px-2 py-1 text-left">Manufacturer</th>
                              <th className="border px-2 py-1 text-right">Price</th>
                            </tr>
                          </thead>
                          <tbody>
                            {anomalyData.anomalies.map((item, index) => (
                              <tr key={index} className="bg-red-50">
                                <td className="border px-2 py-1">{item.nombre_comercial}</td>
                                <td className="border px-2 py-1">{item.fabricante}</td>
                                <td className="border px-2 py-1 text-right">${item.precio_por_tableta.toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      ) : (
                        <p className="text-gray-500">No anomalies detected</p>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-500">Loading anomaly detection results...</p>
                  </div>
                )}
              </div>
            )}
            
            {viewType === 'clusters' && (
              // Clustering View
              <div className="h-96">
                {clusterData && clusterData.clusters ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
                    <div className="bg-white p-4 rounded shadow">
                      <h3 className="text-lg font-medium mb-2">Price Clusters</h3>
                      <table className="min-w-full">
                        <thead>
                          <tr>
                            <th className="border px-2 py-1 text-left">Cluster</th>
                            <th className="border px-2 py-1 text-center">Products</th>
                            <th className="border px-2 py-1 text-right">Avg Price</th>
                            <th className="border px-2 py-1 text-right">Range</th>
                          </tr>
                        </thead>
                        <tbody>
                          {clusterData.clusters.map((cluster, index) => (
                            <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                              <td className="border px-2 py-1">Cluster {cluster.cluster_id + 1}</td>
                              <td className="border px-2 py-1 text-center">{cluster.count}</td>
                              <td className="border px-2 py-1 text-right">${cluster.avg_price.toFixed(2)}</td>
                              <td className="border px-2 py-1 text-right">${cluster.min_price.toFixed(2)} - ${cluster.max_price.toFixed(2)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    
                    <div className="bg-white p-4 rounded shadow">
                      <h3 className="text-lg font-medium mb-2">Cluster Visualization</h3>
                      <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={clusterData.clusters}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="cluster_id" label={{ value: 'Cluster', position: 'insideBottom', offset: -5 }} />
                          <YAxis label={{ value: 'Price', angle: -90, position: 'insideLeft' }} />
                          <Tooltip 
                            formatter={(value) => [`$${value.toFixed(2)}`, 'Price']}
                            labelFormatter={(label) => `Cluster ${parseInt(label) + 1}`}
                          />
                          <Legend />
                          <Bar dataKey="avg_price" name="Average Price" fill="#8884d8" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-500">Loading clustering results...</p>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Data Table Preview */}
          <div className="mt-4 overflow-x-auto">
            <h3 className="text-lg font-medium mb-2">Data Preview</h3>
            <table className="min-w-full bg-white border">
              <thead>
                <tr>
                  <th className="border px-4 py-2">Name</th>
                  <th className="border px-4 py-2">Active Ingredient</th>
                  <th className="border px-4 py-2">Manufacturer</th>
                  <th className="border px-4 py-2">Concentration</th>
                  <th className="border px-4 py-2">Price</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.slice(0, 10).map((item, index) => (
                  <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                    <td className="border px-4 py-2">{item.nombre_comercial}</td>
                    <td className="border px-4 py-2">{item.principio_activo}</td>
                    <td className="border px-4 py-2">{item.fabricante}</td>
                    <td className="border px-4 py-2">{item.concentracion}</td>
                    <td className="border px-4 py-2">${item.precio_por_tableta.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredData.length > 10 && (
              <p className="text-sm text-gray-500 mt-2">Showing 10 of {filteredData.length} items</p>
            )}
          </div>
          
          {/* Machine Learning Insights Section */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <h3 className="text-lg font-medium mb-2">Machine Learning Features</h3>
            <p className="mb-2">This application demonstrates several machine learning capabilities:</p>
            <ul className="list-disc pl-5">
              <li><strong>Price Anomaly Detection:</strong> Isolation Forest algorithm to identify unusually priced medications</li>
              <li><strong>Price Clustering:</strong> K-means clustering to group medications into price segments</li>
              <li><strong>Statistical Analysis:</strong> Box plots and histograms for deeper price distribution insights</li>
            </ul>
            <p className="mt-2">Try the "Anomalies" and "Clusters" visualization types to see machine learning in action!</p>
          </div>
        </>
      )}
    </div>
  );
};

export default DrugPriceVisualizer;