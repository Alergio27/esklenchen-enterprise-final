from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Personal Information
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    
    # Address Information
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state_province = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(50))
    
    # Professional Information
    occupation = db.Column(db.String(100))
    company = db.Column(db.String(200))
    annual_income = db.Column(db.Float)
    investment_experience = db.Column(db.String(20))  # beginner, intermediate, advanced, expert
    
    # Investment Profile
    investment_budget_min = db.Column(db.Float)
    investment_budget_max = db.Column(db.Float)
    risk_tolerance = db.Column(db.String(20))  # low, medium, high
    investment_goals = db.Column(db.Text)  # JSON array
    preferred_locations = db.Column(db.Text)  # JSON array
    preferred_property_types = db.Column(db.Text)  # JSON array
    
    # Account Information
    client_type = db.Column(db.String(20), default='individual')  # individual, company, fund
    status = db.Column(db.String(20), default='active')  # active, inactive, suspended
    source = db.Column(db.String(50))  # website, referral, social_media, advertising
    
    # Financial Summary
    total_invested = db.Column(db.Float, default=0)
    total_revenue = db.Column(db.Float, default=0)
    total_profit = db.Column(db.Float, default=0)
    average_roi = db.Column(db.Float, default=0)
    
    # Communication Preferences
    preferred_contact_method = db.Column(db.String(20), default='email')  # email, phone, whatsapp
    language_preference = db.Column(db.String(10), default='es')  # es, en, ca
    newsletter_subscribed = db.Column(db.Boolean, default=True)
    marketing_consent = db.Column(db.Boolean, default=False)
    
    # Legal and Compliance
    kyc_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    kyc_documents = db.Column(db.Text)  # JSON array of document URLs
    tax_id = db.Column(db.String(50))
    legal_representative = db.Column(db.String(200))
    
    # Notes and Tags
    notes = db.Column(db.Text)
    tags = db.Column(db.Text)  # JSON array of tags
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact_date = db.Column(db.DateTime)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        address_parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state_province,
            self.postal_code,
            self.country
        ]
        return ", ".join([part for part in address_parts if part])
    
    def get_investment_goals(self):
        """Get investment goals as Python list"""
        if self.investment_goals:
            return json.loads(self.investment_goals)
        return []
    
    def set_investment_goals(self, goals_list):
        """Set investment goals from Python list"""
        self.investment_goals = json.dumps(goals_list)
    
    def get_preferred_locations(self):
        """Get preferred locations as Python list"""
        if self.preferred_locations:
            return json.loads(self.preferred_locations)
        return []
    
    def set_preferred_locations(self, locations_list):
        """Set preferred locations from Python list"""
        self.preferred_locations = json.dumps(locations_list)
    
    def get_preferred_property_types(self):
        """Get preferred property types as Python list"""
        if self.preferred_property_types:
            return json.loads(self.preferred_property_types)
        return []
    
    def set_preferred_property_types(self, types_list):
        """Set preferred property types from Python list"""
        self.preferred_property_types = json.dumps(types_list)
    
    def get_kyc_documents(self):
        """Get KYC documents as Python list"""
        if self.kyc_documents:
            return json.loads(self.kyc_documents)
        return []
    
    def set_kyc_documents(self, documents_list):
        """Set KYC documents from Python list"""
        self.kyc_documents = json.dumps(documents_list)
    
    def get_tags(self):
        """Get tags as Python list"""
        if self.tags:
            return json.loads(self.tags)
        return []
    
    def set_tags(self, tags_list):
        """Set tags from Python list"""
        self.tags = json.dumps(tags_list)
    
    def calculate_portfolio_performance(self):
        """Calculate overall portfolio performance"""
        if self.total_invested > 0:
            self.average_roi = ((self.total_revenue - self.total_invested) / self.total_invested) * 100
            self.total_profit = self.total_revenue - self.total_invested
        return {
            'total_invested': self.total_invested,
            'total_revenue': self.total_revenue,
            'total_profit': self.total_profit,
            'average_roi': self.average_roi
        }
    
    def get_active_projects_count(self):
        """Get count of active projects"""
        from src.models.project import Project
        return Project.query.filter_by(client_id=self.id, status='active').count()
    
    def get_completed_projects_count(self):
        """Get count of completed projects"""
        from src.models.project import Project
        return Project.query.filter_by(client_id=self.id, status='completed').count()
    
    def to_dict(self, include_sensitive=False):
        """Convert client to dictionary for API responses"""
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'nationality': self.nationality,
            'city': self.city,
            'country': self.country,
            'occupation': self.occupation,
            'company': self.company,
            'investment_experience': self.investment_experience,
            'investment_budget_min': self.investment_budget_min,
            'investment_budget_max': self.investment_budget_max,
            'risk_tolerance': self.risk_tolerance,
            'investment_goals': self.get_investment_goals(),
            'preferred_locations': self.get_preferred_locations(),
            'preferred_property_types': self.get_preferred_property_types(),
            'client_type': self.client_type,
            'status': self.status,
            'source': self.source,
            'total_invested': self.total_invested,
            'total_revenue': self.total_revenue,
            'total_profit': self.total_profit,
            'average_roi': self.average_roi,
            'preferred_contact_method': self.preferred_contact_method,
            'language_preference': self.language_preference,
            'kyc_status': self.kyc_status,
            'tags': self.get_tags(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_contact_date': self.last_contact_date.isoformat() if self.last_contact_date else None,
            'active_projects_count': self.get_active_projects_count(),
            'completed_projects_count': self.get_completed_projects_count()
        }
        
        if include_sensitive:
            data.update({
                'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
                'full_address': self.full_address,
                'annual_income': self.annual_income,
                'tax_id': self.tax_id,
                'legal_representative': self.legal_representative,
                'kyc_documents': self.get_kyc_documents(),
                'notes': self.notes
            })
        
        return data
    
    @staticmethod
    def search_clients(query_text, status=None, client_type=None, kyc_status=None):
        """Search clients with filters"""
        query = Client.query
        
        if query_text:
            query = query.filter(
                db.or_(
                    Client.first_name.contains(query_text),
                    Client.last_name.contains(query_text),
                    Client.email.contains(query_text),
                    Client.company.contains(query_text)
                )
            )
        
        if status:
            query = query.filter_by(status=status)
        
        if client_type:
            query = query.filter_by(client_type=client_type)
        
        if kyc_status:
            query = query.filter_by(kyc_status=kyc_status)
        
        return query.order_by(Client.created_at.desc()).all()
    
    @staticmethod
    def get_top_investors(limit=10):
        """Get top investors by total invested amount"""
        return Client.query.filter(Client.total_invested > 0).order_by(
            Client.total_invested.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_clients_by_roi(limit=10):
        """Get clients with highest ROI"""
        return Client.query.filter(Client.average_roi > 0).order_by(
            Client.average_roi.desc()
        ).limit(limit).all()
    
    def __repr__(self):
        return f'<Client {self.full_name}>'


class ClientContact(db.Model):
    __tablename__ = 'client_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    contact_type = db.Column(db.String(20), nullable=False)  # call, email, meeting, whatsapp
    subject = db.Column(db.String(200))
    description = db.Column(db.Text)
    outcome = db.Column(db.String(50))  # successful, follow_up_needed, no_response, closed
    
    contact_date = db.Column(db.DateTime, default=datetime.utcnow)
    follow_up_date = db.Column(db.DateTime)
    
    # Staff member who made the contact
    staff_member = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    client = db.relationship('Client', backref='contacts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'contact_type': self.contact_type,
            'subject': self.subject,
            'description': self.description,
            'outcome': self.outcome,
            'contact_date': self.contact_date.isoformat(),
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'staff_member': self.staff_member,
            'created_at': self.created_at.isoformat()
        }


class ClientDocument(db.Model):
    __tablename__ = 'client_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    document_type = db.Column(db.String(50), nullable=False)  # id, passport, tax_document, bank_statement, etc.
    document_name = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    verification_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    verified_by = db.Column(db.String(100))
    verification_date = db.Column(db.DateTime)
    verification_notes = db.Column(db.Text)
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    client = db.relationship('Client', backref='documents')
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'document_type': self.document_type,
            'document_name': self.document_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'verification_status': self.verification_status,
            'verified_by': self.verified_by,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'verification_notes': self.verification_notes,
            'uploaded_at': self.uploaded_at.isoformat()
        }

