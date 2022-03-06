from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Category, PostCategory
from .filters import PostFilter
from datetime import datetime
from .forms import PostForm
from .tasks import send_mail_for_sub_once


class PostList(ListView):
    model = Post
    template_name = 'flatpages/news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-dateCreation')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filter'] = PostFilter(
            self.request.GET, queryset=self.get_queryset())
        return context


class PostDetail(DetailView):
    model = Post, PostCategory
    template_name = 'flatpages/post.html'
    queryset = Post.objects.all()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs.get('pk')
        qwe = Category.objects.filter(pk=Post.objects.get(pk=id).postCategory.id).values("subscribers__username")
        context['is_not_subscribe'] = not qwe.filter(subscribers__username=self.request.user).exists()
        context['is_subscribe'] = qwe.filter(subscribers__username=self.request.user).exists()
        return context

class PostSearch(PostList):
    template_name = 'flatpages/search.html'
    context_object_name = 'search'
    filter_class = PostFilter


    def get_filter(self):
        return PostFilter(self.request.GET, queryset=super().get_queryset())


    def get_queryset(self):
        return self.get_filter().qs



class PostCreate(LoginRequiredMixin, CreateView):
    template_name = 'flatpages/add.html'
    form_class = PostForm

class PostUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'flatpages/edit.html'
    form_class = PostForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


# дженерик для удаления товара
class PostDelete(LoginRequiredMixin, DeleteView):
    template_name = 'flatpages/delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'


@login_required
def add_subscribe(request, **kwargs):
    pk = request.GET.get('pk', )
    print('Пользователь', request.user, 'добавлен в подписчики категории:', Category.objects.get(pk=pk))
    Category.objects.get(pk=pk).subscribers.add(request.user)
    return redirect('/news/')



@login_required
def del_subscribe(request, **kwargs):
    pk = request.GET.get('pk', )
    print('Пользователь', request.user, 'удален из подписчиков категории:', Category.objects.get(pk=pk))
    Category.objects.get(pk=pk).subscribers.remove(request.user)
    return redirect('/news/')

def send_mail_for_sub(instance):
    print('Представления - начало')
    print()
    print()
    print('====================ПРОВЕРКА СИГНАЛОВ===========================')
    print()
    print('задача - отправка письма подписчикам при добавлении новой статьи')

    sub_text = instance.text
    category = Category.objects.get(pk=Post.objects.get(pk=instance.pk).postCategory.pk)
    print()
    print('category:', category)
    print()
    subscribers = category.subscribers.all()

    print('Адреса рассылки:')
    for qaz in subscribers:
        print(qaz.email)

    print()
    print()
    print()
    for subscriber in subscribers:
        print('**********************', subscriber.email, '**********************')
        print(subscriber)
        print('Адресат:', subscriber.email)

        html_content = render_to_string(
            'mail.html', {'user': subscriber, 'text': sub_text[:50], 'post': instance})

        sub_username = subscriber.username
        sub_useremail = subscriber.email

        print()
        print(html_content)
        print()

        send_mail_for_sub_once.delay(sub_username, sub_useremail, html_content)



    print('Представления - конец')

    return redirect('/news/')
