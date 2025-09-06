# Epicly - Event Booking System

A comprehensive event booking system built with FastAPI and PostgreSQL, featuring user authentication, event management, venue operations, and booking functionality. This system supports various event types including movies, comedy shows, sports events, and concerts.

## 🎬 Features

- **User Management**: Registration, authentication, and profile management
- **Event Management**: Browse events with filtering by type, language, genre, city, and date
- **Venue & Seating**: Manage venues, sections, and seats with different pricing tiers
- **Schedule Management**: Handle event schedules across multiple venues and time slots
- **Booking System**: Book tickets with seat selection and temporary seat locking
- **Payment Processing**: Handle payments with multiple payment methods (UPI, Card, Net Banking, Wallet)
- **RESTful API**: Complete REST API with comprehensive endpoints and documentation

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.8+)
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **Authentication**: Simple email-based authentication
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Auto-generated with FastAPI/OpenAPI

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local development)
- PostgreSQL 15+ (if running without Docker)

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/rakshit-2/Epicly.git
   cd Epicly
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Local Development Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database configuration
   ```

3. **Start PostgreSQL database**
   ```bash
   docker-compose up db -d
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## 🏗️ Architecture

### Database Schema

<img width="1214" height="924" alt="Untitled" src="https://github.com/user-attachments/assets/3daad293-8bc5-4cb1-8e38-6b97648955a0" />

The system uses a well-structured relational database with the following key entities:

- **Users**: User registration and authentication
- **Venues**: Physical locations with multiple sections
- **Sections**: Different areas within venues (screens, zones, stands)
- **Seats**: Individual seats with pricing and type information
- **Events**: Movies, shows, concerts, and sports events
- **Schedules**: Time-based event scheduling
- **Bookings**: User reservations with seat assignments
- **Payments**: Transaction processing and status tracking

### Key Components

- **FastAPI Application**: Modern, fast web framework with automatic API documentation
- **SQLAlchemy Models**: Comprehensive data models with relationships and constraints
- **Database Layer**: Connection management with health checks and graceful shutdown
- **API Router**: Organized endpoints for different functionalities

## 📚 API Endpoints

### Events
- `GET /events` - List all events with filtering options
- `GET /events/{event_id}` - Get event details
- `GET /events/{event_id}/schedules` - Get event schedules

### Schedules & Seats
- `GET /schedules/{schedule_id}/seats` - Get available seats for a schedule
- `POST /seats/lock` - Temporarily lock seats (5-minute hold)

### Bookings
- `POST /bookings` - Create a new booking
- `GET /bookings/{booking_id}` - Get booking details

### Payments
- `POST /payments` - Process payment for a booking
- `GET /payments/{payment_id}` - Get payment status

### Users
- `POST /users/register` - Register a new user
- `POST /users/login` - User login
- `GET /users/{user_id}/bookings` - Get user's booking history

### System
- `GET /` - API status and environment info
- `GET /health` - Health check endpoint
- `GET /test` - Configuration details (development only)

## 🔧 Configuration

The application uses environment variables for configuration:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=epicly_db
DB_USER=postgres
DB_PASSWORD=password

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=info

# Security
ALLOWED_HOSTS=["*"]
```

## 📖 Usage Examples

### Register a User
```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890"
  }'
```

### Browse Events
```bash
curl "http://localhost:8000/events?type=MOVIE&city=Bangalore&date=2025-09-12"
```

### Book Tickets
```bash
# 1. Lock seats
curl -X POST "http://localhost:8000/seats/lock" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_id": 49,
    "seat_ids": [301, 302, 303]
  }'

# 2. Create booking
curl -X POST "http://localhost:8000/bookings" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "event_id": 2,
    "schedule_id": 49,
    "seat_ids": [301, 302, 303],
    "payment_method": "UPI"
  }'

# 3. Process payment
curl -X POST "http://localhost:8000/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": 1,
    "amount": 900,
    "method": "UPI"
  }'
```

## 🗂️ Project Structure

```
Epicly/
├── main.py              # Application entry point
├── api.py               # API routes and endpoints
├── models.py            # SQLAlchemy database models
├── database.py          # Database connection and utilities
├── settings.py          # Configuration management
├── schema.sql           # Database schema
├── seed_data.py         # Sample data for testing
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker container configuration
├── docker-compose.yaml  # Multi-container setup
├── LLD.md              # Low-level design documentation
├── all_curl.md         # API testing examples
└── README.md           # This file
```

## 🧪 Testing

The project includes comprehensive API examples in `all_curl.md`. You can also:

1. **Use the interactive API docs**: Visit http://localhost:8000/docs
2. **Run health checks**: `curl http://localhost:8000/health`
3. **Test with sample data**: Use the provided curl examples

## 🚀 Deployment

### Production Deployment

1. **Set environment to production**
   ```env
   ENVIRONMENT=production
   DEBUG=false
   ```

2. **Use production database**
   ```env
   DB_HOST=your-production-db-host
   DB_PASSWORD=secure-password
   ```

3. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Scaling Considerations

- **Database**: Use connection pooling and read replicas for high traffic
- **Caching**: Implement Redis for seat availability and event data
- **Load Balancing**: Use multiple API instances behind a load balancer
- **Monitoring**: Add logging, metrics, and health monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- **Repository**: https://github.com/rakshit-2/Epicly
- **API Documentation**: http://localhost:8000/docs (when running)
- **Issues**: https://github.com/rakshit-2/Epicly/issues

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the examples in `all_curl.md`

---

**Built with ❤️ using FastAPI and PostgreSQL**
