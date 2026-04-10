# Quick Start Guide

## 🎯 Get Started in 5 Minutes

### Windows Users

1. **Run the setup script**
   ```
   setup.bat
   ```

2. **Start the development server**
   ```
   python manage.py runserver
   ```

3. **Access the application**
   - Website: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - Email: admin@ecommerce.com
   - Password: admin123

### macOS/Linux Users

1. **Run the setup script**
   ```bash
   chmod +x setup.sh
   bash setup.sh
   ```

2. **Start the development server**
   ```bash
   python manage.py runserver
   ```

3. **Access the application**
   - Website: http://localhost:8000
   - Admin: http://localhost:8000/admin
   - Email: admin@ecommerce.com
   - Password: admin123

## 🐳 Using Docker

### Quick Start with Docker Compose

```bash
# Build and start containers
docker-compose up --build

# In another terminal, run migrations
docker-compose exec web python manage.py migrate

# Create sample data
docker-compose exec web python manage.py create_sample_data
```

Access: http://localhost:8000

## 📋 Manual Setup

If you prefer to set up manually:

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment file
cp .env.example .env
# Edit .env with your settings

# 4. Run migrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Create sample data
python manage.py create_sample_data

# 7. Collect static files
python manage.py collectstatic

# 8. Run development server
python manage.py runserver
```

## 🔑 Environment Configuration

Before starting, configure your `.env` file:

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
DB_ENGINE=django.db.backends.sqlite3

# Stripe (for payments)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

## 🧪 Testing the API

### Using curl

```bash
# Register a user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "password2": "SecurePass123",
    "first_name": "John"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'

# Get products
curl http://localhost:8000/api/products/

# Get categories
curl http://localhost:8000/api/products/categories/
```

### Using Postman

1. Import the API collection from `postman_collection.json` (to be created)
2. Set base URL to `http://localhost:8000`
3. Test endpoints with provided examples

## 📚 Next Steps

1. **Configure Email** - Update email settings in `.env`
2. **Setup Stripe** - Add Stripe keys for payment processing
3. **Configure Database** - Switch to PostgreSQL for production
4. **Add Custom Templates** - Customize HTML templates for branding
5. **Configure Redis** - For caching and background tasks
6. **Deploy** - Use Gunicorn + Nginx or Docker

## 🆘 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'django'"

**Solution:** Activate virtual environment first
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Issue: "Connection refused" (Database error)

**Solution:** Run migrations
```bash
python manage.py migrate
```

### Issue: "Static files not found"

**Solution:** Collect static files
```bash
python manage.py collectstatic
```

### Issue: Port 8000 already in use

**Solution:** Use a different port
```bash
python manage.py runserver 8001
```

## 📖 Documentation

- Full documentation: See [README.md](README.md)
- API documentation: Available at `/api/` endpoints
- Admin documentation: Django admin provides built-in help

## 💬 Need Help?

- Check the [README.md](README.md) for detailed information
- Review Django documentation: https://docs.djangoproject.com
- Check Django REST Framework docs: https://www.django-rest-framework.org

---

Happy coding! 🚀
