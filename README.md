# Technocracy

An interactive AI-powered character simulation platform featuring 1,000 unique characters that can engage in conversations, answer questions, and interact within a dynamic 2D world.

## 🌟 Overview

Technocracy combines a Next.js frontend with a Flask backend to create an immersive experience where AI-powered characters have distinct personalities, opinions, and the ability to engage in meaningful conversations. Each character is powered by OpenAI's GPT models and maintains conversation history through Redis caching.

### Key Features

- **1,000 Unique Characters**: Each with custom sprites, personalities, and attributes
- **AI-Powered Conversations**: Characters can answer questions and engage in multi-turn conversations
- **Interactive 2D World**: Real-time character simulation with smooth animations
- **Passion Scoring**: Characters express varying levels of interest in topics
- **Persistent State**: Redis-backed storage for conversation history and character states
- **Scalable Architecture**: Designed for deployment on Vercel with serverless functions

## 📁 Project Structure

```
technocracy/
├── frontend/              # Next.js application
│   ├── app/              # Next.js app directory
│   ├── components/       # React components & UI library
│   ├── src/
│   │   ├── components/   # Character world components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── lib/          # Utility functions and classes
│   │   └── types/        # TypeScript type definitions
│   ├── public/
│   │   └── characters/   # 1,000 character assets and metadata
│   └── scripts/          # Character download and cleanup utilities
│
└── backend/              # Flask API server
    ├── api/              # Vercel serverless function entry point
    ├── prompts/          # AI prompt templates
    ├── generateResponses.py  # Main Flask application
    └── requirements.txt  # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 20+ and npm
- **Python** 3.11+
- **Redis** (local or Upstash for production)
- **OpenAI API Key**

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Download character assets (optional, takes 3-5 minutes)
npm run download:characters

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3003`

### Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export REDIS_URL="redis://localhost:6379"

# Start Redis (if running locally)
redis-server

# Run the Flask server
python generateResponses.py
```

The backend will be available at `http://localhost:5037`

## 🎮 Usage

### Interactive World

The main interface displays an interactive 2D world where characters move and interact. Use the controls to:

- **Zoom**: Mouse wheel or zoom controls
- **Pan**: Click and drag the canvas
- **Speed Control**: Adjust simulation speed
- **Character Selection**: Click characters to view details

### API Endpoints

#### Ask All Characters a Question

```bash
POST /api/question
Content-Type: application/json

{
  "question": "Should I buy these shoes?"
}
```

Returns responses from 100 characters with their answers, passion scores, and reasoning.

#### Have a Conversation

```bash
POST /api/conversation
Content-Type: application/json

{
  "character_id": 1,
  "message": "Hello! What do you think about technology?"
}
```

Maintains conversation history for continued dialogue.

#### Get Character Data

```bash
GET /api/characters        # Get all characters
GET /api/characters/<id>   # Get specific character
GET /api/health           # Health check
```

## 🎨 Character System

### Character Attributes

Each character includes:
- **Identity**: Gender, name, unique persona
- **Appearance**: Skin color, hair style/color, clothing colors
- **Sprites**: Idle, walk, and sit animations
- **AI Personality**: Generated persona for GPT conversations
- **State**: Conversation history, opinions, passion levels

### Character Data Format

```typescript
{
  "id": 1,
  "gender": "male",
  "name": "Alex Chen",
  "description": "A boy with bronze skin...",
  "persona": "I am an energetic software engineer...",
  "attributes": {
    "skin_color": "bronze",
    "hair_color": "chestnut",
    "hair_style": "twists_straight",
    "shirt_color": "slate",
    "leg_color": "navy",
    "shoe_color": "maroon"
  },
  "sprites": {
    "idle": { "url": "/characters/character_0001/idle.png" },
    "walk": { "url": "/characters/character_0001/walk.png" },
    "sit": { "url": "/characters/character_0001/sit.png" }
  }
}
```

## 🛠️ Technology Stack

### Frontend
- **Next.js 16** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **TanStack Query** - Data fetching and caching
- **Tailwind CSS** - Styling
- **Radix UI** - Component primitives
- **Canvas API** - Character rendering and animations

### Backend
- **Flask** - Python web framework
- **OpenAI GPT** - AI language models
- **Redis** - In-memory data store for caching
- **Python 3.11+** - Core language

### Infrastructure
- **Vercel** - Hosting and serverless functions
- **Upstash Redis** - Managed Redis for production

## 🚢 Deployment

### Deploy to Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Set Up Upstash Redis**
   - Create account at [console.upstash.com](https://console.upstash.com/)
   - Create a Redis database (free tier available)
   - Copy the `REDIS_URL`

3. **Deploy Backend**
   ```bash
   cd backend
   vercel login
   vercel
   ```

4. **Configure Environment Variables**
   
   In Vercel Dashboard → Settings → Environment Variables:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `REDIS_URL` - Upstash Redis connection string

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

6. **Deploy Frontend**
   ```bash
   cd frontend
   vercel
   ```

For detailed deployment instructions, see:
- [backend/QUICK_START.md](backend/QUICK_START.md)
- [backend/README.md](backend/README.md)

## 📚 Documentation

- **[Character Documentation](frontend/CHARACTERS_README.md)** - Complete guide to character data and assets
- **[Backend README](backend/README.md)** - API documentation and local development
- **[Quick Start Guide](backend/QUICK_START.md)** - Fast deployment instructions

## 🔧 Development Scripts

### Frontend

```bash
npm run dev                          # Start dev server on port 3003
npm run build                        # Build for production
npm run lint                         # Run Biome linter
npm run format                       # Format code with Biome
npm run download:characters          # Download all 1,000 characters
npm run download:characters:resume   # Resume interrupted download
npm run cleanup:characters           # Clean up character data
```

### Backend

```bash
python generateResponses.py          # Start Flask server
python test.py                       # Run tests
python add_character_fields.py       # Add new fields to character data
python reformat.py                   # Reformat character data
```

## 🤝 Contributing

This project was created for the OpenAI Hackathon. Contributions, issues, and feature requests are welcome!

## 📄 License

This project uses character data from [Physda-Labs/technocracy](https://github.com/Physda-Labs/technocracy). Please refer to their repository for licensing information regarding character assets.

## 🙏 Acknowledgments

- Character sprites and data from [Physda-Labs/technocracy](https://github.com/Physda-Labs/technocracy)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Powered by OpenAI's GPT models

---

**Built with ❤️ for the OpenAI Hackathon**
