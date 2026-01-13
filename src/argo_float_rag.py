#!/usr/bin/env python3
"""
ARGO Float RAG (Retrieval-Augmented Generation) System
=====================================================

This module provides LLM + RAG integration for ARGO float data queries,
automatic data fetching, and intelligent responses about oceanographic data.

Author: ARGO Research Dashboard Team
Date: September 2025
"""

import re
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
import json
import random

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArgoFloatRAG:
    """RAG system for ARGO float data queries and responses"""
    
    def __init__(self):
        self.float_database = self._initialize_float_database()
        self.query_patterns = self._initialize_query_patterns()
        self.response_templates = self._initialize_response_templates()
        
    def _initialize_float_database(self) -> Dict[str, Dict]:
        """Initialize comprehensive ARGO float database for Indian Ocean"""
        logger.info("Initializing ARGO float database with 150 floats...")
        
        np.random.seed(42)  # For consistent data
        floats = {}
        # Generate 150 ARGO floats across Indian Ocean
        for i in range(150):
            float_id = f"ARGO_{5000 + i:04d}"
            
            # Generate realistic Indian Ocean coordinates (avoiding land)
            lat, lon = self._generate_ocean_coordinates()
            
            # Generate oceanographic data based on location
            surface_temp = self._calculate_realistic_temp(lat, lon)
            surface_salinity = self._calculate_realistic_salinity(lat, lon)
            max_depth = np.random.uniform(800, 2000)
            
            # Generate deployment and status info
            deployment_date = self._generate_deployment_date()
            last_contact = self._generate_last_contact(deployment_date)
            status = self._determine_status(last_contact)
            
            # Generate profile data
            profile_data = self._generate_profile_data(surface_temp, surface_salinity, max_depth)
            
            floats[float_id] = {
                'float_id': float_id,
                'latitude': round(lat, 3),
                'longitude': round(lon, 3),
                'surface_temperature': round(surface_temp, 2),
                'surface_salinity': round(surface_salinity, 2),
                'max_depth': round(max_depth, 1),
                'deployment_date': deployment_date,
                'last_contact': last_contact,
                'status': status,
                'total_profiles': np.random.randint(50, 300),
                'platform_type': np.random.choice(['APEX', 'NOVA', 'ARVOR'], p=[0.5, 0.3, 0.2]),
                'wmo_id': f"{59000 + i:05d}",
                'profile_data': profile_data,
                'region': self._determine_region(lat, lon),
                'data_quality': np.random.choice(['Good', 'Acceptable', 'Marginal'], p=[0.7, 0.25, 0.05])
            }
        
        logger.info(f"Initialized {len(floats)} ARGO floats")
        return floats
    
    def _calculate_realistic_temp(self, lat: float, lon: float) -> float:
        """Calculate realistic temperature based on location"""
        # Temperature decreases with latitude (distance from equator)
        base_temp = 28 - 0.4 * abs(lat)
        
        # Regional variations
        if 50 <= lon <= 75:  # Arabian Sea - warmer
            base_temp += 1.5
        elif 80 <= lon <= 100:  # Bay of Bengal - warmer
            base_temp += 2.0
        elif lat < -20:  # Southern Indian Ocean - cooler
            base_temp -= 3.0
        
        # Add seasonal and random variation
        temp = base_temp + np.random.normal(0, 1.5)
        return max(5.0, min(32.0, temp))
    
    def _calculate_realistic_salinity(self, lat: float, lon: float) -> float:
        """Calculate realistic salinity based on location"""
        base_salinity = 35.0
        
        # Regional variations
        if 50 <= lon <= 75:  # Arabian Sea - higher salinity
            base_salinity += 0.8
        elif 80 <= lon <= 100 and lat > 0:  # Bay of Bengal - lower salinity (river input)
            base_salinity -= 1.2
        elif lat < -30:  # Southern Indian Ocean
            base_salinity += 0.3
        
        # Add variation
        salinity = base_salinity + np.random.normal(0, 0.3)
        return max(32.0, min(37.5, salinity))
    
    def _generate_deployment_date(self) -> str:
        """Generate realistic deployment date"""
        # Deploy over last 8 years
        days_ago = np.random.randint(30, 8*365)
        deploy_date = datetime.now() - timedelta(days=days_ago)
        return deploy_date.strftime('%Y-%m-%d')
    
    def _generate_last_contact(self, deployment_date: str) -> str:
        """Generate last contact date based on deployment"""
        deploy_dt = datetime.strptime(deployment_date, '%Y-%m-%d')
        
        # Most floats have recent contact, some are older
        if np.random.random() < 0.7:  # 70% recent contact
            days_since = np.random.randint(1, 30)
        else:  # 30% older contact
            days_since = np.random.randint(30, 365)
        
        last_contact = datetime.now() - timedelta(days=days_since)
        return last_contact.strftime('%Y-%m-%d')
    
    def _determine_status(self, last_contact: str) -> str:
        """Determine float status based on last contact"""
        contact_dt = datetime.strptime(last_contact, '%Y-%m-%d')
        days_since = (datetime.now() - contact_dt).days
        
        if days_since <= 15:
            return "Active"
        elif days_since <= 60:
            return "Monitoring"
        else:
            return "Inactive"
    
    def _generate_ocean_coordinates(self) -> Tuple[float, float]:
        """Generate coordinates that are guaranteed to be in the Indian Ocean (not on land)"""
        
        max_attempts = 100  # Prevent infinite loops
        attempts = 0
        
        while attempts < max_attempts:
            attempts += 1
            
            # Define ocean regions within Indian Ocean basin (avoiding land masses)
            ocean_regions = [
                # (name, lat_min, lat_max, lon_min, lon_max, weight)
                ("Arabian Sea", 8, 25, 50, 75, 25),          # Northern Arabian Sea
                ("Bay of Bengal", 5, 22, 80, 95, 20),         # Bay of Bengal  
                ("Central Indian", -10, 5, 70, 90, 20),       # Central Indian Ocean
                ("Southern Indian", -35, -10, 35, 110, 20),   # Southern Indian Ocean
                ("Western Indian", -15, 10, 35, 55, 15),      # Western Indian Ocean
            ]
            
            # Select region based on weights
            regions = [r[0] for r in ocean_regions]
            weights = [r[5] for r in ocean_regions]
            selected_region = np.random.choice(regions, p=np.array(weights)/sum(weights))
            
            # Get bounds for selected region
            region_data = next(r for r in ocean_regions if r[0] == selected_region)
            lat_min, lat_max = region_data[1], region_data[2]
            lon_min, lon_max = region_data[3], region_data[4]
            
            # Generate coordinates within region
            lat = np.random.uniform(lat_min, lat_max)
            lon = np.random.uniform(lon_min, lon_max)
            
            # Check if coordinates are on land
            if not self._is_on_land(lat, lon):
                return lat, lon
        
        # If we can't find ocean coordinates after max attempts, use a safe fallback
        logger.warning("Could not generate ocean coordinates after max attempts, using safe fallback")
        return np.random.uniform(-25, -15), np.random.uniform(60, 80)  # Safe ocean area
    
    def _is_on_land(self, lat: float, lon: float) -> bool:
        """Check if given coordinates are on land in the Indian Ocean region"""
        
        # Define major land areas to avoid in the Indian Ocean region
        
        # 1. African continent (west of ~50°E)
        if lon < 50 and lat > -35 and lat < 35:
            return True
        
        # 2. Arabian Peninsula
        if 45 <= lon <= 65 and 12 <= lat <= 30:
            return True
        
        # 3. Indian subcontinent
        if 68 <= lon <= 90 and 8 <= lat <= 35:
            return True
        
        # 4. Sri Lanka
        if 79 <= lon <= 82 and 5.5 <= lat <= 10:
            return True
        
        # 5. Southeast Asian mainland
        if 92 <= lon <= 110 and -5 <= lat <= 25:
            return True
        
        # 6. Indonesian islands (major ones)
        if 95 <= lon <= 125 and -10 <= lat <= 10:
            return True
        
        # 7. Madagascar
        if 43 <= lon <= 51 and -25 <= lat <= -12:
            return True
        
        # 8. Maldives and Lakshadweep islands
        if 72 <= lon <= 74 and 0 <= lat <= 8:
            return True
        
        # 9. Mauritius and Reunion islands
        if 55 <= lon <= 58 and -21 <= lat <= -19:
            return True
        
        # 10. Seychelles
        if 55 <= lon <= 56 and -5 <= lat <= -4:
            return True
        
        # Additional land areas in the Arabian Sea region
        if 50 <= lon <= 75 and 15 <= lat <= 25:
            # Check for specific coastal areas that might be land
            if lon < 58 and lat > 20:  # Oman/Saudi Arabia coast
                return True
            if lon < 60 and lat < 12:  # Somalia/Yemen coast
                return True
        
        # Additional land areas in Bay of Bengal
        if 80 <= lon <= 95 and 5 <= lat <= 22:
            # Check for Myanmar/Bangladesh/India east coast
            if lon > 90 and lat > 15:  # Myanmar/Bangladesh
                return True
            if lon > 85 and lat < 12:  # India east coast
                return True
        
        # Southern Indian Ocean - generally more open but avoid Antarctica
        if lat < -60:
            return True
        
        # All other areas in our defined regions are considered ocean
        return False
    
    def _generate_profile_data(self, surface_temp: float, surface_salinity: float, max_depth: float) -> Dict:
        """Generate realistic profile data for a float"""
        # Generate depth profile (0 to max_depth)
        depths = np.linspace(0, max_depth, 50)
        
        # Temperature profile with thermocline
        temps = []
        for depth in depths:
            if depth < 50:  # Mixed layer
                temp = surface_temp + np.random.normal(0, 0.5)
            elif depth < 200:  # Thermocline
                temp = surface_temp - (depth - 50) * 0.15 + np.random.normal(0, 0.8)
            else:  # Deep water
                temp = surface_temp - 22 - (depth - 200) * 0.002 + np.random.normal(0, 0.3)
            temps.append(max(2.0, temp))
        
        # Salinity profile
        sals = []
        for depth in depths:
            if depth < 100:  # Surface layer
                sal = surface_salinity + np.random.normal(0, 0.1)
            else:  # Deep water - slight increase
                sal = surface_salinity + (depth - 100) * 0.0003 + np.random.normal(0, 0.05)
            sals.append(max(32.0, min(37.5, sal)))
        
        # Pressure (approximately depth in decibars)
        pressures = depths * 1.02  # Slight conversion factor
        
        return {
            'depths': [round(d, 1) for d in depths],
            'temperatures': [round(t, 2) for t in temps],
            'salinities': [round(s, 2) for s in sals],
            'pressures': [round(p, 1) for p in pressures]
        }
    
    def _determine_region(self, lat: float, lon: float) -> str:
        """Determine oceanographic region"""
        # Use the same regions as coordinate generation
        if 50 <= lon <= 75 and 8 <= lat <= 25:
            return "Arabian Sea"
        elif 80 <= lon <= 95 and 5 <= lat <= 22:
            return "Bay of Bengal"
        elif 70 <= lon <= 90 and -10 <= lat <= 5:
            return "Central Indian Ocean"
        elif 35 <= lon <= 110 and -35 <= lat <= -10:
            return "Southern Indian Ocean"
        elif 35 <= lon <= 55 and -15 <= lat <= 10:
            return "Western Indian Ocean"
        else:
            return "Indian Ocean"
    
    def _initialize_query_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for detecting different types of queries"""
        return {
            'float_mention': [
                r'ARGO[_\s]?(\d{4,5})',
                r'float[_\s]?(\d{4,5})',
                r'(\d{4,5})[_\s]?float',
                r'WMO[_\s]?(\d{5})'
            ],
            'temperature_query': [
                r'temperature', r'temp', r'thermal', r'warm', r'cold', r'heating', r'cooling'
            ],
            'salinity_query': [
                r'salinity', r'salt', r'saline', r'psu', r'conductivity'
            ],
            'depth_query': [
                r'depth', r'deep', r'shallow', r'profile', r'vertical', r'pressure'
            ],
            'location_query': [
                r'location', r'position', r'coordinates', r'latitude', r'longitude', r'where'
            ],
            'status_query': [
                r'status', r'active', r'inactive', r'working', r'operational', r'contact'
            ],
            'comparison_query': [
                r'compare', r'comparison', r'versus', r'vs', r'difference', r'similar'
            ],
            'region_query': [
                r'arabian sea', r'bay of bengal', r'indian ocean', r'southern indian', r'central indian', r'western indian',
                r'region', r'area', r'zone', r'sector', r'find.*in', r'floats.*in', r'show.*in'
            ]
        }
    
    def _initialize_response_templates(self) -> Dict[str, List[str]]:
        """Initialize response templates for different query types"""
        return {
            'float_info': [
                "🌊 **{float_id}** ({platform_type}) - **{region}**\n"
                "📍 **{lat}°N, {lon}°E** | Status: **{status}**\n"
                "🌡️ **{temp}°C** | 🧂 **{sal} PSU** | 📊 **{depth:.0f}m**",
                
                "🔍 **{float_id}** in **{region}**\n"
                "📍 Position: **{lat}°N, {lon}°E**\n"
                "🌡️ Temp: **{temp}°C** | 🧂 Sal: **{sal} PSU** | Status: **{status}**"
            ],
            'temperature_analysis': [
                "🌡️ **Temperature Analysis for {float_id}:**\n\n"
                "The float shows a **{temp}°C** surface temperature with a typical thermocline structure:\n"
                "• **Mixed Layer (0-50m):** ~{temp}°C\n"
                "• **Thermocline (50-200m):** Rapid cooling\n"
                "• **Deep Water (>200m):** ~{deep_temp}°C\n\n"
                "This profile is typical for the **{region}** region. 📈",
                
                "🔥 The temperature profile for **{float_id}** reveals interesting thermal structure!\n\n"
                "**Surface warming** at {temp}°C indicates {season_desc}. The thermocline depth suggests {mixing_desc}.\n\n"
                "📊 Temperature gradient: **{gradient}°C/100m** in the upper ocean."
            ],
            'salinity_analysis': [
                "🧂 **Salinity Analysis for {float_id}:**\n\n"
                "Surface salinity of **{sal} PSU** is {sal_desc} for the {region}.\n"
                "• **Surface Layer:** {sal} PSU\n"
                "• **Subsurface Maximum:** ~{max_sal} PSU\n"
                "• **Deep Water:** ~{deep_sal} PSU\n\n"
                "This indicates {water_mass_desc}. 🌊"
            ],
            'location_info': [
                "📍 **Location Details for {float_id}:**\n\n"
                "• **Coordinates:** {lat}°N, {lon}°E\n"
                "• **Region:** {region}\n"
                "• **Deployment Date:** {deployment}\n"
                "• **Distance from Coast:** ~{distance}km\n\n"
                "This location is characterized by {location_desc}. 🗺️"
            ],
            'status_info': [
                "📡 **Status Report for {float_id}:**\n\n"
                "• **Current Status:** {status}\n"
                "• **Last Contact:** {last_contact}\n"
                "• **Platform Type:** {platform_type}\n"
                "• **WMO ID:** {wmo_id}\n"
                "• **Total Profiles:** {profiles}\n\n"
                "{status_desc} 🔋"
            ],
            'no_float_found': [
                "❓ I couldn't find the specific ARGO float you mentioned. Let me show you some similar floats in the region:\n\n"
                "🌊 **Available Floats:**\n{float_list}\n\n"
                "Would you like detailed information about any of these floats?",
                
                "🔍 That float ID doesn't exist in our database, but I can help you explore other active floats!\n\n"
                "Here are some **active floats** in the Indian Ocean:\n{float_list}\n\n"
                "Just mention any float ID (like ARGO_5001) to get detailed analysis! 📊"
            ],
            'region_search': [
                "🌊 **ARGO Floats in {region}:**\n\n"
                "Found **{count}** floats actively collecting data in this region:\n\n{floats_list}\n\n"
                "📊 These floats provide comprehensive oceanographic data including temperature, salinity, and depth profiles.\n\n"
                "Click on any float ID to see detailed analysis and plots! 🗺️",
                
                "🔍 **{region} Float Network:**\n\n"
                "Here are the active ARGO floats monitoring ocean conditions in {region}:\n\n{floats_list}\n\n"
                "📈 Each float collects profiles every 10 days, providing continuous data on ocean circulation and climate patterns."
            ]
        }

    def extract_float_ids(self, message: str) -> List[str]:
        """Extract ARGO float IDs from a message"""
        float_ids = []
        
        for pattern in self.query_patterns['float_mention']:
            matches = re.findall(pattern, message.upper())
            for match in matches:
                # Convert to standard ARGO format
                if len(match) == 4:
                    float_id = f"ARGO_{match}"
                elif len(match) == 5:
                    float_id = f"ARGO_{match[-4:]}"  # Take last 4 digits
                else:
                    continue
                
                if float_id not in float_ids:
                    float_ids.append(float_id)
        
        return float_ids

    def extract_region(self, message: str) -> Optional[str]:
        """Extract oceanographic region from a message"""
        message_lower = message.lower()
        
        region_mappings = {
            'arabian sea': 'Arabian Sea',
            'bay of bengal': 'Bay of Bengal', 
            'central indian ocean': 'Central Indian Ocean',
            'southern indian ocean': 'Southern Indian Ocean',
            'western indian ocean': 'Western Indian Ocean',
            'indian ocean': 'Indian Ocean'
        }
        
        for key, region in region_mappings.items():
            if key in message_lower:
                return region
        
        return None

    def get_float_data(self, float_id: str) -> Optional[Dict]:
        """Get comprehensive data for a specific float"""
        if float_id in self.float_database:
            return self.float_database[float_id]
        
        # If float not found, generate approximate data
        logger.warning(f"Float {float_id} not found, generating approximate data")
        return self._generate_approximate_float_data(float_id)

    def _generate_approximate_float_data(self, float_id: str) -> Dict:
        """Generate approximate data for missing floats"""
        # Use hash of float_id for consistent random generation
        seed = hash(float_id) % 10000
        np.random.seed(seed)
        
        lat, lon = self._generate_ocean_coordinates()
        surface_temp = self._calculate_realistic_temp(lat, lon)
        surface_salinity = self._calculate_realistic_salinity(lat, lon)
        max_depth = np.random.uniform(800, 2000)
        
        return {
            'float_id': float_id,
            'latitude': round(lat, 3),
            'longitude': round(lon, 3),
            'surface_temperature': round(surface_temp, 2),
            'surface_salinity': round(surface_salinity, 2),
            'max_depth': round(max_depth, 1),
            'deployment_date': self._generate_deployment_date(),
            'last_contact': (datetime.now() - timedelta(days=np.random.randint(1, 30))).strftime('%Y-%m-%d'),
            'status': np.random.choice(['Active', 'Monitoring'], p=[0.8, 0.2]),
            'total_profiles': np.random.randint(50, 200),
            'platform_type': np.random.choice(['APEX', 'NOVA', 'ARVOR']),
            'wmo_id': f"{59000 + abs(hash(float_id)) % 1000:05d}",
            'profile_data': self._generate_profile_data(surface_temp, surface_salinity, max_depth),
            'region': self._determine_region(lat, lon),
            'data_quality': 'Estimated'
        }

    def analyze_query_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user query to determine intent and extract information"""
        message_lower = message.lower()
        
        intent = {
            'type': 'general',
            'float_ids': self.extract_float_ids(message),
            'region': self.extract_region(message),
            'topics': [],
            'requires_plotting': False,
            'requires_comparison': False
        }
        
        # Check for specific topics
        for topic, patterns in self.query_patterns.items():
            if topic in ['float_mention', 'region_query']:
                continue
            
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    intent['topics'].append(topic)
                    break
        
        # Check for region queries
        if any(re.search(pattern, message_lower) for pattern in self.query_patterns['region_query']):
            intent['topics'].append('region_query')
        
        # Determine if plotting is needed
        if intent['float_ids'] or any(topic in ['temperature_query', 'salinity_query', 'depth_query'] for topic in intent['topics']):
            intent['requires_plotting'] = True
        
        # Check for comparison requests
        if any(re.search(pattern, message_lower) for pattern in self.query_patterns['comparison_query']):
            intent['requires_comparison'] = True
        
        # Determine primary intent type
        if intent['float_ids']:
            intent['type'] = 'float_specific'
        elif intent['region']:
            intent['type'] = 'region_search'
        elif 'temperature_query' in intent['topics']:
            intent['type'] = 'temperature_analysis'
        elif 'salinity_query' in intent['topics']:
            intent['type'] = 'salinity_analysis'
        elif 'location_query' in intent['topics']:
            intent['type'] = 'location_query'
        elif 'status_query' in intent['topics']:
            intent['type'] = 'status_query'
        
        return intent

    def generate_response(self, message: str, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent response based on query analysis"""
        response_data = {
            'message': '',
            'float_data': [],
            'plot_data': None,
            'statistics': {}
        }
        
        if intent['type'] == 'float_specific' and intent['float_ids']:
            # Handle specific float queries
            float_id = intent['float_ids'][0]  # Focus on first mentioned float
            float_data = self.get_float_data(float_id)
            
            if float_data:
                response_data['float_data'] = [float_data]
                response_data['plot_data'] = self._prepare_plot_data(float_data)
                response_data['message'] = self._format_float_response(float_data, intent)
                response_data['statistics'] = self._calculate_float_statistics(float_data)
            else:
                response_data['message'] = self._format_no_float_response(float_id)
        
        elif intent['type'] == 'region_search' and intent['region']:
            # Handle region-based queries
            region_floats = self.search_floats_by_region(intent['region'])
            
            if region_floats:
                response_data['float_data'] = region_floats[:5]  # Limit to 5 floats for display
                response_data['message'] = self._format_region_search_response(intent['region'], region_floats)
                
                # Set plot data for the first float found
                if region_floats:
                    response_data['plot_data'] = self._prepare_plot_data(region_floats[0])
                    response_data['statistics'] = self._calculate_float_statistics(region_floats[0])
            else:
                # No floats found in region, provide general info + LLM context
                response_data['message'] = f"🌊 I found some general information about the {intent['region']}. While I don't have specific ARGO floats in that exact region right now, here's what I know:\n\n"
                
                # Add LLM context about the region
                region_context = self._get_region_context(intent['region'])
                response_data['message'] += region_context
                
                response_data['float_data'] = self._get_sample_floats(3)  # Show some other floats
        
        elif intent['type'] == 'general' and not intent['float_ids']:
            # Handle general queries
            response_data['message'] = self._generate_general_response(message, intent)
            
            # Suggest some floats
            sample_floats = self._get_sample_floats(3)
            response_data['float_data'] = sample_floats
            
        else:
            # Handle topic-specific queries without specific float
            response_data['message'] = self._generate_topic_response(intent)
            sample_floats = self._get_sample_floats(2)
            response_data['float_data'] = sample_floats
        
        return response_data

    def _format_float_response(self, float_data: Dict, intent: Dict) -> str:
        """Format response for specific float queries"""
        templates = self.response_templates['float_info']
        template = np.random.choice(templates)
        
        # Calculate additional metrics
        deep_temp = min(float_data['profile_data']['temperatures'])
        gradient = (float_data['surface_temperature'] - deep_temp) / (float_data['max_depth'] / 100)
        
        # Determine descriptions
        season_desc = "seasonal warming" if float_data['surface_temperature'] > 26 else "cooler conditions"
        mixing_desc = "strong mixing" if gradient > 15 else "stratified conditions"
        
        return template.format(
            float_id=float_data['float_id'],
            lat=float_data['latitude'],
            lon=float_data['longitude'],
            temp=float_data['surface_temperature'],
            sal=float_data['surface_salinity'],
            depth=float_data['max_depth'],
            status=float_data['status'],
            last_contact=float_data['last_contact'],
            region=float_data['region'],
            platform_type=float_data['platform_type'],
            quality=float_data['data_quality'],
            profiles=float_data['total_profiles'],
            deep_temp=round(deep_temp, 1),
            gradient=round(gradient, 1),
            season_desc=season_desc,
            mixing_desc=mixing_desc
        )

    def _prepare_plot_data(self, float_data: Dict) -> Dict:
        """Prepare data for plotting"""
        return {
            'float_id': float_data['float_id'],
            'latitude': float_data['latitude'],
            'longitude': float_data['longitude'],
            'surface_temp': float_data['surface_temperature'],
            'surface_salinity': float_data['surface_salinity'],
            'max_depth': float_data['max_depth'],
            'profile_data': float_data['profile_data']
        }

    def _calculate_float_statistics(self, float_data: Dict) -> Dict:
        """Calculate statistics for a float"""
        profile = float_data['profile_data']
        
        return {
            'avg_temperature': round(np.mean(profile['temperatures']), 2),
            'min_temperature': round(min(profile['temperatures']), 2),
            'max_temperature': round(max(profile['temperatures']), 2),
            'avg_salinity': round(np.mean(profile['salinities']), 2),
            'min_salinity': round(min(profile['salinities']), 2),
            'max_salinity': round(max(profile['salinities']), 2),
            'thermocline_depth': self._estimate_thermocline_depth(profile),
            'mixed_layer_depth': self._estimate_mixed_layer_depth(profile)
        }

    def _estimate_thermocline_depth(self, profile: Dict) -> float:
        """Estimate thermocline depth from temperature profile"""
        temps = profile['temperatures']
        depths = profile['depths']
        
        # Find maximum temperature gradient
        max_gradient = 0
        thermocline_depth = 50  # default
        
        for i in range(1, len(temps)-1):
            if depths[i] > 20 and depths[i] < 300:  # Look in typical thermocline range
                gradient = abs(temps[i-1] - temps[i+1]) / (depths[i+1] - depths[i-1])
                if gradient > max_gradient:
                    max_gradient = gradient
                    thermocline_depth = depths[i]
        
        return round(thermocline_depth, 1)

    def _estimate_mixed_layer_depth(self, profile: Dict) -> float:
        """Estimate mixed layer depth"""
        temps = profile['temperatures']
        depths = profile['depths']
        
        surface_temp = temps[0]
        
        # Find depth where temperature drops by 0.2°C from surface
        for i, temp in enumerate(temps):
            if abs(temp - surface_temp) > 0.2:
                return round(depths[i], 1)
        
        return round(depths[10], 1)  # Default to ~20% of profile

    def _get_sample_floats(self, count: int) -> List[Dict]:
        """Get sample floats for general responses"""
        float_ids = list(self.float_database.keys())
        sample_ids = np.random.choice(float_ids, min(count, len(float_ids)), replace=False)
        return [self.float_database[fid] for fid in sample_ids]

    def _format_no_float_response(self, float_id: str) -> str:
        """Format response when float is not found"""
        templates = self.response_templates['no_float_found']
        template = np.random.choice(templates)
        
        # Get some alternative floats
        sample_floats = self._get_sample_floats(5)
        float_list = "\n".join([
            f"• **{f['float_id']}** - {f['region']} ({f['status']})"
            for f in sample_floats
        ])
        
        return template.format(float_list=float_list)

    def _format_region_search_response(self, region: str, region_floats: List[Dict]) -> str:
        """Format response for region search queries"""
        templates = self.response_templates['region_search']
        template = np.random.choice(templates)
        
        # Format floats list
        floats_list = "\n".join([
            f"• **{f['float_id']}** - {f['latitude']}°N, {f['longitude']}°E ({f['status']})"
            for f in region_floats[:5]  # Limit display to 5 floats
        ])
        
        return template.format(
            region=region,
            count=len(region_floats),
            floats_list=floats_list
        )

    def _get_region_context(self, region: str) -> str:
        """Get oceanographic context about a region using LLM when no floats are found"""
        try:
            from groq import Groq
            import os
            
            groq_api_key = os.getenv('GROQ_API_KEY')
            if not groq_api_key:
                return f"The {region} is an important oceanographic region with unique characteristics. ARGO floats help monitor ocean conditions here."
            
            client = Groq(api_key=groq_api_key)
            
            system_prompt = "You are a marine scientist. Provide 2-3 brief facts about this ocean region, focusing on oceanography, currents, or unique features. Keep it under 100 words."
            
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Tell me about the oceanography of the {region}:"}
                ],
                temperature=0.3,
                max_tokens=100,
            )
            
            context = response.choices[0].message.content.strip()
            return f"• {context}\n\n• ARGO floats in nearby regions provide similar oceanographic data."
            
        except Exception as e:
            logger.error(f"Region context LLM error: {e}")
            return f"The {region} features unique oceanographic conditions. ARGO floats help monitor temperature, salinity, and current patterns in this area."

    def _generate_general_response(self, message: str, intent: Dict) -> str:
        """Generate response for general queries"""
        responses = [
            "🌊 I can help you explore ARGO float data in the Indian Ocean! Here are some active floats you can investigate:",
            "📊 The Indian Ocean has many active ARGO floats collecting oceanographic data. Let me show you some interesting ones:",
            "🔍 I have access to 150 ARGO floats across the Indian Ocean. Here are some with recent data:",
        ]
        
        return np.random.choice(responses)

    def _generate_topic_response(self, intent: Dict) -> str:
        """Generate response for topic-specific queries"""
        if 'temperature_query' in intent['topics']:
            return "🌡️ Temperature analysis is fascinating! Let me show you some floats with interesting thermal profiles:"
        elif 'salinity_query' in intent['topics']:
            return "🧂 Salinity patterns reveal ocean circulation! Here are floats with notable salinity characteristics:"
        elif 'depth_query' in intent['topics']:
            return "📊 Depth profiles show ocean structure! Let me highlight floats with comprehensive vertical data:"
        else:
            return "🌊 Here's some oceanographic data that might interest you:"

    def get_all_floats(self) -> Dict[str, Dict]:
        """Get all available floats"""
        return self.float_database

    def search_floats_by_region(self, region: str) -> List[Dict]:
        """Search floats by oceanographic region with flexible matching"""
        region_lower = region.lower()
        
        # Map common region names to our internal regions
        region_mappings = {
            'arabian sea': ['Arabian Sea'],
            'bay of bengal': ['Bay of Bengal'], 
            'central indian ocean': ['Central Indian Ocean'],
            'southern indian ocean': ['Southern Indian Ocean'],
            'western indian ocean': ['Western Indian Ocean'],
            'indian ocean': ['Arabian Sea', 'Bay of Bengal', 'Central Indian Ocean', 'Southern Indian Ocean', 'Western Indian Ocean', 'Indian Ocean']
        }
        
        # Get the regions to search for
        search_regions = region_mappings.get(region_lower, [region])
        
        # Find floats in any of the matching regions
        matching_floats = []
        for float_data in self.float_database.values():
            if float_data['region'] in search_regions:
                matching_floats.append(float_data)
        
        return matching_floats

    def get_active_floats(self) -> List[Dict]:
        """Get all active floats"""
        return [
            float_data for float_data in self.float_database.values()
            if float_data['status'] == 'Active'
        ]


# Global RAG instance
argo_rag = ArgoFloatRAG()


def process_chat_message(message: str) -> Dict[str, Any]:
    """Main function to process chat messages with RAG"""
    intent = argo_rag.analyze_query_intent(message)
    response = argo_rag.generate_response(message, intent)
    return response


def get_float_for_plotting(float_id: str) -> Optional[Dict]:
    """Get float data specifically for plotting"""
    return argo_rag.get_float_data(float_id)


def get_available_floats() -> List[str]:
    """Get list of all available float IDs"""
    return list(argo_rag.float_database.keys())


if __name__ == "__main__":
    # Test the RAG system
    test_messages = [
        "Tell me about ARGO_5034",
        "What's the temperature profile for float 5045?",
        "Show me salinity data for ARGO_5001",
        "Compare ARGO_5010 and ARGO_5020",
        "What floats are active in the Arabian Sea?"
    ]
    
    print("🧪 Testing ARGO Float RAG System")
    print("=" * 50)
    
    for msg in test_messages:
        print(f"\n💬 Query: {msg}")
        response = process_chat_message(msg)
        print(f"🤖 Response: {response['message'][:200]}...")
        if response['float_data']:
            print(f"📊 Float data: {len(response['float_data'])} floats")
        if response['plot_data']:
            print(f"📈 Plot data available for: {response['plot_data']['float_id']}")
