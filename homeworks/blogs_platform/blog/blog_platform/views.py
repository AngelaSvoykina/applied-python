from .models import Post, Comment
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect
from django.utils import timezone



def post_list(request):
    posts = Post.objects.filter(is_hidden=False).order_by('published_date')
    return render(request, 'blog_platform/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=pk).order_by('created_date')
    return render(request, 'blog_platform/post_detail.html', {'post': post, 'comments': comments})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog_platform/post_edit.html', {'form': form})
