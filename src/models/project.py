from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)  # apartamento, casa, villa, estudio
    category = db.Column(db.String(50), nullable=False)  # reforma-sin-coste, compra-venta, gestion-completa
    
    # Property Details
    surface = db.Column(db.Float)  # m²
    rooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    floor = db.Column(db.String(20))
    year_built = db.Column(db.Integer)
    
    # Financial Data
    purchase_price = db.Column(db.Float)
    renovation_cost = db.Column(db.Float)
    total_investment = db.Column(db.Float)
    expected_revenue = db.Column(db.Float)
    actual_revenue = db.Column(db.Float)
    roi_percentage = db.Column(db.Float)
    
    # Project Timeline
    start_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    duration_days = db.Column(db.Integer)
    
    # Status and Performance
    status = db.Column(db.String(20), default='planning')  # planning, active, completed, sold
    occupancy_rate = db.Column(db.Float)  # percentage
    average_rating = db.Column(db.Float)
    total_reviews = db.Column(db.Integer, default=0)
    
    # Images and Media
    main_image = db.Column(db.String(255))
    before_image = db.Column(db.String(255))
    after_image = db.Column(db.String(255))
    gallery_images = db.Column(db.Text)  # JSON array of image URLs
    
    # Features and Amenities
    features = db.Column(db.Text)  # JSON array of features
    amenities = db.Column(db.Text)  # JSON array of amenities
    
    # SEO and Marketing
    slug = db.Column(db.String(200), unique=True)
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    client = db.relationship('Client', backref='projects')
    
    def __init__(self, **kwargs):
        super(Project, self).__init__(**kwargs)
        if not self.slug:
            self.slug = self.generate_slug()
    
    def generate_slug(self):
        """Generate URL-friendly slug from title"""
        import re
        slug = re.sub(r'[^\w\s-]', '', self.title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def get_features(self):
        """Get features as Python list"""
        if self.features:
            return json.loads(self.features)
        return []
    
    def set_features(self, features_list):
        """Set features from Python list"""
        self.features = json.dumps(features_list)
    
    def get_amenities(self):
        """Get amenities as Python list"""
        if self.amenities:
            return json.loads(self.amenities)
        return []
    
    def set_amenities(self, amenities_list):
        """Set amenities from Python list"""
        self.amenities = json.dumps(amenities_list)
    
    def get_gallery_images(self):
        """Get gallery images as Python list"""
        if self.gallery_images:
            return json.loads(self.gallery_images)
        return []
    
    def set_gallery_images(self, images_list):
        """Set gallery images from Python list"""
        self.gallery_images = json.dumps(images_list)
    
    def calculate_roi(self):
        """Calculate ROI percentage"""
        if self.total_investment and self.actual_revenue:
            self.roi_percentage = ((self.actual_revenue - self.total_investment) / self.total_investment) * 100
        return self.roi_percentage
    
    def calculate_duration(self):
        """Calculate project duration in days"""
        if self.start_date and self.completion_date:
            self.duration_days = (self.completion_date - self.start_date).days
        return self.duration_days
    
    def to_dict(self):
        """Convert project to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'property_type': self.property_type,
            'category': self.category,
            'surface': self.surface,
            'rooms': self.rooms,
            'bathrooms': self.bathrooms,
            'floor': self.floor,
            'year_built': self.year_built,
            'purchase_price': self.purchase_price,
            'renovation_cost': self.renovation_cost,
            'total_investment': self.total_investment,
            'expected_revenue': self.expected_revenue,
            'actual_revenue': self.actual_revenue,
            'roi_percentage': self.roi_percentage,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'duration_days': self.duration_days,
            'status': self.status,
            'occupancy_rate': self.occupancy_rate,
            'average_rating': self.average_rating,
            'total_reviews': self.total_reviews,
            'main_image': self.main_image,
            'before_image': self.before_image,
            'after_image': self.after_image,
            'gallery_images': self.get_gallery_images(),
            'features': self.get_features(),
            'amenities': self.get_amenities(),
            'slug': self.slug,
            'meta_title': self.meta_title,
            'meta_description': self.meta_description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'client_id': self.client_id
        }
    
    @staticmethod
    def get_featured_projects(limit=6):
        """Get featured projects for homepage"""
        return Project.query.filter_by(status='completed').order_by(
            Project.roi_percentage.desc(),
            Project.average_rating.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_by_category(category, limit=None):
        """Get projects by category"""
        query = Project.query.filter_by(category=category).order_by(Project.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def search_projects(query_text, location=None, property_type=None, category=None):
        """Search projects with filters"""
        query = Project.query
        
        if query_text:
            query = query.filter(
                db.or_(
                    Project.title.contains(query_text),
                    Project.description.contains(query_text),
                    Project.location.contains(query_text)
                )
            )
        
        if location:
            query = query.filter(Project.location.contains(location))
        
        if property_type:
            query = query.filter_by(property_type=property_type)
        
        if category:
            query = query.filter_by(category=category)
        
        return query.order_by(Project.created_at.desc()).all()
    
    def __repr__(self):
        return f'<Project {self.title}>'


class ProjectImage(db.Model):
    __tablename__ = 'project_images'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    image_type = db.Column(db.String(20), nullable=False)  # main, before, after, gallery
    caption = db.Column(db.String(255))
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('Project', backref='images')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'image_url': self.image_url,
            'image_type': self.image_type,
            'caption': self.caption,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat()
        }


class ProjectAnalytics(db.Model):
    __tablename__ = 'project_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Monthly Performance Data
    month = db.Column(db.Date, nullable=False)
    revenue = db.Column(db.Float, default=0)
    expenses = db.Column(db.Float, default=0)
    occupancy_days = db.Column(db.Integer, default=0)
    total_days = db.Column(db.Integer, default=30)
    bookings_count = db.Column(db.Integer, default=0)
    average_daily_rate = db.Column(db.Float, default=0)
    guest_rating = db.Column(db.Float, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('Project', backref='analytics')
    
    @property
    def occupancy_rate(self):
        """Calculate occupancy rate for the month"""
        if self.total_days > 0:
            return (self.occupancy_days / self.total_days) * 100
        return 0
    
    @property
    def net_profit(self):
        """Calculate net profit for the month"""
        return self.revenue - self.expenses
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'month': self.month.isoformat(),
            'revenue': self.revenue,
            'expenses': self.expenses,
            'occupancy_days': self.occupancy_days,
            'total_days': self.total_days,
            'occupancy_rate': self.occupancy_rate,
            'bookings_count': self.bookings_count,
            'average_daily_rate': self.average_daily_rate,
            'guest_rating': self.guest_rating,
            'net_profit': self.net_profit,
            'created_at': self.created_at.isoformat()
        }

