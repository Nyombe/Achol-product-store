# E-Commerce Platform - Django

A production-ready, scalable e-commerce platform built with Django and Django REST Framework, designed similarly to Jumia with full payment integration support.

## 🌟 Features

### Core Features
- **Product Management**: Complete product catalog with categories, images, and attributes
- **Price Tracking**: Automatic price history tracking with visualization
- **Shopping Cart**: Session-based cart system with persistent storage
- **Order Management**: Complete order lifecycle management
- **User Authentication**: Secure user registration and authentication with email verification
- **Payment Integration**: Stripe payment gateway with refund support
- **Search & Filtering**: Advanced search, filtering by category and price range
- **Product Reviews**: Customer reviews and ratings system
- **Admin Dashboard**: Comprehensive Django admin interface

### Security Features
- CSRF Protection
- XSS Prevention
- SQL Injection Protection (via Django ORM)
- Secure password hashing (PBKDF2)
- HTTPS/SSL support
- Secure cookie settings
- Input validation and sanitization
- Rate limiting ready
- Secure file uploads

### Technical Architecture
- Django 4.2 with Django REST Framework
- PostgreSQL for production, SQLite for development
- Redis for caching and asynchronous tasks
- Celery for background job processing
- Gunicorn + Nginx for production deployment
- Docker support ready
- API-first design for microservices future

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip and virtualenv
- PostgreSQL (for production)
- Redis (optional, for caching)

### Installation

1. **Clone and setup the project**
```bash
cd Achol
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env file with your settings
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create sample data**
```bash
python manage.py create_sample_data
```

6. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

7. **Run development server**
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

### Admin Access
- URL: `http://localhost:8000/admin`
- Credentials: admin@ecommerce.com / admin123

## 📁 Project Structure

```
Achol/
├── config/                 # Django configuration
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI config
│   └── settings/
│       ├── base.py        # Base settings
│       ├── development.py # Dev settings
│       └── production.py  # Prod settings
├── core/                  # Core app (homepage)
├── users/                 # User authentication & management
├── products/              # Product catalog
├── orders/                # Cart & order management
├── payments/              # Payment processing
├── static/                # Static files
├── templates/             # HTML templates
├── media/                 # User uploads
├── logs/                  # Application logs
├── tests/                 # Test suite
└── manage.py             # Django management script
```

## 🔌 API Endpoints

### Authentication
```
POST   /api/auth/register/          # Register new user
POST   /api/auth/login/             # User login
POST   /api/auth/logout/            # User logout
GET    /api/auth/profile/           # Get user profile
PUT    /api/auth/profile/update/    # Update profile
```

### Products
```
GET    /api/products/               # List all products
GET    /api/products/<slug>/        # Product details
GET    /api/products/<slug>/price-history/  # Price history
GET    /api/products/categories/    # List categories
GET    /api/products/categories/<slug>/    # Category details
```

### Cart
```
GET    /api/orders/cart/            # View cart
POST   /api/orders/cart/add/        # Add to cart
PATCH  /api/orders/cart/items/<id>/ # Update cart item
DELETE /api/orders/cart/items/<id>/ # Remove from cart
```

### Orders
```
GET    /api/orders/                 # User orders
GET    /api/orders/<id>/            # Order details
POST   /api/orders/checkout/        # Create order
```

### Payments
```
POST   /api/payments/process/       # Process payment
GET    /api/payments/methods/       # List payment methods
POST   /api/payments/webhook/stripe/ # Stripe webhook
```

## 🔐 Security Best Practices

### Environment Variables
Always store sensitive configuration in `.env` file:
- `SECRET_KEY`
- `STRIPE_SECRET_KEY`
- Database credentials
- Email passwords

### HTTPS
Enable in production by setting:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### CORS
Configure allowed origins in `CORS_ALLOWED_ORIGINS`

### Database
- Use PostgreSQL in production
- Enable connection pooling
- Regular backups

## 📊 Database Models

### Users App
- `CustomUser` - Extended user model
- `UserPreferences` - User settings and preferences

### Products App
- `Category` - Product categories
- `Product` - Product catalog
- `ProductImage` - Product images
- `PriceHistory` - Price tracking
- `ProductReview` - Customer reviews

### Orders App
- `Cart` - Shopping cart
- `CartItem` - Items in cart
- `Order` - Customer orders
- `OrderItem` - Items in order

### Payments App
- `Payment` - Payment transactions
- `PaymentMethod` - Saved payment methods

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific app tests
pytest products/tests/
```

## 📦 Deployment

### Using Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Using Docker
```dockerfile
# Build image
docker build -t ecommerce .

# Run container
docker run -p 8000:8000 ecommerce
```

### Environment Setup
For production deployment, ensure all variables are configured:
```bash
DEBUG=False
SECRET_KEY=<strong-secret-key>
DB_ENGINE=postgresql
DB_NAME=<database-name>
DB_USER=<database-user>
DB_PASSWORD=<database-password>
DB_HOST=<database-host>
STRIPE_SECRET_KEY=<stripe-key>
```

## 💳 Payment Integration

### Stripe
The platform includes built-in Stripe integration:

1. **Configure Stripe Keys**
   ```
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

2. **Process Payment**
   ```bash
   POST /api/payments/process/
   {
       "order_id": 1,
       "payment_method": "pm_1234567890"
   }
   ```

3. **Webhook Handling**
   Stripe webhooks are automatically handled at `/api/payments/webhook/stripe/`

### Future Integrations
The architecture supports easy integration of:
- PayPal
- Mobile Money (Africa-focused)
- Bank Transfers

## 🛠️ Development Tools

### Management Commands
```bash
# Create sample data
python manage.py create_sample_data

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### Debug Tools
- Django Debug Toolbar enabled in development
- Logging to `/logs/django.log`
- Security logs to `/logs/security.log`

## 📈 Performance Optimization

- Database query optimization with `select_related()` and `prefetch_related()`
- Static file compression with WhiteNoise
- Pagination on all list views
- Redis caching (when configured)
- Database connection pooling
- Index optimization on frequently queried fields

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 📞 Support

For issues, feature requests, or questions, please create an issue on the repository.

## 🚀 Roadmap

- [ ] Frontend React application
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Seller/Vendor system
- [ ] Affiliate program
- [ ] Multi-language support
- [ ] GraphQL API
- [ ] Kubernetes deployment

---

**Built with ❤️ for scalable e-commerce**
