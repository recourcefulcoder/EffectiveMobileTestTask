from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

STATUS_WAIT = "wait"
STATUS_DONE = "done"
STATUS_PAID = "paid"

STATUS_CHOICES = [
    (STATUS_WAIT, _("order pending")),
    (STATUS_DONE, _("order ready")),
    (STATUS_PAID, _("order paid")),
]

STATUS_LENGTH = 0
for tup in STATUS_CHOICES:
    STATUS_LENGTH = max(STATUS_LENGTH, len(tup[0]))


def validate_items(field_value) -> None:
    if not field_value:
        raise ValidationError(_("Each order must contain at least one item"))
    for key, value in field_value.items():
        try:
            int_val = int(value)
        except ValueError:
            raise ValidationError(
                _("%(key)s has invalid price type"), params={"key": key}
            )
        if int_val <= 0:
            raise ValidationError(
                _("%(key)s has non-positive price value"), params={"key": key}
            )
        if not key:
            raise ValidationError(
                _("dish name with price %(value)s not provided"),
                params={"value": value},
            )


class Order(models.Model):
    table_number = models.SmallIntegerField()
    items = models.JSONField(validators=[validate_items])
    total_price = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        choices=STATUS_CHOICES, max_length=STATUS_LENGTH, default="wait"
    )

    def save(self, force_update=False, **kwargs) -> None:
        exclude = {"total_price"}
        if force_update:
            exclude.add("id")
        self.full_clean(exclude=exclude)
        self.total_price = 0
        for key in self.items.keys():
            self.total_price += int(self.items[key])
        super().save(**kwargs)

    class Meta:
        ordering = ["-id"]
