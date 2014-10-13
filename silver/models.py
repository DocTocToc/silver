"""Models for the silver app."""
from django.db import models
from international.models import countries, currencies

INTERVALS = (
    ('day', 'Day'),
    ('week', 'Week'),
    ('month', 'Month'),
    ('year', 'Year')
)

STATES = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('past_due', 'Past Due'),
    ('on_trial', 'On Trial'),
    ('canceled', 'Canceled'),
    ('ended', 'Ended')
)


class Plan(models.Model):
    name = models.CharField(
        max_length=20, help_text='Display name of the plan.'
    )
    interval = models.CharField(
        choices=INTERVALS, max_length=12, default=INTERVALS[2][0],
        help_text='The frequency with which a subscription should be billed.'
    )
    interval_count = models.PositiveIntegerField(
        help_text='The number of intervals between each subscription billing'
    )
    amount = models.FloatField(
        help_text='The amount in the specified currency to be charged on the '
                  'interval specified.'
    )
    currency = models.CharField(
        choices=currencies, max_length=4, default=currencies[0][0],
        help_text='The currency in which the subscription will be charged.'
    )
    trial_period_days = models.PositiveIntegerField(
        null=True,
        help_text='Number of trial period days granted when subscribing a '
                  'customer to this plan.'
    )
    metered_features = models.ManyToManyField(
        'MeteredFeature',
        help_text="A list of the plan's metered features."
    )
    due_days = models.PositiveIntegerField(
        help_text='Due days for generated invoice.'
    )
    generate_after = models.PositiveIntegerField(
        default=0,
        help_text='Number of seconds to wait after current billing cycle ends '
                  'before generating the invoice. This can be used to allow '
                  'systems to finish updating feature counters.'
    )

    def __unicode__(self):
        return self.name


class MeteredFeature(models.Model):
    name = models.CharField(
        max_length=32,
        help_text='The feature display name.'
    )
    price_per_unit = models.FloatField(help_text='The price per unit.')
    included_units = models.FloatField(
        help_text='The number of included units per plan interval.'
    )

    def __unicode__(self):
        return self.name


class Subscription(models.Model):
    plan = models.ForeignKey(
        'Plan',
        help_text='The plan the customer is subscribed to.'
    )
    customer = models.ForeignKey(
        'Customer',
        help_text='The customer who is subscribed to the plan.'
    )
    trial_end = models.DateTimeField(
        null=True,
        help_text='The date at which the trial ends. '
                  'If set, overrides the computed trial end date from the plan.'
    )
    start_date = models.DateTimeField(
        help_text='The starting date for the subscription.'
    )
    ended_at = models.DateTimeField(
        null=True,
        help_text='The date when the subscription ended.'
    )
    state = models.CharField(
        choices=STATES, max_length=12, default=STATES[1][0],
        help_text='The state the subscription is in.'
    )

    def __unicode__(self):
        return '%s (%s)' % (self.customer, self.plan)


class BillingDetail(models.Model):
    name = models.CharField(
        max_length=128,
        help_text='The name to be used for billing purposes.'
    )
    company = models.CharField(
        max_length=128, blank=True, null=True,
        help_text='Company to issue invoices to.'
    )
    address1 = models.CharField(max_length=128)
    address2 = models.CharField(max_length=48, blank=True, null=True)
    country = models.CharField(choices=countries, max_length=3,
                               default=countries[0][0])
    city = models.CharField(max_length=128, blank=True, null=True)
    zip_code = models.CharField(max_length=32, blank=True, null=True)
    extra = models.TextField(
        blank=True, null=True,
        help_text='Extra information to display on the invoice (markdown formatted).'
    )


class Customer(models.Model):
    customer_reference = models.CharField(
        max_length=256, blank=True, null=True,
        help_text="It's a reference to be passed between silver and clients. "
                  "It usually points to an account ID."
    )
    billing_details = models.OneToOneField(
        'BillingDetail',
        help_text='An hash consisting of billing information. '
        'None are mandatory and all will show up on the invoice.'
    )
    sales_tax_percent = models.FloatField(
        null=True,
        help_text="Whenever to add sales tax. "
                  "If null, it won't show up on the invoice."
    )
    sales_tax_name = models.CharField(
        max_length=64, help_text="Sales tax name (eg. 'sales tax' or 'VAT')."
    )
    consolidated_billing = models.BooleanField(
        default=False, help_text='A flag indicating consolidated billing.'
    )

    def __unicode__(self):
        return self.billing_details.name
