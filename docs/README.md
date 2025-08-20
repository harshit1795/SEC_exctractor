# 📚 FinQ SEC Extractor - Documentation Hub

Welcome to the comprehensive documentation for the FinQ SEC Extractor application. This documentation is organized by application area to help you quickly find the information you need.

## 🗂️ Documentation Structure

### 📋 [Setup & Installation](./setup/)
**Getting started with the application**
- **README.md** - Main project overview and initial setup instructions
- Firebase configuration and authentication setup
- Local development environment setup
- First-time user guide

### 🚀 [Deployment](./deployment/)
**Production deployment and cloud hosting**
- **DEPLOYMENT.md** - Complete deployment guide for Streamlit Cloud
- Firebase project configuration
- OAuth client setup
- Environment variables and secrets management
- Production deployment steps

### 🛠️ [Development](./development/)
**Development guidelines and project context**
- **SAVED_RULES.md** - Critical development rules and best practices
- **gemini.md** - Project context and architectural principles
- **PROJECT_MEMORIES.md** - Session logs and development timeline
- Development workflow and troubleshooting

### 🏗️ [Architecture](./architecture/)
**Technical architecture and design**
- **CHATBOT_ARCHITECTURE.md** - MCP architecture for the enhanced chatbot
- System design principles
- Component architecture
- Data flow and integration patterns

### 📖 [Reference](./reference/)
**Quick reference and troubleshooting**
- **QUICK_REFERENCE.md** - Fast commands and quick fixes
- Common error solutions
- Package installation guides
- Streamlit Cloud setup reference

## 🎯 Quick Navigation

### For New Users
1. Start with **[Setup & Installation](./setup/README.md)**
2. Follow the Firebase configuration guide
3. Run the application locally

### For Developers
1. Review **[Development Guidelines](./development/SAVED_RULES.md)**
2. Understand the **[Architecture](./architecture/CHATBOT_ARCHITECTURE.md)**
3. Use **[Quick Reference](./reference/QUICK_REFERENCE.md)** for common tasks

### For Deployment
1. Follow the **[Deployment Guide](./deployment/DEPLOYMENT.md)**
2. Configure Streamlit Cloud secrets
3. Set up production environment

## 🔍 Search by Topic

### Authentication & Firebase
- Setup: [Setup Guide](./setup/README.md)
- Deployment: [Deployment Guide](./deployment/DEPLOYMENT.md)
- Development: [Development Rules](./development/SAVED_RULES.md)

### Chatbot & AI Features
- Architecture: [Chatbot Architecture](./architecture/CHATBOT_ARCHITECTURE.md)
- Development: [Project Context](./development/gemini.md)

### Troubleshooting
- Quick fixes: [Quick Reference](./reference/QUICK_REFERENCE.md)
- Development issues: [Project Memories](./development/PROJECT_MEMORIES.md)
- Best practices: [Saved Rules](./development/SAVED_RULES.md)

## 📝 Contributing to Documentation

When adding new documentation:
1. **Identify the appropriate category** based on content
2. **Use consistent naming** (e.g., `FEATURE_NAME.md`)
3. **Update this index** with new entries
4. **Cross-reference** related documents when appropriate

## 🚨 Important Notes

- **API Keys**: Never commit API keys to version control
- **Secrets**: Use `.streamlit/secrets.toml` for local development
- **Firebase**: Keep credentials secure and rotate regularly
- **Dependencies**: Document all package requirements in `requirements.txt`

---

*This documentation structure makes it easy to find information based on your current needs - whether you're setting up, developing, deploying, or troubleshooting the application.*
