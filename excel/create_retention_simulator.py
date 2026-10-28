"""
05_Telecom_Churn: Excel Dynamic Customer Retention Simulator & CLV Model
Author: worker_m5_telco
Builds Telecom_Customer_Retention_Simulator.xlsx with 5 comprehensive worksheets:
1. Executive Dashboard (KPI Cards, Contract Breakdown, Strategic Recommendations)
2. Retention Campaign Simulator (Interactive Financial Model, What-If Logic, Dynamic Formulas)
3. 2-Way Sensitivity Matrix (Save Rate % vs Offer Cost $, Color Scales)
4. Cohort Heatmap (Tenure Bands vs Contract Type Attrition Rates)
5. Customer Cohorts (Complete Scored Customer Records with Dynamic Formulas)
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule
import pandas as pd

def build_retention_simulator():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    clean_dir = os.path.join(base_dir, 'data', 'clean')
    scored_csv = os.path.join(clean_dir, 'telco_scored_customers.csv')
    excel_dir = os.path.join(base_dir, 'excel')
    os.makedirs(excel_dir, exist_ok=True)
    
    print(f"[1/4] Reading scored customer data from {scored_csv}...")
    df_scored = pd.read_csv(scored_csv)
    
    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)
    
    # Common Palette Styles
    navy_header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    steel_blue_fill  = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    accent_blue_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    card_header_fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
    input_gold_fill  = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    output_green_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    zebra_light_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    
    font_title       = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    font_section     = Font(name="Calibri", size=13, bold=True, color="1F4E79")
    font_header_w    = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_header_b    = Font(name="Calibri", size=11, bold=True, color="000000")
    font_bold        = Font(name="Calibri", size=11, bold=True)
    font_regular     = Font(name="Calibri", size=11)
    font_small       = Font(name="Calibri", size=9, italic=True, color="595959")
    font_kpi_num     = Font(name="Calibri", size=18, bold=True, color="1F4E79")
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    thick_bottom = Border(bottom=Side(style='medium', color='1F4E79'))
    double_bottom = Border(
        top=Side(style='thin', color='1F4E79'),
        bottom=Side(style='double', color='1F4E79')
    )
    
    # =========================================================================
    # TAB 1: EXECUTIVE DASHBOARD
    # =========================================================================
    print("[2/4] Assembling Sheet 1: Executive Dashboard...")
    ws_dash = wb.create_sheet(title="Executive Dashboard")
    ws_dash.views.sheetView[0].showGridLines = True
    
    # Title Banner
    ws_dash.merge_cells("A1:H2")
    ws_dash["A1"] = "TELECOM CUSTOMER CHURN & RETENTION COMMAND CENTER"
    ws_dash["A1"].font = font_title
    ws_dash["A1"].fill = navy_header_fill
    ws_dash["A1"].alignment = Alignment(horizontal="center", vertical="center")
    
    # Subtitle
    ws_dash["A3"] = "Executive Portfolio Summary, Unit Economics & Retention ROI Model"
    ws_dash["A3"].font = font_small
    
    # KPI Summary Cards (Row 5 to Row 7)
    kpis = [
        ("Total Customer Base", "=COUNTA('Customer Cohorts'!A4:A7046)", "#,##0", "B5", "B6"),
        ("Total Monthly MRR", "=SUM('Customer Cohorts'!I4:I7046)", "$#,##0", "C5", "C6"),
        ("Overall Churn Rate", "=COUNTIF('Customer Cohorts'!K4:K7046, 1)/B6", "0.0%", "D5", "D6"),
        ("Immediate MRR at Risk", "=SUMIF('Customer Cohorts'!M4:M7046, \"High\", 'Customer Cohorts'!I4:I7046)", "$#,##0", "E5", "E6"),
        ("Total CLV at Risk", "=SUMIF('Customer Cohorts'!M4:M7046, \"High\", 'Customer Cohorts'!O4:O7046)", "$#,##0", "F5", "F6"),
        ("Projected Campaign ROI", "='Retention Campaign Simulator'!C20", "0.0%", "G5", "G6")
    ]
    
    for title, formula, fmt, cell_h, cell_v in kpis:
        ws_dash[cell_h] = title
        ws_dash[cell_h].font = font_bold
        ws_dash[cell_h].fill = card_header_fill
        ws_dash[cell_h].alignment = Alignment(horizontal="center", vertical="center")
        ws_dash[cell_h].border = thin_border
        
        ws_dash[cell_v] = formula
        ws_dash[cell_v].font = font_kpi_num
        ws_dash[cell_v].alignment = Alignment(horizontal="center", vertical="center")
        ws_dash[cell_v].number_format = fmt
        ws_dash[cell_v].border = thin_border
        
    # Section: Contract Cohort Breakdown Table
    ws_dash["B9"] = "CUSTOMER BASE & CHURN BREAKDOWN BY CONTRACT TYPE"
    ws_dash["B9"].font = font_section
    
    headers_contract = ["Contract Tier", "Total Accounts", "Churned Accounts", "Churn Rate %", "Total MRR", "Churned MRR", "MRR Loss %"]
    for col_idx, h in enumerate(headers_contract, start=2):
        cell = ws_dash.cell(row=10, column=col_idx, value=h)
        cell.font = font_header_w
        cell.fill = steel_blue_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
        
    contract_rows = [
        ("Month-to-month", 11),
        ("One year", 12),
        ("Two year", 13)
    ]
    
    for c_name, r_idx in contract_rows:
        ws_dash.cell(row=r_idx, column=2, value=c_name).font = font_bold
        ws_dash.cell(row=r_idx, column=3, value=f"=COUNTIF('Customer Cohorts'!E4:E7046, \"{c_name}\")").number_format = "#,##0"
        ws_dash.cell(row=r_idx, column=4, value=f"=COUNTIFS('Customer Cohorts'!E4:E7046, \"{c_name}\", 'Customer Cohorts'!K4:K7046, 1)").number_format = "#,##0"
        ws_dash.cell(row=r_idx, column=5, value=f"=D{r_idx}/C{r_idx}").number_format = "0.0%"
        ws_dash.cell(row=r_idx, column=6, value=f"=SUMIF('Customer Cohorts'!E4:E7046, \"{c_name}\", 'Customer Cohorts'!I4:I7046)").number_format = "$#,##0"
        ws_dash.cell(row=r_idx, column=7, value=f"=SUMIFS('Customer Cohorts'!I4:I7046, 'Customer Cohorts'!E4:E7046, \"{c_name}\", 'Customer Cohorts'!K4:K7046, 1)").number_format = "$#,##0"
        ws_dash.cell(row=r_idx, column=8, value=f"=G{r_idx}/F{r_idx}").number_format = "0.0%"
        
        for c_idx in range(2, 9):
            ws_dash.cell(row=r_idx, column=c_idx).border = thin_border
            
    # Total Row
    ws_dash.cell(row=14, column=2, value="Total Portfolio").font = font_bold
    ws_dash.cell(row=14, column=3, value="=SUM(C11:C13)").number_format = "#,##0"
    ws_dash.cell(row=14, column=4, value="=SUM(D11:D13)").number_format = "#,##0"
    ws_dash.cell(row=14, column=5, value="=D14/C14").number_format = "0.0%"
    ws_dash.cell(row=14, column=6, value="=SUM(F11:F13)").number_format = "$#,##0"
    ws_dash.cell(row=14, column=7, value="=SUM(G11:G13)").number_format = "$#,##0"
    ws_dash.cell(row=14, column=8, value="=G14/F14").number_format = "0.0%"
    for c_idx in range(2, 9):
        ws_dash.cell(row=14, column=c_idx).font = font_bold
        ws_dash.cell(row=14, column=c_idx).border = double_bottom
        ws_dash.cell(row=14, column=c_idx).fill = card_header_fill

    # Strategic Recommendations Block
    ws_dash["B16"] = "STRATEGIC RECOMMENDATIONS & OPERATIONAL INTERVENTIONS"
    ws_dash["B16"].font = font_section
    
    recs = [
        ("1. Early-Tenure Onboarding & White-Glove Support (0-6 Months)", 
         "Survival analysis proves >52% of all churn occurs in the first 6 months. Implement proactive onboarding check-ins and free 90-day technical support setup to eliminate early subscriber attrition."),
        ("2. TechSupport & Security Bundle Attachment Campaign", 
         "Unbundled Fiber Optic accounts experience an 86.5% churn rate. Prescribe automated bundle discounts ($10/mo discount for attaching TechSupport + OnlineSecurity) to lock in account stickiness."),
        ("3. Electronic Check to Automated Payment Migration", 
         "Electronic check accounts exhibit 35%+ churn due to payment friction. Offer a one-time $15 bill credit for customers enrolling in automated credit card or bank transfer payment methods."),
        ("4. High-ROI Contract Migration Engine", 
         "Month-to-month contracts represent $131K+ in lost MRR. Target high-risk deciles with 12-month agreement incentives capped at $35 offer cost, generating a projected 300%+ net ROI.")
    ]
    
    curr_r = 17
    for title, desc in recs:
        ws_dash.cell(row=curr_r, column=2, value=title).font = font_bold
        ws_dash.cell(row=curr_r, column=2).fill = accent_blue_fill
        ws_dash.merge_cells(start_row=curr_r, start_column=2, end_row=curr_r, end_column=8)
        
        ws_dash.cell(row=curr_r+1, column=2, value=desc).font = font_regular
        ws_dash.merge_cells(start_row=curr_r+1, start_column=2, end_row=curr_r+1, end_column=8)
        curr_r += 3

    # =========================================================================
    # TAB 2: RETENTION CAMPAIGN SIMULATOR
    # =========================================================================
    print("[3/4] Assembling Sheet 2: Retention Campaign Simulator & Sheet 3: Sensitivity Matrix...")
    ws_sim = wb.create_sheet(title="Retention Campaign Simulator")
    ws_sim.views.sheetView[0].showGridLines = True
    
    ws_sim.merge_cells("A1:F2")
    ws_sim["A1"] = "INTERACTIVE RETENTION CAMPAIGN SIMULATOR & FINANCIAL MODEL"
    ws_sim["A1"].font = font_title
    ws_sim["A1"].fill = navy_header_fill
    ws_sim["A1"].alignment = Alignment(horizontal="center", vertical="center")
    
    ws_sim["A3"] = "Model calibrated on XGBoost risk deciles and CLV preservation economics"
    ws_sim["A3"].font = font_small
    
    # Input Assumptions Block
    ws_sim["B5"] = "CAMPAIGN INPUT ASSUMPTIONS"
    ws_sim["B5"].font = font_section
    
    assumptions = [
        ("Target High-Risk Customer Population", "=COUNTIF('Customer Cohorts'!M4:M7046, \"High\")", "#,##0", "Total accounts in top ML risk tier", 6),
        ("Campaign Outreach Coverage %", 0.80, "0.0%", "Share of high-risk cohort actively targeted", 7),
        ("Retention Offer Incentive Cost ($)", 35.00, "$#,##0.00", "Cost of retention concession per customer", 8),
        ("Offer Acceptance / Save Rate %", 0.18, "0.0%", "Expected proportion of targeted customers retained", 9),
        ("Average Monthly Revenue per Target ($)", "=AVERAGEIF('Customer Cohorts'!M4:M7046, \"High\", 'Customer Cohorts'!I4:I7046)", "$#,##0.00", "Baseline monthly spend of targeted accounts", 10),
        ("Retained Extension Horizon (Months)", 12, "0", "Average contract duration preserved by campaign", 11)
    ]
    
    for label, val, fmt, note, r in assumptions:
        ws_sim.cell(row=r, column=2, value=label).font = font_bold
        ws_sim.cell(row=r, column=2).border = thin_border
        
        c_val = ws_sim.cell(row=r, column=3, value=val)
        c_val.font = font_bold
        c_val.alignment = Alignment(horizontal="right")
        c_val.number_format = fmt
        c_val.fill = input_gold_fill
        c_val.border = thin_border
        
        ws_sim.cell(row=r, column=4, value=note).font = font_small
        
    # Financial Output Block
    ws_sim["B13"] = "PROJECTED OPERATIONAL & FINANCIAL PERFORMANCE"
    ws_sim["B13"].font = font_section
    
    outputs = [
        ("Total Contacted Accounts", "=ROUND(C6*C7, 0)", "#,##0", "Customers receiving retention offer", 14),
        ("Total Campaign Budget Required", "=C14*C8", "$#,##0.00", "Outreach & incentive marketing expenditure", 15),
        ("Successfully Retained Accounts (Saves)", "=ROUND(C14*C9, 0)", "#,##0", "Customers preserved from churning", 16),
        ("Preserved Customer Lifetime Revenue", "=C16*C10*C11", "$#,##0.00", "Gross revenue protected over horizon", 17),
        ("Gross Profit on Retained Revenue (80%)", "=C17*0.80", "$#,##0.00", "Contribution margin on retained billing", 18),
        ("Net Preserved Campaign Profit", "=C17-C15", "$#,##0.00", "Total preserved revenue minus campaign cost", 19),
        ("Net Incremental Margin", "=C18-C15", "$#,##0.00", "Gross contribution profit minus campaign cost", 20),
        ("Net Campaign ROI %", "=IF(C15=0, 0, C19/C15)", "0.0%", "Net return on marketing capital invested", 21)
    ]
    
    for label, formula, fmt, note, r in outputs:
        ws_sim.cell(row=r, column=2, value=label).font = font_bold
        ws_sim.cell(row=r, column=2).border = thin_border
        
        c_out = ws_sim.cell(row=r, column=3, value=formula)
        c_out.font = font_bold
        c_out.alignment = Alignment(horizontal="right")
        c_out.number_format = fmt
        c_out.fill = output_green_fill
        c_out.border = thin_border
        
        ws_sim.cell(row=r, column=4, value=note).font = font_small
        
    ws_sim.cell(row=21, column=2).border = double_bottom
    ws_sim.cell(row=21, column=3).border = double_bottom
    ws_sim.cell(row=21, column=3).font = font_kpi_num

    # =========================================================================
    # TAB 3: 2-WAY SENSITIVITY MATRIX
    # =========================================================================
    ws_sens = wb.create_sheet(title="2-Way Sensitivity Matrix")
    ws_sens.views.sheetView[0].showGridLines = True
    
    ws_sens.merge_cells("A1:H2")
    ws_sens["A1"] = "2-WAY SENSITIVITY MATRIX: RETENTION CAMPAIGN NET PROFIT ($)"
    ws_sens["A1"].font = font_title
    ws_sens["A1"].fill = navy_header_fill
    ws_sens["A1"].alignment = Alignment(horizontal="center", vertical="center")
    
    ws_sens["A3"] = "Dynamic stress-testing of Net Campaign Profit across Offer Incentive Cost ($) vs Acceptance Save Rate (%)"
    ws_sens["A3"].font = font_small
    
    costs = [20.0, 30.0, 35.0, 50.0, 75.0, 100.0]
    save_rates = [0.10, 0.14, 0.18, 0.22, 0.26, 0.30]
    
    ws_sens["B5"] = "Save Rate % \\ Cost $"
    ws_sens["B5"].font = font_header_w
    ws_sens["B5"].fill = steel_blue_fill
    ws_sens["B5"].alignment = Alignment(horizontal="center", vertical="center")
    ws_sens["B5"].border = thin_border
    
    for c_idx, cost in enumerate(costs, start=3):
        cell = ws_sens.cell(row=5, column=c_idx, value=cost)
        cell.font = font_header_w
        cell.fill = steel_blue_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.number_format = "$#,##0"
        cell.border = thin_border
        
    start_r = 6
    for r_offset, sr in enumerate(save_rates):
        r_num = start_r + r_offset
        c_lbl = ws_sens.cell(row=r_num, column=2, value=sr)
        c_lbl.font = font_bold
        c_lbl.fill = card_header_fill
        c_lbl.alignment = Alignment(horizontal="center", vertical="center")
        c_lbl.number_format = "0.0%"
        c_lbl.border = thin_border
        
        for c_offset, cost in enumerate(costs):
            col_letter = get_column_letter(3 + c_offset)
            c_val = ws_sens.cell(row=r_num, column=3 + c_offset)
            # Formula: (TargetPop * ContactRate * SaveRate) * AvgCharge * Horizon - (TargetPop * ContactRate * Cost)
            c_val.value = f"=('Retention Campaign Simulator'!$C$6 * 'Retention Campaign Simulator'!$C$7 * $B{r_num}) * 'Retention Campaign Simulator'!$C$10 * 'Retention Campaign Simulator'!$C$11 - ('Retention Campaign Simulator'!$C$6 * 'Retention Campaign Simulator'!$C$7 * {col_letter}$5)"
            c_val.font = font_regular
            c_val.alignment = Alignment(horizontal="right")
            c_val.number_format = "$#,##0"
            c_val.border = thin_border
            
    # Add Color Scale Conditional Formatting to Matrix (Green to Red)
    matrix_range = f"C6:H{start_r + len(save_rates) - 1}"
    color_scale = ColorScaleRule(
        start_type='num', start_value=50000, start_color='F8696B', # Soft Red
        mid_type='num', mid_value=300000, mid_color='FFEB84',      # Soft Yellow
        end_type='num', end_value=800000, end_color='63BE7B'       # Soft Green
    )
    ws_sens.conditional_formatting.add(matrix_range, color_scale)

    # =========================================================================
    # TAB 4: COHORT HEATMAP
    # =========================================================================
    ws_heat = wb.create_sheet(title="Cohort Heatmap")
    ws_heat.views.sheetView[0].showGridLines = True
    
    ws_heat.merge_cells("A1:F2")
    ws_heat["A1"] = "TENURE LIFECYCLE VS CONTRACT TYPE ATTRITION HEATMAP"
    ws_heat["A1"].font = font_title
    ws_heat["A1"].fill = navy_header_fill
    ws_heat["A1"].alignment = Alignment(horizontal="center", vertical="center")
    
    ws_heat["A3"] = "Cohort Churn Rate (%) across Tenure Lifecycle Stages and Contract Types"
    ws_heat["A3"].font = font_small
    
    # Headers
    heat_cols = ["Tenure Band", "Lifecycle Stage", "Month-to-month", "One year", "Two year", "Total Cohort"]
    for col_idx, h in enumerate(heat_cols, start=2):
        cell = ws_heat.cell(row=5, column=col_idx, value=h)
        cell.font = font_header_w
        cell.fill = steel_blue_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
        
    bands = [
        ("0-6 Months", "Infant Mortality", 0, 6),
        ("7-12 Months", "Early Adoption", 7, 12),
        ("13-24 Months", "Renewal Window", 13, 24),
        ("25-48 Months", "Established", 25, 48),
        ("49-72 Months", "Mature Loyalist", 49, 72)
    ]
    
    for b_idx, (b_name, b_stage, min_m, max_m) in enumerate(bands, start=6):
        ws_heat.cell(row=b_idx, column=2, value=b_name).font = font_bold
        ws_heat.cell(row=b_idx, column=3, value=b_stage).font = font_small
        
        # Month-to-month Churn %
        ws_heat.cell(row=b_idx, column=4, value=f"=COUNTIFS('Customer Cohorts'!D4:D7046, \">={min_m}\", 'Customer Cohorts'!D4:D7046, \"<={max_m}\", 'Customer Cohorts'!E4:E7046, \"Month-to-month\", 'Customer Cohorts'!K4:K7046, 1) / MAX(1, COUNTIFS('Customer Cohorts'!D4:D7046, \">={min_m}\", 'Customer Cohorts'!D4:D7046, \"<={max_m}\", 'Customer Cohorts'!E4:E7046, \"Month-to-month\"))").number_format = "0.0%"
        # One year Churn %
        ws_heat.cell(row=b_idx, column=5, value=f"=COUNTIFS('Customer Cohorts'!D4:D7046, \">={min_m}\", 'Customer Cohorts'!D4:D7046, \"<={max_m}\", 'Customer Cohorts'!E4:E7046, \"One year\", 'Customer Cohorts'!K4:K7046, 1) / MAX(1, COUNTIFS('Customer Cohorts'!D4:D7046, \">={min_m}\", 'Customer Cohorts'!D4:D7046, \"<={max_m}\", 'Customer Cohorts'!E4:E7046, \"One year\"))").number_format = "0.0%"
        # Two year Churn %
        ws_heat.cell(row=b_idx, column=6, value=f"=COUNTIFS('Customer Cohorts'!D4:D7046, \">={min_m}\", 'Customer Cohorts'!D4:D7046, \"<={max_m}\", 'Customer Cohorts'!E4:E7046, \"Two year\", 'Customer Cohorts'!K4:K7046, 1) / MAX(1, COUNTIFS('Customer Cohorts'!D4:D7046, \">={min_m}\", 'Customer Cohorts'!D4:D7046, \"<={max_m}\", 'Customer Cohorts'!E4:E7046, \"Two year\"))").number_format = "0.0%"
        # Total Cohort Churn %
        ws_heat.cell(row=b_idx, column=7, value=f"=COUNTIFS('Customer Cohorts'!D4:D7046, \">={min_m}\", 'Customer Cohorts'!D4:D7046, \"<={max_m}\", 'Customer Cohorts'!K4:K7046, 1) / MAX(1, COUNTIFS('Customer Cohorts'!D4:D7046, \">={min_m}\", 'Customer Cohorts'!D4:D7046, \"<={max_m}\"))").number_format = "0.0%"
        
        for c_idx in range(2, 8):
            ws_heat.cell(row=b_idx, column=c_idx).border = thin_border
            
    # Add Heatmap 3-color conditional formatting (Green at 0%, Yellow at 25%, Deep Coral at 60%+)
    heat_range = "D6:G10"
    heat_scale = ColorScaleRule(
        start_type='num', start_value=0.0, start_color='63BE7B',  # Green
        mid_type='num', mid_value=0.25, mid_color='FFEB84',       # Yellow
        end_type='num', end_value=0.60, end_color='F8696B'        # Red
    )
    ws_heat.conditional_formatting.add(heat_range, heat_scale)

    # =========================================================================
    # TAB 5: CUSTOMER COHORTS (SCORED DATA)
    # =========================================================================
    print("[4/4] Writing Sheet 5: Customer Cohorts (7,043 scored customer records)...")
    ws_cust = wb.create_sheet(title="Customer Cohorts")
    ws_cust.views.sheetView[0].showGridLines = True
    
    ws_cust.merge_cells("A1:P2")
    ws_cust["A1"] = "INDIVIDUAL CUSTOMER CHURN RISK SCORING & RETENTION DATASET"
    ws_cust["A1"].font = font_title
    ws_cust["A1"].fill = navy_header_fill
    ws_cust["A1"].alignment = Alignment(horizontal="center", vertical="center")
    
    headers_cust = [
        "Customer ID", "Gender", "Senior Citizen", "Tenure Months", "Contract Type",
        "Internet Service", "Tech Support", "Payment Method", "Monthly Charges",
        "Total Charges", "Actual Churn Flag", "Churn Probability", "Risk Tier",
        "Top Churn Driver", "CLV Estimate", "Revenue at Risk"
    ]
    
    for c_idx, h in enumerate(headers_cust, start=1):
        cell = ws_cust.cell(row=3, column=c_idx, value=h)
        cell.font = font_header_w
        cell.fill = steel_blue_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
        
    for r_idx, row in df_scored.iterrows():
        excel_r = r_idx + 4
        ws_cust.cell(row=excel_r, column=1, value=row['customer_id']).font = font_regular
        ws_cust.cell(row=excel_r, column=2, value=row['gender']).font = font_regular
        ws_cust.cell(row=excel_r, column=3, value=int(row['senior_citizen'])).font = font_regular
        ws_cust.cell(row=excel_r, column=4, value=int(row['tenure_months'])).font = font_regular
        ws_cust.cell(row=excel_r, column=5, value=row['contract_type']).font = font_regular
        ws_cust.cell(row=excel_r, column=6, value=row['internet_service']).font = font_regular
        ws_cust.cell(row=excel_r, column=7, value=row['tech_support']).font = font_regular
        ws_cust.cell(row=excel_r, column=8, value=row['payment_method']).font = font_regular
        
        c9 = ws_cust.cell(row=excel_r, column=9, value=float(row['monthly_charges']))
        c9.number_format = "$#,##0.00"
        
        c10 = ws_cust.cell(row=excel_r, column=10, value=float(row['total_charges']))
        c10.number_format = "$#,##0.00"
        
        ws_cust.cell(row=excel_r, column=11, value=int(row['churn_actual'])).font = font_regular
        
        # Use model predicted probability if available, else churn_probability
        prob_val = float(row.get('model_predicted_prob', row['churn_probability']))
        c12 = ws_cust.cell(row=excel_r, column=12, value=prob_val)
        c12.number_format = "0.0%"
        
        risk_val = row.get('model_risk_tier', row['risk_tier'])
        ws_cust.cell(row=excel_r, column=13, value=str(risk_val)).font = font_bold
        
        ws_cust.cell(row=excel_r, column=14, value=str(row['top_churn_driver'])).font = font_regular
        
        c15 = ws_cust.cell(row=excel_r, column=15, value=float(row['clv_estimate']))
        c15.number_format = "$#,##0.00"
        
        c16 = ws_cust.cell(row=excel_r, column=16, value=float(row['revenue_at_risk']))
        c16.number_format = "$#,##0.00"
        
        # Zebra striping
        if excel_r % 2 == 0:
            for c in range(1, 17):
                ws_cust.cell(row=excel_r, column=c).fill = zebra_light_fill
                
    # Auto-adjust column widths across all sheets
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col[:40]: # check top 40 rows
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
    # Save primary and alias files
    file_primary = os.path.join(excel_dir, "Telecom_Customer_Retention_Simulator.xlsx")
    file_alias   = os.path.join(excel_dir, "05_Telecom_Churn_Retention_Model.xlsx")
    
    wb.save(file_primary)
    wb.save(file_alias)
    print(f"\n[SUCCESS] Saved Excel models:")
    print(f"          - {file_primary}")
    print(f"          - {file_alias}")

if __name__ == '__main__':
    build_retention_simulator()
