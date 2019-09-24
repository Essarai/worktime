from django.db import models
from tinymce.models import HTMLField

# Create your models here.
class Student(models.Model):

    status_choices1 = (
        (0, '技术开发部'),
        (1, '秘书部'),
        (2, '编辑部'),
        (3, '管理部'),
        (4, '部门5'),
        (5, '部门6'),
        (6, '部门7'),
        (7, '部门8')
    )

    status_choices2 = (
        (0, '总队'),
        (1, '副总队'),
        (2, '部长'),
        (3, '副部长'),
        (4, '队员'),
    )

    Student_id  = models.CharField(primary_key=True, max_length=11, verbose_name='学号')
    Student_name =models.CharField(max_length=32,verbose_name='姓名')
    Student_department = models.SmallIntegerField(default=0,choices=status_choices1,verbose_name='部门')
    Student_position = models.SmallIntegerField(default=0,choices=status_choices2,verbose_name='职位')

    class Meta:
        db_table = 'student_test'
        #         verbose_name = '学生表'
        #         verbose_name_plural = verbose_name


class Work(models.Model):
    work= models.ForeignKey('Student', on_delete=models.CASCADE)
    which_week = models.SmallIntegerField(default=1,verbose_name='第几周')
    work_times = models.FloatField(default=0.0, verbose_name='工作时长')
    work_details = HTMLField(verbose_name='工作详情')
    work_is_activate = models.BooleanField(default=False,verbose_name='是否审核通过')

    class Meta:
        db_table = 'worktime_test'
        unique_together = (("work", "which_week"),)
        #         verbose_name = '工作量表'
        #         verbose_name_plural = verbose_name
