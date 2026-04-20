from .models import Category

def categories_processor(request):
    """
    Context processor to retrieve all active categories dynamically
    so they can be populated in global headers (like the search bar dropdown)
    across all user-facing views natively.
    """
    return {'global_categories': Category.objects.filter(is_active=True)}
