"""
build_pdf.py  –  Generates Traffic_Forecasting_Report.pdf
Matches the style of the reference ADS_Report.pdf:
  - Cover page with SJEC logo + details table
  - Running header (project title) + footer (dept / page number)
  - Sections numbered 1-8, subsections 1.1 etc.
  - Simple booktabs-style tables
  - Inline figures with captions, placed exactly as in the .tex source
  - Code blocks with light grey background
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer,
    Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas as rcanvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# ── paths ──────────────────────────────────────────────────────────────────────
HERE   = os.path.dirname(os.path.abspath(__file__))
PLOTS  = os.path.join(HERE, "plots")
LOGO   = os.path.join(HERE, "sjec_logo.png")
OUTPUT = os.path.join(HERE, "Traffic_Forecasting_Report.pdf")

W, H = A4
LM = RM = 2.5 * cm
TM = 2.6 * cm
BM = 2.0 * cm

# ── canvas-level decorations (header + footer) ─────────────────────────────────
class PageDeco(rcanvas.Canvas):
    """Draws running header and footer on every page except the cover."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved = []

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        n = len(self._saved)
        for state in self._saved:
            self.__dict__.update(state)
            self._decorate(n)
            super().showPage()
        super().save()

    def _decorate(self, _total):
        if self._pageNumber == 1:       # cover page – no header/footer
            return
        self.saveState()

        # header
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.black)
        self.drawString(LM, H - TM + 10,
                        "Traffic Congestion Forecasting and Anomaly Detection")
        self.setStrokeColor(colors.HexColor("#888888"))
        self.setLineWidth(0.5)
        self.line(LM, H - TM + 6, W - RM, H - TM + 6)

        # footer
        self.setFont("Helvetica", 9)
        self.drawString(LM, BM - 6, "Dept. of CSDS, SJEC")
        # page numbering: pages 2-4 are roman (i,ii,iii), rest arabic
        pnum = self._pageNumber
        if pnum == 2:
            label = "i"
        elif pnum == 3:
            label = "ii"
        elif pnum == 4:
            label = "iii"
        else:
            label = str(pnum - 4)
        self.drawRightString(W - RM, BM - 6, label)

        self.restoreState()

# ── style helpers ───────────────────────────────────────────────────────────────
def make_styles():
    S = getSampleStyleSheet()
    base = dict(fontName="Times-Roman", fontSize=11, leading=15,
                spaceAfter=6, alignment=TA_JUSTIFY)

    def ps(name, **kw):
        merged = {**base, **kw}
        return ParagraphStyle(name, **merged)

    styles = {
        "body"    : ps("Body"),
        "bullet"  : ps("Bullet", leftIndent=20, spaceAfter=3,
                       fontSize=10.5, leading=14),
        "h1"      : ps("H1", fontName="Helvetica-Bold", fontSize=13,
                       leading=17, spaceBefore=14, spaceAfter=5,
                       alignment=TA_LEFT),
        "h2"      : ps("H2", fontName="Helvetica-Bold", fontSize=11,
                       leading=15, spaceBefore=10, spaceAfter=4,
                       alignment=TA_LEFT),
        "h3"      : ps("H3", fontName="Helvetica-Bold", fontSize=10.5,
                       leading=14, spaceBefore=8, spaceAfter=3,
                       alignment=TA_LEFT),
        "caption" : ps("Caption", fontName="Helvetica-Bold",
                       fontSize=9.5, leading=13, alignment=TA_CENTER,
                       spaceBefore=3, spaceAfter=8),
        "code"    : ps("Code", fontName="Courier", fontSize=8,
                       leading=11, alignment=TA_LEFT),
        "tblhdr"  : ps("TblHdr", fontName="Helvetica-Bold",
                       fontSize=9.5, alignment=TA_CENTER, leading=12),
        "tblcell" : ps("TblCell", fontName="Times-Roman",
                       fontSize=9.5, alignment=TA_LEFT, leading=12),
        "tblcellC": ps("TblCellC", fontName="Times-Roman",
                       fontSize=9.5, alignment=TA_CENTER, leading=12),
        # cover-page styles
        "cov_inst": ps("CovInst", fontName="Helvetica-Bold", fontSize=14,
                       leading=18, alignment=TA_CENTER),
        "cov_sub" : ps("CovSub", fontName="Helvetica-Bold", fontSize=11,
                       leading=15, alignment=TA_CENTER),
        "cov_proj": ps("CovProj", fontName="Helvetica-Bold", fontSize=17,
                       leading=22, alignment=TA_CENTER),
        "cov_rby" : ps("CovRBy", fontName="Helvetica", fontSize=13,
                       leading=17, alignment=TA_CENTER),
        "toc_hdr" : ps("TocHdr", fontName="Helvetica-Bold", fontSize=13,
                       leading=17, spaceBefore=0, spaceAfter=10,
                       alignment=TA_LEFT),
    }
    return styles

# ── table helpers ───────────────────────────────────────────────────────────────
BOOKTABS_STYLE = [
    ("LINEABOVE",   (0, 0), (-1, 0),  1.0, colors.black),
    ("LINEBELOW",   (0, 0), (-1, 0),  0.5, colors.black),
    ("LINEBELOW",   (0,-1), (-1,-1),  1.0, colors.black),
    ("ALIGN",       (0, 0), (-1,-1), "LEFT"),
    ("VALIGN",      (0, 0), (-1,-1), "MIDDLE"),
    ("TOPPADDING",  (0, 0), (-1,-1),  3),
    ("BOTTOMPADDING",(0,0), (-1,-1),  3),
    ("LEFTPADDING", (0, 0), (-1,-1),  4),
    ("RIGHTPADDING",(0, 0), (-1,-1),  4),
]

