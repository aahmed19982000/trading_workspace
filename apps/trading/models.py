from django.db import models


class TradingAccount(models.Model):
    ACCOUNT_TYPES = (
        ('demo', 'تجريبي'),
        ('live', 'حقيقي'),
    )
    BROKER_STATUSES = (
        ('active', 'نشط'),
        ('inactive', 'غير نشط'),
        ('suspended', 'موقوف'),
    )

    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='trading_accounts',
        verbose_name='المستخدم',
    )
    broker_name = models.CharField('اسم الوسيط', max_length=100)
    account_id = models.CharField('معرف الحساب', max_length=100, unique=True)
    account_type = models.CharField(
        'نوع الحساب',
        max_length=10,
        choices=ACCOUNT_TYPES,
        default='demo',
    )
    balance = models.DecimalField('الرصيد', max_digits=15, decimal_places=2, default=0)
    equity = models.DecimalField('حقوق الملكية', max_digits=15, decimal_places=2, default=0)
    currency = models.CharField('العملة', max_length=10, default='USD')
    leverage = models.CharField('الرافعة المالية', max_length=20, blank=True)
    server_name = models.CharField('اسم الخادم', max_length=100, blank=True)
    is_connected = models.BooleanField('متصل', default=False)
    status = models.CharField(
        'الحالة',
        max_length=20,
        choices=BROKER_STATUSES,
        default='active',
    )
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    def __str__(self):
        return f'{self.user.email} - {self.account_id}'

    class Meta:
        verbose_name = 'حساب تداول'
        verbose_name_plural = 'حسابات التداول'


class RiskSettings(models.Model):
    account = models.OneToOneField(
        'trading.TradingAccount',
        on_delete=models.CASCADE,
        related_name='risk_settings',
        verbose_name='حساب التداول',
    )
    risk_per_trade = models.DecimalField(
        'نسبة المخاطرة لكل صفقة',
        max_digits=5,
        decimal_places=2,
        default=1.00,
    )
    daily_loss_limit = models.DecimalField(
        'الحد اليومي للخسارة',
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    max_open_trades = models.PositiveIntegerField('أقصى عدد صفقات مفتوحة', default=3)
    position_size_limit = models.DecimalField(
        'الحد الأقصى لحجم الصفقة',
        max_digits=10,
        decimal_places=2,
        default=1.00,
    )
    stop_loss_required = models.BooleanField('إلزامية وقف الخسارة', default=True)
    allow_weekend_holding = models.BooleanField('السماح بالاحتفاظ لعطلة نهاية الأسبوع', default=False)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    def __str__(self):
        return f'Risk settings for {self.account.account_id}'

    class Meta:
        verbose_name = 'إعدادات المخاطر'
        verbose_name_plural = 'إعدادات المخاطر'


class Trade(models.Model):
    ORDER_TYPES = (
        ('buy', 'شراء'),
        ('sell', 'بيع'),
    )
    TRADE_STATUSES = (
        ('pending', 'قيد الانتظار'),
        ('open', 'مفتوحة'),
        ('closed', 'مغلقة'),
        ('cancelled', 'ملغاة'),
        ('failed', 'فشلت'),
    )

    account = models.ForeignKey(
        'trading.TradingAccount',
        on_delete=models.CASCADE,
        related_name='trades',
        verbose_name='حساب التداول',
    )
    strategy = models.ForeignKey(
        'strategies.Strategy',
        on_delete=models.SET_NULL,
        related_name='trades',
        null=True,
        blank=True,
        verbose_name='الاستراتيجية',
    )
    symbol = models.CharField('الرمز', max_length=20)
    order_type = models.CharField('نوع الأمر', max_length=10, choices=ORDER_TYPES)
    volume = models.DecimalField('الحجم', max_digits=10, decimal_places=2)
    entry_price = models.DecimalField('سعر الدخول', max_digits=15, decimal_places=5)
    exit_price = models.DecimalField('سعر الخروج', max_digits=15, decimal_places=5, null=True, blank=True)
    stop_loss = models.DecimalField('وقف الخسارة', max_digits=15, decimal_places=5, null=True, blank=True)
    take_profit = models.DecimalField('جني الأرباح', max_digits=15, decimal_places=5, null=True, blank=True)
    pnl = models.DecimalField('الربح والخسارة', max_digits=15, decimal_places=2, default=0)
    status = models.CharField('الحالة', max_length=20, choices=TRADE_STATUSES, default='pending')
    external_ticket = models.CharField('رقم العملية الخارجي', max_length=100, blank=True)
    notes = models.TextField('ملاحظات', blank=True)
    opened_at = models.DateTimeField('تاريخ الفتح')
    closed_at = models.DateTimeField('تاريخ الإغلاق', null=True, blank=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)
    updated_at = models.DateTimeField('تاريخ التحديث', auto_now=True)

    def __str__(self):
        return f'{self.symbol} - {self.order_type} - {self.status}'

    class Meta:
        verbose_name = 'صفقة'
        verbose_name_plural = 'الصفقات'


class PerformanceReport(models.Model):
    account = models.ForeignKey(
        'trading.TradingAccount',
        on_delete=models.CASCADE,
        related_name='performance_reports',
        verbose_name='حساب التداول',
    )
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='performance_reports',
        verbose_name='المستخدم',
    )
    report_period = models.CharField('الفترة', max_length=50)
    total_trades = models.PositiveIntegerField('إجمالي الصفقات', default=0)
    win_rate = models.DecimalField('نسبة الربح', max_digits=5, decimal_places=2, default=0)
    net_profit = models.DecimalField('صافي الربح', max_digits=15, decimal_places=2, default=0)
    max_drawdown = models.DecimalField('أقصى تراجع', max_digits=15, decimal_places=2, default=0)
    report_data = models.JSONField('بيانات التقرير', default=dict, blank=True)
    generated_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.report_period}'

    class Meta:
        verbose_name = 'تقرير أداء'
        verbose_name_plural = 'تقارير الأداء'


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('system', 'نظام'),
        ('trade', 'صفقة'),
        ('risk', 'مخاطر'),
        ('analysis', 'تحليل'),
    )

    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='المستخدم',
    )
    trade = models.ForeignKey(
        'trading.Trade',
        on_delete=models.SET_NULL,
        related_name='notifications',
        null=True,
        blank=True,
        verbose_name='الصفقة',
    )
    title = models.CharField('العنوان', max_length=200)
    message = models.TextField('الرسالة')
    notification_type = models.CharField(
        'نوع الإشعار',
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='system',
    )
    is_read = models.BooleanField('تمت القراءة', default=False)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
