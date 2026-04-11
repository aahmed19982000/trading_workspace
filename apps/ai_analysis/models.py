from django.db import models


class AIAnalysis(models.Model):
    ANALYSIS_TYPES = (
        ('strategy', 'تحليل استراتيجية'),
        ('risk', 'تحليل مخاطر'),
        ('performance', 'تحليل أداء'),
        ('market', 'تحليل سوق'),
    )

    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='ai_analyses',
        verbose_name='المستخدم',
    )
    strategy = models.ForeignKey(
        'strategies.Strategy',
        on_delete=models.CASCADE,
        related_name='ai_analyses',
        verbose_name='الاستراتيجية',
    )
    trading_account = models.ForeignKey(
        'trading.TradingAccount',
        on_delete=models.SET_NULL,
        related_name='ai_analyses',
        null=True,
        blank=True,
        verbose_name='حساب التداول',
    )
    analysis_type = models.CharField(
        'نوع التحليل',
        max_length=20,
        choices=ANALYSIS_TYPES,
        default='strategy',
    )
    prompt = models.TextField('الطلب المرسل للذكاء الاصطناعي')
    analysis_result = models.JSONField('نتيجة التحليل', default=dict, blank=True)
    confidence_score = models.DecimalField(
        'درجة الثقة',
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    risk_score = models.DecimalField(
        'درجة المخاطرة',
        max_digits=5,
        decimal_places=2,
        default=0,
    )
    recommendations = models.JSONField('التوصيات', default=list, blank=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    def __str__(self):
        return f'{self.get_analysis_type_display()} - {self.strategy.title}'

    class Meta:
        verbose_name = 'تحليل ذكاء اصطناعي'
        verbose_name_plural = 'تحليلات الذكاء الاصطناعي'
