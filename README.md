# Dota 2 Pro Match Analysis & TI14 Predictions

A comprehensive data science project analyzing professional Dota 2 matches to predict outcomes for The International 14 (TI14).

## 🎯 Project Goals

- **Data Collection**: Gather pro match data from various tournaments
- **Player/Team Modeling**: Create comprehensive player and team profiles
- **Rating Systems**: Implement ELO and other ranking algorithms
- **Predictive Models**: Build ML models to predict match outcomes
- **TI14 Analysis**: Apply insights to predict TI14 results

## 📚 Learning Objectives

This project covers key data science concepts:
- Data scraping and cleaning
- Feature engineering
- Time series analysis
- Machine learning (classification, regression)
- Statistical modeling
- Data visualization
- Model evaluation and validation

## 🏗️ Project Structure

```
dota_ds/
├── data/                   # Raw and processed data
├── src/                    # Source code
│   ├── data_collection/    # Data scraping modules
│   ├── models/            # Data models and schemas
│   ├── features/          # Feature engineering
│   ├── ml/                # Machine learning models
│   └── analysis/          # Analysis and visualization
├── notebooks/             # Jupyter notebooks for exploration
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
└── config/               # Configuration files
```

## 🚀 Getting Started

1. **Clone and setup:**
   ```bash
   git clone <your-repo-url>
   cd dota_ds
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up OpenDota API key (recommended):**
   ```bash
   python3 setup_api_key.py
   ```
   - Go to [OpenDota](https://www.opendota.com/)
   - Sign in with your Steam account
   - Generate an API key in your profile settings
   - Run the setup script and enter your key

3. **Run the project:**
   ```bash
   python3 main.py
   ```

4. **Explore data in notebooks**
5. **Train models and make predictions**

## 📊 Data Sources

- OpenDota API
- Liquipedia (tournament data)
- Team Liquid (match results)
- Official Dota 2 tournament APIs

## 🔮 What We'll Build

- **Player Rating System**: ELO-based player rankings
- **Team Performance Models**: Historical performance analysis
- **Match Prediction Engine**: ML models for outcome prediction
- **Tournament Analysis**: Meta analysis and trends
- **TI14 Predictions**: Final predictions and insights

## 🎓 Skills You'll Practice

- Python programming
- Data manipulation (pandas, numpy)
- Machine learning (scikit-learn)
- Data visualization (matplotlib, seaborn)
- Statistical analysis
- API integration
- Database design
- Model deployment

Ready to dive into the world of Dota 2 data science? Let's start building! 🎮📈
