from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'blog'
    verbose_name = 'Blog'
    verbose_name_plural = 'Blogs'

    def ready(self):
        import blog.signals
