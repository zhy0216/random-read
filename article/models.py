from django.db import models
from django.contrib.auth.models import User

from utils import redis_conn

'''
primary means whether the article is the 
first similar article added

'''
class Article(models.Model):
    original_url    = models.CharField(max_length=512)
    title           = models.CharField(max_length=128)
    content         = models.TextField(default="")
    finished        = models.BooleanField(default=False)

    primary         = models.BooleanField(default=False)
    # only exist when primary is false
    primary_article = models.ForeignKey("Article", null=True, blank=True)
    create_time     = models.DateTimeField(auto_now=True)


    ALL_PRIMARY_IDS_KEY = "all-primary-article-id"


    def _catch_image(self):
        from utils.image_crawler import change_image
        change_image(self)

    def to_dict(self, exclude=None):
        exclude = exclude or []
        _dict = {
            "id": str(self.id),
            "original_url": self.original_url,
            "title": self.title,
            "content": self.content,
        }
        for key in exclude:
            del _dict[key]
        return _dict


    def __unicode__(self):
        return "<Article: %s>"%self.title


### user -- article relationship

class UserArticleRelationship(models.Model):
    user            = models.ForeignKey(User)
    article         = models.ForeignKey("Article")
    create_time     = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        unique_together = ('user', 'article',)

    @classmethod
    def get_rs_by_user(cls, user, filters=None):
        filters = filters or {}
        return cls.objects.filter(user=user).filter(**filters)

    @classmethod
    def get_rs_by_user_article(cls, user, article, filters=None):
        filters = filters or {}
        return cls.objects.filter(user=user).filter(**filters).first()

    @classmethod
    def has_rs_between_user_article(cls, user, article):
        return bool(cls.objects.filter(user=user, article=article).first())

class UserPostArticle(UserArticleRelationship):
    # to inbox

    def defer_process(self):
        from readability.readability import Document
        import urllib
        article  = self.article
        if not article.finished:
            html = urllib.urlopen(article.original_url).read()
            article.content = Document(html).summary()
            article.title = Document(html).short_title()
            article._catch_image()
            article.primary = True # TODO
            article.finished = True
            redis_conn.sadd(Article.ALL_PRIMARY_IDS_KEY, article.id)
            article.save()

    def __unicode__(self):
        return "[UserPostArticle: <%s -> %s>]"%(self.user, self.article)


class UserReadArticle(UserArticleRelationship):
    # reading history 
    # advance feature??
    # to nothing only record this value

    def __unicode__(self):
        return "[UserReadArticle: <%s -> %s>]"%(self.user, self.article)


class UserStarArticle(UserArticleRelationship):
    # to star

    def __unicode__(self):
        return "[UserStarArticle: <%s -> %s>]"%(self.user, self.article)

class UserArchiveArticle(UserArticleRelationship):
    '''this is used when user archive a article
       recorded this data, might be useful
    '''
    # archive

class UserRemoveArticle(UserArticleRelationship):
    '''this is used when user delete a article
       recorded this data, might be useful
    '''
    # do nothing
    # 


    def __unicode__(self):
        return "[UserRemoveArticle: <%s -> %s>]"%(self.user, self.article)





