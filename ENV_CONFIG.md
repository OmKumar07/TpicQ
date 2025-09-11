# Environment Configuration Guide

This project uses environment variables to manage different configurations for development and production environments.

## Backend Configuration

### Development (.env)
```properties
# Frontend and Backend URLs for development
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### Production (.env.production)
```properties
# Frontend and Backend URLs for production
FRONTEND_URL=https://topicq.netlify.app
BACKEND_URL=https://tpicq.onrender.com
```

### Environment Variables in Backend

- `FRONTEND_URL`: The URL of the frontend application (used for CORS configuration)
- `BACKEND_URL`: The URL of the backend API (used for self-reference)
- `GEMINI_API_KEY_1-4`: Multiple Gemini API keys for rotation
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)

## Frontend Configuration

### Development (frontend/.env)
```properties
REACT_APP_BACKEND_URL=http://localhost:8000
```

### Production (frontend/.env.production)
```properties
REACT_APP_BACKEND_URL=https://tpicq.onrender.com
```

### Environment Variables in Frontend

- `REACT_APP_BACKEND_URL`: The URL of the backend API that the frontend will communicate with

## Usage

### Development
1. Use the default `.env` files for local development
2. Run `npm start` for frontend (automatically uses `.env`)
3. Run `uvicorn main:app --reload` for backend (automatically uses `.env`)

### Production

#### Backend (Render)
Set these environment variables in your Render dashboard:
```
FRONTEND_URL=https://topicq.netlify.app
BACKEND_URL=https://tpicq.onrender.com
GEMINI_API_KEY_1=your_key_1
GEMINI_API_KEY_2=your_key_2
GEMINI_API_KEY_3=your_key_3
GEMINI_API_KEY_4=your_key_4
DATABASE_URL=sqlite:///:memory:
```

#### Frontend (Netlify)
Set these environment variables in your Netlify dashboard:
```
REACT_APP_BACKEND_URL=https://tpicq.onrender.com
```

## Benefits

1. **Environment Separation**: Different configurations for dev/prod
2. **Easy Deployment**: No hardcoded URLs to change
3. **CORS Management**: Dynamic CORS origins based on environment
4. **Security**: Sensitive data in environment variables
5. **Flexibility**: Easy to change URLs without code modifications

## File Structure

```
project/
├── .env                          # Backend development config
├── .env.production              # Backend production config
├── frontend/
│   ├── .env                     # Frontend development config
│   └── .env.production          # Frontend production config
└── ENV_CONFIG.md               # This guide
```
