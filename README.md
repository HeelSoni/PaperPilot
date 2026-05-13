<div align="center">

<h1>📚 PaperPilot</h1>

<p><strong>AI-Powered Research Paper Assistant — Discover, Analyze & Understand Academic Research Instantly</strong></p>

<p>
  <a href="https://paper-pilot-five.vercel.app/" target="_blank">
    <img src="https://img.shields.io/badge/🚀 Live Demo-Vercel-black?style=for-the-badge&logo=vercel" />
  </a>
  <img src="https://img.shields.io/badge/Backend-Railway-8B5CF6?style=for-the-badge&logo=railway" />
  <img src="https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?style=for-the-badge&logo=react" />
  <img src="https://img.shields.io/badge/AI-HuggingFace-FF9A00?style=for-the-badge&logo=huggingface" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python" />
  <img src="https://img.shields.io/badge/FastAPI-0.110-009688?style=flat&logo=fastapi" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react" />
  <img src="https://img.shields.io/badge/arXiv-API-B31B1B?style=flat" />
  <img src="https://img.shields.io/badge/Semantic%20Scholar-API-4285F4?style=flat" />
</p>

</div>

---

## 🌟 What is PaperPilot?

**PaperPilot** is a full-stack AI Research Assistant that transforms how students, researchers, and developers interact with academic literature. Instead of reading through dense papers manually, PaperPilot uses AI to extract insights, generate summaries, answer your questions, and map citation networks — all in seconds.

> **Built for the next generation of researchers.** Whether you're a student tackling your first literature review or a professional staying up-to-date with the latest AI breakthroughs, PaperPilot accelerates your research workflow by 10x.

---

## ✨ Core Features

