from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.messages.views import SuccessMessageMixin
from .tasks import send_mail_to_admin, notification_to_user, contact_us
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string

from catalog.forms import RegisterForm, ContactForm, CommentForm
from catalog.models import Quote

from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic

User = get_user_model()


def index(request):
    num_users = User.objects.all().count()
    num_quotes = Quote.objects.filter(status="published").all().count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        'catalog/index.html',
        context={
            'num_users': num_users,
            'num_quotes': num_quotes,
            'num_visits': num_visits,
        },
    )


class UserListView(generic.ListView):
    model = User
    template_name = 'catalog/users_list.html'
    paginate_by = 8


class RegisterFormView(generic.FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save()
        user = authenticate(username=user.username, password=form.cleaned_data.get("password1"))
        login(self.request, user)
        return super(RegisterFormView, self).form_valid(form)


class UpdateProfile(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = User
    fields = ['username', "first_name", "last_name", "email"]
    template_name = 'registration/update_profile.html'
    success_url = reverse_lazy("profile")
    success_message = "Profile updated successfully!"

    def get_object(self, queryset=None):
        user = self.request.user
        return user


class UserProfile(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = "registration/profile.html"

    def get_object(self, queryset=None):
        user = self.request.user
        return user


class QuoteCreate(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Quote
    fields = ["heading", 'description', "message", 'image', "status"]
    template_name = 'catalog/create_post.html'
    success_url = reverse_lazy("my_posts")
    success_message = "Create new post successfully!"

    def form_valid(self, form):
        form.instance.author = self.request.user
        text = f"{form.instance.author} create new post right now!"
        send_mail_to_admin.delay(text)
        return super().form_valid(form)


class QuoteDelete(LoginRequiredMixin, SuccessMessageMixin, generic.DeleteView):
    model = Quote
    template_name = 'catalog/delete_post.html'
    success_message = "Quote was deleted successfully!"
    success_url = reverse_lazy('my_posts')


class QuoteListView(generic.ListView):
    model = Quote
    template_name = 'catalog/quote_list.html'
    paginate_by = 10
    queryset = Quote.objects.filter(status="published").all()


def user_info(request, id):
    """Information abut just one author"""
    user = User.objects.get(id=id)
    quote_user = Quote.objects.select_related('author').filter(author_id=id, status='published')
    paginator = Paginator(quote_user, 5)
    page_num = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_num)
    except EmptyPage:
        raise Http404()
    except PageNotAnInteger:
        raise Http404()
    return render(
        request,
        'catalog/detail_user.html',
        {'username': user.username,
         'first_name': user.first_name,
         'last_name': user.last_name,
         'email': user.email,
         'quote_user': quote_user,
         'page_obj': page_obj
         }
    )


class LoanedQuotesByUserListView(LoginRequiredMixin, generic.ListView):
    model = Quote
    template_name = 'catalog/my_posts.html'
    paginate_by = 5

    def get_queryset(self):
        return Quote.objects.filter(
            author=self.request.user
        )


class QuoteChange(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Quote
    fields = ["heading", "message", "status", 'description', 'image']
    template_name = 'catalog/change_my_post.html'
    success_url = reverse_lazy("my_posts")
    success_message = "Quote updated successfully!"


def contact(request):
    data = dict()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            data['form_is_valid'] = True
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            messages.add_message(request, messages.SUCCESS, 'Message was sent successfully!')
            contact_us.delay(subject, message, from_email)
            data['contact_form'] = render_to_string('base_site.html')
        else:
            data['form_is_valid'] = False
    else:
        form = ContactForm()
    context = {'form': form}
    data['html_form'] = render_to_string('catalog/contact.html', context, request=request)
    return JsonResponse(data)

def detail_post(request, pk):
    post = get_object_or_404(Quote, pk=pk, status='published')
    author = post.author
    comments = post.comments.filter(published=True)
    paginator = Paginator(comments, 5)
    page_num = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_num)
    except EmptyPage:
        raise Http404()
    except PageNotAnInteger:
        raise Http404()
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            messages.add_message(request, messages.SUCCESS, 'Create new comment!')
            text = f'New comment to post {post.heading} by {post.author} from {new_comment.name}'
            send_mail_to_admin.delay(text)
            url = request.build_absolute_uri()
            message = f'You get new comment to your post {post.heading} {url} from {new_comment.name}'
            notification_to_user.delay(message, author.email)

    else:
        comment_form = CommentForm()
    return render(request,
                  'catalog/detail_post.html',
                  {'post': post,
                   'comments': comments,
                   'comment_form': comment_form,
                   'page_obj': page_obj,
                   }
                  )
