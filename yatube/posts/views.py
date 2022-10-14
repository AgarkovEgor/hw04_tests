from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Post, Group, User
from .forms import PostForm


PAGE_CONSTANT = 10


def pagi(post_list, request):
    paginator = Paginator(post_list, PAGE_CONSTANT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    posts = Post.objects.all()
    context = {
        'page_obj': pagi(request=request, post_list=posts),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
        'page_obj': pagi(request=request, post_list=posts),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    context = {
        'page_obj': pagi(request=request, post_list=posts),
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not request.method == 'POST':
        return render(request, 'posts/create_post.html', {'form': form})

    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})

    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if not request.user == post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {'is_edit': True, 'form': form}
    return render(request, 'posts/create_post.html', context)
