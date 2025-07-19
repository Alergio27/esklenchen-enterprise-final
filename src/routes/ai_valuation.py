from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.ai_valuation import db, PropertyValuation, MarketData
from datetime import datetime, date
import time

ai_valuation_bp = Blueprint('ai_valuation', __name__)

@ai_valuation_bp.route('/valuation/property', methods=['POST'])
@cross_origin()
def create_property_valuation():
    """Create new property valuation using AI"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['location', 'property_type', 'surface']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Record start time for processing time calculation
        start_time = time.time()
        
        # Create new valuation
        valuation = PropertyValuation(
            location=data['location'],
            property_type=data['property_type'],
            surface=data['surface'],
            rooms=data.get('rooms'),
            bathrooms=data.get('bathrooms'),
            floor=data.get('floor'),
            year_built=data.get('year_built'),
            neighborhood=data.get('neighborhood'),
            distance_to_beach=data.get('distance_to_beach'),
            distance_to_center=data.get('distance_to_center'),
            transport_score=data.get('transport_score'),
            amenities_score=data.get('amenities_score'),
            condition=data.get('condition', 'good'),
            renovation_needed=data.get('renovation_needed', False),
            estimated_renovation_cost=data.get('estimated_renovation_cost'),
            current_market_price=data.get('current_market_price'),
            requester_name=data.get('requester_name'),
            requester_email=data.get('requester_email'),
            requester_phone=data.get('requester_phone'),
            request_purpose=data.get('request_purpose', 'curiosity')
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        valuation.processing_time_seconds = processing_time
        
        db.session.add(valuation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'valuation': valuation.to_dict(),
            'message': 'Property valuation completed successfully',
            'processing_time': f"{processing_time:.2f} seconds"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_valuation_bp.route('/valuation/quick', methods=['POST'])
@cross_origin()
def quick_valuation():
    """Quick property valuation for website forms"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['location', 'surface']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create simplified valuation
        valuation = PropertyValuation(
            location=data['location'],
            property_type=data.get('property_type', 'apartamento'),
            surface=data['surface'],
            rooms=data.get('rooms'),
            condition='good',  # Default assumption
            requester_name=data.get('name'),
            requester_email=data.get('email'),
            requester_phone=data.get('phone'),
            request_purpose='website_form'
        )
        
        db.session.add(valuation)
        db.session.commit()
        
        # Return simplified response for quick valuation
        return jsonify({
            'success': True,
            'valuation_id': valuation.id,
            'estimated_value': valuation.ai_estimated_value,
            'price_per_sqm': valuation.price_per_sqm,
            'rental_potential_monthly': valuation.rental_potential_monthly,
            'rental_yield_percentage': valuation.rental_yield_percentage,
            'expected_roi_1year': valuation.expected_roi_1year,
            'investment_potential': valuation.investment_potential,
            'confidence_score': valuation.ai_confidence_score,
            'recommendations': valuation.get_recommendations()[:3],  # Top 3 recommendations
            'message': 'Valoración completada. Un experto te contactará pronto para análisis detallado.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_valuation_bp.route('/valuation/<int:valuation_id>', methods=['GET'])
@cross_origin()
def get_valuation(valuation_id):
    """Get specific valuation by ID"""
    try:
        valuation = PropertyValuation.query.get_or_404(valuation_id)
        return jsonify({
            'success': True,
            'valuation': valuation.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_valuation_bp.route('/valuations', methods=['GET'])
@cross_origin()
def get_valuations():
    """Get all valuations with optional filtering"""
    try:
        # Get query parameters
        location = request.args.get('location')
        property_type = request.args.get('property_type')
        status = request.args.get('status')
        requester_email = request.args.get('requester_email')
        limit = request.args.get('limit', type=int)
        
        # Build query
        query = PropertyValuation.query
        
        if location:
            query = query.filter(PropertyValuation.location.contains(location))
        if property_type:
            query = query.filter_by(property_type=property_type)
        if status:
            query = query.filter_by(status=status)
        if requester_email:
            query = query.filter_by(requester_email=requester_email)
        
        # Order by creation date (newest first)
        query = query.order_by(PropertyValuation.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        valuations = query.all()
        
        return jsonify({
            'success': True,
            'valuations': [valuation.to_dict() for valuation in valuations],
            'total': len(valuations)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_valuation_bp.route('/valuations/recent', methods=['GET'])
@cross_origin()
def get_recent_valuations():
    """Get recent valuations"""
    try:
        limit = request.args.get('limit', 10, type=int)
        valuations = PropertyValuation.get_recent_valuations(limit)
        
        return jsonify({
            'success': True,
            'valuations': [valuation.to_dict() for valuation in valuations]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_valuation_bp.route('/valuations/by-location/<location>', methods=['GET'])
@cross_origin()
def get_valuations_by_location(location):
    """Get valuations by location"""
    try:
        limit = request.args.get('limit', 5, type=int)
        valuations = PropertyValuation.get_valuations_by_location(location, limit)
        
        return jsonify({
            'success': True,
            'location': location,
            'valuations': [valuation.to_dict() for valuation in valuations]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_valuation_bp.route('/market-data', methods=['GET'])
@cross_origin()
def get_market_data():
    """Get market data for locations and property types"""
    try:
        location = request.args.get('location')
        property_type = request.args.get('property_type')
        
        query = MarketData.query
        
        if location:
            query = query.filter(MarketData.location.contains(location))
        if property_type:
            query = query.filter_by(property_type=property_type)
        
        market_data = query.order_by(MarketData.data_date.desc()).all()
        
        return jsonify({
            'success': True,
            'market_data': [data.to_dict() for data in market_data]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_valuation_bp.route('/valuation/compare', methods=['POST'])
@cross_origin()
def compare_properties():
    """Compare multiple properties"""
    try:
        data = request.get_json()
        
        if 'properties' not in data or len(data['properties']) < 2:
            return jsonify({
                'success': False,
                'error': 'At least 2 properties required for comparison'
            }), 400
        
        comparisons = []
        
        for prop_data in data['properties']:
            # Create temporary valuation for comparison
            valuation = PropertyValuation(
                location=prop_data['location'],
                property_type=prop_data.get('property_type', 'apartamento'),
                surface=prop_data['surface'],
                rooms=prop_data.get('rooms'),
                condition=prop_data.get('condition', 'good'),
                request_purpose='comparison'
            )
            
            comparisons.append({
                'location': valuation.location,
                'property_type': valuation.property_type,
                'surface': valuation.surface,
                'estimated_value': valuation.ai_estimated_value,
                'price_per_sqm': valuation.price_per_sqm,
                'rental_potential_monthly': valuation.rental_potential_monthly,
                'rental_yield_percentage': valuation.rental_yield_percentage,
                'expected_roi_1year': valuation.expected_roi_1year,
                'investment_potential': valuation.investment_potential,
                'risk_level': valuation.risk_level,
                'confidence_score': valuation.ai_confidence_score
            })
        
        # Find best investment opportunity
        best_roi = max(comparisons, key=lambda x: x['expected_roi_1year'] or 0)
        best_value = min(comparisons, key=lambda x: x['price_per_sqm'] or float('inf'))
        
        return jsonify({
            'success': True,
            'comparisons': comparisons,
            'analysis': {
                'best_roi': best_roi,
                'best_value': best_value,
                'total_properties': len(comparisons)
            },
            'message': 'Property comparison completed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_valuation_bp.route('/valuation/stats', methods=['GET'])
@cross_origin()
def get_valuation_stats():
    """Get valuation statistics"""
    try:
        total_valuations = PropertyValuation.query.count()
        completed_valuations = PropertyValuation.query.filter_by(status='completed').count()
        
        # Average confidence score
        avg_confidence = db.session.query(db.func.avg(PropertyValuation.ai_confidence_score)).scalar() or 0
        
        # Average processing time
        avg_processing_time = db.session.query(db.func.avg(PropertyValuation.processing_time_seconds)).scalar() or 0
        
        # Valuations by location
        locations = db.session.query(
            PropertyValuation.location,
            db.func.count(PropertyValuation.id),
            db.func.avg(PropertyValuation.price_per_sqm)
        ).group_by(PropertyValuation.location).limit(10).all()
        
        # Valuations by property type
        property_types = db.session.query(
            PropertyValuation.property_type,
            db.func.count(PropertyValuation.id),
            db.func.avg(PropertyValuation.ai_estimated_value)
        ).group_by(PropertyValuation.property_type).all()
        
        # Investment potential distribution
        investment_potential = db.session.query(
            PropertyValuation.investment_potential,
            db.func.count(PropertyValuation.id)
        ).group_by(PropertyValuation.investment_potential).all()
        
        # Risk level distribution
        risk_levels = db.session.query(
            PropertyValuation.risk_level,
            db.func.count(PropertyValuation.id)
        ).group_by(PropertyValuation.risk_level).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_valuations': total_valuations,
                'completed_valuations': completed_valuations,
                'average_confidence_score': round(avg_confidence, 2),
                'average_processing_time': round(avg_processing_time, 2),
                'top_locations': [
                    {
                        'location': loc,
                        'count': count,
                        'avg_price_per_sqm': round(avg_price, 2) if avg_price else 0
                    }
                    for loc, count, avg_price in locations
                ],
                'property_types': [
                    {
                        'type': prop_type,
                        'count': count,
                        'avg_value': round(avg_value, 2) if avg_value else 0
                    }
                    for prop_type, count, avg_value in property_types
                ],
                'investment_potential': [
                    {'potential': potential, 'count': count}
                    for potential, count in investment_potential
                ],
                'risk_levels': [
                    {'risk_level': risk, 'count': count}
                    for risk, count in risk_levels
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_valuation_bp.route('/valuation/renovation-proposal', methods=['POST'])
@cross_origin()
def generate_renovation_proposal():
    """Generate renovation proposal for 'Reforma sin Coste' program"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['location', 'property_type', 'surface', 'current_condition']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create valuation for renovation analysis
        valuation = PropertyValuation(
            location=data['location'],
            property_type=data['property_type'],
            surface=data['surface'],
            rooms=data.get('rooms'),
            condition=data['current_condition'],
            renovation_needed=True,
            requester_name=data.get('name'),
            requester_email=data.get('email'),
            requester_phone=data.get('phone'),
            request_purpose='renovation_proposal'
        )
        
        # Calculate renovation costs and potential
        base_renovation_cost = valuation.surface * 800  # €800 per m² average
        
        # Adjust based on condition
        condition_multipliers = {
            'poor': 1.3,
            'fair': 1.1,
            'good': 0.8,
            'excellent': 0.5
        }
        
        renovation_cost = base_renovation_cost * condition_multipliers.get(data['current_condition'], 1.0)
        valuation.estimated_renovation_cost = renovation_cost
        
        # Calculate post-renovation value
        post_renovation_value = valuation.ai_estimated_value * 1.25  # 25% increase after renovation
        
        # Calculate program benefits
        monthly_rental_post_renovation = valuation.rental_potential_monthly * 1.4  # 40% increase
        annual_rental = monthly_rental_post_renovation * 12
        payback_period_months = renovation_cost / monthly_rental_post_renovation if monthly_rental_post_renovation > 0 else 0
        
        db.session.add(valuation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'valuation_id': valuation.id,
            'renovation_proposal': {
                'current_value': valuation.ai_estimated_value,
                'post_renovation_value': post_renovation_value,
                'value_increase': post_renovation_value - valuation.ai_estimated_value,
                'renovation_cost': renovation_cost,
                'current_rental_potential': valuation.rental_potential_monthly,
                'post_renovation_rental': monthly_rental_post_renovation,
                'rental_increase': monthly_rental_post_renovation - valuation.rental_potential_monthly,
                'annual_rental_income': annual_rental,
                'payback_period_months': round(payback_period_months, 1),
                'roi_first_year': round((annual_rental / renovation_cost) * 100, 2) if renovation_cost > 0 else 0,
                'program_benefits': [
                    "Financiación 100% de la reforma",
                    "Sin coste inicial para el propietario",
                    "Gestión completa del proyecto",
                    "Garantía de calidad y plazos",
                    "Incremento inmediato del valor",
                    "Optimización para alquiler turístico"
                ],
                'next_steps': [
                    "Visita técnica gratuita",
                    "Presupuesto detallado",
                    "Firma del acuerdo",
                    "Inicio de obras",
                    "Entrega y puesta en marcha"
                ]
            },
            'confidence_score': valuation.ai_confidence_score,
            'message': 'Propuesta de reforma generada. Te contactaremos para concretar detalles.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

