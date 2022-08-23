from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.messages.views import SuccessMessageMixin
from .tasks import send_mail_to_admin, notification_to_user
from bs4 import BeautifulSoup
import requests

from catalog.forms import RegisterForm, ContactForm, CommentForm
from catalog.models import Quote, Comment

from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponseRedirect
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
    paginate_by = 20


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
    fields = ["first_name", "last_name", "email"]
    template_name = 'registration/update_profile.html'
    success_url = reverse_lazy("index")
    success_message = "Profile updated"

    def get_object(self, queryset=None):
        user = self.request.user
        return user


class UserProfile(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = "registration/profile.html"


    def get_object(self, queryset=None):
        user = self.request.user
        return user


class QuoteCreate(LoginRequiredMixin, generic.CreateView):
    model = Quote
    fields = ["heading", "message", "status"]
    template_name = 'catalog/create_post.html'
    success_url = reverse_lazy("my_posts")

    def form_valid(self, form):
        form.instance.author = self.request.user
        text = f"{form.instance.author} create new post right now!"
        send_mail_to_admin.delay(text)
        return super().form_valid(form)



class QuoteListView(generic.ListView):
    model = Quote
    template_name = 'catalog/quote_list.html'
    paginate_by = 10
    queryset = Quote.objects.filter(status="published").all()


def user_info(request, id):
    """Information abut just one author"""
    user = User.objects.get(id=id)
    quote_user = Quote.objects.select_related('author').filter(author_id=id, status='published')
    return render(
        request,
        'catalog/detail_user.html',
        {'name': user.username,
         'email': user.email,
         'quotes': quote_user
         }
    )


class LoanedQuotesByUserListView(LoginRequiredMixin, generic.ListView):
    model = Quote
    template_name = 'catalog/my_posts.html'
    paginate_by = 10

    def get_queryset(self):
        return Quote.objects.filter(
            author=self.request.user
        )


class QuoteChange(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Quote
    fields = ["heading", "message", "status"]
    template_name = 'catalog/change_my_post.html'
    success_url = reverse_lazy("my_posts")
    success_message = "Quote updated"


def contact_form(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message']
            send_mail_to_admin.delay(subject, message, from_email)
            messages.add_message(request, messages.SUCCESS, 'Message sent')
            try:
                send_mail(subject, message, from_email, ['admin@example.com'])
                messages.add_message(request, messages.SUCCESS, 'Message sent')
            except BadHeaderError:
                messages.add_message(request, messages.ERROR, 'Message not sent')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(
        request,
        "catalog/contact.html",
        context={
            "form": form,
        }
    )


def detail_post(request, pk):
    post = get_object_or_404(Quote, pk=pk, status='published')
    comments = post.comments.filter(published=True)
    page = request.GET.get('page', 1)
    paginator = Paginator(comments, 5)
    page_obj = paginator.page(page)
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            text = f'New comment to post {post.heading} by {post.author} from {new_comment.name}'
            send_mail_to_admin.delay(text)
            url = request.build_absolute_uri()
            r = requests.get(url)
            s = BeautifulSoup(r.content, 'html.parser')
            url_part = s.find("div", {'class': "col-sm-10"}).a.get('href')
            url_user = 'http://127.0.0.1:8000' + url_part
            user_request = requests.get(url_user)
            s2 = BeautifulSoup(user_request.content, 'html.parser')
            user_email = s2.find("ul", {'class': "email"}).get_text()
            message = f'You get new comment to your post {post.heading} {url} from {new_comment.name}'
            notification_to_user.delay(message, user_email)

    else:
        comment_form = CommentForm()
    return render(request,
                  'catalog/detail_post.html',
                  {'post': post,
                   'comments': comments,
                   'comment_form': comment_form,
                   'page_obj': page_obj
                   }
                  )
