# 🏥 Clinic Lead Generation Agent

An intelligent AI-powered agent that automates the discovery and extraction of clinic leads. It searches for clinics using Google Maps and web search, scrapes detailed contact information, validates the data, and exports structured leads — all autonomously.

---

## 📌 Overview

This project is a multi-tool AI agent built with **LangGraph** that automates the entire clinic lead generation pipeline:

- 🔍 Searches for clinics via **Google Maps API** and **Web Search**
- 🌐 Scrapes clinic websites for contact details
- ✅ Validates extracted data (emails, phone numbers, addresses)
- 📋 Exports clean, structured leads to **CSV**
- 🤖 Uses a **graph-based agent** with planning, memory, and tool-use capabilities

---

## 🗂️ Project Structure

```
clinic-lead-generation-agent/
│
├── app/
│   ├── agent/          # AI agent logic (planner, memory, prompts)
│   ├── graph/          # LangGraph nodes, edges, state, and graph
│   ├── schemas/        # Data models (clinic, request, response)
│   ├── services/       # Core services (search, extraction)
│   ├── tools/          # Tools (Google Maps, web search, scraper, validator)
│   └── utils/          # Helpers, logger, constants
│
├── outputs/            # Generated CSV lead files
├── examples/           # Sample input/output JSON
├── tests/              # Unit tests
├── config.py           # Configuration and environment settings
├── main.py             # Entry point
└── requirements.txt    # Python dependencies
```

---

## ⚙️ Tech Stack

| Layer        | Technology                        |
|--------------|-----------------------------------|
| Language     | Python 3.10+                      |
| Agent Framework | LangGraph + LangChain          |
| Search       | Google Maps API, Web Search       |
| Scraping     | BeautifulSoup / custom scraper    |
| Validation   | Custom validators (email, phone)  |
| Output       | CSV export                        |
| Config       | `.env` based environment variables|

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/sadesh19/clinic-lead-generation-agent.git
cd clinic-lead-generation-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 4. Run the Agent

```bash
python main.py
```

---

## 📤 Output

Generated leads are saved to the `outputs/` directory as a CSV file with fields like:

- Clinic Name
- Address
- Phone Number
- Email
- Website
- Appointment Method

---

## 🧪 Running Tests

```bash
pytest tests/
```

---

## 📄 License

This project is for private use. All rights reserved.
