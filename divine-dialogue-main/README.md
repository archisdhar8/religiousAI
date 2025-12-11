# Divine Wisdom Guide - Frontend

React + TypeScript frontend for the Divine Wisdom Guide application.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend API server running (see main [README.md](../README.md))

### Installation

```bash
# Install dependencies
npm install

# Create .env file (optional - defaults to http://localhost:8000)
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

The app will be available at http://localhost:8080

## 📁 Project Structure

```
divine-dialogue-main/
├── src/
│   ├── pages/              # Page components
│   │   ├── Chat.tsx        # Main chat interface
│   │   ├── Community.tsx   # Community features
│   │   ├── Landing.tsx     # Landing page
│   │   └── Login.tsx       # Authentication
│   │
│   ├── components/         # Reusable components
│   │   ├── chat/          # Chat-specific components
│   │   └── ui/            # shadcn/ui components
│   │
│   ├── lib/
│   │   ├── api.ts         # API client functions
│   │   └── utils.ts       # Utility functions
│   │
│   └── hooks/             # Custom React hooks
│
├── public/                # Static assets
└── package.json
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

For production, set this to your production API URL.

## 🛠️ Development

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **React Router** - Navigation

## 🔌 API Integration

The frontend communicates with the backend via REST API. All API calls are in `src/lib/api.ts`.

### Authentication

- Uses Bearer tokens stored in localStorage
- Automatically includes token in API requests
- Handles token expiration

### Features

- **Chat Interface**: Real-time chat with AI advisor
- **Multiple Conversations**: Create and manage multiple chat threads
- **Authentication**: Sign up, login, logout
- **Community**: Profile creation, matching, connections
- **Daily Wisdom**: Personalized daily quotes

## 📚 Documentation

- Main project: [../README.md](../README.md)
- Integration guide: [../INTEGRATION.md](../INTEGRATION.md)
- Supabase setup: [../SUPABASE_SETUP.md](../SUPABASE_SETUP.md)

## 🐛 Troubleshooting

### Can't connect to API

- Verify backend is running: `curl http://localhost:8000/`
- Check `VITE_API_URL` in `.env`
- Check browser console for errors

### CORS errors

- Ensure backend CORS allows `http://localhost:8080`
- Check backend is running on correct port

### Build errors

- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version` (should be 18+)

---

For full setup instructions, see the main [README.md](../README.md).
