from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _


STATUS_CHOICES = [
    ("wait", _("order pending")),
    ("done", _("order ready")),
    ("paid", _("order paid")),
]


def validate_items(field_value):
    if not field_value:
        raise ValidationError(_("Each order must contain at least one item"))
    for key, value in field_value.items():
        if int(field_value[key]) <= 0:
            raise ValidationError(
                _("%(key)s has non-positive price value"), params={"key": key}
            )


class Order(models.Model):
    table_number = models.SmallIntegerField()
    items = models.JSONField(validators=[validate_items])
    total_price = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=4, default="wait"
    )

    def save(self, **kwargs):
        self.total_price = 0
        for key in self.items.keys():
            self.total_price += self.items[key]
        super().save(**kwargs)
