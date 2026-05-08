import os
import django
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from analytics.views import AnalyticsDashboardView
from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.get(username='admin')

request = RequestFactory().get('/management/analytics/')
request.user = admin

view = AnalyticsDashboardView()
view.request = request
try:
    response = view.dispatch(request)
    response.render()
    print("SUCCESS! Rendered", len(response.content), "bytes.")
except Exception as e:
    import traceback
    traceback.print_exc()
