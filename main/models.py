import datetime

from django.conf import settings
from django.db import models


CATEGORIES = {
    'Bug': 1,
    'Enhancement': 2,
    'Documentation': 3,
}

STATUSES = {
    'Open': 1,
    'More information requested': 10,
    'Work in progress': 20,
    'Duplicate': 30,
    'Delivered': 40,
    'Failed verification': 50,
    'Closed, verified': 60,
    'Closed, not verified': 61,
}

class Issue(models.Model):
    """
    Model representing Issue in this minimalistic issue tracker.
    """

    filed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    filer = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='filer_set',
        on_delete=models.SET_NULL, null=True)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='assignee_set',
        on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    category = models.PositiveSmallIntegerField(
        choices=tuple((v, k) for k, v in CATEGORIES.items()),
        default=CATEGORIES['Bug'])
    status = models.PositiveSmallIntegerField(
        choices=tuple((v, k) for k, v in STATUSES.items()),
        default=STATUSES['Open'])
    last_modified_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(blank=True, null=True, db_index=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_status = self.status

    def __str__(self):
        return self.title

    def close_as_verified(self):
        """
        Assigns current datetime to self.closed_at,
        change status to 'Closed, verified' and save to DB.
        """
        self.status = STATUSES['Closed, verified']
        self.save()

    def close_as_notverified(self):
        """
        Assigns current datetime to self.closed_at,
        change status to 'Closed, not verified' and save to DB.
        """
        self.status = STATUSES['Closed, verified']
        self.save()

    def reopen(self):
        """
        Re-open issue by changing its status to 'Open'.
        """
        self.status = STATUSES['Open']
        self.save()

    def save(self, *args, **kwargs):
        # Assigning current datetime to closed_at if status changed
        # from anything to Closed.
        closed_statuses = [
            STATUSES['Closed, verified'], STATUSES['Closed, not verified']]
        if (self.status in closed_statuses and
                self.status != self.__original_status):
            self.closed_at = datetime.datetime.now()
        super().save(*args, **kwargs)
