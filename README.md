# 🚀 FinQ SEC Extractor

> **Intelligent Financial Data Extraction & Analysis Platform**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Firebase](https://img.shields.io/badge/Firebase-Auth-green.svg)](https://firebase.google.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 What is FinQ?

FinQ is an advanced financial analysis platform that automatically extracts and analyzes financial data from SEC reports, providing intelligent insights through AI-powered analysis. Built with Streamlit and Firebase, it offers a modern web interface for financial professionals, analysts, and investors.

## ✨ Key Features

- 🔐 **Secure Authentication** - Firebase-powered user management
- 📊 **Multi-Source Data** - Yahoo Finance, FRED, SEC filings, fundamentals
- 🤖 **AI-Powered Analysis** - Google Gemini integration for intelligent insights
- 📈 **Real-time Updates** - Live financial data and market indicators
- 🏗️ **MCP Architecture** - Model Context Protocol for universal data access
- 📱 **Responsive UI** - Modern Streamlit interface with dashboard tabs

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Firebase project with Google Authentication
- Google Generative AI API key
- FRED API key (optional)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/SEC_exctractor.git
cd SEC_exctractor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys (see Configuration section)
# Run the application
streamlit run Home.py
```

### Configuration
1. **Firebase Setup**: Create a Firebase project and enable Google Authentication
2. **API Keys**: Configure your API keys in `.streamlit/secrets.toml`
3. **Credentials**: Place Firebase credentials in the project root

## 📚 Documentation

📖 **Complete documentation is organized by application area:**

- **[📋 Setup & Installation](docs/setup/README.md)** - Get started with FinQ
- **[🚀 Deployment](docs/deployment/DEPLOYMENT.md)** - Deploy to production
- **[🛠️ Development](docs/development/)** - Development guidelines and context
- **[🏗️ Architecture](docs/architecture/)** - Technical design and MCP architecture
- **[📖 Reference](docs/reference/)** - Quick commands and troubleshooting

## 🏗️ Architecture

FinQ uses a **Model Context Protocol (MCP) architecture** that provides:

- **Universal Data Access** - Connect to any financial data source
- **Intelligent Caching** - Optimized performance with smart data management
- **Modular Design** - Clean separation of concerns and easy maintenance
- **AI Integration** - Context-aware financial analysis and insights

## 🔧 Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Authentication**: Firebase Authentication (Google provider)
- **AI/ML**: Google Generative AI (Gemini)
- **Data Sources**: Yahoo Finance, FRED, SEC filings
- **Database**: Firebase Firestore (optional)
- **Deployment**: Streamlit Cloud, Docker support

## 📊 Data Sources

- **Company Data**: Real-time stock data, financial statements, earnings
- **Economic Indicators**: GDP, unemployment, inflation, interest rates
- **SEC Filings**: Annual and quarterly reports for public companies
- **Fundamentals**: Historical financial metrics and ratios

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/README.md](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/SEC_exctractor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/SEC_exctractor/discussions)

## 🙏 Acknowledgments

- **SEC.gov** for providing public financial data
- **Yahoo Finance** for real-time market data
- **Federal Reserve (FRED)** for economic indicators
- **Google** for AI capabilities and Firebase services
- **Streamlit** for the amazing web framework

---

**Made with ❤️ for the financial analysis community**

*For detailed setup instructions, troubleshooting, and development guidelines, please refer to our [comprehensive documentation](docs/README.md).*
