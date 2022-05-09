from django.db import models

# Create your models here.


class Docs(models.Model):
    id = models.AutoField(primary_key=True)
    project = models.CharField(max_length=1000)
    title = models.CharField(max_length=1000)
    author = models.CharField(max_length=1000)
    created_at = models.DateField()
    link = models.TextField()
    doc_type = models.CharField(max_length=100)
    state = models.SmallIntegerField(default=0)
    display = models.SmallIntegerField(default=1)
    create_time = models.DateTimeField(auto_now=True, db_index=True)
    update_time = models.DateTimeField(auto_now_add=True, db_index=True)

    # class Meta:
    #     app_label = 'crawler_studio_be'
    #     verbose_name = '文档表'
    #     db_table = 'docs'


class DocsType(models.Model):
    id = models.AutoField(primary_key=True)
    doc_type = models.CharField(max_length=100)
    state = models.SmallIntegerField(default=0)

    # class Meta:
    #     app_label = 'crawler_studio_be'
    #     verbose_name = '文档类型表'
    #     db_table = 'docs_type'
