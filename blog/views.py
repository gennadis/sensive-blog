from django.db.models import Count
from django.shortcuts import render
from blog.models import Comment, Post, Tag


def get_related_posts_count(tag):
    return tag.posts.count()


def serialize_post_optimized(post):
    return {
        "title": post.title,
        "teaser_text": post.text[:200],
        "author": post.author.username,
        "comments_amount": post.comments_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": post.tags.all(),
        "first_tag_title": post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {"title": tag.title, "posts_with_tag": tag.posts_with_tag}


def index(request):
    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related("author", "tags")[:5]
        .fetch_with_comments_count()
    )

    fresh_posts = Post.objects.prefetch_related("author", "tags").annotate(
        comments_count=Count("comments")
    )

    most_fresh_posts = fresh_posts.order_by("-published_at")[:5]

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        "most_popular_posts": [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
        "page_posts": [serialize_post_optimized(post) for post in most_fresh_posts],
        "popular_tags": most_popular_tags,
    }
    return render(request, "index.html", context)


def post_detail(request, slug):
    posts = Post.objects.popular().prefetch_related("author", "comments")
    most_popular_posts = posts[:5].fetch_with_comments_count()

    comments = Comment.objects.all().prefetch_related("author")

    post = posts.get(slug=slug)
    serialized_post = {
        "title": post.title,
        "text": post.text,
        "author": post.author.username,
        "comments": comments.filter(post=post),
        "likes_amount": post.likes_count,
        "image_url": post.image.url if post.image else None,
        "published_at": post.published_at,
        "slug": post.slug,
        "tags": post.tags.all(),
    }

    tags = Tag.objects.popular()
    most_popular_tags = tags[:5]

    context = {
        "post": serialized_post,
        "popular_tags": most_popular_tags,
        "most_popular_posts": most_popular_posts,
    }
    return render(request, "post-details.html", context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]

    most_popular_posts = (
        Post.objects.popular()
        .prefetch_related("author")[:5]
        .fetch_with_comments_count()
    )

    related_posts = tag.posts.all()[:20]

    context = {
        "tag": tag.title,
        "popular_tags": most_popular_tags,
        "posts": related_posts,
        "most_popular_posts": [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, "posts-list.html", context)


def contacts(request):
    # ?????????? ?????????? ?????????? ?????? ?????? ???????????????????? ?????????????? ???? ?????? ????????????????
    # ?? ?????? ???????????? ??????????????
    return render(request, "contacts.html", {})
