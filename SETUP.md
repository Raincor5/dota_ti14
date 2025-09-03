# Dota 2 Data Science Project - Setup Guide

This guide will help you set up and run the Dota 2 data science project for predicting TI14 outcomes.

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### 2. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd dota_ds

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Get OpenDota API Key (Optional but Recommended)

1. Visit [OpenDota](https://www.opendota.com/)
2. Sign up for an account
3. Go to your profile settings
4. Generate an API key
5. Set environment variable:

```bash
# On Windows:
set OPENDOTA_API_KEY=your_api_key_here

# On macOS/Linux:
export OPENDOTA_API_KEY=your_api_key_here
```

## 📊 Running the Project

### Option 1: Run Main Script

```bash
# Run the main project script
python src/main.py
```

This will:
- Initialize the data collector
- Collect recent pro match data (if none exists)
- Demonstrate the ELO rating system
- Show project summary

### Option 2: Run Data Collection Only

```bash
# Run data collection
python src/data_collection/main.py
```

### Option 3: Run ELO Demo

```bash
# Run ELO system demonstration
python examples/elo_demo.py
```

## 🔧 Project Structure

```
dota_ds/
├── src/                    # Source code
│   ├── models/            # Data models (Player, Team, Match, Tournament)
│   ├── features/          # Feature engineering (ELO system, etc.)
│   ├── data_collection/   # Data collection modules
│   └── ml/                # Machine learning models (future)
├── data/                  # Data storage
│   ├── raw/               # Raw collected data
│   ├── processed/         # Processed CSV files
│   └── models/            # Trained ML models (future)
├── notebooks/             # Jupyter notebooks for analysis
├── examples/              # Example scripts
├── config/                # Configuration files
├── tests/                 # Unit tests
└── requirements.txt       # Python dependencies
```

## 📈 What You'll Learn

This project covers essential data science concepts:

### 1. **Data Collection & APIs**
- Working with REST APIs (OpenDota)
- Rate limiting and error handling
- Data validation and cleaning

### 2. **Data Modeling**
- Object-oriented design
- Data structures and relationships
- Serialization and persistence

### 3. **Feature Engineering**
- ELO rating systems
- Performance metrics calculation
- Time series analysis

### 4. **Machine Learning Preparation**
- Feature extraction
- Data preprocessing
- Model evaluation metrics

### 5. **Real-world Application**
- Sports analytics
- Predictive modeling
- Tournament analysis

## 🎯 Key Features

### ELO Rating System
- **Dynamic K-factor** based on player experience and match importance
- **Rating decay** for inactive players/teams
- **Tournament weighting** (TI matches count more than qualifiers)
- **Confidence scoring** for predictions

### Data Models
- **Player**: Individual performance tracking, hero preferences, role analysis
- **Team**: Roster management, composition analysis, strength assessment
- **Match**: Detailed game statistics, meta analysis, outcome prediction
- **Tournament**: Bracket tracking, standings calculation, meta trends

### Data Collection
- **OpenDota API integration** for pro match data
- **Rate limiting** to respect API constraints
- **Error handling** and retry logic
- **Data validation** and quality checks

## 🔍 Exploring the Data

### Jupyter Notebooks

1. **01_data_exploration.ipynb** - Initial data analysis and visualization
2. **02_feature_engineering.ipynb** - Creating features for ML models
3. **03_model_building.ipynb** - Building and training predictive models
4. **04_ti14_predictions.ipynb** - Making predictions for The International

### Data Analysis Examples

```python
# Load collected data
import pandas as pd
players_df = pd.read_csv('data/processed/players.csv')
teams_df = pd.read_csv('data/processed/teams.csv')
matches_df = pd.read_csv('data/processed/matches.csv')

# Basic statistics
print(f"Total players: {len(players_df)}")
print(f"Total teams: {len(teams_df)}")
print(f"Total matches: {len(matches_df)}")

# ELO rating analysis
print(f"Average player ELO: {players_df['elo_rating'].mean():.1f}")
print(f"Average team ELO: {teams_df['team_elo'].mean():.1f}")
```

## 🚧 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the project root directory
   cd dota_ds
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **API Rate Limits**
   ```bash
   # Set your API key for higher limits
   export OPENDOTA_API_KEY=your_key_here
   ```

3. **Data Collection Fails**
   ```bash
   # Check internet connection
   # Verify API endpoints are accessible
   # Check rate limiting settings
   ```

4. **Memory Issues**
   ```bash
   # Reduce batch size in data collection
   # Process data in smaller chunks
   ```

### Getting Help

- Check the logs in `logs/dota2_analysis.log`
- Review error messages for specific issues
- Ensure all dependencies are installed correctly

## 🎮 Next Steps

After setting up the project:

1. **Run the demo** to see the ELO system in action
2. **Collect some data** using the data collection script
3. **Explore the data** in Jupyter notebooks
4. **Build your own models** for TI14 predictions
5. **Analyze tournament trends** and meta evolution

## 📚 Learning Resources

- **Dota 2 Meta**: [Liquipedia](https://liquipedia.net/dota2/)
- **Data Science**: [scikit-learn documentation](https://scikit-learn.org/)
- **Python**: [Real Python tutorials](https://realpython.com/)
- **Sports Analytics**: [FiveThirtyEight](https://fivethirtyeight.com/)

## 🤝 Contributing

This is an educational project! Feel free to:

- Add new features and analysis
- Improve the ELO rating system
- Create new data collection sources
- Build better predictive models
- Share insights and findings

## 📄 License

This project is for educational purposes. Please respect the terms of service of any APIs you use.

---

**Ready to dive into Dota 2 data science? Let's predict TI14! 🏆🎮📊**
