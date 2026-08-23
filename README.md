# GlowMatch AI 🌟

> **AI-Powered Skincare Product Discovery, Color Science Typology & Routine Builder Engine**

GlowMatch AI is a modern hybrid retrieval and computer vision application engineered to recommend skincare products based on individual skin profiles, strict ingredient safety constraints, budget ceilings, and white-balanced facial selfie color science.

---

## 🚀 Key Features

* **Hybrid Neural Retrieval (RRF + Cross-Encoder):**
  Combines Dense Vector Search (`BAAI/bge-small-en-v1.5` embeddings in Qdrant) and Sparse Lexical BM25 search via Reciprocal Rank Fusion (RRF), re-ranked by `BAAI/bge-reranker-base` to optimize product search latency (<200ms).

* **Facial Skin Tone Typology ($\text{ITA}^\circ$ Color Science):**
  Calculates the **Individual Typology Angle ($\text{ITA}^\circ$)** from CIE LAB color space ($L^*, a^*, b^*$) extracted from upper-central facial skin regions (excluding clothing & hair). Computes dynamic, pixel-level skin concern standard deviations (Uneven Tone, Redness, Hyperpigmentation, Excess Oil).

* **Interactive Live WebRTC Camera Selfie & File Upload:**
  Supports both native device photo uploads and an interactive live webcam viewfinder with a real-time frame capture shutter button.

* **Safe AM / PM Routine Builder:**
  Generates tailored 4-step morning and evening routines split by custom budget ceilings (Cleanser, Moisturizer, Treatment, Sunscreen). Evaluates real-time ingredient safety, active separation, and pregnancy/lactation exclusions.

* **Structured Catalog Filtering via MongoDB Atlas:**
  Processes 8,000+ normalized skincare products with price ceiling filtering, skin-type tagging, and safety flags (`is_fragrance_free`, `is_pregnancy_safe`).

* **Modern Responsive Interface (Light & Dark Mode):**
  Built with React, Tailwind CSS v4, Lucide Icons, and dynamic CSS custom properties with full dark/light theme toggle.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite, Tailwind CSS v4, Lucide React, HTML5 WebRTC Canvas |
| **Backend API** | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| **Vector DB & Search** | Qdrant Vector Engine, BM25 Lexical Index, Reciprocal Rank Fusion (RRF) |
| **AI Models** | `BAAI/bge-small-en-v1.5` (Embeddings), `BAAI/bge-reranker-base` (Reranking) |
| **LLM Provider** | Groq Compound API (`groq/compound`) for explanation generation |
| **Database & Cache** | MongoDB Atlas (Product Catalog), In-Memory LRU Cache |
| **Cloud & Container** | Docker, Google Cloud Run (GCP) |

---

## 🏗️ Architecture Flow

```
[ User Query / Selfie Photo ]
             │
             ├──> [ WebRTC / Image Processing ] ──> CIE LAB (L*, a*, b*) ──> ITA° Tone & Concerns
             │
             └──> [ Hybrid Retrieval Pipeline ]
                        │
                        ├──> Dense Vector Search (Qdrant + BAAI/bge-small-en-v1.5)
                        ├──> Sparse Lexical BM25 Keyword Search
                        │
                        ├──> Reciprocal Rank Fusion (RRF) & Candidate Pool
                        ├──> Cross-Encoder Reranking (BAAI/bge-reranker-base)
                        └──> MongoDB Attribute & Price Range Filtering
                        │
                        └──> [ FastAPI Endpoint ] ──> [ React SPA Frontend ]
```

---

## ⚡ Quick Start & Local Setup

### Prerequisites
* Python 3.11+
* Node.js 18+
* MongoDB Atlas Cluster URI
* Groq API Key

### 1. Clone Repository & Setup Environment

```bash
git clone https://github.com/sh1vam31/GlowMatch_AI.git
cd GlowMatch_AI

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=groq/compound
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
MONGO_DB=glowmatch
QDRANT_PATH=./qdrant_data
RETRIEVAL_STRATEGY=hybrid_rrf_ce
```

### 3. Build & Run Application

```bash
# Build frontend production bundle
cd frontend && npm run build && cd ..

# Launch FastAPI development server
make dev
# Server will start on http://127.0.0.1:8000
```

---

## ☁️ Deployment on Render (Recommended & Free)

This repository includes a production `Dockerfile` optimized for **Render.com**.

### 1. Connect Repository
1. Go to **[dashboard.render.com](https://dashboard.render.com)** and log in with your GitHub account.
2. Click **New +** $\rightarrow$ **Web Service**.
3. Select your repository: **`sh1vam31/GlowMatch_AI`**.

### 2. Configure Service Settings
* **Name:** `glowmatch-ai`
* **Runtime:** `Docker` (Automatically detected from `Dockerfile`)
* **Instance Type:** `Free`

### 3. Add Environment Variables
In the Render Web Service configuration screen under **Environment Variables**, add:

| Key | Value |
| :--- | :--- |
| `GROQ_API_KEY` | `gsk_...` |
| `GROQ_MODEL` | `groq/compound` |
| `MONGO_URI` | `mongodb+srv://...` |
| `MONGO_DB` | `glowmatch` |

Click **Deploy Web Service** to launch your live application!

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
