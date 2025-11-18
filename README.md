# 🌌 Death Star Weather Command

**Imperial Weather Command - A Darth Vader themed weather chatbot**

A Star Wars themed weather application where Darth Vader himself delivers weather forecasts in his signature dramatic style.

---

## 🎯 About This Project

This is a test project built by **Diana Bogdanova** to explore AI-powered natural language processing and creative API integration.

### Built With
- **Backend:** Flask (Python) hosted on Render
- **AI:** Claude API (Anthropic) for natural language understanding and response generation
- **Weather Data:** Open-Meteo API
- **Frontend:** Vanilla HTML/CSS/JavaScript with Death Star command center theme

---

## ✨ Features

- 🤖 **Natural Language Input** - Claude AI parses conversational queries like "dear empire, tell me about Rome next week"
- 🎭 **Vader Personality** - Responses in Darth Vader's dramatic, menacing style with Star Wars references
- 📊 **Weather Intelligence** - Current conditions, forecasts, and historical data
- 🎨 **Command Center UI** - Retro sci-fi interface with radar scanner and system diagnostics
- 📱 **Mobile Responsive** - Works seamlessly on all devices
- ⚡ **Rate Limiting** - Built-in protection (10 requests/minute per IP)

---

## 🚀 How It Works

1. **User Input** → Natural language weather query (e.g., "Tokyo weather tomorrow")
2. **Claude AI Parsing** → Extracts location, timeframe, and query type
3. **Weather API** → Fetches real-time data from Open-Meteo
4. **Claude AI Response** → Generates a dramatic 3-sentence Vader-style response
5. **Frontend Display** → Typing animation in Death Star command center interface

---

## 🛠️ Tech Stack

**Backend (Python/Flask):**
- Flask web framework
- Anthropic Claude API for NLP
- Open-Meteo weather API
- CORS enabled for cross-origin requests
- Rate limiting with in-memory tracking

**Frontend:**
- Pure HTML/CSS/JavaScript
- No frameworks - vanilla code
- Google Fonts: Orbitron & Share Tech Mono
- Responsive CSS Grid layout
- Typing animation effects

**Deployment:**
- Backend: Render.com
- Frontend: Can be hosted anywhere (static files)

---

## 📦 Setup & Installation

### Prerequisites
- Python 3.8+
- Anthropic API key ([Get one here](https://console.anthropic.com))

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/DianaBogdanova/darth-vader-weather-bot.git
cd darth-vader-weather-bot
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
Create a `.env` file:
```
ANTHROPIC_API_KEY=your-api-key-here
```

5. **Run the Flask app:**
```bash
python app.py
```

6. **Open the frontend:**
- For local testing, update `index.html` API_URL to `http://127.0.0.1:5001/api/weather`
- Open `index.html` in your browser

---

## 🌐 Live Demo

**Backend API:** https://darth-vader-weather-bot.onrender.com

**Try these queries:**
- "San Diego weather now"
- "Tokyo forecast for next 5 days"
- "What was London weather yesterday?"
- "dear empire, tell me about Barcelona next week"

---

## 🎬 Example Responses

**Query:** "San Diego weather now"

**Vader's Response:**
> "The Force reveals San Diego's conditions: a pleasant 72°F with clear skies. The Empire finds such weather... acceptable. SPF 50 is mandatory, young one."

---

## 📝 API Endpoints

### `POST /api/weather`
Process weather queries with Claude AI

**Request:**
```json
{
  "query": "Tokyo weather now"
}
```

**Response:**
```json
{
  "location": "Tokyo, Japan",
  "response": "The Dark Side shows me Tokyo's atmosphere..."
}
```

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "The Empire is operational"
}
```

---

## 🔮 Future Enhancements

### Next Steps:
- [ ] **Star Wars Database Integration** - Add a database of Star Wars planets, ships, and lore
- [ ] **Custom MCP Server** - Build a Model Context Protocol server with Star Wars knowledge base
- [ ] **Weather Comparisons** - Compare Earth weather to Star Wars planets (e.g., "Today feels like Tatooine")
- [ ] **Extended Universe** - Add other Star Wars characters (Yoda, Emperor, etc.)

---

## 🎨 Design Philosophy

The UI draws inspiration from:
- 1970s-80s sci-fi command centers
- Star Wars Death Star control rooms
- Retro terminal aesthetics (green/red phosphor displays)
- Military/tactical interfaces

---

## 🤝 Contributing

This is a personal learning project, but suggestions and feedback are welcome!

---

## 📄 License

MIT License - feel free to use and modify for your own projects

---

## 🙏 Acknowledgments

- **Anthropic** - Claude API for natural language processing
- **Open-Meteo** - Free weather API
- **Star Wars** - Inspiration and beloved franchise
- **George Lucas** - For creating this amazing universe

---

## 📧 Contact

**Diana Bogdanova**

Questions or feedback? Open an issue on GitHub!

---

*"I find your lack of weather knowledge... disturbing." - Darth Vader*

---

**May the Force be with you! ⚡**# darth-vader-weather-bot
Imperial Weather Command - A Darth Vader themed weather chatbot
