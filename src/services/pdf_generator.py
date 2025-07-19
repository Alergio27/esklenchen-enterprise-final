from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from datetime import datetime, date
import os
import json

class ESKLENCHENPDFGenerator:
    """Professional PDF generator for ESKLENCHEN reports"""
    
    def __init__(self):
        self.colors = {
            'primary': HexColor('#1F3A5F'),      # Navy blue
            'secondary': HexColor('#F4C430'),     # Yellow
            'accent': HexColor('#E04E2F'),        # Terracotta
            'light_grey': HexColor('#F8F9FA'),
            'dark_grey': HexColor('#6C757D'),
            'success': HexColor('#28A745'),
            'warning': HexColor('#FFC107'),
            'danger': HexColor('#DC3545')
        }
        
        self.styles = self._create_styles()
        
    def _create_styles(self):
        """Create custom styles for ESKLENCHEN documents"""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='ESKLENCHENTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=self.colors['primary'],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        styles.add(ParagraphStyle(
            name='ESKLENCHENSubtitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=self.colors['primary'],
            spaceAfter=20,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        styles.add(ParagraphStyle(
            name='ESKLENCHENSection',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.colors['accent'],
            spaceAfter=15,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        styles.add(ParagraphStyle(
            name='ESKLENCHENBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=black,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Highlight style
        styles.add(ParagraphStyle(
            name='ESKLENCHENHighlight',
            parent=styles['Normal'],
            fontSize=12,
            textColor=self.colors['primary'],
            spaceAfter=10,
            fontName='Helvetica-Bold',
            backColor=self.colors['light_grey'],
            borderPadding=8
        ))
        
        # Footer style
        styles.add(ParagraphStyle(
            name='ESKLENCHENFooter',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.colors['dark_grey'],
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        return styles
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Header
        canvas.setFillColor(self.colors['primary'])
        canvas.rect(0, A4[1] - 80, A4[0], 80, fill=1)
        
        # ESKLENCHEN logo/text in header
        canvas.setFillColor(white)
        canvas.setFont('Helvetica-Bold', 20)
        canvas.drawString(50, A4[1] - 50, "ESKLENCHEN")
        canvas.setFont('Helvetica', 12)
        canvas.drawString(50, A4[1] - 65, "Real Estate Solutions")
        
        # Contact info in header
        canvas.setFont('Helvetica', 10)
        canvas.drawRightString(A4[0] - 50, A4[1] - 45, "+34 624 737 299")
        canvas.drawRightString(A4[0] - 50, A4[1] - 60, "contact@esklenchen.com")
        
        # Footer
        canvas.setFillColor(self.colors['light_grey'])
        canvas.rect(0, 0, A4[0], 50, fill=1)
        
        canvas.setFillColor(self.colors['dark_grey'])
        canvas.setFont('Helvetica', 9)
        canvas.drawString(50, 25, f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.drawRightString(A4[0] - 50, 25, f"Página {doc.page}")
        canvas.drawCentredString(A4[0] / 2, 15, "ESKLENCHEN - Inversión Inmobiliaria Inteligente")
        
        canvas.restoreState()
    
    def generate_property_valuation_report(self, valuation_data, output_path):
        """Generate comprehensive property valuation report"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=100,
                bottomMargin=70
            )
            
            story = []
            
            # Title
            story.append(Paragraph("INFORME DE VALORACIÓN INMOBILIARIA", self.styles['ESKLENCHENTitle']))
            story.append(Spacer(1, 20))
            
            # Property summary table
            property_data = [
                ['Ubicación', valuation_data.get('location', 'N/A')],
                ['Tipo de Propiedad', valuation_data.get('property_type', 'N/A')],
                ['Superficie', f"{valuation_data.get('surface', 0)} m²"],
                ['Habitaciones', str(valuation_data.get('rooms', 'N/A'))],
                ['Baños', str(valuation_data.get('bathrooms', 'N/A'))],
                ['Estado', valuation_data.get('condition', 'N/A')],
                ['Año de Construcción', str(valuation_data.get('year_built', 'N/A'))]
            ]
            
            property_table = Table(property_data, colWidths=[4*cm, 8*cm])
            property_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (0, -1), white),
                ('BACKGROUND', (1, 0), (1, -1), self.colors['light_grey']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(Paragraph("DATOS DE LA PROPIEDAD", self.styles['ESKLENCHENSection']))
            story.append(property_table)
            story.append(Spacer(1, 30))
            
            # Valuation results
            story.append(Paragraph("RESULTADOS DE LA VALORACIÓN", self.styles['ESKLENCHENSection']))
            
            valuation_results = [
                ['Valor Estimado', f"€{valuation_data.get('ai_estimated_value', 0):,.0f}"],
                ['Precio por m²', f"€{valuation_data.get('price_per_sqm', 0):,.0f}"],
                ['Potencial de Alquiler Mensual', f"€{valuation_data.get('rental_potential_monthly', 0):,.0f}"],
                ['Rentabilidad Anual', f"{valuation_data.get('rental_yield_percentage', 0):.2f}%"],
                ['ROI Esperado (1 año)', f"{valuation_data.get('expected_roi_1year', 0):.2f}%"],
                ['ROI Esperado (3 años)', f"{valuation_data.get('expected_roi_3year', 0):.2f}%"],
                ['ROI Esperado (5 años)', f"{valuation_data.get('expected_roi_5year', 0):.2f}%"],
                ['Nivel de Riesgo', valuation_data.get('risk_level', 'N/A').title()],
                ['Potencial de Inversión', valuation_data.get('investment_potential', 'N/A').title()]
            ]
            
            valuation_table = Table(valuation_results, colWidths=[6*cm, 6*cm])
            valuation_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.colors['secondary']),
                ('TEXTCOLOR', (0, 0), (0, -1), black),
                ('BACKGROUND', (1, 0), (1, -1), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(valuation_table)
            story.append(Spacer(1, 30))
            
            # AI Confidence and Analysis
            confidence_score = valuation_data.get('ai_confidence_score', 0)
            story.append(Paragraph("ANÁLISIS DE CONFIANZA IA", self.styles['ESKLENCHENSection']))
            story.append(Paragraph(
                f"<b>Puntuación de Confianza:</b> {confidence_score:.1f}% - "
                f"{'Muy Alta' if confidence_score >= 90 else 'Alta' if confidence_score >= 80 else 'Media' if confidence_score >= 70 else 'Baja'}",
                self.styles['ESKLENCHENHighlight']
            ))
            story.append(Spacer(1, 20))
            
            # Recommendations
            recommendations = valuation_data.get('ai_recommendations', [])
            if isinstance(recommendations, str):
                try:
                    recommendations = json.loads(recommendations)
                except:
                    recommendations = []
            
            if recommendations:
                story.append(Paragraph("RECOMENDACIONES", self.styles['ESKLENCHENSection']))
                for i, rec in enumerate(recommendations, 1):
                    story.append(Paragraph(f"{i}. {rec}", self.styles['ESKLENCHENBody']))
                story.append(Spacer(1, 20))
            
            # Risk factors
            risk_factors = valuation_data.get('risk_factors', [])
            if isinstance(risk_factors, str):
                try:
                    risk_factors = json.loads(risk_factors)
                except:
                    risk_factors = []
            
            if risk_factors:
                story.append(Paragraph("FACTORES DE RIESGO", self.styles['ESKLENCHENSection']))
                for i, risk in enumerate(risk_factors, 1):
                    story.append(Paragraph(f"• {risk}", self.styles['ESKLENCHENBody']))
                story.append(Spacer(1, 20))
            
            # Market analysis
            story.append(Paragraph("ANÁLISIS DE MERCADO", self.styles['ESKLENCHENSection']))
            market_text = f"""
            El análisis de mercado para {valuation_data.get('location', 'la zona')} indica una tendencia 
            {valuation_data.get('market_trend', 'estable')} en los precios inmobiliarios. 
            La competencia en la zona es {valuation_data.get('competition_level', 'media')}, 
            lo que influye en el potencial de alquiler y la velocidad de venta.
            
            Basándose en datos comparables de propiedades similares en la zona, 
            la valoración presenta un nivel de confianza del {confidence_score:.1f}%, 
            considerando factores como ubicación, características de la propiedad, 
            estado del mercado local y tendencias de inversión.
            """
            story.append(Paragraph(market_text, self.styles['ESKLENCHENBody']))
            story.append(Spacer(1, 30))
            
            # Disclaimer
            story.append(Paragraph("AVISO LEGAL", self.styles['ESKLENCHENSection']))
            disclaimer_text = """
            Esta valoración ha sido generada mediante algoritmos de inteligencia artificial 
            desarrollados por ESKLENCHEN Real Estate Solutions. Los resultados son estimaciones 
            basadas en datos de mercado y características de la propiedad. Para una valoración 
            oficial, se recomienda consultar con un tasador certificado. ESKLENCHEN no se hace 
            responsable de decisiones de inversión basadas únicamente en este informe.
            """
            story.append(Paragraph(disclaimer_text, self.styles['ESKLENCHENBody']))
            
            # Build PDF with custom header/footer
            doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
            
            return True, "PDF generado exitosamente"
            
        except Exception as e:
            return False, f"Error generando PDF: {str(e)}"
    
    def generate_client_portfolio_report(self, client_data, projects_data, output_path):
        """Generate client portfolio performance report"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=100,
                bottomMargin=70
            )
            
            story = []
            
            # Title
            story.append(Paragraph("INFORME DE PORTFOLIO DE INVERSIÓN", self.styles['ESKLENCHENTitle']))
            story.append(Spacer(1, 20))
            
            # Client information
            story.append(Paragraph("INFORMACIÓN DEL CLIENTE", self.styles['ESKLENCHENSection']))
            
            client_info = [
                ['Nombre', client_data.get('full_name', 'N/A')],
                ['Email', client_data.get('email', 'N/A')],
                ['Tipo de Cliente', client_data.get('client_type', 'N/A').title()],
                ['Experiencia en Inversión', client_data.get('investment_experience', 'N/A').title()],
                ['Tolerancia al Riesgo', client_data.get('risk_tolerance', 'N/A').title()],
                ['Cliente desde', client_data.get('created_at', 'N/A')[:10] if client_data.get('created_at') else 'N/A']
            ]
            
            client_table = Table(client_info, colWidths=[4*cm, 8*cm])
            client_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (0, -1), white),
                ('BACKGROUND', (1, 0), (1, -1), self.colors['light_grey']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(client_table)
            story.append(Spacer(1, 30))
            
            # Portfolio summary
            story.append(Paragraph("RESUMEN DEL PORTFOLIO", self.styles['ESKLENCHENSection']))
            
            total_invested = client_data.get('total_invested', 0)
            total_revenue = client_data.get('total_revenue', 0)
            total_profit = client_data.get('total_profit', 0)
            average_roi = client_data.get('average_roi', 0)
            
            portfolio_summary = [
                ['Total Invertido', f"€{total_invested:,.0f}"],
                ['Ingresos Totales', f"€{total_revenue:,.0f}"],
                ['Beneficio Total', f"€{total_profit:,.0f}"],
                ['ROI Promedio', f"{average_roi:.2f}%"],
                ['Proyectos Activos', str(client_data.get('active_projects_count', 0))],
                ['Proyectos Completados', str(client_data.get('completed_projects_count', 0))]
            ]
            
            portfolio_table = Table(portfolio_summary, colWidths=[6*cm, 6*cm])
            portfolio_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.colors['secondary']),
                ('TEXTCOLOR', (0, 0), (0, -1), black),
                ('BACKGROUND', (1, 0), (1, -1), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(portfolio_table)
            story.append(Spacer(1, 30))
            
            # Projects detail
            if projects_data:
                story.append(Paragraph("DETALLE DE PROYECTOS", self.styles['ESKLENCHENSection']))
                
                for project in projects_data:
                    story.append(Paragraph(f"<b>{project.get('title', 'Proyecto sin título')}</b>", self.styles['ESKLENCHENBody']))
                    
                    project_details = [
                        ['Ubicación', project.get('location', 'N/A')],
                        ['Tipo', project.get('property_type', 'N/A')],
                        ['Estado', project.get('status', 'N/A').title()],
                        ['Inversión', f"€{project.get('total_investment', 0):,.0f}"],
                        ['Ingresos', f"€{project.get('actual_revenue', 0):,.0f}"],
                        ['ROI', f"{project.get('roi_percentage', 0):.2f}%"]
                    ]
                    
                    project_table = Table(project_details, colWidths=[3*cm, 4*cm])
                    project_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), self.colors['light_grey']),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 0.5, grey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 4),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    
                    story.append(project_table)
                    story.append(Spacer(1, 15))
            
            # Performance analysis
            story.append(Paragraph("ANÁLISIS DE RENDIMIENTO", self.styles['ESKLENCHENSection']))
            
            performance_text = f"""
            Su portfolio de inversión con ESKLENCHEN muestra un rendimiento 
            {'excelente' if average_roi > 10 else 'bueno' if average_roi > 6 else 'moderado'} 
            con un ROI promedio del {average_roi:.2f}%.
            
            Con una inversión total de €{total_invested:,.0f}, ha generado ingresos por 
            €{total_revenue:,.0f}, resultando en un beneficio neto de €{total_profit:,.0f}.
            
            {'Su estrategia de diversificación está funcionando bien.' if len(projects_data) > 2 else 'Considere diversificar su portfolio con más propiedades.' if len(projects_data) <= 2 else ''}
            """
            
            story.append(Paragraph(performance_text, self.styles['ESKLENCHENBody']))
            story.append(Spacer(1, 20))
            
            # Recommendations
            story.append(Paragraph("RECOMENDACIONES", self.styles['ESKLENCHENSection']))
            
            recommendations = []
            if average_roi < 6:
                recommendations.append("Considere propiedades con mayor potencial de alquiler turístico")
            if len(projects_data) < 3:
                recommendations.append("Diversifique su portfolio con propiedades en diferentes ubicaciones")
            if total_invested < 200000:
                recommendations.append("Explore oportunidades de inversión adicionales para maximizar beneficios")
            
            recommendations.extend([
                "Mantenga un seguimiento regular del rendimiento de sus propiedades",
                "Considere el programa 'Reforma sin Coste' para optimizar propiedades existentes",
                "Evalúe oportunidades en el mercado del Maresme y Barcelona"
            ])
            
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['ESKLENCHENBody']))
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
            
            return True, "PDF de portfolio generado exitosamente"
            
        except Exception as e:
            return False, f"Error generando PDF de portfolio: {str(e)}"
    
    def generate_renovation_proposal_pdf(self, proposal_data, output_path):
        """Generate renovation proposal PDF for 'Reforma sin Coste' program"""
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=100,
                bottomMargin=70
            )
            
            story = []
            
            # Title
            story.append(Paragraph("PROPUESTA REFORMA SIN COSTE", self.styles['ESKLENCHENTitle']))
            story.append(Spacer(1, 20))
            
            # Program introduction
            story.append(Paragraph("PROGRAMA REFORMA SIN COSTE", self.styles['ESKLENCHENSection']))
            intro_text = """
            ESKLENCHEN le presenta su programa exclusivo 'Reforma sin Coste', diseñado para 
            maximizar el valor y rentabilidad de su propiedad sin inversión inicial por su parte. 
            Nuestro equipo se encarga de la financiación, gestión y ejecución completa del proyecto.
            """
            story.append(Paragraph(intro_text, self.styles['ESKLENCHENBody']))
            story.append(Spacer(1, 20))
            
            # Property details
            story.append(Paragraph("DETALLES DE LA PROPIEDAD", self.styles['ESKLENCHENSection']))
            
            property_info = [
                ['Ubicación', proposal_data.get('location', 'N/A')],
                ['Tipo', proposal_data.get('property_type', 'N/A')],
                ['Superficie', f"{proposal_data.get('surface', 0)} m²"],
                ['Estado Actual', proposal_data.get('current_condition', 'N/A')],
                ['Habitaciones', str(proposal_data.get('rooms', 'N/A'))]
            ]
            
            property_table = Table(property_info, colWidths=[4*cm, 8*cm])
            property_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.colors['primary']),
                ('TEXTCOLOR', (0, 0), (0, -1), white),
                ('BACKGROUND', (1, 0), (1, -1), self.colors['light_grey']),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(property_table)
            story.append(Spacer(1, 30))
            
            # Financial analysis
            story.append(Paragraph("ANÁLISIS FINANCIERO", self.styles['ESKLENCHENSection']))
            
            renovation_proposal = proposal_data.get('renovation_proposal', {})
            
            financial_data = [
                ['Valor Actual', f"€{renovation_proposal.get('current_value', 0):,.0f}"],
                ['Valor Post-Renovación', f"€{renovation_proposal.get('post_renovation_value', 0):,.0f}"],
                ['Incremento de Valor', f"€{renovation_proposal.get('value_increase', 0):,.0f}"],
                ['Coste de Renovación', f"€{renovation_proposal.get('renovation_cost', 0):,.0f}"],
                ['Alquiler Actual Potencial', f"€{renovation_proposal.get('current_rental_potential', 0):,.0f}/mes"],
                ['Alquiler Post-Renovación', f"€{renovation_proposal.get('post_renovation_rental', 0):,.0f}/mes"],
                ['Incremento Alquiler', f"€{renovation_proposal.get('rental_increase', 0):,.0f}/mes"],
                ['Ingresos Anuales', f"€{renovation_proposal.get('annual_rental_income', 0):,.0f}"],
                ['Período de Amortización', f"{renovation_proposal.get('payback_period_months', 0):.1f} meses"],
                ['ROI Primer Año', f"{renovation_proposal.get('roi_first_year', 0):.2f}%"]
            ]
            
            financial_table = Table(financial_data, colWidths=[6*cm, 6*cm])
            financial_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), self.colors['secondary']),
                ('TEXTCOLOR', (0, 0), (0, -1), black),
                ('BACKGROUND', (1, 0), (1, -1), white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            
            story.append(financial_table)
            story.append(Spacer(1, 30))
            
            # Program benefits
            story.append(Paragraph("BENEFICIOS DEL PROGRAMA", self.styles['ESKLENCHENSection']))
            
            benefits = renovation_proposal.get('program_benefits', [])
            for benefit in benefits:
                story.append(Paragraph(f"✓ {benefit}", self.styles['ESKLENCHENBody']))
            
            story.append(Spacer(1, 20))
            
            # Next steps
            story.append(Paragraph("PRÓXIMOS PASOS", self.styles['ESKLENCHENSection']))
            
            next_steps = renovation_proposal.get('next_steps', [])
            for i, step in enumerate(next_steps, 1):
                story.append(Paragraph(f"{i}. {step}", self.styles['ESKLENCHENBody']))
            
            story.append(Spacer(1, 30))
            
            # Contact information
            story.append(Paragraph("CONTACTO", self.styles['ESKLENCHENSection']))
            contact_text = """
            Para proceder con esta propuesta o resolver cualquier duda, contacte con nuestro 
            equipo de expertos:
            
            Teléfono: +34 624 737 299
            Email: contact@esklenchen.com
            
            Nuestro equipo le contactará en las próximas 24 horas para programar la visita técnica 
            y comenzar el proceso de reforma sin coste.
            """
            story.append(Paragraph(contact_text, self.styles['ESKLENCHENBody']))
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
            
            return True, "PDF de propuesta de reforma generado exitosamente"
            
        except Exception as e:
            return False, f"Error generando PDF de propuesta: {str(e)}"

