from django.db import models


class Strategy(models.Model):
    STRATEGY_STATUSES = (
        ('draft', 'مسودة'),
        ('active', 'نشطة'),
        ('archived', 'مؤرشفة'),
    )

    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='strategies',
        verbose_name='المستخدم',
    )
    title = models.CharField('العنوان', max_length=200)
    description = models.TextField('الوصف', blank=True)
    market = models.CharField('السوق', max_length=50, blank=True)
    timeframe = models.CharField('الإطار الزمني', max_length=20)
    entry_rules = models.JSONField('قواعد الدخول', default=dict, blank=True)
    exit_rules = models.JSONField('قواعد الخروج', default=dict, blank=True)
    indicators = models.JSONField('المؤشرات', default=list, blank=True)
    status = models.CharField('الحالة', max_length=20, choices=STRATEGY_STATUSES, default='draft')
    version = models.PositiveIntegerField('الإصدار الحالي', default=1)
    is_public = models.BooleanField('متاحة للجميع', default=False)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'استراتيجية'
        verbose_name_plural = 'الاستراتيجيات'


class StrategyVersion(models.Model):
    strategy = models.ForeignKey(
        'strategies.Strategy',
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='الاستراتيجية',
    )
    version_number = models.PositiveIntegerField('رقم الإصدار')
    title_snapshot = models.CharField('عنوان الإصدار', max_length=200)
    description_snapshot = models.TextField('وصف الإصدار', blank=True)
    rules_snapshot = models.JSONField('نسخة القواعد', default=dict, blank=True)
    change_notes = models.TextField('ملاحظات التغيير', blank=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    def __str__(self):
        return f'{self.strategy.title} v{self.version_number}'

    class Meta:
        verbose_name = 'إصدار استراتيجية'
        verbose_name_plural = 'إصدارات الاستراتيجيات'
        unique_together = ('strategy', 'version_number')


class StrategyTemplate(models.Model):
    CATEGORIES = (
        ('scalping', 'سكالبينج'),
        ('day_trading', 'تداول يومي'),
        ('swing', 'سوينج'),
        ('position', 'مركزي'),
        ('custom', 'مخصص'),
    )

    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='strategy_templates',
        null=True,
        blank=True,
        verbose_name='المستخدم',
    )
    name = models.CharField('اسم القالب', max_length=200)
    category = models.CharField('الفئة', max_length=30, choices=CATEGORIES, default='custom')
    description = models.TextField('الوصف', blank=True)
    template_data = models.JSONField('بيانات القالب', default=dict, blank=True)
    is_public = models.BooleanField('قالب عام', default=False)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'قالب استراتيجية'
        verbose_name_plural = 'قوالب الاستراتيجيات'
