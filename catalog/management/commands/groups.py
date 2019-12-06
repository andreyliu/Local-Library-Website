from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand

from catalog.models import BookInstance, Book


class Command(BaseCommand):
    help = 'Creates user groups and assigns relevant permissions'

    def handle(self, *args, **options):

        librarian_group, _ = Group.objects.get_or_create(name='Librarian')

        inst = ContentType.objects.get_for_model(BookInstance)
        mark_return, _ = Permission.objects.get_or_create(codename='can_mark_returned', name='Set book as returned',
                                                          content_type=inst)

        book = ContentType.objects.get_for_model(Book)
        maintain, _ = Permission.objects.get_or_create(codename='can_maintain', name='Can edit book index',
                                                       content_type=book)

        def add_permission(group, perm):
            group.permissions.add(perm)

        add_permission(librarian_group, mark_return)
        add_permission(librarian_group, maintain)
