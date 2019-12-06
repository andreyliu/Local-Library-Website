from django.test import TestCase
from catalog.models import Author


class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Author.objects.create(first_name='Big', last_name='Bob')

    @staticmethod
    def author():
        return Author.objects.get(id=1)

    def test_first_name_label(self):
        author = self.author()
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEquals('first name', field_label)

    def test_last_name_label(self):
        author = self.author()
        label = author._meta.get_field('last_name').verbose_name
        self.assertEquals('last name', label)

    def test_date_of_death_label(self):
        author = self.author()
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEquals('died', field_label)

    def test_date_of_birth_label(self):
        author = self.author()
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEqual('date of birth', field_label)

    def test_first_name_max_length(self):
        author = self.author()
        max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(max_length, 100)

    def test_last_name_max_length(self):
        author = self.author()
        max_length = author._meta.get_field('last_name').max_length
        self.assertEqual(100, max_length)

    def test_object_name_is_format(self):
        author = self.author()
        expected_name = f'{author.last_name}, {author.first_name}'
        self.assertEquals(expected_name, str(author))

    def test_get_absolute_url(self):
        author = self.author()
        self.assertEquals('/catalog/author/1', author.get_absolute_url())


