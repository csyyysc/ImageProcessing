# Image Processing Application

A full-stack image processing application with FastAPI backend and Streamlit frontend, featuring user authentication, image upload, transformation, and management capabilities. 

> **Project Source**: This project is based on the [Image Processing Service](https://roadmap.sh/projects/image-processing-service) roadmap project from roadmap.sh


## 🏗️ Project Structure

```
ImageProcessingApp/
├── backend/                    # FastAPI backend
│   ├── api/                   # API endpoints
│   ├── models/               # Pydantic models
│   ├── services/             # Business logic
│   ├── middleware/           # FastAPI middleware
│   ├── utils/                # Utility functions
│   ├── exceptions/           # Custom exceptions
│   ├── tests/                # Backend tests
│   ├── database.py           # Database operations
│   └── main.py               # FastAPI application
├── frontend/                 # Streamlit frontend
│   ├── api/                  # API client modules
│   ├── components/           # UI components
│   ├── utils/                # Frontend utilities
│   ├── tests/                # Frontend tests
│   ├── auth.py               # Legacy authentication module
│   └── app.py                # Main Streamlit application
├── shared/                   # Shared components
│   ├── config.py             # Configuration settings
│   └── models/               # Shared models
├── scripts/                  # Utility scripts
├── data/                     # Database storage
├── uploads/                  # Image storage directory
├── docker-compose.yml        # Docker Compose configuration
├── docker-compose.dev.yml    # Development Docker Compose
├── Dockerfile                # Docker configuration
├── Makefile                  # Build automation
├── nginx.conf                # Nginx configuration
├── main.py                   # Application entry point
├── pyproject.toml            # Project dependencies
├── uv.lock                   # Dependency lock file
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd ImageProcessingApp
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

### Running the Application

#### Start the Application

```bash
# Start both backend and frontend
uv run main.py dev
```

**Other commands:**
```bash
# Start backend only
uv run main.py backend

# Start frontend only  
uv run main.py frontend

# Start Streamlit deployment (production mode)
uv run main.py streamlit
```

This will start:
- **Backend** at http://localhost:8000
- **Frontend** at http://localhost:8501

#### Direct Commands

**Backend:**
```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
uv run streamlit run frontend/app.py --server.port 8501
```

## 📚 API Documentation

Once the backend is running, you can access:

- **API Documentation (Swagger):** http://localhost:8000/docs
- **Alternative API Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 🎯 Features

### 🔐 User Authentication
- **User Registration**: Create new user accounts
- **Secure Login**: Password-based authentication
- **Session Management**: Basic session handling

### 📸 Image Management
- **Image Upload**: Support for PNG, JPG, JPEG formats (up to 10MB)
- **Image Storage**: Secure file storage with metadata tracking
- **Image Gallery**: View all uploaded images with pagination
- **Image Deletion**: Remove unwanted images with confirmation

### 🎨 Image Transformations
- **Basic Operations**:
  - **Resize**: Change image dimensions
  - **Crop**: Extract specific regions
  - **Rotate**: Rotate images by any angle
  - **Flip**: Horizontal flip (left-right)
  - **Mirror**: Vertical flip (top-bottom)

- **Advanced Operations**:
  - **Watermark**: Add text watermarks
  - **Compress**: Adjust image quality
  - **Format Conversion**: Convert between JPEG, PNG, WEBP, BMP
  - **Filters**: Apply grayscale, sepia, blur, sharpen, edge detection

### 🖥️ User Interface
- **Modern Design**: Clean, responsive interface with consistent styling
- **View Modes**: 
  - **Grid View**: Compact 3-column layout (300x300px images)
  - **Large View**: Full-width display for detailed viewing
- **Auto-refresh**: Automatic data updates when switching tabs
- **Real-time Statistics**: Live image count and storage usage in sidebar
- **Smart Pagination**: Navigate through large image collections

### 📊 Dashboard Features
- **Image Statistics**: Total images, storage usage, average file size
- **System Status**: Backend connectivity monitoring
- **User Information**: Current user details in sidebar
- **Bulk Operations**: Delete all images with confirmation

## 🔧 Technical Features

### Backend (FastAPI)
- **RESTful API**: Complete CRUD operations for users and images
- **File Processing**: PIL-based image manipulation
- **Database Integration**: SQLite with SQLAlchemy ORM
- **Security**: Password hashing, rate limiting, input validation
- **Error Handling**: Comprehensive error responses and logging
- **CORS Support**: Cross-origin resource sharing for frontend

### Frontend (Streamlit)
- **Multi-tab Interface**: Organized functionality across tabs
- **Real-time Updates**: Automatic refresh and cache management
- **Responsive Design**: Consistent image containers and styling
- **User Experience**: Loading states, confirmations, and feedback
- **State Management**: Session-based state persistence

### Image Processing
- **Format Support**: PNG, JPG, JPEG input/output
- **Quality Control**: Configurable compression and quality settings
- **Transformation Pipeline**: Multiple operations in sequence
- **Metadata Preservation**: File information tracking
- **Error Recovery**: Graceful handling of processing failures

## 🛠️ Development

### Environment Variables

You can customize the application using environment variables:

```bash
# API Configuration
export API_HOST=0.0.0.0
export API_PORT=8000
export API_RELOAD=true

# Frontend Configuration
export FRONTEND_HOST=0.0.0.0
export FRONTEND_PORT=8501

# Backend URL for frontend
export BACKEND_URL=http://localhost:8000

# Database
export DATABASE_URL=sqlite:///./data/app.db

# Security
export SECRET_KEY=your-secret-key-here
export ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
export LOG_LEVEL=INFO
```

### Adding Dependencies

```bash
# Add a new dependency
uv add package_name

# Add a development dependency
uv add --dev package_name

# Update dependencies
uv sync
```

## 🧪 Testing

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test user registration
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123", "email": "test@example.com"}'

# Test user login
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'

# Test image upload (with authentication token)
curl -X POST http://localhost:8000/api/images/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@image.jpg" \
  -F "user_id=1"
```

### Frontend Testing

1. Start the application: `uv run python main.py dev`
2. Navigate to http://localhost:8501
3. Register a new user or login
4. Upload test images
5. Try different transformations
6. Test view modes and pagination

## 📦 Deployment

### Production Setup

1. **Environment Configuration**:
   ```bash
   export SECRET_KEY=your-production-secret-key
   export DATABASE_URL=postgresql://user:pass@localhost/dbname
   export BACKEND_URL=https://your-api-domain.com
   ```

2. **Database Migration**:
   ```bash
   # The application will create tables automatically on first run
   uv run python -c "from backend.database import init_db; init_db()"
   ```

3. **Static File Serving**:
   - Configure nginx or similar for serving uploaded images
   - Set up proper file permissions for uploads directory

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

# Create uploads directory
RUN mkdir -p uploads

EXPOSE 8000 8501

CMD ["uv", "run", "python", "main.py", "dev"]
```

### Security Considerations

- **Authentication**: Basic token system for user sessions
- **File Upload**: File type validation and size limits implemented
- **HTTPS**: Use SSL/TLS in production
- **Secrets**: Store sensitive data in environment variables

## 🆘 Troubleshooting

### Common Issues

**Backend not starting:**
- Check if port 8000 is already in use
- Ensure all dependencies are installed: `uv sync`
- Verify database permissions

**Frontend can't connect to backend:**
- Verify backend is running on http://localhost:8000
- Check CORS settings in backend configuration
- Ensure firewall isn't blocking the connection

**Image upload issues:**
- Check uploads directory permissions
- Verify file size limits (10MB max)
- Ensure supported formats (PNG, JPG, JPEG)

**Authentication problems:**
- Clear browser cache and cookies
- Check if user account is locked due to failed attempts
- Verify backend authentication service is running

**Package installation issues:**
- Update uv: `pip install --upgrade uv`
- Clear cache: `uv cache clean`
- Reinstall dependencies: `rm uv.lock && uv sync`

### Getting Help

- Check the logs for detailed error messages
- Verify your Python version: `python --version`
- Ensure uv is properly installed: `uv --version`
- Check database connectivity and permissions

## 🔮 Future Enhancements

- **Advanced Filters**: More image filters and effects
- **Batch Processing**: Process multiple images simultaneously
- **Cloud Storage**: Integration with AWS S3, Google Cloud Storage
- **Image Search**: Search and filter images by metadata
- **tests**: frontend/backend unit tests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Update documentation if needed
6. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.
---

Happy Image Processing! 📸✨