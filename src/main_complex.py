from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import logging

# Import route blueprints
from src.routes.projects import projects_bp
from src.routes.clients import clients_bp
from src.routes.ai_valuation import ai_valuation_bp
from src.routes.auth import auth_bp

# Import models to ensure tables are created
from src.models.project import db as project_db
from src.models.client import db as client_db
from src.models.ai_valuation import db as valuation_db

# Import services
from src.services.pdf_generator import ESKLENCHENPDFGenerator

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__, static_folder='static', static_url_path='')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'esklenchen-secret-key-2025')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///esklenchen.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Enable CORS for all routes
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Initialize database
    project_db.init_app(app)
    client_db.init_app(app)
    valuation_db.init_app(app)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    
    # Create tables
    with app.app_context():
        project_db.create_all()
        client_db.create_all()
        valuation_db.create_all()
    
    # Register blueprints
    app.register_blueprint(projects_bp, url_prefix='/api')
    app.register_blueprint(clients_bp, url_prefix='/api')
    app.register_blueprint(ai_valuation_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    
    # Serve React app
    @app.route('/')
    def serve_react_app():
        """Serve React app index.html"""
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_react_static(path):
        """Serve React static files or fallback to index.html for SPA routing"""
        try:
            return send_from_directory(app.static_folder, path)
        except:
            # Fallback to index.html for SPA routing
            return send_from_directory(app.static_folder, 'index.html')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'service': 'ESKLENCHEN Enterprise Backend',
            'version': '3.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'features': {
                'projects_management': True,
                'client_crm': True,
                'ai_valuation': True,
                'pdf_generation': True,
                'user_authentication': True,
                'analytics': True
            }
        })
    
    # Contact form endpoint
    @app.route('/api/contact', methods=['POST'])
    def contact_form():
        """Handle contact form submissions"""
        try:
            data = request.get_json()
            
            # Log contact submission
            app.logger.info(f"Contact form submission: {data.get('email', 'unknown')}")
            
            # In production, you might want to save to database or send email
            contact_data = {
                'name': data.get('name'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'message': data.get('message'),
                'form_type': data.get('form_type', 'general'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return jsonify({
                'success': True,
                'message': 'Mensaje recibido correctamente. Te contactaremos pronto.',
                'contact_id': f"ESKA{datetime.now().strftime('%Y%m%d%H%M%S')}"
            })
            
        except Exception as e:
            app.logger.error(f"Error in contact form: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error procesando el formulario'
            }), 500
    
    # PDF generation endpoints
    @app.route('/api/generate-pdf/valuation/<int:valuation_id>', methods=['GET'])
    def generate_valuation_pdf(valuation_id):
        """Generate PDF for property valuation"""
        try:
            from src.models.ai_valuation import PropertyValuation
            
            valuation = PropertyValuation.query.get_or_404(valuation_id)
            
            # Create reports directory if it doesn't exist
            reports_dir = os.path.join(os.getcwd(), 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate PDF
            pdf_generator = ESKLENCHENPDFGenerator()
            filename = f"valoracion_{valuation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = os.path.join(reports_dir, filename)
            
            success, message = pdf_generator.generate_property_valuation_report(
                valuation.to_dict(), 
                output_path
            )
            
            if success:
                return send_file(
                    output_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/pdf'
                )
            else:
                return jsonify({
                    'success': False,
                    'error': message
                }), 500
                
        except Exception as e:
            app.logger.error(f"Error generating valuation PDF: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error generando PDF'
            }), 500
    
    @app.route('/api/generate-pdf/portfolio/<int:client_id>', methods=['GET'])
    def generate_portfolio_pdf(client_id):
        """Generate PDF for client portfolio"""
        try:
            from src.models.client import Client
            from src.models.project import Project
            
            client = Client.query.get_or_404(client_id)
            projects = Project.query.filter_by(client_id=client_id).all()
            
            # Create reports directory if it doesn't exist
            reports_dir = os.path.join(os.getcwd(), 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate PDF
            pdf_generator = ESKLENCHENPDFGenerator()
            filename = f"portfolio_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_path = os.path.join(reports_dir, filename)
            
            success, message = pdf_generator.generate_client_portfolio_report(
                client.to_dict(include_sensitive=True),
                [project.to_dict() for project in projects],
                output_path
            )
            
            if success:
                return send_file(
                    output_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/pdf'
                )
            else:
                return jsonify({
                    'success': False,
                    'error': message
                }), 500
                
        except Exception as e:
            app.logger.error(f"Error generating portfolio PDF: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error generando PDF de portfolio'
            }), 500
    
    # Dashboard stats endpoint
    @app.route('/api/dashboard/stats', methods=['GET'])
    def dashboard_stats():
        """Get dashboard statistics"""
        try:
            from src.models.project import Project
            from src.models.client import Client
            from src.models.ai_valuation import PropertyValuation
            
            # Projects stats
            total_projects = Project.query.count()
            active_projects = Project.query.filter_by(status='active').count()
            completed_projects = Project.query.filter_by(status='completed').count()
            
            # Clients stats
            total_clients = Client.query.count()
            active_clients = Client.query.filter_by(status='active').count()
            
            # Valuations stats
            total_valuations = PropertyValuation.query.count()
            recent_valuations = PropertyValuation.query.filter_by(status='completed').count()
            
            # Financial stats
            total_investment = project_db.session.query(project_db.func.sum(Project.total_investment)).scalar() or 0
            total_revenue = project_db.session.query(project_db.func.sum(Project.actual_revenue)).scalar() or 0
            
            # Recent activity
            recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
            recent_clients = Client.query.order_by(Client.created_at.desc()).limit(5).all()
            recent_vals = PropertyValuation.query.order_by(PropertyValuation.created_at.desc()).limit(5).all()
            
            return jsonify({
                'success': True,
                'stats': {
                    'projects': {
                        'total': total_projects,
                        'active': active_projects,
                        'completed': completed_projects
                    },
                    'clients': {
                        'total': total_clients,
                        'active': active_clients
                    },
                    'valuations': {
                        'total': total_valuations,
                        'completed': recent_valuations
                    },
                    'financial': {
                        'total_investment': total_investment,
                        'total_revenue': total_revenue,
                        'total_profit': total_revenue - total_investment
                    }
                },
                'recent_activity': {
                    'projects': [project.to_dict() for project in recent_projects],
                    'clients': [client.to_dict() for client in recent_clients],
                    'valuations': [val.to_dict() for val in recent_vals]
                }
            })
            
        except Exception as e:
            app.logger.error(f"Error getting dashboard stats: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error obteniendo estadísticas'
            }), 500
    
    # Legal pages endpoints
    @app.route('/api/legal/privacy', methods=['GET'])
    def privacy_policy():
        """Get privacy policy content"""
        privacy_content = """
        <h1>Política de Privacidad - ESKLENCHEN</h1>
        
        <h2>1. Responsable del Tratamiento</h2>
        <p>ESKLENCHEN Real Estate Solutions es responsable del tratamiento de sus datos personales.</p>
        
        <h2>2. Datos que Recopilamos</h2>
        <p>Recopilamos los siguientes tipos de datos:</p>
        <ul>
            <li>Datos de contacto (nombre, email, teléfono)</li>
            <li>Información de inversión y preferencias</li>
            <li>Datos de navegación y cookies</li>
        </ul>
        
        <h2>3. Finalidad del Tratamiento</h2>
        <p>Utilizamos sus datos para:</p>
        <ul>
            <li>Proporcionar nuestros servicios de inversión inmobiliaria</li>
            <li>Comunicarnos con usted sobre oportunidades de inversión</li>
            <li>Cumplir con obligaciones legales</li>
        </ul>
        
        <h2>4. Base Legal</h2>
        <p>El tratamiento se basa en su consentimiento y en la ejecución de contratos.</p>
        
        <h2>5. Derechos del Usuario</h2>
        <p>Tiene derecho a acceder, rectificar, suprimir y portar sus datos.</p>
        
        <h2>6. Contacto</h2>
        <p>Para ejercer sus derechos, contacte: contact@esklenchen.com</p>
        """
        
        return jsonify({
            'success': True,
            'content': privacy_content
        })
    
    @app.route('/api/legal/cookies', methods=['GET'])
    def cookies_policy():
        """Get cookies policy content"""
        cookies_content = """
        <h1>Política de Cookies - ESKLENCHEN</h1>
        
        <h2>¿Qué son las cookies?</h2>
        <p>Las cookies son pequeños archivos de texto que se almacenan en su dispositivo cuando visita nuestro sitio web.</p>
        
        <h2>Tipos de cookies que utilizamos</h2>
        <ul>
            <li><strong>Cookies técnicas:</strong> Necesarias para el funcionamiento del sitio</li>
            <li><strong>Cookies analíticas:</strong> Para analizar el uso del sitio web</li>
            <li><strong>Cookies de personalización:</strong> Para recordar sus preferencias</li>
        </ul>
        
        <h2>Gestión de cookies</h2>
        <p>Puede gestionar las cookies desde la configuración de su navegador.</p>
        
        <h2>Cookies de terceros</h2>
        <p>Utilizamos Google Analytics para analizar el tráfico del sitio web.</p>
        """
        
        return jsonify({
            'success': True,
            'content': cookies_content
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

