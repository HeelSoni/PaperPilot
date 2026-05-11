# 🚀 PaperPilot: Your AI-Powered Research Assistant

PaperPilot is a next-generation research assistant designed to help researchers, students, and academics discover, summarize, and manage scientific literature with ease. Powered by advanced NLP models, it provides semantic search, AI-driven summarization, and interactive citation mapping.

![PaperPilot Dashboard](https://raw.githubusercontent.com/HeelSoni/PaperPilot/main/screenshots/dashboard.png)

## ✨ Features

- **Semantic Discovery**: Go beyond keyword matching. Our SPECTER-powered engine understands the context of your research topic.
- **AI Summarization**: Instantly condense long abstracts into concise, actionable summaries using BART.
- **Citation Graph**: Visualize paper relationships and discover influential research in your field.
- **Smart Library**: Save papers to your personal reading list with persistent search history.
- **Research Trends**: Track the growth and popularity of research topics over time.
- **Fail-Safe Search**: Integrated fallbacks to Semantic Scholar and Smart Mocking to ensure you always have data to work with.

## 🛠️ Technology Stack

- **Frontend**: React (Vite), Framer Motion, Lucide React, Plotly.js.
- **Backend**: FastAPI, SQLAlchemy (SQLite), Uvicorn.
- **AI/ML**: Transformers (BART, SPECTER), Scikit-Learn.
- **Data Sources**: arXiv API, Semantic Scholar API.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Developer Mode enabled (for Hugging Face symlinks on Windows)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/HeelSoni/PaperPilot.git
   cd PaperPilot
   ```

2. **Setup Backend**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Frontend**:
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the Backend**:
   ```bash
   # From the root directory
   python -m backend.app
   ```

2. **Start the Frontend**:
   ```bash
   # In a new terminal
   cd frontend
   npm run dev
   ```

3. Open your browser to `http://localhost:5173`.

## 📈 Future Roadmap

- [ ] **PDF Chat (RAG)**: Chat with your research papers using a vector-based Q&A pipeline.
- [ ] **User Authentication**: Secure accounts to sync your library across devices.
- [ ] **Export Options**: Export citations in BibTeX, APA, and MLA formats.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
Built with ❤️ for the Research Community.