### 🔍 1. Semantic Paper Search
- Search over **millions of papers** from the [arXiv](https://arxiv.org) database
- Results ranked by relevance score and returned in **under 3 seconds**
- Supports any topic: AI, biology, physics, economics, and more

### ⚡ 2. AI Key Insights Extraction
- Automatically extracts **5 structured insights** from every paper:
  - 🔬 **Methodology** — How the research was conducted
  - 📊 **Dataset** — What data was used
  - 🏆 **Key Results** — What was achieved
  - ⚠️ **Limitations** — What didn't work or needs improvement
  - 🚀 **Future Work** — Where the research is heading
- Uses **clause-aware NLP extraction** — works even on single-sentence abstracts
- Falls back intelligently with meaningful content, never generic placeholders

### 🤖 3. AI Executive Summary
- Powered by **Facebook BART-Large-CNN** (HuggingFace Inference API)
- Condenses long abstracts into concise, readable executive summaries
- Ideal for quickly deciding whether a paper is worth reading in full

### 💬 4. Chat with Paper
- Ask **any question** about a paper in natural language
- Question-type routing: methodology questions → methodology sentences, dataset questions → data sentences
- Gives **different, specific answers** per question type
- Powered by smart clause-based NLP with zero latency

### 🕸️ 5. Citation Topology Graph
- Visual network map showing how papers cite each other
- Built with **react-force-graph-2d** with animated link particles
- **Discovery Cluster Fallback**: If a paper is new or niche, automatically builds a similarity graph using related ArXiv papers — so you always see a network
- Click any node to open the paper on ArXiv

### 📈 6. Research Trends
- Visualizes publication growth for any research topic over time (2018–2024)
- Lightweight CSS-based bar chart — zero external chart library dependencies

### 📚 7. Personal Research Library
- Save papers to your personal reading list with one click
- Access saved papers anytime from the **Library** tab
- Full CRUD: add, view, and remove papers

### 🕐 8. Search History
- Automatically logs all your searches
- Quick-access buttons to re-run previous queries instantly

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│               Frontend (Vercel)              │
│   React 18 + Vite + Framer Motion           │
│   react-force-graph-2d • Lucide Icons       │
└──────────────────────┬──────────────────────┘
                       │ HTTPS (REST API)
┌──────────────────────▼──────────────────────┐
│              Backend (Railway)               │
│   FastAPI + SQLAlchemy + SQLite             │
│   ┌─────────────┐   ┌──────────────────┐   │
│   │ recommender │   │   summarizer.py  │   │
│   │    .py      │   │  (AI Insights,   │   │
│   │ (ArXiv +    │   │   Summary, Chat) │   │
│   │  Sem. Sch.) │   └────────┬─────────┘   │
│   └─────────────┘            │              │
└──────────────────────────────┼──────────────┘
                               │ HTTPS
┌──────────────────────────────▼──────────────┐
│            External APIs                     │
│  🤗 HuggingFace • 📄 arXiv • 🔬 Sem. Scholar│
└─────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite | UI Framework |
| **Styling** | Custom CSS + Framer Motion | Animations & Design |
| **Graph** | react-force-graph-2d | Citation Network |
| **Backend** | FastAPI (Python) | REST API |
| **Database** | SQLite + SQLAlchemy | Reading List & History |
| **AI Summary** | facebook/bart-large-cnn | Paper Summarization |
| **Paper Search** | arXiv API | Academic Paper Data |
| **Citations** | Semantic Scholar API | Citation Graph Data |
| **Hosting** | Vercel (FE) + Railway (BE) | Production Deployment |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A free [HuggingFace API key](https://huggingface.co/settings/tokens)

### Backend Setup
```bash
# Clone the repo
git clone https://github.com/HeelSoni/PaperPilot.git
cd PaperPilot/backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export HUGGINGFACE_API_KEY=your_key_here

# Start the server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
cd PaperPilot/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

> The frontend is pre-configured to connect to the production Railway backend.  
> For local development, update `API_BASE` in `src/App.jsx` to `http://localhost:8000`.

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|---------|-------------|
| `GET` | `/health` | Server health check |
| `POST` | `/search` | Search papers by query |
| `POST` | `/summarize` | Generate AI summary |
| `POST` | `/extract-insights` | Extract 5 structured insights |
| `POST` | `/chat` | Ask a question about a paper |
| `GET` | `/citation-graph/{id}` | Get citation network graph |
| `GET` | `/recommend/{id}` | Get related paper recommendations |
| `GET` | `/trends/{topic}` | Get publication trend data |
| `GET` | `/reading-list` | Get saved papers |
| `POST` | `/reading-list` | Save a paper |
| `DELETE` | `/reading-list/{id}` | Remove a saved paper |
| `GET` | `/history` | Get search history |

---

## 🌐 Live Demo

| Service | URL |
|---------|-----|
| 🌍 **Frontend** | [paper-pilot-five.vercel.app](https://paper-pilot-five.vercel.app/) |
| ⚙️ **Backend API** | [paperpilot-production-cda3.up.railway.app](https://paperpilot-production-cda3.up.railway.app/health) |
| 💻 **GitHub** | [github.com/HeelSoni/PaperPilot](https://github.com/HeelSoni/PaperPilot) |

---

## 🧠 AI Models Used

| Feature | Model | Provider |
|---------|-------|----------|
| Executive Summary | `facebook/bart-large-cnn` | HuggingFace |
| Key Insights | Clause-aware NLP (no API) | Built-in |
| Chat with Paper | Question-routing NLP (no API) | Built-in |

> **Note**: The Key Insights and Chat features use deterministic NLP extraction that runs entirely on the server — no external AI API calls needed. This ensures they are **always fast and never fail** due to rate limits or model unavailability.

---

## 📂 Project Structure

```
PaperPilot/
├── backend/
│   ├── app.py              # FastAPI routes & middleware
│   ├── recommender.py      # ArXiv + Semantic Scholar integration
│   ├── summarizer.py       # AI summary, insights & chat
│   ├── trends.py           # Publication trend analysis
│   ├── models.py           # SQLAlchemy database models
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React application
│   │   └── App.css         # Styling
│   ├── index.html
│   └── package.json
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [Heel Soni](https://github.com/HeelSoni)**

*If you found this helpful, please ⭐ star the repo!*

</div>
