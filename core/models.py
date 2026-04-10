from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model for timestamped fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel):
    """Abstract base model with ID and timestamps."""
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
