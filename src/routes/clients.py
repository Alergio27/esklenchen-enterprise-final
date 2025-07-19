from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.models.client import db, Client, ClientContact, ClientDocument
from datetime import datetime, date
import json

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/clients', methods=['GET'])
@cross_origin()
def get_clients():
    """Get all clients with optional filtering"""
    try:
        # Get query parameters
        status = request.args.get('status')
        client_type = request.args.get('client_type')
        kyc_status = request.args.get('kyc_status')
        search = request.args.get('search')
        limit = request.args.get('limit', type=int)
        
        # Build query
        if search:
            clients = Client.search_clients(search, status, client_type, kyc_status)
        else:
            query = Client.query
            
            if status:
                query = query.filter_by(status=status)
            if client_type:
                query = query.filter_by(client_type=client_type)
            if kyc_status:
                query = query.filter_by(kyc_status=kyc_status)
            
            query = query.order_by(Client.created_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            clients = query.all()
        
        return jsonify({
            'success': True,
            'clients': [client.to_dict() for client in clients],
            'total': len(clients)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clients_bp.route('/clients/<int:client_id>', methods=['GET'])
@cross_origin()
def get_client(client_id):
    """Get specific client by ID"""
    try:
        client = Client.query.get_or_404(client_id)
        include_sensitive = request.args.get('include_sensitive', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'client': client.to_dict(include_sensitive=include_sensitive)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clients_bp.route('/clients', methods=['POST'])
@cross_origin()
def create_client():
    """Create new client"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Check if email already exists
        existing_client = Client.query.filter_by(email=data['email']).first()
        if existing_client:
            return jsonify({
                'success': False,
                'error': 'Client with this email already exists'
            }), 400
        
        # Create new client
        client = Client(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            nationality=data.get('nationality'),
            address_line1=data.get('address_line1'),
            address_line2=data.get('address_line2'),
            city=data.get('city'),
            state_province=data.get('state_province'),
            postal_code=data.get('postal_code'),
            country=data.get('country'),
            occupation=data.get('occupation'),
            company=data.get('company'),
            annual_income=data.get('annual_income'),
            investment_experience=data.get('investment_experience', 'beginner'),
            investment_budget_min=data.get('investment_budget_min'),
            investment_budget_max=data.get('investment_budget_max'),
            risk_tolerance=data.get('risk_tolerance', 'medium'),
            client_type=data.get('client_type', 'individual'),
            source=data.get('source', 'website'),
            preferred_contact_method=data.get('preferred_contact_method', 'email'),
            language_preference=data.get('language_preference', 'es'),
            newsletter_subscribed=data.get('newsletter_subscribed', True),
            marketing_consent=data.get('marketing_consent', False),
            tax_id=data.get('tax_id'),
            legal_representative=data.get('legal_representative'),
            notes=data.get('notes')
        )
        
        # Set array fields if provided
        if 'investment_goals' in data:
            client.set_investment_goals(data['investment_goals'])
        if 'preferred_locations' in data:
            client.set_preferred_locations(data['preferred_locations'])
        if 'preferred_property_types' in data:
            client.set_preferred_property_types(data['preferred_property_types'])
        if 'tags' in data:
            client.set_tags(data['tags'])
        
        # Parse date of birth if provided
        if 'date_of_birth' in data and data['date_of_birth']:
            client.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        
        db.session.add(client)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'client': client.to_dict(),
            'message': 'Client created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clients_bp.route('/clients/<int:client_id>', methods=['PUT'])
@cross_origin()
def update_client(client_id):
    """Update existing client"""
    try:
        client = Client.query.get_or_404(client_id)
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'first_name', 'last_name', 'email', 'phone', 'nationality',
            'address_line1', 'address_line2', 'city', 'state_province',
            'postal_code', 'country', 'occupation', 'company', 'annual_income',
            'investment_experience', 'investment_budget_min', 'investment_budget_max',
            'risk_tolerance', 'client_type', 'status', 'source',
            'preferred_contact_method', 'language_preference', 'newsletter_subscribed',
            'marketing_consent', 'kyc_status', 'tax_id', 'legal_representative',
            'notes', 'total_invested', 'total_revenue', 'total_profit', 'average_roi'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(client, field, data[field])
        
        # Handle special fields
        if 'investment_goals' in data:
            client.set_investment_goals(data['investment_goals'])
        if 'preferred_locations' in data:
            client.set_preferred_locations(data['preferred_locations'])
        if 'preferred_property_types' in data:
            client.set_preferred_property_types(data['preferred_property_types'])
        if 'tags' in data:
            client.set_tags(data['tags'])
        if 'kyc_documents' in data:
            client.set_kyc_documents(data['kyc_documents'])
        
        # Parse date of birth if provided
        if 'date_of_birth' in data and data['date_of_birth']:
            client.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        
        # Update last contact date if provided
        if 'last_contact_date' in data and data['last_contact_date']:
            client.last_contact_date = datetime.strptime(data['last_contact_date'], '%Y-%m-%d %H:%M:%S')
        
        client.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'client': client.to_dict(),
            'message': 'Client updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clients_bp.route('/clients/<int:client_id>', methods=['DELETE'])
@cross_origin()
def delete_client(client_id):
    """Delete client"""
    try:
        client = Client.query.get_or_404(client_id)
        
        # Delete related records first
        ClientContact.query.filter_by(client_id=client_id).delete()
        ClientDocument.query.filter_by(client_id=client_id).delete()
        
        db.session.delete(client)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Client deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clients_bp.route('/clients/<int:client_id>/contacts', methods=['GET'])
@cross_origin()
def get_client_contacts(client_id):
    """Get contact history for client"""
    try:
        client = Client.query.get_or_404(client_id)
        contacts = ClientContact.query.filter_by(client_id=client_id).order_by(
            ClientContact.contact_date.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'client_id': client_id,
            'client_name': client.full_name,
            'contacts': [contact.to_dict() for contact in contacts]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clients_bp.route('/clients/<int:client_id>/contacts', methods=['POST'])
@cross_origin()
def add_client_contact(client_id):
    """Add new contact record for client"""
    try:
        client = Client.query.get_or_404(client_id)
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['contact_type', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Create new contact record
        contact = ClientContact(
            client_id=client_id,
            contact_type=data['contact_type'],
            subject=data.get('subject'),
            description=data['description'],
            outcome=data.get('outcome'),
            staff_member=data.get('staff_member'),
            contact_date=datetime.utcnow()
        )
        
        # Parse follow-up date if provided
        if 'follow_up_date' in data and data['follow_up_date']:
            contact.follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d %H:%M:%S')
        
        # Update client's last contact date
        client.last_contact_date = datetime.utcnow()
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'contact': contact.to_dict(),
            'message': 'Contact record added successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clients_bp.route('/clients/<int:client_id>/documents', methods=['GET'])
@cross_origin()
def get_client_documents(client_id):
    """Get documents for client"""
    try:
        client = Client.query.get_or_404(client_id)
        documents = ClientDocument.query.filter_by(client_id=client_id).order_by(
            ClientDocument.uploaded_at.desc()
        ).all()
        
        return jsonify({
            'success': True,
            'client_id': client_id,
            'client_name': client.full_name,
            'documents': [doc.to_dict() for doc in documents]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clients_bp.route('/clients/<int:client_id>/portfolio', methods=['GET'])
@cross_origin()
def get_client_portfolio(client_id):
    """Get client's investment portfolio performance"""
    try:
        client = Client.query.get_or_404(client_id)
        
        # Get client's projects
        from src.models.project import Project
        projects = Project.query.filter_by(client_id=client_id).all()
        
        # Calculate portfolio performance
        portfolio_performance = client.calculate_portfolio_performance()
        
        return jsonify({
            'success': True,
            'client_id': client_id,
            'client_name': client.full_name,
            'portfolio_performance': portfolio_performance,
            'projects': [project.to_dict() for project in projects],
            'projects_summary': {
                'total_projects': len(projects),
                'active_projects': client.get_active_projects_count(),
                'completed_projects': client.get_completed_projects_count()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clients_bp.route('/clients/top-investors', methods=['GET'])
@cross_origin()
def get_top_investors():
    """Get top investors by investment amount"""
    try:
        limit = request.args.get('limit', 10, type=int)
        clients = Client.get_top_investors(limit)
        
        return jsonify({
            'success': True,
            'top_investors': [client.to_dict() for client in clients]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clients_bp.route('/clients/top-roi', methods=['GET'])
@cross_origin()
def get_clients_by_roi():
    """Get clients with highest ROI"""
    try:
        limit = request.args.get('limit', 10, type=int)
        clients = Client.get_clients_by_roi(limit)
        
        return jsonify({
            'success': True,
            'top_roi_clients': [client.to_dict() for client in clients]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clients_bp.route('/clients/stats', methods=['GET'])
@cross_origin()
def get_clients_stats():
    """Get overall client statistics"""
    try:
        total_clients = Client.query.count()
        active_clients = Client.query.filter_by(status='active').count()
        kyc_approved = Client.query.filter_by(kyc_status='approved').count()
        
        # Calculate total portfolio value
        total_invested = db.session.query(db.func.sum(Client.total_invested)).scalar() or 0
        total_revenue = db.session.query(db.func.sum(Client.total_revenue)).scalar() or 0
        
        # Clients by type
        client_types = db.session.query(
            Client.client_type,
            db.func.count(Client.id)
        ).group_by(Client.client_type).all()
        
        # Clients by source
        sources = db.session.query(
            Client.source,
            db.func.count(Client.id)
        ).group_by(Client.source).all()
        
        # Clients by country
        countries = db.session.query(
            Client.country,
            db.func.count(Client.id)
        ).filter(Client.country.isnot(None)).group_by(Client.country).limit(10).all()
        
        # Average investment per client
        clients_with_investment = Client.query.filter(Client.total_invested > 0).all()
        avg_investment = sum(c.total_invested for c in clients_with_investment) / len(clients_with_investment) if clients_with_investment else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_clients': total_clients,
                'active_clients': active_clients,
                'kyc_approved': kyc_approved,
                'total_invested': total_invested,
                'total_revenue': total_revenue,
                'total_profit': total_revenue - total_invested,
                'average_investment_per_client': round(avg_investment, 2),
                'client_types': [{'type': ct, 'count': count} for ct, count in client_types],
                'sources': [{'source': src, 'count': count} for src, count in sources],
                'top_countries': [{'country': country, 'count': count} for country, count in countries]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@clients_bp.route('/clients/<int:client_id>/kyc-approve', methods=['POST'])
@cross_origin()
def approve_client_kyc(client_id):
    """Approve client KYC"""
    try:
        client = Client.query.get_or_404(client_id)
        data = request.get_json()
        
        client.kyc_status = 'approved'
        client.updated_at = datetime.utcnow()
        
        # Add contact record for KYC approval
        contact = ClientContact(
            client_id=client_id,
            contact_type='email',
            subject='KYC Approved',
            description='Client KYC documentation has been approved',
            outcome='successful',
            staff_member=data.get('approved_by', 'System'),
            contact_date=datetime.utcnow()
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'client': client.to_dict(),
            'message': 'Client KYC approved successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