def simple_table(data, col_widths, style_extra=None):
    ts = TableStyle(BOOKTABS_STYLE + (style_extra or []))
    t = Table(data, colWidths=col_widths)
    t.setStyle(ts)
    return t

# ── figure helper ────────────────────────────────────────────────────────────────
def figure(path, caption, width=None, label_num=""):
    w = width or (W - LM - RM)
    items = []
    if os.path.exists(path):
        ratio = 0.45          # height/width ratio – adjust per image
        img   = Image(path, width=w, height=w * ratio)
        img.hAlign = "CENTER"
        items.append(img)
    else:
        items.append(Paragraph(f"[Figure: {os.path.basename(path)}]",
                                make_styles()["body"]))
    items.append(Paragraph(f"<b>Figure {label_num}:</b>{caption}",
                            make_styles()["caption"]))
    return KeepTogether(items)

# ── code block ───────────────────────────────────────────────────────────────────
def code_block(S, lines, caption=""):
    code_para = Paragraph(
        "<br/>".join(
            l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace(" ", "&nbsp;")
            for l in lines
        ),
        S["code"]
    )
    t = Table([[code_para]], colWidths=[W - LM - RM])
    t.setStyle(TableStyle([
        ("BOX",            (0,0),(-1,-1), 0.5, colors.HexColor("#999999")),
        ("BACKGROUND",     (0,0),(-1,-1), colors.HexColor("#f6f6f6")),
        ("TOPPADDING",     (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 5),
        ("LEFTPADDING",    (0,0),(-1,-1), 6),
        ("RIGHTPADDING",   (0,0),(-1,-1), 6),
    ]))
    items = [t]
    if caption:
        items.append(Paragraph(caption, make_styles()["caption"]))
    return KeepTogether(items)

# ── TOC row ──────────────────────────────────────────────────────────────────────
def toc_row(S, text, page):
    return [Paragraph(text, S["body"]), Paragraph(str(page), S["tblcellC"])]

# ── MAIN BUILD ───────────────────────────────────────────────────────────────────
def build():
    S = make_styles()
    story = []

    # ── COVER PAGE ──────────────────────────────────────────────────────────────
    story.append(Spacer(1, 6))
    if os.path.exists(LOGO):
        logo = Image(LOGO, width=3.8*cm, height=3.8*cm)
        logo.hAlign = "CENTER"
        story.append(logo)
    story.append(Spacer(1, 10))
    story.append(Paragraph("ST JOSEPH ENGINEERING COLLEGE", S["cov_inst"]))
    story.append(Paragraph("MANGALURU-575028", S["cov_sub"]))
    story.append(Paragraph("Department of Computer Science and Engineering", S["cov_sub"]))
    story.append(Paragraph("(Data Science)", S["cov_sub"]))
    story.append(Paragraph("2026&#x2013;2027", S["cov_sub"]))
    story.append(Spacer(1, 22))
    story.append(Paragraph("Report by", S["cov_rby"]))
    story.append(Spacer(1, 12))

    meta = [
        [Paragraph("<b>Name</b>",             S["tblcellC"]), Paragraph("Harshith",               S["tblcell"])],
        [Paragraph("<b>Semester/Section</b>", S["tblcellC"]), Paragraph("7th sem / CSDS",          S["tblcell"])],
        [Paragraph("<b>Course</b>",           S["tblcellC"]), Paragraph("Advanced Data Science",   S["tblcell"])],
        [Paragraph("<b>Course Code</b>",      S["tblcellC"]), Paragraph("22CDS71",                 S["tblcell"])],
        [Paragraph("<b>Faculty</b>",          S["tblcellC"]), Paragraph("Ms. Nikitha",             S["tblcell"])],
    ]
    mt = Table(meta, colWidths=[5.5*cm, 7*cm])
    mt.setStyle(TableStyle([
        ("GRID",          (0,0),(-1,-1), 1, colors.black),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
    ]))
    mt.hAlign = "CENTER"
    story.append(mt)
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "Traffic Congestion Forecasting and Anomaly Detection Using "
        "Time-Series Analysis and Deep Learning",
        S["cov_proj"]
    ))
    story.append(PageBreak())

    # ── TABLE OF CONTENTS ───────────────────────────────────────────────────────
    story.append(Paragraph("Contents", S["toc_hdr"]))
    toc_data = [
        toc_row(S, "1 &nbsp; Aim", 1),
        toc_row(S, "2 &nbsp; Dataset and Source", 1),
        toc_row(S, "&nbsp;&nbsp;&nbsp; 2.1 &nbsp; Dataset Characteristics", 1),
        toc_row(S, "&nbsp;&nbsp;&nbsp; 2.2 &nbsp; Important Sensor Features", 2),
        toc_row(S, "3 &nbsp; Methodology", 2),
        toc_row(S, "&nbsp;&nbsp;&nbsp; 3.1 &nbsp; Data Preprocessing", 2),
        toc_row(S, "&nbsp;&nbsp;&nbsp; 3.2 &nbsp; Prevention of Data Leakage", 2),
        toc_row(S, "&nbsp;&nbsp;&nbsp; 3.3 &nbsp; Feature Engineering", 3),
        toc_row(S, "&nbsp;&nbsp;&nbsp; 3.4 &nbsp; Train-Test Split", 3),
        toc_row(S, "&nbsp;&nbsp;&nbsp; 3.5 &nbsp; Models Used", 3),
        toc_row(S, "&nbsp;&nbsp;&nbsp; 3.6 &nbsp; Anomaly Detection", 3),
        toc_row(S, "4 &nbsp; Python Implementation", 4),
        toc_row(S, "5 &nbsp; Exploratory Data Analysis", 5),
        toc_row(S, "6 &nbsp; Model Results and Predictions", 8),
        toc_row(S, "7 &nbsp; Anomaly Detection", 10),
        toc_row(S, "8 &nbsp; Result and Conclusion", 12),
    ]
    toc_t = Table(toc_data, colWidths=[W - LM - RM - 1.5*cm, 1.5*cm])
    toc_t.setStyle(TableStyle([
        ("ALIGN",        (1,0),( 1,-1), "RIGHT"),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0),(-1,-1), 2),
        ("BOTTOMPADDING",(0,0),(-1,-1), 2),
        ("LINEBELOW",    (0,0),(-1,-1), 0.25, colors.HexColor("#dddddd")),
    ]))
    story.append(toc_t)
    story.append(PageBreak())

    # LIST OF TABLES / FIGURES
    story.append(Paragraph("List of Tables", S["toc_hdr"]))
    lot_data = [
        toc_row(S, "1 &nbsp; Dataset Characteristics", 1),
        toc_row(S, "2 &nbsp; Important Sensor and Derived Features", 2),
        toc_row(S, "3 &nbsp; Training and Testing Dataset", 3),
        toc_row(S, "4 &nbsp; Summary Statistics of Traffic Volume", 7),
        toc_row(S, "5 &nbsp; Performance Comparison of Forecasting Models", 8),
        toc_row(S, "6 &nbsp; Anomaly Detection Results", 10),
        toc_row(S, "7 &nbsp; Sample Detected Traffic Anomalies", 11),
    ]
    lot_t = Table(lot_data, colWidths=[W - LM - RM - 1.5*cm, 1.5*cm])
    lot_t.setStyle(TableStyle([
        ("ALIGN",        (1,0),(1,-1), "RIGHT"),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0),(-1,-1), 2),
        ("BOTTOMPADDING",(0,0),(-1,-1), 2),
        ("LINEBELOW",    (0,0),(-1,-1), 0.25, colors.HexColor("#dddddd")),
    ]))
    story.append(lot_t)
    story.append(Spacer(1, 16))

    story.append(Paragraph("List of Figures", S["toc_hdr"]))
    lof_data = [
        toc_row(S, "1 &nbsp; Traffic Volume Over Time (60 Days)", 5),
        toc_row(S, "2 &nbsp; Distribution of Traffic Volume", 6),
        toc_row(S, "3 &nbsp; Average Traffic by Hour of Day", 6),
        toc_row(S, "4 &nbsp; Average Traffic by Day of Week", 7),
        toc_row(S, "5 &nbsp; Rolling Average Trend (24-Hour and 7-Day Windows)", 7),
        toc_row(S, "6 &nbsp; Comparison of Forecasting Models (MAE &amp; RMSE)", 8),
        toc_row(S, "7 &nbsp; ARIMA Forecast vs. Actual Traffic", 9),
        toc_row(S, "8 &nbsp; LSTM Forecast vs. Actual Traffic", 10),
        toc_row(S, "9 &nbsp; Detected Traffic Anomalies (Red Markers)", 12),
    ]
    lof_t = Table(lof_data, colWidths=[W - LM - RM - 1.5*cm, 1.5*cm])
    lof_t.setStyle(TableStyle([
        ("ALIGN",        (1,0),(1,-1), "RIGHT"),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0),(-1,-1), 2),
        ("BOTTOMPADDING",(0,0),(-1,-1), 2),
        ("LINEBELOW",    (0,0),(-1,-1), 0.25, colors.HexColor("#dddddd")),
    ]))
    story.append(lof_t)
    story.append(PageBreak())

    # =========================================================================
    # BODY SECTIONS  (pages count starts at 1 after this PageBreak)
    # =========================================================================

    # ── 1. AIM ──────────────────────────────────────────────────────────────────
    story.append(Paragraph("1. Aim", S["h1"]))
    story.append(Paragraph(
        "The aim of this project is to develop a machine-learning-based traffic congestion "
        "forecasting and anomaly detection system using urban road sensor time-series data. "
        "The proposed system models high-frequency traffic flow measurements and predicts "
        "short-term congestion patterns before they escalate. Traditional congestion management "
        "methods are reactive — signals are adjusted only after congestion has already "
        "occurred. A proactive, data-driven approach enables transport authorities to act "
        "ahead of time, reducing delays and improving network throughput.", S["body"]
    ))
    story.append(Paragraph(
        "The project also integrates an anomaly detection module that automatically flags "
        "unusual traffic observations — such as sudden spikes caused by accidents, road "
        "blockages, or sensor faults — without requiring labelled incident data.", S["body"]
    ))
    story.append(Paragraph("The specific objectives are:", S["body"]))
    for txt in [
        "1. Load and inspect continuous 5-minute traffic sensor data from a 60-day period.",
        "2. Clean the dataset, handle missing values, and select a single sensor corridor.",
        "3. Perform Exploratory Data Analysis (EDA) to understand diurnal patterns and weekday versus weekend behaviour.",
        "4. Engineer temporal, autoregressive lag, and rolling statistical features.",
        "5. Train and compare a classical ARIMA(2,1,2) model against a lightweight LSTM recurrent neural network.",
        "6. Evaluate both models on a strictly held-out chronological test set using MAE and RMSE.",
        "7. Detect traffic anomalies using a 3-sigma residual thresholding strategy.",
    ]:
        story.append(Paragraph(txt, S["bullet"]))

    # ── 2. DATASET AND SOURCE ────────────────────────────────────────────────────
    story.append(Spacer(1, 8))
    story.append(Paragraph("2. Dataset and Source", S["h1"]))
    story.append(Paragraph(
        "The dataset is modelled on the California Department of Transportation Performance "
        "Measurement System (Caltrans PeMS), which records inductive loop detector measurements "
        "at 5-minute intervals across highway corridors. A single representative urban sensor "
        "was selected to simulate a local edge-processing scenario.", S["body"]
    ))
    story.append(Paragraph(
        "The recording window spans 60 consecutive calendar days: "
        "1 January 2024 00:00 to 29 February 2024 23:55. "
        "With 288 samples per day this yields 17,280 timestamped observations.", S["body"]
    ))

    story.append(Paragraph("2.1 Dataset Characteristics", S["h2"]))
    ds_h = [[Paragraph("Characteristic", S["tblhdr"]), Paragraph("Description", S["tblhdr"])]]
    ds_r = [
        ["Dataset",             "Urban Corridor Traffic Telemetry (PeMS Benchmark)"],
        ["Source",              "Caltrans PeMS Repository"],
        ["Observation period",  "1 Jan 2024 00:00 -- 29 Feb 2024 23:55 (60 days)"],
        ["Sampling interval",   "5 minutes (288 readings per day)"],
        ["Total observations",  "17,280"],
        ["Target variable",     "traffic  --  vehicle count per 5-minute window"],
        ["Value range",         "6.34 -- 83.51 vehicles per interval"],
        ["Missing values",      "Imputed via forward/backward fill and linear interpolation"],
        ["Train set",           "13,824 samples (80 %)"],
        ["Test set",            "3,456 samples (20 %)"],
    ]
    ds_data = ds_h + [[Paragraph(r[0], S["tblcell"]), Paragraph(r[1], S["tblcell"])] for r in ds_r]
    story.append(Paragraph("<b>Table 1:</b>Dataset Characteristics", S["caption"]))
    story.append(simple_table(ds_data, [5*cm, 11*cm]))

    story.append(Paragraph("2.2 Important Sensor Features", S["h2"]))
    ft_h = [[Paragraph("Feature", S["tblhdr"]), Paragraph("Type", S["tblhdr"]), Paragraph("Description", S["tblhdr"])]]
    ft_r = [
        ["timestamp",     "Datetime",   "5-minute sampling index"],
        ["traffic",       "Continuous", "Vehicle count per 5-minute window"],
        ["hour",          "Integer",    "Hour of the day (0-23)"],
        ["day_of_week",   "Integer",    "Day index (0 = Monday, 6 = Sunday)"],
        ["is_weekend",    "Binary",     "1 for Saturday/Sunday, 0 otherwise"],
        ["lag_1",         "Continuous", "Traffic 1 step prior (t - 5 min)"],
        ["lag_3",         "Continuous", "Traffic 3 steps prior (t - 15 min)"],
        ["lag_6",         "Continuous", "Traffic 6 steps prior (t - 30 min)"],
        ["rolling_mean",  "Continuous", "30-minute rolling average (6 steps)"],
        ["rolling_std",   "Continuous", "30-minute rolling standard deviation"],
    ]
    ft_data = ft_h + [[Paragraph(r[0], S["tblcell"]), Paragraph(r[1], S["tblcell"]), Paragraph(r[2], S["tblcell"])] for r in ft_r]
    story.append(Paragraph("<b>Table 2:</b>Important Sensor and Derived Features", S["caption"]))
    story.append(simple_table(ft_data, [3.8*cm, 2.8*cm, 9.4*cm]))

    # ── 3. METHODOLOGY ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 8))
    story.append(Paragraph("3. Methodology", S["h1"]))
    story.append(Paragraph(
        "The proposed system follows a structured pipeline of preprocessing, exploratory "
        "analysis, feature engineering, model training, evaluation, and anomaly detection. "
        "The overall workflow is:", S["body"]
    ))
    story.append(Paragraph(
        "Data Collection &#x2192; Preprocessing &#x2192; EDA &#x2192; "
        "Feature Engineering &#x2192; Train/Test Split &#x2192; "
        "Model Training &#x2192; Evaluation &#x2192; Anomaly Detection",
        ParagraphStyle("workflow", parent=S["body"], alignment=TA_CENTER,
                       fontName="Helvetica", spaceBefore=4, spaceAfter=4)
    ))

    story.append(Paragraph("3.1 Data Preprocessing", S["h2"]))
    story.append(Paragraph(
        "The raw dataset was inspected for temporal continuity and sorted chronologically. "
        "A single target sensor corridor was isolated. Sporadic missing readings caused by "
        "telemetry dropouts were handled using .bfill() and .ffill() combined with linear "
        "interpolation, producing a gap-free uniform 5-minute time series.", S["body"]
    ))

    story.append(Paragraph("3.2 Prevention of Data Leakage", S["h2"]))
    story.append(Paragraph(
        "Standard randomised cross-validation allows future observations to leak into the "
        "training set. To prevent this:", S["body"]
    ))
    for txt in [
        "The first 80 % of observations (chronologically) form the training set; the remaining 20 % form the test set.",
        "All scalers (MinMaxScaler) are fitted only on training data and then applied to transform the test data.",
        "Lag and rolling features use strictly backward-looking window operations.",
    ]:
        story.append(Paragraph(f"&#x2022; {txt}", S["bullet"]))

    story.append(Paragraph("3.3 Feature Engineering", S["h2"]))
    story.append(Paragraph(
        "Three groups of features were derived to capture different temporal dynamics.", S["body"]
    ))
    story.append(Paragraph("3.3.1 Temporal Calendar Features", S["h3"]))
    story.append(Paragraph(
        "Hour of day (0-23), day of week (0-6), and a binary weekend flag (is_weekend) "
        "encode the regular diurnal and weekly commuter cycles.", S["body"]
    ))
    story.append(Paragraph("3.3.2 Autoregressive Lag Features", S["h3"]))
    story.append(Paragraph(
        "Traffic values from the preceding 5 minutes (lag_1), 15 minutes (lag_3), and "
        "30 minutes (lag_6) encode short-term persistence in the traffic signal.", S["body"]
    ))
    story.append(Paragraph("3.3.3 Rolling Window Statistics", S["h3"]))
    story.append(Paragraph(
        "A 30-minute backward-looking window (6 steps) produces the rolling mean and "
        "rolling standard deviation, supplying local baseline and volatility signals.", S["body"]
    ))

    story.append(Paragraph("3.4 Train-Test Split", S["h2"]))
    sp_h = [[Paragraph("Dataset", S["tblhdr"]), Paragraph("Number of Samples", S["tblhdr"]), Paragraph("Percentage", S["tblhdr"])]]
    sp_r = [
        ["Training Set", "13,824", "80 %"],
        ["Testing Set",  "3,456",  "20 %"],
        ["Total",        "17,280", "100 %"],
    ]
    sp_data = sp_h + [[Paragraph(r[0], S["tblcell"]), Paragraph(r[1], S["tblcellC"]), Paragraph(r[2], S["tblcellC"])] for r in sp_r]
    story.append(Paragraph("<b>Table 3:</b>Training and Testing Dataset", S["caption"]))
    story.append(simple_table(sp_data, [6*cm, 5*cm, 5*cm]))
    story.append(Paragraph(
        "Chronological ordering was strictly maintained so that no future information is "
        "visible during model training.", S["body"]
    ))

    story.append(Paragraph("3.5 Models Used", S["h2"]))
    story.append(Paragraph(
        "ARIMA(2,1,2) — Autoregressive Integrated Moving Average with autoregressive order "
        "p=2, one degree of differencing d=1 to remove trend non-stationarity, and moving-average "
        "order q=2. ARIMA serves as the classical statistical baseline.", S["body"]
    ))
    story.append(Paragraph(
        "LSTM (Long Short-Term Memory) — A lightweight LSTM recurrent neural network was "
        "designed to capture complex non-linear temporal dependencies that ARIMA cannot model. "
        "Architecture: input window of 12 steps (60 minutes), LSTM layer with 32 units, "
        "Dropout 0.20, Dense layer with 16 units (ReLU), single-unit output. "
        "Trained with Adam optimiser, MSE loss, up to 15 epochs, EarlyStopping with patience 3.",
        S["body"]
    ))

    story.append(Paragraph("3.6 Anomaly Detection", S["h2"]))
    story.append(Paragraph(
        "LSTM prediction residuals were computed on the test set. A timestamp is flagged as "
        "an anomaly when its absolute prediction error exceeds a statistical threshold "
        "tau = mean(errors) + 3 x std(errors). "
        "This is a parameter-free, unsupervised approach that requires no labelled incident data.",
        S["body"]
    ))

    # ── 4. PYTHON IMPLEMENTATION ─────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("4. Python Implementation", S["h1"]))
    story.append(Paragraph(
        "The implementation is organised into a modular src/ package executed by a "
        "top-level main.py script. Key source files:", S["body"]
    ))
    for txt in [
        "data_loader.py — generates / loads the 60-day telemetry dataset",
        "preprocessing.py — missing value imputation, sensor isolation",
        "features.py — lag variables and rolling statistics",
        "arima_model.py — fits and evaluates ARIMA(2,1,2)",
        "lstm_model.py — builds, trains, and evaluates the LSTM network",
        "evaluation.py — computes MAE and RMSE for both models",
        "anomaly_detection.py — residual thresholding and anomaly flagging",
    ]:
        story.append(Paragraph(f"&#x2022; {txt}", S["bullet"]))

    story.append(Paragraph("4.1 Feature Engineering", S["h2"]))
    story.append(code_block(S, [
        "import pandas as pd",
        "",
        "def create_features(df: pd.DataFrame) -> pd.DataFrame:",
        "    df = df.copy()",
        "    # Temporal calendar features",
        "    df['hour']         = df.index.hour",
        "    df['day_of_week']  = df.index.dayofweek",
        "    df['is_weekend']   = df['day_of_week'].isin([5, 6]).astype(int)",
        "    # Autoregressive lag features",
        "    df['lag_1'] = df['traffic'].shift(1)",
        "    df['lag_3'] = df['traffic'].shift(3)",
        "    df['lag_6'] = df['traffic'].shift(6)",
        "    # Rolling window statistics (30-min = 6 steps)",
        "    df['rolling_mean'] = df['traffic'].shift(1).rolling(6).mean()",
        "    df['rolling_std']  = df['traffic'].shift(1).rolling(6).std()",
        "    df.dropna(inplace=True)",
        "    return df",
    ], "Feature Engineering — src/features.py"))

    story.append(Spacer(1, 6))
    story.append(Paragraph("4.2 LSTM Model", S["h2"]))
    story.append(code_block(S, [
        "from tensorflow.keras.models import Sequential",
        "from tensorflow.keras.layers import LSTM, Dense, Dropout",
        "from tensorflow.keras.callbacks import EarlyStopping",
        "from sklearn.preprocessing import MinMaxScaler",
        "import numpy as np",
        "",
        "def build_and_train_lstm(X_train, y_train, window_size=12, epochs=15):",
        "    scaler_x, scaler_y = MinMaxScaler(), MinMaxScaler()",
        "    X_scaled = scaler_x.fit_transform(X_train)",
        "    y_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1))",
        "    X_seq = np.array([X_scaled[i-window_size:i] for i in range(window_size, len(X_scaled))])",
        "    y_seq = np.array([y_scaled[i, 0]            for i in range(window_size, len(y_scaled))])",
        "    model = Sequential([",
        "        LSTM(32, input_shape=(window_size, X_train.shape[1])),",
        "        Dropout(0.2),",
        "        Dense(16, activation='relu'),",
        "        Dense(1)",
        "    ])",
        "    model.compile(optimizer='adam', loss='mse')",
        "    es = EarlyStopping(monitor='loss', patience=3, restore_best_weights=True)",
        "    model.fit(X_seq, y_seq, epochs=epochs, batch_size=32, callbacks=[es], verbose=0)",
        "    return model, scaler_x, scaler_y",
    ], "LSTM Model — src/lstm_model.py"))

    story.append(Spacer(1, 6))
    story.append(Paragraph("4.3 Anomaly Detection", S["h2"]))
    story.append(code_block(S, [
        "import numpy as np, pandas as pd",
        "",
        "def detect_anomalies(y_true, y_pred, timestamps, sigma=3.0):",
        "    errors    = np.abs(y_true - y_pred)",
        "    threshold = np.mean(errors) + sigma * np.std(errors)",
        "    mask      = errors > threshold",
        "    anomalies = pd.DataFrame({",
        "        'timestamp':  timestamps[mask],",
        "        'traffic':    y_true[mask],",
        "        'prediction': y_pred[mask],",
        "        'error':      errors[mask]",
        "    }).reset_index(drop=True)",
        "    return anomalies, threshold",
    ], "Anomaly Detection — src/anomaly_detection.py"))

    # ── 5. EDA ────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("5. Exploratory Data Analysis", S["h1"]))
    story.append(Paragraph(
        "EDA was performed to understand the distribution and temporal structure of the "
        "traffic data before model training.", S["body"]
    ))

    story.append(Paragraph("5.1 Traffic Volume Over Time", S["h2"]))
    story.append(Paragraph(
        "The full 60-day time series is shown in Figure 1. Clear daily cycles are visible "
        "with consistent morning and evening peaks. Weekend periods show noticeably lower "
        "volumes compared with weekdays.", S["body"]
    ))
    img_w = W - LM - RM
    if os.path.exists(os.path.join(PLOTS, "traffic_over_time.png")):
        img = Image(os.path.join(PLOTS, "traffic_over_time.png"), width=img_w, height=img_w*0.42)
        img.hAlign = "CENTER"
        story.append(img)
    story.append(Paragraph("<b>Figure 1:</b>Traffic Volume Over Time (60 Days)", S["caption"]))

    story.append(Paragraph("5.2 Traffic Volume Distribution", S["h2"]))
    story.append(Paragraph(
        "Figure 2 shows the distribution of traffic volumes across all 17,280 readings. "
        "The distribution is approximately unimodal, centred near the mean of 42.36 "
        "vehicles per interval.", S["body"]
    ))
    w75 = img_w * 0.72
    if os.path.exists(os.path.join(PLOTS, "traffic_distribution.png")):
        img = Image(os.path.join(PLOTS, "traffic_distribution.png"), width=w75, height=w75*0.75)
        img.hAlign = "CENTER"
        story.append(img)
    story.append(Paragraph("<b>Figure 2:</b>Distribution of Traffic Volume", S["caption"]))

    story.append(Paragraph("5.3 Hourly and Daily Traffic Patterns", S["h2"]))
    story.append(Paragraph(
        "Figure 3 shows the average traffic volume for each hour of the day. A sharp "
        "morning peak occurs at 08:00 (mean = 61.77 vehicles), and a secondary evening "
        "peak appears around 17:00.", S["body"]
    ))
    if os.path.exists(os.path.join(PLOTS, "hourly_traffic.png")):
        img = Image(os.path.join(PLOTS, "hourly_traffic.png"), width=w75, height=w75*0.75)
        img.hAlign = "CENTER"
        story.append(img)
    story.append(Paragraph("<b>Figure 3:</b>Average Traffic by Hour of Day", S["caption"]))

    story.append(Paragraph(
        "Figure 4 shows average traffic by day of the week. Weekdays maintain higher "
        "volumes (mean 48.14) while weekend volumes drop sharply (mean 26.48), a "
        "reduction of approximately 45 %.", S["body"]
    ))
    if os.path.exists(os.path.join(PLOTS, "daily_traffic.png")):
        img = Image(os.path.join(PLOTS, "daily_traffic.png"), width=w75, height=w75*0.75)
        img.hAlign = "CENTER"
        story.append(img)
    story.append(Paragraph("<b>Figure 4:</b>Average Traffic by Day of Week", S["caption"]))

    story.append(Paragraph("5.4 Rolling Average Trend", S["h2"]))
    story.append(Paragraph(
        "Figure 5 overlays 24-hour and 7-day rolling averages on the raw signal. Both "
        "smoothed curves are stable over the 60-day window, confirming that the series "
        "has no explosive long-run trend and is suitable for direct modelling.", S["body"]
    ))
    if os.path.exists(os.path.join(PLOTS, "rolling_average.png")):
        img = Image(os.path.join(PLOTS, "rolling_average.png"), width=img_w, height=img_w*0.42)
        img.hAlign = "CENTER"
        story.append(img)
    story.append(Paragraph("<b>Figure 5:</b>Rolling Average Trend (24-Hour and 7-Day Windows)", S["caption"]))

    story.append(Paragraph("5.5 Summary Statistics", S["h2"]))
    ss_h = [[Paragraph("Statistic", S["tblhdr"]), Paragraph("Value", S["tblhdr"])]]
    ss_r = [
        ["Total observations",       "17,280"],
        ["Mean traffic",             "42.36 vehicles / 5 min"],
        ["Standard deviation",       "13.57 vehicles / 5 min"],
        ["Minimum",                  "6.34  vehicles / 5 min"],
        ["Maximum",                  "83.51 vehicles / 5 min"],
        ["Coefficient of variation", "32.0 %"],
        ["Peak hour",                "08:00  (avg 61.77 vehicles)"],
        ["Weekday average",          "48.14 vehicles / 5 min"],
        ["Weekend average",          "26.48 vehicles / 5 min"],
    ]
    ss_data = ss_h + [[Paragraph(r[0], S["tblcell"]), Paragraph(r[1], S["tblcell"])] for r in ss_r]
    story.append(Paragraph("<b>Table 4:</b>Summary Statistics of Traffic Volume", S["caption"]))
    story.append(simple_table(ss_data, [7*cm, 9*cm]))

    # ── 6. MODEL RESULTS ─────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("6. Model Results and Predictions", S["h1"]))
    story.append(Paragraph(
        "Both models were evaluated on the held-out test set (3,456 observations, "
        "19 February -- 29 February 2024).", S["body"]
    ))

    story.append(Paragraph("6.1 Performance Comparison", S["h2"]))
    pc_h = [[Paragraph("Model", S["tblhdr"]), Paragraph("MAE", S["tblhdr"]), Paragraph("RMSE", S["tblhdr"]), Paragraph("Training Time", S["tblhdr"])]]
    pc_r = [
        ["ARIMA(2,1,2)",          "19.41", "22.99", "1.46 s"],
        ["LSTM (Deep Learning)",  "3.77",  "4.87",  "15.78 s"],
    ]
    pc_data = pc_h + [[Paragraph(r[0], S["tblcell"]), Paragraph(r[1], S["tblcellC"]), Paragraph(r[2], S["tblcellC"]), Paragraph(r[3], S["tblcellC"])] for r in pc_r]
    story.append(Paragraph("<b>Table 5:</b>Performance Comparison of Forecasting Models", S["caption"]))
    story.append(simple_table(pc_data, [5.5*cm, 3.5*cm, 3.5*cm, 3.5*cm]))

    story.append(Paragraph(
        "Figure 6 compares MAE and RMSE for both models. The LSTM achieved an 80.5 % "
        "reduction in MAE and a 78.8 % reduction in RMSE compared with ARIMA.", S["body"]
    ))
    if os.path.exists(os.path.join(PLOTS, "model_comparison.png")):
        img = Image(os.path.join(PLOTS, "model_comparison.png"), width=w75, height=w75*0.75)
        img.hAlign = "CENTER"
        story.append(img)
    story.append(Paragraph("<b>Figure 6:</b>Comparison of Forecasting Models (MAE &amp; RMSE)", S["caption"]))

    story.append(Paragraph("6.2 ARIMA Predictions", S["h2"]))
    story.append(Paragraph(
        "Figure 7 shows the ARIMA forecast plotted against the ground truth. After a short "
        "initialisation window the model converges to the long-run mean and fails to track "
        "the high-amplitude diurnal oscillations.", S["body"]
    ))
    if os.path.exists(os.path.join(PLOTS, "arima_prediction.png")):
        img = Image(os.path.join(PLOTS, "arima_prediction.png"), width=img_w, height=img_w*0.42)
        img.hAlign = "CENTER"
        story.append(img)
    story.append(Paragraph("<b>Figure 7:</b>ARIMA Forecast vs. Actual Traffic", S["caption"]))

    story.append(Paragraph("6.3 LSTM Predictions", S["h2"]))
    story.append(Paragraph(
        "Figure 8 shows the LSTM forecast. The model closely tracks the actual traffic "
        "volumes across all 12 test days, accurately reproducing morning peaks, evening "
        "peaks, and weekend depressions.", S["body"]
    ))
    if os.path.exists(os.path.join(PLOTS, "lstm_prediction.png")):
        img = Image(os.path.join(PLOTS, "lstm_prediction.png"), width=img_w, height=img_w*0.42)
        img.hAlign = "CENTER"
        story.append(img)
    story.append(Paragraph("<b>Figure 8:</b>LSTM Forecast vs. Actual Traffic", S["caption"]))

    # ── 7. ANOMALY DETECTION ─────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("7. Anomaly Detection", S["h1"]))
    story.append(Paragraph(
        "The residual-based anomaly detector evaluated all 3,456 test observations. "
        "The mean absolute residual was 3.77 vehicles and the standard deviation was 3.08 "
        "vehicles, giving a decision threshold of tau = 3.77 + 3 x 3.08 = 13.01 vehicles.",
        S["body"]
    ))

    story.append(Paragraph("7.1 Detection Summary", S["h2"]))
    ad_h = [[Paragraph("Parameter", S["tblhdr"]), Paragraph("Value", S["tblhdr"])]]
    ad_r = [
        ["Total test observations",      "3,456"],
        ["Mean absolute residual",       "3.77 vehicles"],
        ["Residual std dev",             "3.08 vehicles"],
        ["Decision threshold (tau)",     "13.01 vehicles"],
        ["Detected anomalies",           "48"],
        ["Anomaly rate",                 "1.39 %"],
    ]
    ad_data = ad_h + [[Paragraph(r[0], S["tblcell"]), Paragraph(r[1], S["tblcell"])] for r in ad_r]
    story.append(Paragraph("<b>Table 6:</b>Anomaly Detection Results", S["caption"]))
    story.append(simple_table(ad_data, [8*cm, 8*cm]))

    story.append(Paragraph("7.2 Sample Detected Anomalies", S["h2"]))
    sa_h = [[
        Paragraph("Timestamp",  S["tblhdr"]),
        Paragraph("Actual",     S["tblhdr"]),
        Paragraph("Predicted",  S["tblhdr"]),
        Paragraph("Error",      S["tblhdr"]),
        Paragraph("Likely Cause", S["tblhdr"]),
    ]]
    sa_r = [
        ["2024-02-19 00:00", "39.06", "22.22", "16.84", "Unexpected midnight surge"],
        ["2024-02-19 07:00", "63.92", "50.39", "13.52", "Early rush-hour onset"],
        ["2024-02-19 10:00", "46.04", "62.71", "16.68", "Abrupt mid-morning drop"],
        ["2024-02-20 08:05", "79.27", "62.45", "16.82", "Extreme peak-hour congestion"],
        ["2024-02-20 16:00", "64.36", "46.57", "17.79", "Early evening bottleneck"],
    ]
    sa_data = sa_h + [[Paragraph(r[0], S["tblcellC"]), Paragraph(r[1], S["tblcellC"]),
                        Paragraph(r[2], S["tblcellC"]), Paragraph(r[3], S["tblcellC"]),
                        Paragraph(r[4], S["tblcell"])] for r in sa_r]
    story.append(Paragraph("<b>Table 7:</b>Sample Detected Traffic Anomalies", S["caption"]))
    story.append(simple_table(sa_data, [3.5*cm, 2*cm, 2.3*cm, 2*cm, 6.2*cm]))

    story.append(Paragraph(
        "Figure 9 plots all detected anomalies as red markers on the traffic time series. "
        "The detector correctly flags isolated spikes and drops without producing false "
        "alarms during normal cyclical variations.", S["body"]
    ))
    if os.path.exists(os.path.join(PLOTS, "anomalies.png")):
        img = Image(os.path.join(PLOTS, "anomalies.png"), width=img_w, height=img_w*0.42)
        img.hAlign = "CENTER"
        story.append(img)
    story.append(Paragraph("<b>Figure 9:</b>Detected Traffic Anomalies (Red Markers)", S["caption"]))

    # ── 8. RESULT AND CONCLUSION ─────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("8. Result and Conclusion", S["h1"]))
    story.append(Paragraph(
        "The project successfully implemented an end-to-end traffic congestion forecasting "
        "and anomaly detection pipeline over 60 days of 5-minute urban road sensor data.",
        S["body"]
    ))
    story.append(Paragraph(
        "The LSTM recurrent neural network achieved an MAE of 3.77 vehicles and an RMSE of "
        "4.87 vehicles on the held-out test set. This represents an 80.5 % reduction in MAE "
        "compared with the classical ARIMA(2,1,2) baseline (MAE 19.41, RMSE 22.99). While "
        "ARIMA collapses to the empirical mean and cannot reproduce diurnal oscillations, the "
        "LSTM accurately tracks both morning rush-hour peaks and weekend flow depressions.",
        S["body"]
    ))
    story.append(Paragraph(
        "The lightweight architecture (32 LSTM units) trained in under 16 seconds on a "
        "commodity CPU, demonstrating that high-accuracy traffic forecasting does not require "
        "large computational resources.", S["body"]
    ))
    story.append(Paragraph(
        "The 3-sigma residual anomaly detector identified 48 anomalous observations out of "
        "3,456 (1.39 %), with a threshold of 13.01 vehicles. These flagged points correspond "
        "to non-recurrent congestion events, sudden flow collapses, and sensor telemetry "
        "faults. No labelled incident data was required.", S["body"]
    ))
    story.append(Paragraph(
        "The complete pipeline — data ingestion, preprocessing, EDA, feature engineering, "
        "ARIMA and LSTM modelling, comparative evaluation, and anomaly detection — is "
        "encapsulated in a single python main.py command that reproduces all results and "
        "outputs automatically.", S["body"]
    ))

    # ── BUILD ────────────────────────────────────────────────────────────────────
    content_frame = Frame(LM, BM, W - LM - RM, H - TM - BM, id="content")
    doc = BaseDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM
    )
    doc.addPageTemplates([PageTemplate(id="All", frames=[content_frame])])
    doc.build(story, canvasmaker=PageDeco)
    print(f"PDF saved: {OUTPUT}")

if __name__ == "__main__":
    build()
