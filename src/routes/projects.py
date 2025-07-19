from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.project import db, Project, ProjectImage, ProjectAnalytics
from src.models.client import Client
from datetime import datetime, date
import json

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects', methods=['GET'])
@cross_origin()
def get_projects():
    """Get all projects with optional filtering"""
    try:
        # Get query parameters
        category = request.args.get('category')
        status = request.args.get('status')
        client_id = request.args.get('client_id')
        location = request.args.get('location')
        limit = request.args.get('limit', type=int)
        
        # Build query
        query = Project.query
        
        if category:
            query = query.filter_by(category=category)
        if status:
            query = query.filter_by(status=status)
        if client_id:
            query = query.filter_by(client_id=client_id)
        if location:
            query = query.filter(Project.location.contains(location))
        
        # Order by creation date (newest first)
        query = query.order_by(Project.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        projects = query.all()
        
        return jsonify({
            'success': True,
            'projects': [project.to_dict() for project in projects],
            'total': len(projects)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@projects_bp.route('/projects/<int:project_id>', methods=['GET'])
@cross_origin()
def get_project(project_id):
    """Get specific project by ID"""
    try:
        project = Project.query.get_or_404(project_id)
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@projects_bp.route('/projects', methods=['POST'])
@cross_origin()
def create_project():
    """Create new project"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'location', 'property_type', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create new project
        project = Project(
            title=data['title'],
            description=data.get('description'),
            location=data['location'],
            property_type=data['property_type'],
            category=data['category'],
            surface=data.get('surface'),
            rooms=data.get('rooms'),
            bathrooms=data.get('bathrooms'),
            floor=data.get('floor'),
            year_built=data.get('year_built'),
            purchase_price=data.get('purchase_price'),
            renovation_cost=data.get('renovation_cost'),
            total_investment=data.get('total_investment'),
            expected_revenue=data.get('expected_revenue'),
            client_id=data.get('client_id'),
            main_image=data.get('main_image'),
            before_image=data.get('before_image'),
            after_image=data.get('after_image')
        )
        
        # Set features and amenities if provided
        if 'features' in data:
            project.set_features(data['features'])
        if 'amenities' in data:
            project.set_amenities(data['amenities'])
        if 'gallery_images' in data:
            project.set_gallery_images(data['gallery_images'])
        
        # Parse dates if provided
        if 'start_date' in data and data['start_date']:
            project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'completion_date' in data and data['completion_date']:
            project.completion_date = datetime.strptime(data['completion_date'], '%Y-%m-%d').date()
        
        # Calculate derived fields
        if project.start_date and project.completion_date:
            project.calculate_duration()
        if project.total_investment and project.expected_revenue:
            project.calculate_roi()
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'message': 'Project created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@projects_bp.route('/projects/<int:project_id>', methods=['PUT'])
@cross_origin()
def update_project(project_id):
    """Update existing project"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'title', 'description', 'location', 'property_type', 'category',
            'surface', 'rooms', 'bathrooms', 'floor', 'year_built',
            'purchase_price', 'renovation_cost', 'total_investment',
            'expected_revenue', 'actual_revenue', 'status', 'occupancy_rate',
            'average_rating', 'total_reviews', 'main_image', 'before_image',
            'after_image', 'meta_title', 'meta_description'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(project, field, data[field])
        
        # Handle special fields
        if 'features' in data:
            project.set_features(data['features'])
        if 'amenities' in data:
            project.set_amenities(data['amenities'])
        if 'gallery_images' in data:
            project.set_gallery_images(data['gallery_images'])
        
        # Parse dates if provided
        if 'start_date' in data and data['start_date']:
            project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'completion_date' in data and data['completion_date']:
            project.completion_date = datetime.strptime(data['completion_date'], '%Y-%m-%d').date()
        
        # Recalculate derived fields
        if project.start_date and project.completion_date:
            project.calculate_duration()
        if project.total_investment and project.actual_revenue:
            project.calculate_roi()
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'message': 'Project updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@projects_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@cross_origin()
def delete_project(project_id):
    """Delete project"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Delete related records first
        ProjectImage.query.filter_by(project_id=project_id).delete()
        ProjectAnalytics.query.filter_by(project_id=project_id).delete()
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Project deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@projects_bp.route('/projects/featured', methods=['GET'])
@cross_origin()
def get_featured_projects():
    """Get featured projects for homepage"""
    try:
        limit = request.args.get('limit', 6, type=int)
        projects = Project.get_featured_projects(limit)
        
        return jsonify({
            'success': True,
            'projects': [project.to_dict() for project in projects]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@projects_bp.route('/projects/by-category/<category>', methods=['GET'])
@cross_origin()
def get_projects_by_category(category):
    """Get projects by category"""
    try:
        limit = request.args.get('limit', type=int)
        projects = Project.get_by_category(category, limit)
        
        return jsonify({
            'success': True,
            'projects': [project.to_dict() for project in projects],
            'category': category
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@projects_bp.route('/projects/search', methods=['GET'])
@cross_origin()
def search_projects():
    """Search projects with filters"""
    try:
        query_text = request.args.get('q', '')
        location = request.args.get('location')
        property_type = request.args.get('property_type')
        category = request.args.get('category')
        
        projects = Project.search_projects(query_text, location, property_type, category)
        
        return jsonify({
            'success': True,
            'projects': [project.to_dict() for project in projects],
            'query': query_text,
            'filters': {
                'location': location,
                'property_type': property_type,
                'category': category
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@projects_bp.route('/projects/<int:project_id>/analytics', methods=['GET'])
@cross_origin()
def get_project_analytics(project_id):
    """Get analytics for specific project"""
    try:
        project = Project.query.get_or_404(project_id)
        analytics = ProjectAnalytics.query.filter_by(project_id=project_id).order_by(
            ProjectAnalytics.month.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'project_title': project.title,
            'analytics': [analytic.to_dict() for analytic in analytics]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@projects_bp.route('/projects/<int:project_id>/analytics', methods=['POST'])
@cross_origin()
def add_project_analytics(project_id):
    """Add monthly analytics data for project"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['month', 'revenue', 'expenses']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Check if analytics for this month already exists
        month_date = datetime.strptime(data['month'], '%Y-%m-%d').date()
        existing = ProjectAnalytics.query.filter_by(
            project_id=project_id,
            month=month_date
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': 'Analytics for this month already exists'
            }), 400
        
        # Create new analytics record
        analytics = ProjectAnalytics(
            project_id=project_id,
            month=month_date,
            revenue=data['revenue'],
            expenses=data['expenses'],
            occupancy_days=data.get('occupancy_days', 0),
            total_days=data.get('total_days', 30),
            bookings_count=data.get('bookings_count', 0),
            average_daily_rate=data.get('average_daily_rate', 0),
            guest_rating=data.get('guest_rating', 0)
        )
        
        db.session.add(analytics)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'analytics': analytics.to_dict(),
            'message': 'Analytics added successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@projects_bp.route('/projects/stats', methods=['GET'])
@cross_origin()
def get_projects_stats():
    """Get overall projects statistics"""
    try:
        total_projects = Project.query.count()
        active_projects = Project.query.filter_by(status='active').count()
        completed_projects = Project.query.filter_by(status='completed').count()
        
        # Calculate average ROI
        projects_with_roi = Project.query.filter(Project.roi_percentage.isnot(None)).all()
        avg_roi = sum(p.roi_percentage for p in projects_with_roi) / len(projects_with_roi) if projects_with_roi else 0
        
        # Calculate total investment and revenue
        total_investment = db.session.query(db.func.sum(Project.total_investment)).scalar() or 0
        total_revenue = db.session.query(db.func.sum(Project.actual_revenue)).scalar() or 0
        
        # Projects by category
        categories = db.session.query(
            Project.category,
            db.func.count(Project.id)
        ).group_by(Project.category).all()
        
        # Projects by location
        locations = db.session.query(
            Project.location,
            db.func.count(Project.id)
        ).group_by(Project.location).limit(10).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_projects': total_projects,
                'active_projects': active_projects,
                'completed_projects': completed_projects,
                'average_roi': round(avg_roi, 2),
                'total_investment': total_investment,
                'total_revenue': total_revenue,
                'total_profit': total_revenue - total_investment,
                'categories': [{'category': cat, 'count': count} for cat, count in categories],
                'top_locations': [{'location': loc, 'count': count} for loc, count in locations]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

