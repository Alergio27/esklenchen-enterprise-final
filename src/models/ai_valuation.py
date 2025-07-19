from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import random
import math

db = SQLAlchemy()

class PropertyValuation(db.Model):
    __tablename__ = 'property_valuations'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Property Basic Information
    location = db.Column(db.String(100), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)  # apartamento, casa, villa, estudio
    surface = db.Column(db.Float, nullable=False)  # m²
    rooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    floor = db.Column(db.String(20))
    year_built = db.Column(db.Integer)
    
    # Location Details
    neighborhood = db.Column(db.String(100))
    distance_to_beach = db.Column(db.Float)  # km
    distance_to_center = db.Column(db.Float)  # km
    transport_score = db.Column(db.Integer)  # 1-10
    amenities_score = db.Column(db.Integer)  # 1-10
    
    # Property Condition
    condition = db.Column(db.String(20))  # excellent, good, fair, poor
    renovation_needed = db.Column(db.Boolean, default=False)
    estimated_renovation_cost = db.Column(db.Float)
    
    # Market Data
    current_market_price = db.Column(db.Float)
    price_per_sqm = db.Column(db.Float)
    rental_potential_monthly = db.Column(db.Float)
    rental_yield_percentage = db.Column(db.Float)
    
    # AI Analysis Results
    ai_estimated_value = db.Column(db.Float)
    ai_confidence_score = db.Column(db.Float)  # 0-100
    ai_analysis_factors = db.Column(db.Text)  # JSON
    ai_recommendations = db.Column(db.Text)  # JSON
    
    # Investment Analysis
    investment_potential = db.Column(db.String(20))  # excellent, good, fair, poor
    expected_roi_1year = db.Column(db.Float)
    expected_roi_3year = db.Column(db.Float)
    expected_roi_5year = db.Column(db.Float)
    
    # Risk Assessment
    risk_level = db.Column(db.String(20))  # low, medium, high
    risk_factors = db.Column(db.Text)  # JSON
    
    # Market Trends
    market_trend = db.Column(db.String(20))  # rising, stable, declining
    seasonal_demand = db.Column(db.Text)  # JSON
    competition_level = db.Column(db.String(20))  # low, medium, high
    
    # Request Information
    requester_name = db.Column(db.String(100))
    requester_email = db.Column(db.String(120))
    requester_phone = db.Column(db.String(20))
    request_purpose = db.Column(db.String(50))  # purchase, sale, investment, curiosity
    
    # Status and Processing
    status = db.Column(db.String(20), default='processing')  # processing, completed, error
    processing_time_seconds = db.Column(db.Float)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __init__(self, **kwargs):
        super(PropertyValuation, self).__init__(**kwargs)
        self.calculate_ai_valuation()
    
    def calculate_ai_valuation(self):
        """Advanced AI valuation algorithm"""
        try:
            # Base price calculation using location and property type
            base_price = self._get_base_price_by_location()
            
            # Apply property-specific multipliers
            size_multiplier = self._calculate_size_multiplier()
            condition_multiplier = self._calculate_condition_multiplier()
            location_multiplier = self._calculate_location_multiplier()
            market_multiplier = self._calculate_market_multiplier()
            
            # Calculate estimated value
            self.ai_estimated_value = base_price * size_multiplier * condition_multiplier * location_multiplier * market_multiplier
            self.price_per_sqm = self.ai_estimated_value / self.surface if self.surface > 0 else 0
            
            # Calculate rental potential
            self._calculate_rental_potential()
            
            # Calculate ROI projections
            self._calculate_roi_projections()
            
            # Assess risk factors
            self._assess_risk_factors()
            
            # Generate AI confidence score
            self._calculate_confidence_score()
            
            # Generate recommendations
            self._generate_recommendations()
            
            self.status = 'completed'
            self.completed_at = datetime.utcnow()
            
        except Exception as e:
            self.status = 'error'
            print(f"Error in AI valuation: {e}")
    
    def _get_base_price_by_location(self):
        """Get base price per m² by location"""
        location_prices = {
            'barcelona': 4500,
            'badalona': 3200,
            'sant adrià': 3000,
            'montgat': 3800,
            'el masnou': 4000,
            'premià de mar': 3500,
            'vilassar de mar': 3600,
            'mataró': 2800,
            'calella': 2500,
            'sitges': 5500,
            'castelldefels': 4200,
            'gavà': 3400
        }
        
        location_lower = self.location.lower()
        for city, price in location_prices.items():
            if city in location_lower:
                return price * self.surface
        
        # Default price for unknown locations
        return 3500 * self.surface
    
    def _calculate_size_multiplier(self):
        """Calculate multiplier based on property size"""
        if self.surface <= 40:
            return 1.1  # Small properties have premium per m²
        elif self.surface <= 70:
            return 1.0
        elif self.surface <= 100:
            return 0.98
        elif self.surface <= 150:
            return 0.95
        else:
            return 0.92  # Large properties have discount per m²
    
    def _calculate_condition_multiplier(self):
        """Calculate multiplier based on property condition"""
        condition_multipliers = {
            'excellent': 1.15,
            'good': 1.0,
            'fair': 0.85,
            'poor': 0.70
        }
        return condition_multipliers.get(self.condition, 1.0)
    
    def _calculate_location_multiplier(self):
        """Calculate multiplier based on location factors"""
        multiplier = 1.0
        
        # Distance to beach bonus
        if self.distance_to_beach:
            if self.distance_to_beach <= 0.5:
                multiplier *= 1.2
            elif self.distance_to_beach <= 1.0:
                multiplier *= 1.1
            elif self.distance_to_beach <= 2.0:
                multiplier *= 1.05
        
        # Transport score bonus
        if self.transport_score:
            multiplier *= (0.9 + (self.transport_score / 100))
        
        # Amenities score bonus
        if self.amenities_score:
            multiplier *= (0.95 + (self.amenities_score / 200))
        
        return multiplier
    
    def _calculate_market_multiplier(self):
        """Calculate multiplier based on market conditions"""
        # Simulate market conditions based on current date
        current_month = datetime.now().month
        
        # Summer months have higher demand
        if current_month in [6, 7, 8]:
            return 1.08
        elif current_month in [4, 5, 9, 10]:
            return 1.03
        else:
            return 0.98
    
    def _calculate_rental_potential(self):
        """Calculate rental potential and yield"""
        # Base rental calculation (typically 0.4-0.8% of property value per month)
        base_rental_rate = 0.006  # 0.6% monthly
        
        # Adjust based on location and property type
        if 'barcelona' in self.location.lower() or 'sitges' in self.location.lower():
            base_rental_rate = 0.007
        elif 'badalona' in self.location.lower() or 'maresme' in self.location.lower():
            base_rental_rate = 0.0065
        
        # Property type adjustments
        if self.property_type == 'estudio':
            base_rental_rate *= 1.1
        elif self.property_type == 'villa':
            base_rental_rate *= 0.9
        
        self.rental_potential_monthly = self.ai_estimated_value * base_rental_rate
        
        # Calculate annual yield
        annual_rental = self.rental_potential_monthly * 12
        self.rental_yield_percentage = (annual_rental / self.ai_estimated_value) * 100 if self.ai_estimated_value > 0 else 0
    
    def _calculate_roi_projections(self):
        """Calculate ROI projections for different time periods"""
        base_appreciation = 0.04  # 4% annual appreciation
        rental_yield = self.rental_yield_percentage / 100 if self.rental_yield_percentage else 0.06
        
        # 1-year ROI (mainly rental yield)
        self.expected_roi_1year = rental_yield * 100
        
        # 3-year ROI (rental + appreciation)
        appreciation_3year = (1 + base_appreciation) ** 3 - 1
        total_rental_3year = rental_yield * 3
        self.expected_roi_3year = (appreciation_3year + total_rental_3year) * 100
        
        # 5-year ROI (rental + appreciation)
        appreciation_5year = (1 + base_appreciation) ** 5 - 1
        total_rental_5year = rental_yield * 5
        self.expected_roi_5year = (appreciation_5year + total_rental_5year) * 100
    
    def _assess_risk_factors(self):
        """Assess investment risk factors"""
        risk_factors = []
        risk_score = 0
        
        # Location risk
        if 'barcelona' in self.location.lower():
            risk_score += 1
            risk_factors.append("Mercado muy competitivo en Barcelona")
        
        # Property age risk
        current_year = datetime.now().year
        if self.year_built and (current_year - self.year_built) > 40:
            risk_score += 2
            risk_factors.append("Propiedad antigua, posibles gastos de mantenimiento")
        
        # Size risk
        if self.surface < 35:
            risk_score += 1
            risk_factors.append("Superficie pequeña, mercado limitado")
        elif self.surface > 200:
            risk_score += 1
            risk_factors.append("Superficie grande, menor liquidez")
        
        # Condition risk
        if self.condition in ['fair', 'poor']:
            risk_score += 2
            risk_factors.append("Estado de conservación requiere atención")
        
        # Renovation risk
        if self.renovation_needed:
            risk_score += 2
            risk_factors.append("Necesita renovación, costes adicionales")
        
        # Determine risk level
        if risk_score <= 2:
            self.risk_level = 'low'
        elif risk_score <= 5:
            self.risk_level = 'medium'
        else:
            self.risk_level = 'high'
        
        self.risk_factors = json.dumps(risk_factors)
    
    def _calculate_confidence_score(self):
        """Calculate AI confidence score based on data quality"""
        confidence = 85  # Base confidence
        
        # Reduce confidence for missing data
        if not self.year_built:
            confidence -= 5
        if not self.condition:
            confidence -= 5
        if not self.distance_to_beach:
            confidence -= 3
        if not self.transport_score:
            confidence -= 3
        if not self.amenities_score:
            confidence -= 3
        
        # Increase confidence for complete data
        if all([self.rooms, self.bathrooms, self.floor]):
            confidence += 5
        
        # Location confidence
        known_locations = ['barcelona', 'badalona', 'sitges', 'mataró', 'calella']
        if any(loc in self.location.lower() for loc in known_locations):
            confidence += 5
        
        self.ai_confidence_score = max(60, min(95, confidence))
    
    def _generate_recommendations(self):
        """Generate AI recommendations"""
        recommendations = []
        
        # Investment potential
        if self.expected_roi_1year > 8:
            self.investment_potential = 'excellent'
            recommendations.append("Excelente oportunidad de inversión con alta rentabilidad")
        elif self.expected_roi_1year > 6:
            self.investment_potential = 'good'
            recommendations.append("Buena oportunidad de inversión")
        elif self.expected_roi_1year > 4:
            self.investment_potential = 'fair'
            recommendations.append("Inversión moderada, considerar otros factores")
        else:
            self.investment_potential = 'poor'
            recommendations.append("Rentabilidad baja, evaluar cuidadosamente")
        
        # Specific recommendations
        if self.renovation_needed:
            recommendations.append("Considerar programa 'Reforma sin Coste' de ESKLENCHEN")
        
        if self.distance_to_beach and self.distance_to_beach <= 1:
            recommendations.append("Proximidad a la playa aumenta potencial turístico")
        
        if self.property_type == 'estudio' and 'barcelona' in self.location.lower():
            recommendations.append("Estudios en Barcelona tienen alta demanda de alquiler")
        
        if self.rental_yield_percentage > 7:
            recommendations.append("Excelente potencial de alquiler turístico")
        
        self.ai_recommendations = json.dumps(recommendations)
    
    def get_analysis_factors(self):
        """Get analysis factors as Python list"""
        if self.ai_analysis_factors:
            return json.loads(self.ai_analysis_factors)
        return []
    
    def get_recommendations(self):
        """Get recommendations as Python list"""
        if self.ai_recommendations:
            return json.loads(self.ai_recommendations)
        return []
    
    def get_risk_factors(self):
        """Get risk factors as Python list"""
        if self.risk_factors:
            return json.loads(self.risk_factors)
        return []
    
    def to_dict(self):
        """Convert valuation to dictionary for API responses"""
        return {
            'id': self.id,
            'location': self.location,
            'property_type': self.property_type,
            'surface': self.surface,
            'rooms': self.rooms,
            'bathrooms': self.bathrooms,
            'floor': self.floor,
            'year_built': self.year_built,
            'neighborhood': self.neighborhood,
            'distance_to_beach': self.distance_to_beach,
            'distance_to_center': self.distance_to_center,
            'transport_score': self.transport_score,
            'amenities_score': self.amenities_score,
            'condition': self.condition,
            'renovation_needed': self.renovation_needed,
            'estimated_renovation_cost': self.estimated_renovation_cost,
            'current_market_price': self.current_market_price,
            'ai_estimated_value': self.ai_estimated_value,
            'price_per_sqm': self.price_per_sqm,
            'rental_potential_monthly': self.rental_potential_monthly,
            'rental_yield_percentage': self.rental_yield_percentage,
            'ai_confidence_score': self.ai_confidence_score,
            'investment_potential': self.investment_potential,
            'expected_roi_1year': self.expected_roi_1year,
            'expected_roi_3year': self.expected_roi_3year,
            'expected_roi_5year': self.expected_roi_5year,
            'risk_level': self.risk_level,
            'risk_factors': self.get_risk_factors(),
            'market_trend': self.market_trend,
            'competition_level': self.competition_level,
            'ai_recommendations': self.get_recommendations(),
            'requester_name': self.requester_name,
            'requester_email': self.requester_email,
            'status': self.status,
            'processing_time_seconds': self.processing_time_seconds,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @staticmethod
    def get_recent_valuations(limit=10):
        """Get recent valuations"""
        return PropertyValuation.query.filter_by(status='completed').order_by(
            PropertyValuation.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_valuations_by_location(location, limit=5):
        """Get valuations by location"""
        return PropertyValuation.query.filter(
            PropertyValuation.location.contains(location),
            PropertyValuation.status == 'completed'
        ).order_by(PropertyValuation.created_at.desc()).limit(limit).all()
    
    def __repr__(self):
        return f'<PropertyValuation {self.location} - {self.property_type}>'


class MarketData(db.Model):
    __tablename__ = 'market_data'
    
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    
    # Market Prices
    average_price_per_sqm = db.Column(db.Float)
    median_price_per_sqm = db.Column(db.Float)
    min_price_per_sqm = db.Column(db.Float)
    max_price_per_sqm = db.Column(db.Float)
    
    # Market Activity
    properties_sold_last_month = db.Column(db.Integer)
    average_days_on_market = db.Column(db.Integer)
    price_trend_percentage = db.Column(db.Float)  # Monthly change
    
    # Rental Market
    average_rental_yield = db.Column(db.Float)
    average_rental_price_per_sqm = db.Column(db.Float)
    occupancy_rate = db.Column(db.Float)
    
    # Data Source and Quality
    data_source = db.Column(db.String(100))
    confidence_level = db.Column(db.Float)
    sample_size = db.Column(db.Integer)
    
    # Timestamps
    data_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'property_type': self.property_type,
            'average_price_per_sqm': self.average_price_per_sqm,
            'median_price_per_sqm': self.median_price_per_sqm,
            'min_price_per_sqm': self.min_price_per_sqm,
            'max_price_per_sqm': self.max_price_per_sqm,
            'properties_sold_last_month': self.properties_sold_last_month,
            'average_days_on_market': self.average_days_on_market,
            'price_trend_percentage': self.price_trend_percentage,
            'average_rental_yield': self.average_rental_yield,
            'average_rental_price_per_sqm': self.average_rental_price_per_sqm,
            'occupancy_rate': self.occupancy_rate,
            'data_source': self.data_source,
            'confidence_level': self.confidence_level,
            'sample_size': self.sample_size,
            'data_date': self.data_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }

