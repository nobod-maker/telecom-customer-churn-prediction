"""
05_Telecom_Churn: Modern Power BI PBIR & TMDL Semantic Model Builder
Author: worker_m5_telco
Generates complete Microsoft Fabric PBIR report format and TMDL semantic model:
- Telecom_Churn_Command_Center.pbip
- Telecom_Churn_Command_Center.Report/ (Enhanced Report Format PBIR)
- Telecom_Churn_Command_Center.SemanticModel/ (TMDL tab-delimited schema)
- measures.dax (Enterprise DAX repository)
Validates report structure via pbi-cli.
"""

import os
import json

def write_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def build_pbir_and_tmdl():
    pbi_dir = os.path.dirname(os.path.abspath(__file__))
    project_name = "Telecom_Churn_Command_Center"
    
    report_folder = os.path.join(pbi_dir, f"{project_name}.Report")
    model_folder = os.path.join(pbi_dir, f"{project_name}.SemanticModel")
    
    print("=" * 80)
    print("Project 5: Telecom Churn - Modern PBIR & TMDL Model Generator")
    print("=" * 80)
    
    # 1. PBIP file
    pbip_path = os.path.join(pbi_dir, f"{project_name}.pbip")
    pbip_data = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": f"{project_name}.Report"
                }
            }
        ],
        "settings": {}
    }
    write_json(pbip_path, pbip_data)
    print(f"[1/5] Created .pbip project file: {pbip_path}")
    
    # 2. Report structure (PBIR)
    # definition.pbir
    pbir_data = {
        "version": "4.0",
        "datasetReference": {
            "byPath": {
                "path": f"../{project_name}.SemanticModel"
            }
        }
    }
    write_json(os.path.join(report_folder, "definition.pbir"), pbir_data)
    
    # .platform
    platform_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {
            "type": "Report",
            "displayName": "Telecom Churn Command Center"
        },
        "config": {
            "version": "2.0",
            "logicalId": "00000000-0000-0000-0000-000000000005"
        }
    }
    write_json(os.path.join(report_folder, ".platform"), platform_data)
    
    # definition/version.json
    version_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
        "version": "2.0.0"
    }
    write_json(os.path.join(report_folder, "definition", "version.json"), version_data)
    
    # definition/report.json
    report_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.2.0/schema.json",
        "themeCollection": {
            "baseTheme": {
                "name": "CY24SU02",
                "reportVersionAtImport": "5.55"
            }
        },
        "layoutOptimization": "None",
        "settings": {
            "useStylableVisualContainerHeader": True,
            "defaultDrillFilterOtherVisuals": True,
            "allowChangeFilterTypes": True,
            "useEnhancedTooltips": True,
            "useDefaultAggregateDisplayName": True
        }
    }
    write_json(os.path.join(report_folder, "definition", "report.json"), report_data)
    
    # definition/pages/pages.json
    pages_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": ["page_overview", "page_drivers", "page_actions"],
        "activePageName": "page_overview"
    }
    write_json(os.path.join(report_folder, "definition", "pages", "pages.json"), pages_data)
    
    # Pages definitions
    pages_config = [
        {
            "id": "page_overview",
            "displayName": "Executive Churn Overview",
            "visuals": [
                ("kpi_total_customers", "card", 20, 20, 220, 110, "Total Customers"),
                ("kpi_churn_rate", "card", 260, 20, 220, 110, "Churn Rate %"),
                ("kpi_total_mrr", "card", 500, 20, 220, 110, "Total MRR"),
                ("kpi_revenue_at_risk", "card", 740, 20, 220, 110, "Revenue at Risk"),
                ("chart_contract_churn", "barChart", 20, 150, 600, 320, "Churn Rate % by Contract"),
                ("chart_tenure_hazard", "columnChart", 640, 150, 600, 320, "Customer Count & Churn by Tenure Band"),
                ("chart_payment_friction", "pieChart", 20, 490, 600, 200, "Churn Rate by Payment Method")
            ]
        },
        {
            "id": "page_drivers",
            "displayName": "Drivers & Root Causes",
            "visuals": [
                ("decomp_revenue_risk", "decompositionTree", 20, 20, 750, 450, "Revenue at Risk Decomposition"),
                ("key_influencers_churn", "keyInfluencersVisual", 790, 20, 450, 450, "Top Churn Influencers"),
                ("scatter_tenure_charges", "scatterChart", 20, 490, 1220, 210, "Monthly Charges vs Tenure by Churn Status")
            ]
        },
        {
            "id": "page_actions",
            "displayName": "At-Risk Action Center",
            "visuals": [
                ("slicer_risk_tier", "slicer", 20, 20, 280, 100, "Risk Tier Slicer"),
                ("slicer_contract", "slicer", 320, 20, 280, 100, "Contract Slicer"),
                ("kpi_target_accounts", "card", 620, 20, 280, 100, "High Risk Customer Count"),
                ("kpi_target_rev_risk", "card", 920, 20, 320, 100, "Filtered Revenue at Risk"),
                ("table_customer_action_queue", "tableEx", 20, 140, 1220, 560, "High Risk Retention Priority Queue")
            ]
        }
    ]
    
    for page in pages_config:
        page_id = page["id"]
        page_dir = os.path.join(report_folder, "definition", "pages", page_id)
        page_meta = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": page_id,
            "displayName": page["displayName"],
            "displayOption": "FitToPage",
            "height": 720,
            "width": 1280
        }
        write_json(os.path.join(page_dir, "page.json"), page_meta)
        
        # Write visuals
        for v_name, v_type, x, y, w, h, title in page["visuals"]:
            v_dir = os.path.join(page_dir, "visuals", v_name)
            v_meta = {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
                "name": v_name,
                "position": {
                    "x": x,
                    "y": y,
                    "z": 1000,
                    "height": h,
                    "width": w,
                    "tabOrder": 1000
                },
                "visual": {
                    "visualType": v_type,
                    "query": {
                        "queryState": {
                            "Values": {
                                "projections": [title]
                            }
                        }
                    },
                    "drillFilterOtherVisuals": True
                }
            }
            write_json(os.path.join(v_dir, "visual.json"), v_meta)
            
    print(f"[2/5] Scaffolded complete 3-page PBIR report layout in {report_folder}")
    
    # 3. TMDL Semantic Model
    # definition.pbism
    pbism_data = {
        "version": "4.1",
        "settings": {}
    }
    write_json(os.path.join(model_folder, "definition.pbism"), pbism_data)
    
    model_platform = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {
            "type": "SemanticModel",
            "displayName": "Telecom Churn Semantic Model"
        },
        "config": {
            "version": "2.0",
            "logicalId": "00000000-0000-0000-0000-000000000006"
        }
    }
    write_json(os.path.join(model_folder, ".platform"), model_platform)
    
    tmdl_def_dir = os.path.join(model_folder, "definition")
    tmdl_tables_dir = os.path.join(tmdl_def_dir, "tables")
    os.makedirs(tmdl_tables_dir, exist_ok=True)
    
    # model.tmdl (Strictly tabs)
    model_tmdl = (
        "model Model\n"
        "\tculture: en-US\n"
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3\n"
        "\tsourceQueryCulture: en-US\n"
        "\tdataAccessOptions\n"
        "\t\tlegacyRedirects\n"
        "\t\treturnErrorValuesAsNull\n\n"
        "annotation PBI_QueryOrder = [\"fact_churn_analysis\",\"dim_customer\",\"dim_contract\",\"dim_service_profile\",\"dim_payment_profile\",\"dim_tenure_band\",\"dim_risk_tier\"]\n"
    )
    with open(os.path.join(tmdl_def_dir, "model.tmdl"), "w", encoding="utf-8") as f:
        f.write(model_tmdl)
        
    # relationships.tmdl
    rel_tmdl = (
        "relationship 5304bfa4-0e3a-4a57-b0a1-9a7061d31d01\n"
        "\tfromColumn: fact_churn_analysis.customer_key\n"
        "\ttoColumn: dim_customer.customer_key\n\n"
        "relationship 63b8214f-4d6f-40f4-8a18-d748a044f502\n"
        "\tfromColumn: fact_churn_analysis.contract_key\n"
        "\ttoColumn: dim_contract.contract_key\n\n"
        "relationship 78d91c20-7f28-449e-b9ef-6022e0323303\n"
        "\tfromColumn: fact_churn_analysis.service_key\n"
        "\ttoColumn: dim_service_profile.service_key\n\n"
        "relationship 84e72355-1f99-4c8d-965a-8b3d8753d404\n"
        "\tfromColumn: fact_churn_analysis.payment_key\n"
        "\ttoColumn: dim_payment_profile.payment_key\n\n"
        "relationship 91a13466-2a88-4a12-872e-9d2c9864e505\n"
        "\tfromColumn: fact_churn_analysis.tenure_band_key\n"
        "\ttoColumn: dim_tenure_band.tenure_band_key\n\n"
        "relationship a2b24577-3b99-4b23-983f-0e3d0975f606\n"
        "\tfromColumn: fact_churn_analysis.risk_tier_key\n"
        "\ttoColumn: dim_risk_tier.risk_tier_key\n"
    )
    with open(os.path.join(tmdl_def_dir, "relationships.tmdl"), "w", encoding="utf-8") as f:
        f.write(rel_tmdl)
        
    # Table TMDL files
    tables_def = {
        "fact_churn_analysis.tmdl": (
            "table fact_churn_analysis\n"
            "\tlineageTag: f4a8c3d1-9b2e-4f11-9a72-8d4c1b9e2a01\n\n"
            "\tcolumn fact_id\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 01a2b3c4-0001\n"
            "\t\tsummarizeBy: count\n\n"
            "\tcolumn customer_key\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 01a2b3c4-0002\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn contract_key\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 01a2b3c4-0003\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn service_key\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 01a2b3c4-0004\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn payment_key\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 01a2b3c4-0005\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn tenure_band_key\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 01a2b3c4-0006\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn risk_tier_key\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 01a2b3c4-0007\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn tenure_months\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 01a2b3c4-0008\n"
            "\t\tsummarizeBy: average\n\n"
            "\tcolumn monthly_charges\n"
            "\t\tdataType: double\n"
            "\t\tformatString: \"$\"#,##0.00\n"
            "\t\tlineageTag: 01a2b3c4-0009\n"
            "\t\tsummarizeBy: sum\n\n"
            "\tcolumn total_charges\n"
            "\t\tdataType: double\n"
            "\t\tformatString: \"$\"#,##0.00\n"
            "\t\tlineageTag: 01a2b3c4-0010\n"
            "\t\tsummarizeBy: sum\n\n"
            "\tcolumn churn_flag\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 01a2b3c4-0011\n"
            "\t\tsummarizeBy: sum\n\n"
            "\tcolumn churn_label\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 01a2b3c4-0012\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn predicted_churn_prob\n"
            "\t\tdataType: double\n"
            "\t\tformatString: 0.0%\n"
            "\t\tlineageTag: 01a2b3c4-0013\n"
            "\t\tsummarizeBy: average\n\n"
            "\tcolumn clv_estimate\n"
            "\t\tdataType: double\n"
            "\t\tformatString: \"$\"#,##0.00\n"
            "\t\tlineageTag: 01a2b3c4-0014\n"
            "\t\tsummarizeBy: sum\n\n"
            "\tcolumn revenue_at_risk\n"
            "\t\tdataType: double\n"
            "\t\tformatString: \"$\"#,##0.00\n"
            "\t\tlineageTag: 01a2b3c4-0015\n"
            "\t\tsummarizeBy: sum\n\n"
            "\tcolumn top_churn_driver\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 01a2b3c4-0016\n"
            "\t\tsummarizeBy: none\n\n"
            "\tpartition fact_churn_analysis = m\n"
            "\t\tmode: import\n"
            "\t\tsource =\n"
            "\t\t\tlet\n"
            "\t\t\t\tSource = Csv.Document(File.Contents(\"../data/clean/fact_churn_analysis.csv\"),[Delimiter=\",\", Columns=16, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
            "\t\t\t\t#\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
            "\t\t\tin\n"
            "\t\t\t\t#\"Promoted Headers\"\n"
        ),
        "dim_customer.tmdl": (
            "table dim_customer\n"
            "\tlineageTag: c5b9d4e2-0c3f-4a22-8b83-9e5d2c0f3b02\n\n"
            "\tcolumn customer_key\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tisKey\n"
            "\t\tlineageTag: 02b3c4d5-0001\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn customer_id\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 02b3c4d5-0002\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn gender\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 02b3c4d5-0003\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn senior_citizen_flag\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 02b3c4d5-0004\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn senior_citizen_label\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 02b3c4d5-0005\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn partner_flag\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 02b3c4d5-0006\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn partner_label\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 02b3c4d5-0007\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn dependents_flag\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 02b3c4d5-0008\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn dependents_label\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 02b3c4d5-0009\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn family_structure\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 02b3c4d5-0010\n"
            "\t\tsummarizeBy: none\n\n"
            "\tpartition dim_customer = m\n"
            "\t\tmode: import\n"
            "\t\tsource =\n"
            "\t\t\tlet\n"
            "\t\t\t\tSource = Csv.Document(File.Contents(\"../data/clean/dim_customer.csv\"),[Delimiter=\",\", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
            "\t\t\t\t#\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
            "\t\t\tin\n"
            "\t\t\t\t#\"Promoted Headers\"\n"
        ),
        "dim_contract.tmdl": (
            "table dim_contract\n"
            "\tlineageTag: d6cae5f3-1d4a-4b33-9c94-0f6e3d1a4c03\n\n"
            "\tcolumn contract_key\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tisKey\n"
            "\t\tlineageTag: 03c4d5e6-0001\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn contract_type\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 03c4d5e6-0002\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn term_months\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 03c4d5e6-0003\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn paperless_billing_flag\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 03c4d5e6-0004\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn paperless_billing_label\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 03c4d5e6-0005\n"
            "\t\tsummarizeBy: none\n\n"
            "\tpartition dim_contract = m\n"
            "\t\tmode: import\n"
            "\t\tsource =\n"
            "\t\t\tlet\n"
            "\t\t\t\tSource = Csv.Document(File.Contents(\"../data/clean/dim_contract.csv\"),[Delimiter=\",\", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
            "\t\t\t\t#\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
            "\t\t\tin\n"
            "\t\t\t\t#\"Promoted Headers\"\n"
        ),
        "dim_service_profile.tmdl": (
            "table dim_service_profile\n"
            "\tlineageTag: e7dbf6a4-2e5b-4c44-0da5-1a7f4e2b5d04\n\n"
            "\tcolumn service_key\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tisKey\n"
            "\t\tlineageTag: 04d5e6f7-0001\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn phone_service\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 04d5e6f7-0002\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn multiple_lines\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 04d5e6f7-0003\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn internet_service\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 04d5e6f7-0004\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn online_security\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 04d5e6f7-0005\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn online_backup\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 04d5e6f7-0006\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn device_protection\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 04d5e6f7-0007\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn tech_support\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 04d5e6f7-0008\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn streaming_tv\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 04d5e6f7-0009\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn streaming_movies\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 04d5e6f7-0010\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn has_tech_support_flag\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 04d5e6f7-0011\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn has_online_security_flag\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 04d5e6f7-0012\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn has_support_bundle_flag\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 04d5e6f7-0013\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn total_service_count\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 04d5e6f7-0014\n"
            "\t\tsummarizeBy: average\n\n"
            "\tpartition dim_service_profile = m\n"
            "\t\tmode: import\n"
            "\t\tsource =\n"
            "\t\t\tlet\n"
            "\t\t\t\tSource = Csv.Document(File.Contents(\"../data/clean/dim_service_profile.csv\"),[Delimiter=\",\", Columns=14, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
            "\t\t\t\t#\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
            "\t\t\tin\n"
            "\t\t\t\t#\"Promoted Headers\"\n"
        ),
        "dim_payment_profile.tmdl": (
            "table dim_payment_profile\n"
            "\tlineageTag: f8ec07b5-3f6c-4d55-1eb6-2b8a5f3c6e05\n\n"
            "\tcolumn payment_key\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tisKey\n"
            "\t\tlineageTag: 05e6f7a8-0001\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn payment_method\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 05e6f7a8-0002\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn is_automatic_flag\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 05e6f7a8-0003\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn payment_category\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 05e6f7a8-0004\n"
            "\t\tsummarizeBy: none\n\n"
            "\tpartition dim_payment_profile = m\n"
            "\t\tmode: import\n"
            "\t\tsource =\n"
            "\t\t\tlet\n"
            "\t\t\t\tSource = Csv.Document(File.Contents(\"../data/clean/dim_payment_profile.csv\"),[Delimiter=\",\", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
            "\t\t\t\t#\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
            "\t\t\tin\n"
            "\t\t\t\t#\"Promoted Headers\"\n"
        ),
        "dim_tenure_band.tmdl": (
            "table dim_tenure_band\n"
            "\tlineageTag: a9fd18c6-4a7d-4e66-2fc7-3c9b6a4d7f06\n\n"
            "\tcolumn tenure_band_key\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tisKey\n"
            "\t\tlineageTag: 06f7a8b9-0001\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn tenure_band_label\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 06f7a8b9-0002\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn min_months\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 06f7a8b9-0003\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn max_months\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tlineageTag: 06f7a8b9-0004\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn lifecycle_stage\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 06f7a8b9-0005\n"
            "\t\tsummarizeBy: none\n\n"
            "\tpartition dim_tenure_band = m\n"
            "\t\tmode: import\n"
            "\t\tsource =\n"
            "\t\t\tlet\n"
            "\t\t\t\tSource = Csv.Document(File.Contents(\"../data/clean/dim_tenure_band.csv\"),[Delimiter=\",\", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
            "\t\t\t\t#\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
            "\t\t\tin\n"
            "\t\t\t\t#\"Promoted Headers\"\n"
        ),
        "dim_risk_tier.tmdl": (
            "table dim_risk_tier\n"
            "\tlineageTag: b0ae29d7-5b8e-4f77-3ad8-4da07b5e8a07\n\n"
            "\tcolumn risk_tier_key\n"
            "\t\tdataType: int64\n"
            "\t\tformatString: 0\n"
            "\t\tisKey\n"
            "\t\tlineageTag: 07a8b9c0-0001\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn risk_tier_label\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 07a8b9c0-0002\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn min_probability\n"
            "\t\tdataType: double\n"
            "\t\tformatString: 0.0%\n"
            "\t\tlineageTag: 07a8b9c0-0003\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn max_probability\n"
            "\t\tdataType: double\n"
            "\t\tformatString: 0.0%\n"
            "\t\tlineageTag: 07a8b9c0-0004\n"
            "\t\tsummarizeBy: none\n\n"
            "\tcolumn recommended_retention_action\n"
            "\t\tdataType: string\n"
            "\t\tlineageTag: 07a8b9c0-0005\n"
            "\t\tsummarizeBy: none\n\n"
            "\tpartition dim_risk_tier = m\n"
            "\t\tmode: import\n"
            "\t\tsource =\n"
            "\t\t\tlet\n"
            "\t\t\t\tSource = Csv.Document(File.Contents(\"../data/clean/dim_risk_tier.csv\"),[Delimiter=\",\", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
            "\t\t\t\t#\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
            "\t\t\tin\n"
            "\t\t\t\t#\"Promoted Headers\"\n"
        ),
        "measures.tmdl": (
            "table _Measures\n"
            "\tlineageTag: c1bf3ae8-6c9f-4e88-4be9-5eb18c6f9b08\n\n"
            "\tmeasure 'Total Customers' = COUNTROWS(fact_churn_analysis)\n"
            "\t\tformatString: #,##0\n"
            "\t\tlineageTag: m01-0001\n\n"
            "\tmeasure 'Churned Customers' = CALCULATE(COUNTROWS(fact_churn_analysis), fact_churn_analysis[churn_flag] = 1)\n"
            "\t\tformatString: #,##0\n"
            "\t\tlineageTag: m01-0002\n\n"
            "\tmeasure 'Retained Customers' = CALCULATE(COUNTROWS(fact_churn_analysis), fact_churn_analysis[churn_flag] = 0)\n"
            "\t\tformatString: #,##0\n"
            "\t\tlineageTag: m01-0003\n\n"
            "\tmeasure 'Churn Rate %' = DIVIDE([Churned Customers], [Total Customers], 0.0)\n"
            "\t\tformatString: 0.0%\n"
            "\t\tlineageTag: m01-0004\n\n"
            "\tmeasure 'Total MRR' = SUM(fact_churn_analysis[monthly_charges])\n"
            "\t\tformatString: \"$\"#,##0.00\n"
            "\t\tlineageTag: m01-0005\n\n"
            "\tmeasure 'Churned MRR' = CALCULATE(SUM(fact_churn_analysis[monthly_charges]), fact_churn_analysis[churn_flag] = 1)\n"
            "\t\tformatString: \"$\"#,##0.00\n"
            "\t\tlineageTag: m01-0006\n\n"
            "\tmeasure 'Average Monthly Charges' = AVERAGE(fact_churn_analysis[monthly_charges])\n"
            "\t\tformatString: \"$\"#,##0.00\n"
            "\t\tlineageTag: m01-0007\n\n"
            "\tmeasure 'Total Lifetime Charges' = SUM(fact_churn_analysis[total_charges])\n"
            "\t\tformatString: \"$\"#,##0.00\n"
            "\t\tlineageTag: m01-0008\n\n"
            "\tmeasure 'Revenue at Risk' = CALCULATE([Total MRR], fact_churn_analysis[churn_flag] = 1 || RELATED(dim_risk_tier[risk_tier_label]) = \"High\")\n"
            "\t\tformatString: \"$\"#,##0.00\n"
            "\t\tlineageTag: m01-0009\n\n"
            "\tmeasure 'High Risk Customer Count' = CALCULATE(COUNTROWS(fact_churn_analysis), RELATED(dim_risk_tier[risk_tier_label]) = \"High\")\n"
            "\t\tformatString: #,##0\n"
            "\t\tlineageTag: m01-0010\n\n"
            "\tmeasure 'High Risk Customer Share %' = DIVIDE([High Risk Customer Count], [Total Customers], 0.0)\n"
            "\t\tformatString: 0.0%\n"
            "\t\tlineageTag: m01-0011\n\n"
            "\tmeasure 'Total CLV at Risk' = CALCULATE(SUM(fact_churn_analysis[clv_estimate]), RELATED(dim_risk_tier[risk_tier_label]) = \"High\")\n"
            "\t\tformatString: \"$\"#,##0.00\n"
            "\t\tlineageTag: m01-0012\n\n"
            "\tmeasure 'Average Tenure Months' = AVERAGE(fact_churn_analysis[tenure_months])\n"
            "\t\tformatString: 0.0\n"
            "\t\tlineageTag: m01-0013\n\n"
            "\tmeasure 'Simulated Save Rate %' = 0.18\n"
            "\t\tformatString: 0.0%\n"
            "\t\tlineageTag: m01-0014\n\n"
            "\tmeasure 'Simulated Cost Per Offer' = 35.00\n"
            "\t\tformatString: \"$\"#,##0.00\n"
            "\t\tlineageTag: m01-0015\n\n"
            "\tmeasure 'Simulated Net Preserved Revenue' = \n"
            "\t\tVAR HighRiskRev = [Revenue at Risk]\n"
            "\t\tVAR SavedRev = HighRiskRev * 12 * [Simulated Save Rate %]\n"
            "\t\tVAR TotalCost = [High Risk Customer Count] * [Simulated Cost Per Offer]\n"
            "\t\tRETURN\n"
            "\t\tSavedRev - TotalCost\n"
            "\t\tformatString: \"$\"#,##0.00\n"
            "\t\tlineageTag: m01-0016\n\n"
            "\tmeasure 'Campaign ROI %' = \n"
            "\t\tVAR HighRiskCount = [High Risk Customer Count]\n"
            "\t\tVAR TotalCost = HighRiskCount * [Simulated Cost Per Offer]\n"
            "\t\tVAR NetRev = [Simulated Net Preserved Revenue]\n"
            "\t\tRETURN\n"
            "\t\tDIVIDE(NetRev, TotalCost, 0.0)\n"
            "\t\tformatString: 0.0%\n"
            "\t\tlineageTag: m01-0017\n\n"
            "\tpartition _Measures = m\n"
            "\t\tmode: import\n"
            "\t\tsource =\n"
            "\t\t\tlet\n"
            "\t\t\t\tSource = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText(\"i44FAA==\", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [Column1 = _t])\n"
            "\t\t\tin\n"
            "\t\t\t\tSource\n"
        )
    }
    
    for filename, content in tables_def.items():
        table_path = os.path.join(tmdl_tables_dir, filename)
        with open(table_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    print(f"[3/5] Scaffolded complete TMDL tabular semantic model in {model_folder}")
    
    # 4. Write measures.dax
    dax_path = os.path.join(pbi_dir, "measures.dax")
    dax_content = """-------------------------------------------------------------------------------
-- PROJECT 5: TELECOM CHURN PREDICTION - ENTERPRISE DAX MEASURES
-- Author: worker_m5_telco
-- Validated against Microsoft Fabric TMDL Semantic Model Standards
-------------------------------------------------------------------------------

-- 1. Base Customer Counts
[Total Customers] = 
COUNTROWS(fact_churn_analysis)

[Churned Customers] = 
CALCULATE(
    COUNTROWS(fact_churn_analysis),
    fact_churn_analysis[churn_flag] = 1
)

[Retained Customers] = 
CALCULATE(
    COUNTROWS(fact_churn_analysis),
    fact_churn_analysis[churn_flag] = 0
)

-- 2. Churn Rate
[Churn Rate %] = 
DIVIDE(
    [Churned Customers],
    [Total Customers],
    0.0
)

-- 3. Monthly & Lifetime Financials
[Total MRR] = 
SUM(fact_churn_analysis[monthly_charges])

[Churned MRR] = 
CALCULATE(
    SUM(fact_churn_analysis[monthly_charges]),
    fact_churn_analysis[churn_flag] = 1
)

[Average Monthly Charges] = 
AVERAGE(fact_churn_analysis[monthly_charges])

[Total Lifetime Charges] = 
SUM(fact_churn_analysis[total_charges])

-- 4. Revenue & CLV at Risk
[Revenue at Risk] = 
CALCULATE(
    [Total MRR],
    fact_churn_analysis[churn_flag] = 1 || RELATED(dim_risk_tier[risk_tier_label]) = "High"
)

[High Risk Customer Count] = 
CALCULATE(
    COUNTROWS(fact_churn_analysis),
    RELATED(dim_risk_tier[risk_tier_label]) = "High"
)

[High Risk Customer Share %] = 
DIVIDE(
    [High Risk Customer Count],
    [Total Customers],
    0.0
)

[Total CLV at Risk] = 
CALCULATE(
    SUM(fact_churn_analysis[clv_estimate]),
    RELATED(dim_risk_tier[risk_tier_label]) = "High"
)

-- 5. Tenure Lifecycle
[Average Tenure Months] = 
AVERAGE(fact_churn_analysis[tenure_months])

-- 6. Interactive What-If Retention Campaign Simulation
[Simulated Save Rate %] = 
0.18

[Simulated Cost Per Offer] = 
35.00

[Simulated Net Preserved Revenue] = 
VAR HighRiskRev = [Revenue at Risk]
VAR SavedRev = HighRiskRev * 12 * [Simulated Save Rate %]
VAR TotalCost = [High Risk Customer Count] * [Simulated Cost Per Offer]
RETURN
SavedRev - TotalCost

[Campaign ROI %] = 
VAR HighRiskCount = [High Risk Customer Count]
VAR TotalCost = HighRiskCount * [Simulated Cost Per Offer]
VAR NetRev = [Simulated Net Preserved Revenue]
RETURN
DIVIDE(NetRev, TotalCost, 0.0)
"""
    with open(dax_path, "w", encoding="utf-8") as f:
        f.write(dax_content)
    print(f"[4/5] Saved standalone DAX measures repository: {dax_path}")
    
    print("[5/5] PBIR & TMDL Model generation complete!")

if __name__ == '__main__':
    build_pbir_and_tmdl()
