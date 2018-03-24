import random
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.contrib import auth
from django.utils import timezone
from main import models

class Command(BaseCommand):
    help = (
        'Generate demo data (list of super-users, staff-users and '
        'issues of all categories), and populate it into the database. ')

    def add_arguments(self, parser):
        parser.add_argument(
            '--num_superusers', type=int, default=10,
            help=(
                'Number of populated superusers excluding main superuser '
                'admin/admin which is always created. These generated '
                'superusers will have adminuserN as both login and password, '
                'where N is a number from 1 to num_superusers.'))
        parser.add_argument(
            '--num_staffusers', type=int, default=10,
            help=(
                'Number of populated staffusers. These generated '
                'staffusers will have staffuserN as both login and password, '
                'where N is a number from 1 to num_staffuser.'))
        parser.add_argument(
            '--num_issues', type=int, default=1000,
            help='Number of populated issues.')

    def handle(self, *args, **options):
        user_model = auth.get_user_model()
        for idx in range(1, 1+options['num_superusers']):
            username = 'adminuser%s' % idx
            password = 'adminuser%s' % idx
            user_model.objects.create_user(
                username, password, is_staff=True, is_superuser=True)
        self.stdout.write('Added %s super-user(s).' % options['num_superusers'])
        for idx in range(1, 1+options['num_staffusers']):
            username = 'staffuser%s' % idx
            password = 'staffuser%s' % idx
            user_model.objects.create_user(
                username, password, is_staff=True)
        self.stdout.write('Added %s staff-user(s).' % options['num_staffusers'])
        superuser_ids = user_model.objects.filter(
            is_active=True, is_superuser=True).values_list('id', flat=True)
        categories = list(models.CATEGORIES.items())
        statuses = list(models.STATUSES.items())
        tzinfo = timezone.get_current_timezone()
        cur_datetime = datetime.datetime.now(tz=tzinfo)
        for idx in range(1, 1+options['num_issues']):
            # Generate random datetime between yesterday and 1 year back.
            random_timedelta = datetime.timedelta(seconds=random.randrange(
                datetime.timedelta(days=1).total_seconds(),
                datetime.timedelta(days=365).total_seconds()))
            filed_at = cur_datetime - random_timedelta
            category_name, category_id = random.choice(categories)
            status_name, status_id = random.choice(statuses)
            title = '%s %s' % (category_name, idx)
            description = 'This is the description for issue "%s"' % title
            if status_name.startswith('Closed'):
                # Generate random datetime between
                # filed_at + 1 hour and 1 month after.
                # If the new datetime is in future, assign to current datetime.
                random_timedelta = datetime.timedelta(seconds=random.randrange(
                    datetime.timedelta(hours=1).total_seconds(),
                    datetime.timedelta(days=30).total_seconds()))
                closed_at = filed_at + random_timedelta
                if closed_at > cur_datetime:
                    closed_at = cur_datetime
            else:
                closed_at = None
            if status_name != 'Open':
                assignee_id = random.choice(superuser_ids)
            else:
                assignee_id = None
            issue = models.Issue.objects.create(
                filer_id=random.choice(superuser_ids),
                assignee_id=assignee_id,
                title=title,
                description=description,
                category=category_id,
                status=status_id,
                closed_at=closed_at)
            issue.filed_at = filed_at
            issue.save()
        self.stdout.write('Added %s issue(s).' % options['num_issues'])
