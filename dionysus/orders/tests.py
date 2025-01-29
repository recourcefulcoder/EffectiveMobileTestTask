from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import Client, TestCase, tag
from django.urls import reverse
from django.utils import translation

from parameterized import parameterized

from .forms import item_form_data_creation
from .models import Order, STATUS_DONE, STATUS_PAID, STATUS_WAIT
from .views import ORDER_LIST_CONTEXT_NAME


@tag("db")
class DatabaseTests(TestCase):
    def test_default(self):
        self.assertTrue(True)

    @parameterized.expand(
        [
            (
                {
                    "bread": 500,
                    "water": 500,
                },
                True,
            ),
            (
                {
                    "bread": "500",
                    "water": "700",
                },
                True,
            ),
            (
                {
                    "bread": "500.545",
                    "water": "700",
                },
                False,
            ),
            ({"bread": ""}, False),
            (
                {},
                False,
            ),
            (
                {
                    "": 1500,
                },
                False,
            ),
            (
                {
                    "cake": 1500,
                    "pineapple": 200,
                    "juice": "",
                },
                False,
            ),
        ]
    )
    def test_items_validation(self, items, valid_data):
        order = Order(table_number=2, items=items, status=STATUS_PAID)
        if not valid_data:
            with self.assertRaises(ValidationError):
                order.full_clean()
        else:
            order.full_clean()

    def test_total_price_auto_created(self):
        order = Order.objects.create(
            items={"milk": 400, "macaronz": 1200},
            table_number=1,
            status=STATUS_DONE,
        )
        self.assertTrue(hasattr(order, "total_price"))

    @parameterized.expand(
        [
            (
                {
                    "scrumbled egg": 500,
                    "pizza": 1500,
                },
                2000,
            ),
            (
                {
                    "pardon-dish": "7545",
                },
                7545,
            ),
            (
                {
                    "milkshake": "1300",
                    "cheeseburger": 300,
                },
                1600,
            ),
        ]
    )
    def test_valid_total_price(self, items, target_value):
        order = Order.objects.create(
            table_number=1, status=STATUS_PAID, items=items
        )
        self.assertEqual(order.total_price, target_value)


@tag("view")
class ViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.c = Client()
        items_pack1 = {
            "milky way": 100,
            "ice cream (vanilla)": 400,
            "pizza": 1500,
        }
        cls.items_pack = items_pack1
        cls.ord_to_delete = Order.objects.create(
            table_number=1, status=STATUS_PAID, items=items_pack1
        )
        for i in range(1, 8):
            setattr(
                cls,
                f"ord{i}",
                Order.objects.create(
                    table_number=i, status=STATUS_PAID, items=items_pack1
                ),
            )

    @classmethod
    def tearDown(cls):
        translation.activate(settings.LANGUAGE_CODE)

    def test_valid_deletion(self):
        pk = self.ord_to_delete.pk
        with self.assertNumQueries(1):
            self.c.get(reverse("orders:delete", args=[self.ord_to_delete.pk]))
        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(pk=pk)

    def test_valid_creation(self):
        data = item_form_data_creation(self.items_pack) | {
            "table_number": 1000,
            "status": STATUS_PAID,
        }
        with self.assertNumQueries(1):
            self.c.post(reverse("orders:add"), data)
        self.assertTrue(Order.objects.filter(table_number=1000).exists())

    def test_valid_edition(self):
        pk = self.ord1.pk
        order = Order.objects.get(pk=pk)
        table_number = order.table_number

        data = item_form_data_creation(self.items_pack) | {
            "table_number": table_number + 1,
            "status": order.status,
        }
        with self.assertNumQueries(1):
            self.c.post(reverse("orders:edit", args=[pk]), data)

        new_order = Order.objects.get(pk=pk)
        self.assertEqual(new_order.table_number, table_number + 1)

    @parameterized.expand(
        [
            ("ord", Order.objects.all()),
            ("pend", Order.objects.filter(status=STATUS_WAIT)),
            ("3", Order.objects.filter(pk=3)),
            ("ready     ", Order.objects.filter(status=STATUS_DONE)),
            ("   ready     ", Order.objects.filter(status=STATUS_DONE)),
            ("   rea dy     ", Order.objects.none()),
            ("57", Order.objects.filter(pk=57)),
            ("   6", Order.objects.filter(pk=6)),
        ]
    )
    def test_valid_order_search_en(self, request, expected_queryset):
        with translation.override("en"):
            response = self.c.get(
                reverse("orders:list"),
                query_params={"q": request},
            )
        queryset = response.context[ORDER_LIST_CONTEXT_NAME]
        self.assertQuerySetEqual(queryset, expected_queryset, ordered=False)

    def test_valid_creation_error_handling(self):
        pass

    def test_valid_edition_error_handling(self):
        pass
