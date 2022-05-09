import datetime
import django
from django.db import models

# Create your models here.


# class Category(models.Model):
#     # id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=100)
#     parent_id = models.IntegerField(default=None)
#     path = models.CharField(max_length=100, default='')
#     full_path = models.CharField(max_length=1000, default='')
#     level = models.SmallIntegerField()
#     state = models.SmallIntegerField(default=1)
#     is_delete = models.SmallIntegerField(default=0)
#     create_time = models.DateTimeField(auto_now=True, db_index=True)
#     update_time = models.DateTimeField(auto_now_add=True, db_index=True)


class Category(models.Model):
    """分类表"""
    CATEGORY_ID = models.IntegerField(primary_key=True)
    CATEGORY_NAME = models.CharField(max_length=1000)
    PARENT_ID = models.IntegerField()
    PATH = models.CharField(max_length=1000)
    LEVEL = models.IntegerField()
    STATE = models.CharField(max_length=2)
    UPDATE_DT = models.DateTimeField()
    IS_DELETE = models.IntegerField()
    FULL_PATH = models.CharField(max_length=1000)

    class Meta:
        db_table = 'source_category'


class SourceBase(models.Model):
    """源表"""
    SOURCE_ID = models.BigIntegerField(primary_key=True)
    SOURCE_NAME = models.CharField(max_length=1000)
    SOURCE_URL = models.CharField(max_length=1000)
    SOURCE_SITE = models.CharField(max_length=1000)
    SOURCE_DESC = models.CharField(max_length=1000)
    SOURCE_TYPE = models.SmallIntegerField()
    SNATCH_TYPE = models.CharField(max_length=1000)
    SOURCE_PARAM = models.CharField(max_length=1000)
    CATEGORY_ID = models.IntegerField()
    CONFIG_ID = models.BigIntegerField()
    CONFIG_ID2 = models.BigIntegerField(default=0)
    CONFIG_ID3 = models.BigIntegerField()
    CLASSIFY = models.CharField(max_length=1000)
    CLASSIFY_SUB = models.CharField(max_length=1000)
    TAGS = models.CharField(max_length=1000)
    DOMAIN = models.CharField(max_length=1000)
    REMARK = models.CharField(max_length=1000)
    SCHEDULE = models.CharField(max_length=1000)
    PRIORITY = models.SmallIntegerField(default=50)
    IS_DELETE = models.SmallIntegerField()
    STATE = models.CharField(max_length=2)
    UPDATE_DT = models.DateTimeField()
    CREATE_DT = models.DateTimeField()
    NEED_CONTENT = models.CharField(max_length=1000)
    XPATH1 = models.CharField(max_length=1000)
    XPATH2 = models.CharField(max_length=1000)
    EXT_ID = models.IntegerField()
    TEMPLET_CODE = models.CharField(max_length=1000)
    LAST_RUN = models.DateTimeField()
    LAST_SUCCESS = models.DateTimeField()
    DATA_CNT = models.IntegerField()
    GROUP_ID = models.CharField(max_length=1000)
    GROUPS = models.CharField(max_length=1000)
    ERROR_CODE = models.CharField(max_length=1000)
    VER = models.DateTimeField()

    class Meta:
        db_table = 'source_base'


class Source2Category(models.Model):
    """源和分类关系表，多对多"""
    SOURCE_ID = models.BigIntegerField(primary_key=True)
    CATEGORY_ID = models.BigIntegerField()
    SEQ = models.IntegerField()
    TYPE = models.CharField(max_length=10)
    UPDATE_DT = models.DateTimeField(default=django.utils.timezone.now)

    class Meta:

        unique_together = (("SOURCE_ID", "CATEGORY_ID"),)
        db_table = 'source_2_category'


class Source2Timer(models.Model):
    SOURCE_ID = models.IntegerField(primary_key=True)
    TIMER_ID = models.CharField(max_length=100)
    TIMER_TYPE = models.CharField(max_length=1000)
    TIMER_EXP = models.CharField(max_length=1000)
    UPDATE_DT = models.DateTimeField()

    class Meta:

        unique_together = (("SOURCE_ID", "TIMER_ID"),)
        db_table = 'source_2_timer'


class ConfigBase(models.Model):
    """消息队列表"""
    CONFIG_ID = models.BigIntegerField(primary_key=True)
    CONFIG_NAME = models.CharField(max_length=1000)
    CONFIG_URL = models.CharField(max_length=1000)
    TEMPLET_CODE = models.CharField(max_length=1000)
    CONFIG_TYPE = models.SmallIntegerField()
    TABLE_ID = models.IntegerField()
    NEED_XPATH = models.IntegerField()
    SEND_TOPIC = models.CharField(max_length=1000)
    NEED_MANUAL = models.IntegerField()
    CORE_PARAM = models.TextField()
    PROXY_CONF = models.CharField(max_length=1000)
    SNATCH_CONF = models.TextField()
    DEFAULT_CATE = models.CharField(max_length=1000)
    URL_RULE = models.CharField(max_length=1000)
    ON_DUPLICATE = models.CharField(max_length=1000)
    CODE_RULE = models.TextField()
    CONTENT_RULE = models.TextField()
    CHECK_RULE = models.TextField()
    DOMAIN = models.CharField(max_length=1000)
    REMARK = models.CharField(max_length=1000)
    STATE = models.CharField(max_length=1000)
    IS_DELETE = models.SmallIntegerField(default=0)
    UPDATE_DT = models.DateTimeField()
    CREATE_DT = models.DateTimeField()

    class Meta:
        db_table = 'config_base'


class SourceState(models.Model):
    """任务状态表"""
    id = models.IntegerField(primary_key=True)
    state = models.CharField(max_length=2)
    remark = models.CharField(max_length=500)
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'source_state'
