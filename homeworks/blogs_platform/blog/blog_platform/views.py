from .models import Post, Comment
from django.shortcuts import render, get_object_or_404
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from django.utils import timezone
from django.core.paginator import Paginator


def post_list(request):
    popular = request.GET.get('popular')
    if popular:
        posts = Post.objects.filter(is_hidden=False).order_by('-page_views')
    else:
        posts = Post.objects.filter(is_hidden=False).order_by('-created_date')
    return render(request, 'blog_platform/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.page_views += 1
    post.save()

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            # comment.author = request.user
            comment.post = post
            comment.created_date = timezone.now()
            comment.save()
            return redirect('post_detail', pk=pk)

    comments_list = Comment.objects.filter(post=pk).order_by('created_date')
    paginator = Paginator(comments_list, 2)

    page = request.GET.get('page')
    comments = paginator.get_page(page)
    form = CommentForm()
    return render(request, 'blog_platform/post_detail.html', {'post': post, 'comments': comments, 'form': form})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.created_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog_platform/post_edit.html', {'form': form})


def post_search(request):
    if 'search' in request.GET and request.GET.get('search'):
        search = request.GET.get('search')
        posts = Post.objects.filter(title__contains=search)
        return render(request, 'blog_platform/post_search.html', {'posts': posts})
    else:
        return redirect('post_list')