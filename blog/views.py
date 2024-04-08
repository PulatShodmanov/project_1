from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post, Category, Comment, Trend
from blog.forms import CreatePostForm, UpdatePostForm, CommentForm
from collections import Counter
from django.db.models import Q

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required

def is_superuser(user):
    return user.is_authenticated and user.is_superuser

check_is_superuser = user_passes_test(is_superuser)


def extract_hashtags(text, trends):
    for word in text.split():
        if word[0] == '#':
            trends.append(word[1:])

        return trends
    
def trends_all(request):
    trends = Trend.objects.all()
    return {"trends": trends}

def home(request):

    for trend in Trend.objects.all():
        trend.delete()

    trends = []
    for post in Post.objects.all():
        text = f"{post.name} {post.summary} {post.text}"
        for word in text.split():
            if word[0] == '#':
                trends.append(word[1:])
        

    for trend in Counter(trends).most_common(10):
        Trend.objects.create(hashtag=trend[0], occurences=trend[1])

    if request.method == 'POST':
        query = request.POST.get('query')
        return redirect('blog:search', query=query)

    posts = Post.objects.all()
    posts_sponsored = Post.objects.filter(status=True)

    categories = Category.objects.all()

    data = {
        'posts': posts,
        'posts_sponsored': posts_sponsored,
        'trends_posts': posts[:5],
        'one': posts[:1],
        'three': posts[3:4],
        'two': posts[:2],
        'categories': categories[:6],
    }
    return render(request, 'home.html', data)


def search(request, query):
    posts = Post.objects.filter(
        Q(name__icontains=query) |
        Q(summary__icontains=query) |
        Q(text__icontains=query)
    )
    data = {
        'posts': posts,
    }
    return render(request, 'search.html', data)


def post_detail(request, id):
    post = get_object_or_404(Post, id=id)

    # less then
    # grater than

    privous_post = Post.objects.filter(
        id__lt=post.id).order_by('-created_at').first()
    next_post = Post.objects.filter(
        id__gt=post.id).order_by('-created_at').first()

    comments = post.comment_set.filter(parent=None).order_by("-created_at")
    comments_count = comments.count()

    parent_id = None

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            body = comment_form.cleaned_data['body']
            parent_id_raw = request.POST.get('parent')
            user = request.user
            if parent_id_raw:
                parent_id = int(parent_id_raw)
                try:
                   parent_comment = Comment.objects.get(id=parent_id)
                   print(parent_comment)
                   new_comment = Comment(
                       user=user, post=post, body=body, parent=parent_comment)
                except Comment.DoesNotExist:
                    pass
            else:
                new_comment = Comment(
                    user=user, post=post, body=body, parent=None)
            new_comment.save()
            return redirect('blog:post_detail', id=post.id)
    else:
        comment_form = CommentForm()

    data = {
        'post': post,
        'comments': comments,
        'comments_count': comments_count,
        'comment_form': comment_form,
        'privous_post': privous_post,
        'next_post': next_post,
    }

    return render(request, 'posts/post_detail.html', data)

@login_required
@check_is_superuser
def post_created(request):

    

    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES)
        user = request.user
        if form.is_valid():
            name = form.cleaned_data['name']
            summary = form.cleaned_data['summary']
            text = form.cleaned_data['text']
            image = form.cleaned_data['image']
            category = form.cleaned_data['category']
            
            post = Post.objects.create(
                name=name,
                summary=summary,
                author=user,
                text=text,
                img=image,
                category=category,
            )
            return redirect('user:dashboard', id=user.id)
    else:
        form = CreatePostForm()


    data = {
        'form': form,
    }

    return render(request, 'posts/post-create.html', data)

@login_required
@check_is_superuser
def post_update(request, id):
    post = get_object_or_404(Post, id=id)

    if request.method == 'POST':
        form = UpdatePostForm(request.POST, request.FILES, instance=post)
        user = request.user
        if form.is_valid():
            post = form.save(commit=False)
            post.img = form.cleaned_data['image']
            post.author = user
            post.save()
            return redirect('user:dashboard', id=user.id)
    else:
        form = UpdatePostForm(instance=post)

    data = {'form': form}
    return render(request, 'posts/post-create.html', data)

@login_required
@check_is_superuser
def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect('user:dashboard', id=request.user.id)