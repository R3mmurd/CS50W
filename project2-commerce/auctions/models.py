from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        'auctions.Listing',
        related_name='watchers',
        related_query_name='watchers'
    )


class TimestampMixin(models.Model):
    """
    Abstract model to handle created datetime.
    """
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True


class Category(models.Model):
    """
    Model to store categories.
    """
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class Listing(TimestampMixin):
    """
    Model for auction listing.
    """
    title = models.CharField(max_length=100)
    description = models.TextField()
    current_amount = models.DecimalField(decimal_places=2, max_digits=8)
    image_url = models.URLField(null=True)
    active = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='listings_on_category',
        related_query_name='listings_on_category',
        null=True
    )
    listed_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listings',
        related_query_name='listings'
    )

    def __str__(self):
        return f'{self.title} - {self.current_amount}'


class Bid(TimestampMixin):
    """
    Model for bid.
    """
    amount = models.DecimalField(decimal_places=2, max_digits=8)
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='listing_bids',
        related_query_name='listing_bids'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bids',
        related_query_name='bids'
    )

    def __str__(self):
        return (f'Bid on {self.listing.title} by {self.author.username} for '
                f'${self.amount}')


class Comment(TimestampMixin):
    """
    Model for comment on a listing.
    """
    text = models.TextField()
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='listing_comments',
        related_query_name='listing_comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        related_query_name='comments'
    )

    def __str__(self):
        return f'Comment on {self.listing.title} by {self.author.username}'
