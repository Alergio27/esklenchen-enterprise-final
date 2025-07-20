from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
import logging

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__, static_folder='../static', static_url_path='')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'esklenchen-secret-key-2025')
    
    # Enable CORS for all routes
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    
    # Serve React app
    @app.route('/')
    def serve_react_app():
        """Serve React app index.html"""
        try:
            return send_from_directory(app.static_folder, 'index.html')
        except Exception as e:
            app.logger.error(f"Error serving index.html: {str(e)}")
            return f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ESKLENCHEN - Inversión Inmobiliaria</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        margin: 0;
                        padding: 0;
                        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                        color: white;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }}
                    .container {{
                        text-align: center;
                        max-width: 800px;
                        padding: 40px 20px;
                    }}
                    .logo {{
                        font-size: 3rem;
                        font-weight: bold;
                        margin-bottom: 20px;
                        color: #ffd700;
                    }}
                    .tagline {{
                        font-size: 1.5rem;
                        margin-bottom: 30px;
                        opacity: 0.9;
                    }}
                    .services {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 20px;
                        margin: 40px 0;
                    }}
                    .service {{
                        background: rgba(255, 255, 255, 0.1);
                        padding: 20px;
                        border-radius: 10px;
                        backdrop-filter: blur(10px);
                    }}
                    .contact {{
                        margin-top: 40px;
                        padding: 20px;
                        background: rgba(255, 215, 0, 0.1);
                        border-radius: 10px;
                    }}
                    .phone {{
                        font-size: 1.5rem;
                        font-weight: bold;
                        color: #ffd700;
                        margin: 10px 0;
                    }}
                    .badges {{
                        display: flex;
                        justify-content: center;
                        gap: 20px;
                        margin-top: 30px;
                        flex-wrap: wrap;
                    }}
                    .badge {{
                        background: rgba(255, 255, 255, 0.2);
                        padding: 10px 15px;
                        border-radius: 20px;
                        font-size: 0.9rem;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="logo">ESKLENCHEN</div>
                    <div class="tagline">Inversión Inmobiliaria Inteligente</div>
                    
                    <div class="services">
                        <div class="service">
                            <h3>🏠 Reforma sin Coste</h3>
                            <p>Reformamos tu propiedad sin inversión inicial. Recuperas la inversión con la venta.</p>
                        </div>
                        <div class="service">
                            <h3>📊 Análisis con IA</h3>
                            <p>Valoraciones automáticas con inteligencia artificial y análisis de mercado.</p>
                        </div>
                        <div class="service">
                            <h3>💼 Gestión Integral</h3>
                            <p>Nos encargamos de todo: compra, reforma, gestión y venta de propiedades.</p>
                        </div>
                        <div class="service">
                            <h3>⭐ Experiencias Premium</h3>
                            <p>Servicios de alta calidad para huéspedes y máxima rentabilidad.</p>
                        </div>
                    </div>
                    
                    <div class="contact">
                        <h3>Contacta con Nosotros</h3>
                        <div class="phone">📞 +34 624 737 299</div>
                        <p>contact@esklenchen.com</p>
                        <p>Especialistas en inversión inmobiliaria con más de 10 años de experiencia</p>
                    </div>
                    
                    <div class="badges">
                        <div class="badge">🔒 SSL Secure</div>
                        <div class="badge">🛡️ GDPR Compliant</div>
                        <div class="badge">💳 Secure Payment</div>
                        <div class="badge">✅ Verified Business</div>
                    </div>
                </div>
            </body>
            </html>
            """
    
    @app.route('/<path:path>')
    def serve_react_static(path):
        """Serve React static files or fallback to index.html for SPA routing"""
        try:
            return send_from_directory(app.static_folder, path)
        except:
            # Fallback to index.html for SPA routing
            return serve_react_app()
    
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
                'contact_forms': True,
                'property_analysis': True,
                'renovation_proposals': True,
                'health_monitoring': True
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
            
            contact_data = {
                'name': data.get('name'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'message': data.get('message'),
                'form_type': data.get('form_type', 'general'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Log the contact data
            app.logger.info(f"Contact data received: {contact_data}")
            
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
    
    # Property analysis endpoint
    @app.route('/api/property-analysis', methods=['POST'])
    def property_analysis():
        """Handle property analysis requests"""
        try:
            data = request.get_json()
            
            # Log analysis request
            app.logger.info(f"Property analysis request: {data.get('location', 'unknown')}")
            
            # Simulate AI analysis
            surface = float(data.get('surface', 80))
            rooms = int(data.get('rooms', 3))
            location = data.get('location', 'Barcelona')
            
            # Simple valuation algorithm
            base_price_per_m2 = {
                'Barcelona': 4500,
                'Madrid': 4200,
                'Valencia': 2800,
                'Sevilla': 2500,
                'Bilbao': 3800,
                'Badalona': 3200
            }.get(location, 3000)
            
            estimated_value = surface * base_price_per_m2
            renovation_cost = estimated_value * 0.15  # 15% for renovation
            potential_value = estimated_value * 1.25  # 25% increase after renovation
            roi_percentage = ((potential_value - estimated_value - renovation_cost) / (estimated_value + renovation_cost)) * 100
            
            analysis_result = {
                'property_id': f"PROP{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'estimated_value': round(estimated_value),
                'renovation_cost': round(renovation_cost),
                'potential_value': round(potential_value),
                'roi_percentage': round(roi_percentage, 2),
                'confidence_level': 87.5,
                'analysis_factors': {
                    'location_score': 8.5,
                    'market_trend': 'positive',
                    'renovation_potential': 'high',
                    'rental_yield': 6.2
                },
                'recommendations': [
                    'Excelente oportunidad de inversión',
                    'Ubicación con alta demanda',
                    'Potencial de revalorización alto',
                    'Reforma recomendada para maximizar ROI'
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            app.logger.info(f"Analysis completed: ROI {roi_percentage}%")
            
            return jsonify({
                'success': True,
                'analysis': analysis_result
            })
            
        except Exception as e:
            app.logger.error(f"Error in property analysis: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error realizando análisis'
            }), 500
    
    # Renovation proposal endpoint
    @app.route('/api/renovation-proposal', methods=['POST'])
    def renovation_proposal():
        """Handle renovation proposal requests"""
        try:
            data = request.get_json()
            
            # Log proposal request
            app.logger.info(f"Renovation proposal request: {data.get('property_type', 'unknown')}")
            
            property_type = data.get('property_type', 'apartment')
            budget = float(data.get('budget', 50000))
            
            # Generate renovation proposal
            proposal = {
                'proposal_id': f"RENOV{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'property_type': property_type,
                'estimated_budget': budget,
                'timeline_weeks': 8,
                'renovation_areas': [
                    {'area': 'Cocina', 'cost': budget * 0.3, 'priority': 'high'},
                    {'area': 'Baños', 'cost': budget * 0.25, 'priority': 'high'},
                    {'area': 'Suelos', 'cost': budget * 0.2, 'priority': 'medium'},
                    {'area': 'Pintura', 'cost': budget * 0.15, 'priority': 'medium'},
                    {'area': 'Instalaciones', 'cost': budget * 0.1, 'priority': 'low'}
                ],
                'expected_roi': 25.5,
                'financing_options': {
                    'reforma_sin_coste': True,
                    'payment_on_sale': True,
                    'guaranteed_roi': True
                },
                'next_steps': [
                    'Visita técnica gratuita',
                    'Presupuesto detallado',
                    'Planificación de obra',
                    'Inicio de reforma'
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return jsonify({
                'success': True,
                'proposal': proposal
            })
            
        except Exception as e:
            app.logger.error(f"Error in renovation proposal: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error generando propuesta'
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

