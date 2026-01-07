# Shrinkage Analysis & Transfer Optimization Engine

This project provides a comprehensive data engineering and analysis pipeline for detecting inventory shrinkage and optimizing inter-site transfers. It is designed to integrate seamlessly with n8n workflows for automated reporting and alerts.

## 🚀 Key Features

- **Automated Shrinkage Detection**: Logic to cross-reference sales, start inventory, and end inventory across 200+ locations.
- **Waste & Spoilage Analysis**: Integrates "Known Adjustments" to isolate actual shrinkage from recorded spoilage.
- **Product Name Enrichment**: A master-dictionary system that translates internal product IDs (AVR/PC) into human-readable descriptive names.
- **Transfer Optimization**: ROI-based logic to suggest inventory rebalancing routes between high-stock and high-sales locations.
- **n8n Integration Ready**: Outputs a consolidated, minified JSON report structured for automation nodes.

## 📂 Primary Output

The core intelligence of the project is contained in:
- `n8n_consolidated_report_final_fixed.json`: The master report containing site rankings, shrinkage insights, and transfer recommendations.

## 🛠 Project Structure

- `shrinkage_detector_v2.py`: The core analysis engine.
- `add_transfer_optimization.py`: Calculates ROI and generates transfer routes.
- `n8n_questions.json`: Configuration for the analyst engine.

## 📈 Dashboard Insights

The report provides the following key insights:
1. **Critical Sites**: Top sites by shrinkage value needing immediate audit.
2. **Top Items**: Specific products contributing most to network-wide loss.
3. **Staff Risk**: Analysis of shrinkage patterns mapped to user audit logs.
4. **Par Recommendations**: Optimized stocking levels to reduce future waste.

---

*Generated for Ultraserv Automated Services Analysis System.*
