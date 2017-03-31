import decimal

from django.core import management
from django.test import TestCase

from django.contrib.auth import get_user_model
# from stripe.error import InvalidRequestError

from mock import patch

from ..models import Customer, Plan, Coupon


class CommandTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="patrick")

    @patch("stripe.Customer.retrieve")
    @patch("stripe.Customer.create")
    def test_init_customer_creates_customer(self, CreateMock, RetrieveMock):
        CreateMock.return_value = dict(
            account_balance=0,
            delinquent=False,
            default_source="card_178Zqj2eZvKYlo2Cr2fUZZz7",
            currency="usd",
            id="cus_XXXXX",
            sources=dict(data=[]),
            subscriptions=dict(data=[]),
        )
        management.call_command("init_customers")
        customer = Customer.objects.get(user=self.user)
        self.assertEquals(customer.stripe_id, "cus_XXXXX")

    @patch("stripe.Plan.all")
    @patch("stripe.Plan.auto_paging_iter", create=True, side_effect=AttributeError)
    def test_plans_create_deprecated(self, PlanAutoPagerMock, PlanAllMock):
        PlanAllMock().data = [{
            "id": "entry-monthly",
            "amount": 954,
            "interval": "monthly",
            "interval_count": 1,
            "currency": None,
            "statement_descriptor": None,
            "trial_period_days": None,
            "name": "Pro",
            "metadata": {}
        }]
        management.call_command("sync_plans")
        self.assertEquals(Plan.objects.count(), 1)
        self.assertEquals(Plan.objects.all()[0].stripe_id, "entry-monthly")
        self.assertEquals(Plan.objects.all()[0].amount, decimal.Decimal("9.54"))

    @patch("stripe.Plan.auto_paging_iter", create=True)
    def test_plans_create(self, PlanAutoPagerMock):
        PlanAutoPagerMock.return_value = [{
            "id": "entry-monthly",
            "amount": 954,
            "interval": "monthly",
            "interval_count": 1,
            "currency": None,
            "statement_descriptor": None,
            "trial_period_days": None,
            "name": "Pro",
            "metadata": {}
        }]
        management.call_command("sync_plans")
        self.assertEquals(Plan.objects.count(), 1)
        self.assertEquals(Plan.objects.all()[0].stripe_id, "entry-monthly")
        self.assertEquals(Plan.objects.all()[0].amount, decimal.Decimal("9.54"))

    @patch("stripe.Coupon.auto_paging_iter", create=True)
    def test_coupons_create(self, CouponAutoPagerMock):
        CouponAutoPagerMock.return_value = [{
            "id": "test-coupon",
            "object": "coupon",
            "amount_off": None,
            "created": 1482132502,
            "currency": "aud",
            "duration": "repeating",
            "duration_in_months": 3,
            "livemode": False,
            "max_redemptions": None,
            "metadata": {
            },
            "percent_off": 25,
            "redeem_by": None,
            "times_redeemed": 0,
            "valid": True
        }]
        management.call_command("sync_coupons")
        self.assertEquals(Coupon.objects.count(), 1)
        self.assertEquals(Coupon.objects.all()[0].stripe_id, "test-coupon")
        self.assertEquals(Coupon.objects.all()[0].percent_off, 25)

    @patch("stripe.Coupon.all")
    @patch("stripe.Coupon.auto_paging_iter", create=True, side_effect=AttributeError)
    def test_coupons_create_deprecated(self, CouponAutoPagerMock, CouponAllMock):
        CouponAllMock().data = [{
            "id": "test-coupon",
            "object": "coupon",
            "amount_off": None,
            "created": 1482132502,
            "currency": "aud",
            "duration": "repeating",
            "duration_in_months": 3,
            "livemode": False,
            "max_redemptions": None,
            "metadata": {
            },
            "percent_off": 25,
            "redeem_by": None,
            "times_redeemed": 0,
            "valid": True
        }]
        management.call_command("sync_coupons")
        self.assertEquals(Coupon.objects.count(), 1)
        self.assertEquals(Coupon.objects.all()[0].stripe_id, "test-coupon")
        self.assertEquals(Coupon.objects.all()[0].percent_off, 25)

    # @patch("stripe.Customer")
    # @patch("stripe.Charge")
    # @patch("stripe.Invoice")
    # @patch("pinax.stripe.actions.charges.sync_charge_from_stripe_data")
    # @patch("pinax.stripe.actions.customers.sync_customer")
    # @patch("pinax.stripe.actions.invoices.sync_invoice_from_stripe_data")
    # @patch("pinax.stripe.actions.plans.sync_plans")
    # def test_sync_customers(
    #     self, StripeCustomerMock, StripeChargeMock,
    #     StripeInvoiceMock, SyncChargeMock, SyncCustomerMock,
    #     SyncInvoiceMock, SyncPlansMock
    # ):

    #     class Collection(object):

    #         total_count = 0

    #         def auto_paging_iter():
    #             """Fake an iterator."""
    #             return iter([])

    #     StripeCustomerMock().list.side_effect = Collection()
    #     StripeChargeMock().list.side_effect = Collection()
    #     StripeInvoiceMock().list.side_effect = Collection()

    #     # user2 = get_user_model().objects.create_user(username="thomas")
    #     # get_user_model().objects.create_user(username="altman")
    #     # Customer.objects.create(stripe_id="cus_XXXXX", user=self.user)
    #     # Customer.objects.create(stripe_id="cus_YYYYY", user=user2)

    #     # management.call_command("sync_customers")
    #     # self.assertEqual(SyncChargesMock.call_count, 0)
    #     # self.assertEqual(SyncInvoicesMock.call_count, 0)
    #     # self.assertEqual(SyncMock.call_count, 2)

    # @patch("stripe.Customer.list")
    # @patch("pinax.stripe.actions.customers.sync_customer")
    # @patch("pinax.stripe.actions.invoices.sync_invoices_for_customer")
    # @patch("pinax.stripe.actions.charges.sync_charges_for_customer")
    # def test_sync_customers_with_unicode_username(self, SyncChargesMock, SyncInvoicesMock, SyncMock, ListMock):
    #     user2 = get_user_model().objects.create_user(username=u"tom\xe1s")
    #     Customer.objects.create(stripe_id="cus_YYYYY", user=user2)
    #     management.call_command("sync_customers")
    #     self.assertEqual(SyncChargesMock.call_count, 1)
    #     self.assertEqual(SyncInvoicesMock.call_count, 1)
    #     self.assertEqual(SyncMock.call_count, 1)
    #     management.call_command("sync_customers")
    #     self.assertEqual(SyncChargesMock.call_count, 2)
    #     self.assertEqual(SyncInvoicesMock.call_count, 2)
    #     self.assertEqual(SyncMock.call_count, 2)

    # @patch("stripe.Customer.retrieve")
    # @patch("pinax.stripe.actions.customers.sync_customer")
    # @patch("pinax.stripe.actions.invoices.sync_invoices_for_customer")
    # @patch("pinax.stripe.actions.charges.sync_charges_for_customer")
    # def test_sync_customers_with_test_customer(self, SyncChargesMock, SyncInvoicesMock, SyncMock, RetrieveMock):
    #     user2 = get_user_model().objects.create_user(username="thomas")
    #     get_user_model().objects.create_user(username="altman")
    #     Customer.objects.create(stripe_id="cus_XXXXX", user=self.user)
    #     Customer.objects.create(stripe_id="cus_YYYYY", user=user2)

    #     SyncMock.side_effect = InvalidRequestError('Unknown customer', None, http_status=404)

    #     management.call_command("sync_customers")
    #     self.assertEqual(SyncChargesMock.call_count, 0)
    #     self.assertEqual(SyncInvoicesMock.call_count, 0)
    #     self.assertEqual(SyncMock.call_count, 2)
