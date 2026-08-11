import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Define NumberedCanvas for Page X of Y footers
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Suppress running header/footer on page 1 title block
        if self._pageNumber > 1:
            # Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1e3a8a"))
            self.drawString(54, 750, "AGAIF 2026 | CERTIFIED ASSESSMENT ASSIGNMENT 3: LEAFLET.JS WEB MAP REPORT")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(558, 750, "Participant: Muhammad Ashraf (MY-411)")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Footer
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 36, "ASEAN GeoAI Fusion 2026 — Interactive Geospatial Web Mapping Project")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        
        self.restoreState()

def create_report():
    pdf_filename = "AGAIF2026_BC1_CA3_MY-411_Muhammad Ashraf/AGAIF2026_BC1_CA3_MY-411_Muhammad Ashraf_Report.pdf"
    
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=1, # Center
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13,
        textColor=colors.HexColor('#2563eb'),
        alignment=1,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    story = []

    # Title Block
    story.append(Paragraph("CERTIFIED ASSESSMENT ASSIGNMENT 3", title_style))
    story.append(Paragraph("AI-Assisted Interactive Web Mapping Using Leaflet.js", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=10))

    # Metadata Table Box
    meta_data = [
        [
            Paragraph("<b>Participant Name:</b> Muhammad Ashraf", body_style),
            Paragraph("<b>Participant Ref Code:</b> MY-411", body_style)
        ],
        [
            Paragraph("<b>Module / Task:</b> Module 1 / Session 3 (CA3)", body_style),
            Paragraph("<b>Target Region:</b> ASEAN 10 Member Nations", body_style)
        ],
        [
            Paragraph("<b>AI Assistant Used:</b> Antigravity AI / DeepSeek GeoAI Assistant", body_style),
            Paragraph("<b>Submission Date:</b> August 11, 2026", body_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1: Executive Summary & Project Purpose
    story.append(Paragraph("1. Executive Summary & Application Overview", h1_style))
    story.append(Paragraph(
        "This project presents the design, development, and deployment of a modern, responsive interactive web mapping application for visualizing municipal places and national boundaries across all 10 ASEAN member nations. Built using <b>Leaflet.js</b>, HTML5, CSS3, and JavaScript, the application transforms raw shapefiles provided in the <code>ASEAN Shp Data</code> package into an interactive geospatial interface.",
        body_style
    ))
    story.append(Paragraph("<b>Key Functional Features Implemented:</b>", h2_style))
    story.append(Paragraph("• <b>Multiple Base Maps:</b> User-selectable tile layers including OpenStreetMap Standard, CartoDB Positron (Light), CartoDB Dark Matter, and Esri Satellite Imagery.", bullet_style))
    story.append(Paragraph("• <b>Geospatial Layer Representation:</b> 230 municipal place point features rendered as circle markers color-coded by settlement type (Capitals, Cities, Towns) alongside 10 country boundary polygons.", bullet_style))
    story.append(Paragraph("• <b>Interactive HTML Popups & Tooltips:</b> Rich popups displaying place name, country flag image, settlement type badge, population count, and precise coordinates, with hover tooltips for national boundaries.", bullet_style))
    story.append(Paragraph("• <b>Dynamic Search & Filtering Controls:</b> Real-time city search bar, country dropdown filter, settlement type filter, and instant visible counter dashboard.", bullet_style))
    story.append(Paragraph("• <b>Extent Management:</b> Automatic extent fitting (<code>map.fitBounds()</code>) on initial load and filter changes, with quick extent reset controls.", bullet_style))
    story.append(Paragraph("• <b>100% Standalone Offline Compatibility:</b> Local bundling of Leaflet libraries and data definitions to eliminate CORS or SSL CDN loading failures.", bullet_style))
    story.append(Spacer(1, 8))

    # Section 2: AI Tool & Exact Prompts Used
    story.append(Paragraph("2. Generative AI Assistance Log & Prompts Used", h1_style))
    story.append(Paragraph(
        "Generative AI (Antigravity AI / DeepSeek / ChatGPT) served as a pair-programming coding assistant throughout the lifecycle of this project. Below are the exact primary prompts submitted to guide data conversion, code synthesis, and UI refinement:",
        body_style
    ))
    
    prompts_data = [
        [
            Paragraph("<b>Phase</b>", h2_style),
            Paragraph("<b>AI Prompt Submitted</b>", h2_style),
            Paragraph("<b>Target Output / Feature</b>", h2_style)
        ],
        [
            Paragraph("<b>Data Conversion</b>", body_style),
            Paragraph("<i>'Write a Python script using shapefile/pyshp to convert ASEAN country boundaries (Asean.shp) and municipal places (Place.shp) into GeoJSON format. Enrich place features with country flags.'</i>", body_style),
            Paragraph("Converted `.shp` files to `asean_countries.geojson` and `asean_places.geojson` with country flag URLs embedded.", body_style)
        ],
        [
            Paragraph("<b>Web App Scaffold</b>", body_style),
            Paragraph("<i>'Generate a modern, responsive HTML5/CSS3 dashboard layout for Leaflet.js with a dark glassmorphism sidebar containing stat counters, search bar, country/type dropdown filters, and layer legend.'</i>", body_style),
            Paragraph("Structured `index.html` and modern CSS variables stylesheet `style.css`.", body_style)
        ],
        [
            Paragraph("<b>Leaflet Logic & Popups</b>", body_style),
            Paragraph("<i>'Write script.js using Leaflet.js to add OSM, CartoDB, and Esri basemaps, render country polygon boundaries with tooltips, and place circle markers with styled HTML popups showing flags, type, and population.'</i>", body_style),
            Paragraph("Leaflet initialization script with layer controls, popups, and hover highlights.", body_style)
        ],
        [
            Paragraph("<b>Search & Extent Fitting</b>", body_style),
            Paragraph("<i>'Implement real-time search filtering by city name and country dropdown. Auto-fit map bounds using map.fitBounds() when filters update, and fix flexbox container sizing with map.invalidateSize().'</i>", body_style),
            Paragraph("Dynamic filter handlers and flexbox layout invalidation logic.", body_style)
        ]
    ]
    t_prompts = Table(prompts_data, colWidths=[80, 240, 184])
    t_prompts.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_prompts)
    story.append(Spacer(1, 8))

    # Section 3: Dataset Description
    story.append(Paragraph("3. Dataset Description & Pre-Processing", h1_style))
    story.append(Paragraph(
        "The project utilizes the official <code>ASEAN Shp Data</code> dataset provided by the ASEAN GeoAI Secretariat:",
        body_style
    ))
    story.append(Paragraph("• <b>Asean.shp (Polygon Layer):</b> Contains national territorial boundaries for 10 ASEAN member states (Malaysia, Indonesia, Thailand, Vietnam, Philippines, Singapore, Brunei, Cambodia, Laos, Myanmar) and official flag image URLs.", bullet_style))
    story.append(Paragraph("• <b>Place.shp & Place.xlsx (Point Layer):</b> Contains 230 municipal place/city locations across Southeast Asia with key spatial attributes including <code>name</code>, <code>type</code> (capital, city, town), <code>population</code>, <code>Country</code>, <code>Lat</code>, and <code>Long</code>.", bullet_style))
    story.append(Paragraph(
        "<b>Data Transformation:</b> Shapefiles were converted to WGS84 GeoJSON files (<code>asean_countries.geojson</code> and <code>asean_places.geojson</code>). To ensure reliable offline loading without local web server CORS restrictions, the datasets were also bundled into <code>asean_data.js</code>.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Section 4: Technical Development, Corrections & Troubleshooting
    story.append(Paragraph("4. Code Corrections, Technical Improvements & Troubleshooting", h1_style))
    story.append(Paragraph(
        "During testing, several technical challenges were identified and successfully resolved:",
        body_style
    ))

    fixes_data = [
        [
            Paragraph("<b>Issue / Challenge</b>", h2_style),
            Paragraph("<b>Root Cause Identified</b>", h2_style),
            Paragraph("<b>Correction & Solution Applied</b>", h2_style)
        ],
        [
            Paragraph("<b>Shapefile Format Incompatibility</b>", body_style),
            Paragraph("Web browsers cannot natively parse binary ESRI `.shp` files.", body_style),
            Paragraph("Converted shapefiles to GeoJSON using Python `pyshp` and embedded national flags into properties.", body_style)
        ],
        [
            Paragraph("<b>CORS & Local File Access Error</b>", body_style),
            Paragraph("Browsers block `fetch('data.geojson')` when loading `file://` URLs.", body_style),
            Paragraph("Generated `data/asean_data.js` attaching datasets to `window.ASEAN_PLACES` for seamless execution.", body_style)
        ],
        [
            Paragraph("<b>CDN & SSL Intercept Blockage</b>", body_style),
            Paragraph("Corporate firewall/SSL proxy blocked external CDN URLs (`unpkg.com`).", body_style),
            Paragraph("Downloaded standalone Leaflet library files directly into `lib/leaflet.js` and `lib/leaflet.css`.", body_style)
        ],
        [
            Paragraph("<b>Map Blank / Flex Sizing Issue</b>", body_style),
            Paragraph("Leaflet requires explicit pixel dimensions when inside flex containers.", body_style),
            Paragraph("Added `map.invalidateSize()` inside a 200ms timeout after DOM load to ensure proper rendering.", body_style)
        ]
    ]
    t_fixes = Table(fixes_data, colWidths=[120, 180, 204])
    t_fixes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_fixes)
    story.append(Spacer(1, 10))

    # Section 5: Application Screenshots
    story.append(Paragraph("5. Interactive Application Screenshots", h1_style))
    story.append(Paragraph("The following high-resolution screenshots demonstrate the functional interactive mapping application:", body_style))
    story.append(Spacer(1, 4))

    img_dir = "AGAIF2026_BC1_CA3_MY-411_Muhammad Ashraf/screenshots"

    # Screenshot 1: Overview
    img1_path = os.path.join(img_dir, "map_overview.png")
    if os.path.exists(img1_path):
        story.append(Paragraph("<b>Figure 1: Full ASEAN Map Overview (10 Nations & 230 Places)</b>", h2_style))
        story.append(Image(img1_path, width=440, height=247))
        story.append(Paragraph("<i>Displays full extent fitting across Southeast Asia with sidebar stats dashboard and layer legend.</i>", ParagraphStyle('Caption1', parent=body_style, fontSize=8, alignment=1)))
        story.append(Spacer(1, 8))

    # Screenshot 2: Search & Filter
    img2_path = os.path.join(img_dir, "map_filter_search.png")
    if os.path.exists(img2_path):
        story.append(Paragraph("<b>Figure 2: Real-time City Search & Automatic Extent Zooming</b>", h2_style))
        story.append(Image(img2_path, width=440, height=247))
        story.append(Paragraph("<i>Filtering place search for 'Kuala Lumpur' dynamically updates visible count to 1 and auto-zooms map bounds.</i>", ParagraphStyle('Caption2', parent=body_style, fontSize=8, alignment=1)))
        story.append(Spacer(1, 8))

    # Screenshot 3: Popup Detail
    img3_path = os.path.join(img_dir, "map_popup_detail.png")
    if os.path.exists(img3_path):
        story.append(Paragraph("<b>Figure 3: Interactive Attribute Popup Card Display</b>", h2_style))
        story.append(Image(img3_path, width=440, height=247))
        story.append(Paragraph("<i>Clicking a place circle marker opens a styled HTML popup with national flag, city name, country, type badge, and coordinates.</i>", ParagraphStyle('Caption3', parent=body_style, fontSize=8, alignment=1)))
        story.append(Spacer(1, 8))

    # Section 6: Learning Reflection
    story.append(Paragraph("6. Reflection on AI-Assisted GeoAI Development", h1_style))
    story.append(Paragraph(
        "Developing this interactive Leaflet.js web application with Generative AI provided valuable insights into modern GeoAI web development:",
        body_style
    ))
    story.append(Paragraph("• <b>Accelerated Prototyping:</b> AI dramatically reduced setup time for GeoJSON data manipulation, Leaflet boilerplate, and CSS layout styling, allowing focus on user experience and GIS data integrity.", bullet_style))
    story.append(Paragraph("• <b>Troubleshooting & Resilience:</b> When faced with browser CORS restrictions, flexbox sizing glitches, and CDN proxy blockages, AI assisted in identifying root causes and synthesizing robust offline fallbacks.", bullet_style))
    story.append(Paragraph("• <b>Responsible AI Usage:</b> All AI-generated code was thoroughly reviewed, debugged, tested, and validated against GIS standards and assignment criteria before final submission.", bullet_style))
    story.append(Spacer(1, 10))

    # Signature Block
    sig_data = [
        [
            Paragraph("<b>Report Prepared By:</b>", body_style),
            Paragraph("<b>Assessment Status:</b>", body_style)
        ],
        [
            Paragraph("Muhammad Ashraf<br/>Participant Reference Code: MY-411<br/>ASEAN GeoAI Fusion 2026", body_style),
            Paragraph("Completed & Fully Verified<br/>Certified Assessment Assignment 3<br/>Submission Package Ready", body_style)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[250, 254])
    t_sig.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_sig)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF Report generated successfully at: {pdf_filename}")

if __name__ == "__main__":
    create_report()
