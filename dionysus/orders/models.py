from django.db import models
from django.utils.translation import gettext as _


STATUS_CHOICES = [
    ('wait', _('order pending')),
    ('done', _('order ready')),
    ('paid', _('order paid')),
]


class Order(models.Model):
    table_number = models.SmallIntegerField()
    items = models.JSONField()
    total_price = models.IntegerField(blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=4)

    def save(self, **kwargs):
        self.total_price = 0
        for key in self.items.keys():
            self.total_price += self.items[key]
        super().save(**kwargs)
