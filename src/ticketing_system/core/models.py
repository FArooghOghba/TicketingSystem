from django.db import models
from django.db.models.query import F, Q
from django.utils import timezone


class BaseModel(models.Model):

    """
    Base model that includes common fields used across multiple models.

    Fields:
    - created_at: DateTimeField representing the creation timestamp.
    - updated_at: DateTimeField representing the last update timestamp.

    Note: This model is abstract and serves as a base for other models.
    """

    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
