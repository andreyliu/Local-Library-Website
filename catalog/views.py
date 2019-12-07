import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from dal import autocomplete

from .models import Book, BookInstance, Author, Language, Genre
from catalog.forms import RenewBookForm, ChangeBookStatusForm, BookForm


# @login_required
def index(request):
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_instances_avail = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_languages = Language.objects.count()

    num_novels = Book.objects.filter(genre__name__iexact='novel').count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_avail,
        'num_authors': num_authors,
        'num_languages': num_languages,
        'num_novels': num_novels,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    paginate_by = 10


class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    paginate_by = 10


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects\
            .filter(borrower=self.request.user)\
            .filter(status__exact='o')\
            .order_by('due_back')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(LoanedBooksByUserListView, self).get_context_data(**kwargs)
        num_overdue = self.get_queryset().filter(due_back__lt=datetime.date.today()).count()
        context['num_overdue'] = num_overdue
        return context


class LoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/loaned_librarian.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects\
            .filter(status__exact='o')\
            .order_by('due_back')


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        default_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': default_renewal_date})

    context = {
     'form': form,
     'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def manage_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = ChangeBookStatusForm(request.POST)

        if form.is_valid():
            status = form.cleaned_data['status']
            book_instance.status = status
            if book_instance.status == 'o':
                book_instance.borrower = form.cleaned_data['borrower']
                book_instance.due_back = form.cleaned_data['due_back']
            book_instance.save()
            return HttpResponseRedirect(reverse('book-detail', kwargs={'pk': book_instance.book.pk}))

    else:
        form = ChangeBookStatusForm()

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_manage_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_maintain'
    model = Author
    fields = '__all__'
    success_url = reverse_lazy('authors')


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_maintain'
    model = Author
    fields = '__all__'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_maintain'
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_maintain'
    model = Book
    template_name = 'catalog/book_form.html'
    form_class = BookForm
    # fields = '__all__'
    # fields = ['title', 'author', 'summary', 'isbn', 'genre']

    def get_object(self, queryset=None):
        return Author.objects.first()


class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_maintain'
    model = Book
    template_name = 'catalog/book_form.html'
    form_class = BookForm
    # fields = '__all__'


class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_maintain'
    model = Book
    success_url = reverse_lazy('books')


class AuthorAutoComplete(PermissionRequiredMixin, autocomplete.Select2QuerySetView):

    permission_required = 'catalog.can_maintain'

    def get_queryset(self):

        if self.q:
            if ' ' not in self.q:
                qs = Author.objects.all()\
                    .filter(Q(first_name__istartswith=self.q) | Q(last_name__istartswith=self.q))
            else:
                names = self.q.split(' ')
                qs = Author.objects.all() \
                    .filter(Q(first_name__istartswith=names[0]) | Q(last_name__istartswith=names[1]))

        else:
            qs = Author.objects.all()

        return qs


class GenreAutoComplete(PermissionRequiredMixin, autocomplete.Select2QuerySetView):

    permission_required = 'catalog.can_maintain'

    def get_queryset(self):
        qs = Genre.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class UserIdAutoComplete(PermissionRequiredMixin, autocomplete.Select2QuerySetView):

    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        qs = User.objects.all()

        if self.q:
            qs = qs.filter(username__istartswith=self.q)

        return qs
