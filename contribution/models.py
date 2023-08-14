
from django.db import models
import uuid
from core import fields
from core import models as core_models
from django.utils.translation import gettext_lazy
from django.contrib.auth.hashers import make_password, check_password
from policy.models import Policy
from payer.models import Payer
  # Import placed after core_models
"""
Merchant wallet model
Mercant is could be any openimis accountant requesting for payment

"""


class PaymentServiceProvider(core_models.VersionedModel):

    id = models.AutoField(db_column="PSPID", primary_key=True)                    
    uuid = models.CharField(db_column="PSPUUID", max_length=36, default=uuid.uuid4, unique= True)
    PSPName = models.CharField(db_column= "PSPName", max_length=50, blank= True, null= True)
    PSPAccount = models.CharField( db_column= "PSPAccount", max_length= 36,  unique=True, null=False, blank=False, default=0)
    Pin = models.CharField(db_column=" Pin", max_length=128, blank=False, null=False, default=False)

    def set_pin(self, pin):
        # Set the PIN using make_password() to hash and encrypt it
        self.pin = make_password(pin)

    def check_pin(self, pin):
        # Check if the provided PIN matches the hashed PIN
        return check_password(pin, self.pin)
    

    def __str__(self):
        return f"{self.PSPName}"

    class Meta:
        managed = True
        db_table = 'tblPaymnet_Service_Provider'




class PayTypeChoices(models.TextChoices):
    BANK_TRANSFER = "B", gettext_lazy("Bank transfer")
    CASH = "C", gettext_lazy("Cash")
    MOBILE = "M", gettext_lazy("Mobile phone")
    FUNDING = "F", gettext_lazy("Funding")


class Premium(core_models.VersionedModel):
    id = models.AutoField(db_column="PremiumId", primary_key=True)
    uuid = models.CharField(
        db_column="PremiumUUID", max_length=36, default=uuid.uuid4, unique=True
    )
    policy = models.ForeignKey(
        Policy, models.DO_NOTHING, db_column="PolicyID",                                                                                                                                            
        blank= True, 
        null= True,
        related_name="premiums")
    payer = models.ForeignKey(
        Payer,
        models.DO_NOTHING,
        db_column="PayerID",
        blank=True,
        null=True,
        related_name="premiums",
    )
    transaction = models.ForeignKey(
        'mobile_payment.Transactions',
        models.DO_NOTHING,
        db_column="Transaction_Id",
        blank=True,
        null=True,
        related_name="premiums",
    )
    amount = models.DecimalField(db_column="Amount", max_digits=18, decimal_places=2)
    remarks = models.TextField(db_column="remarks", max_length=100, blank= True, null= True)
    receipt = models.CharField(db_column="Receipt", max_length=50)
    pay_date = fields.DateField(db_column="PayDate")
    pay_type = models.CharField(
        db_column="PayType", max_length=25,)
    is_photo_fee = models.BooleanField(
        db_column="isPhotoFee", blank=True, null=True, default=False
    )
    is_offline = models.BooleanField(
        db_column="isOffline", blank=True, null=True, default=False
    )
    reporting_id = models.IntegerField(db_column="ReportingId", blank=True, null=True)
    # audit_user_id = models.IntegerField(db_column="AuditUserID")
    # rowid = models.TextField(db_column='RowID', blank=True, null=True)
                                                       


    def __str__(self):
        return f"{self.policy}"

    class Meta:
        managed = True
        db_table = 'tblPremium'


class PremiumMutation(core_models.UUIDModel, core_models.ObjectMutation):
    premium = models.ForeignKey(Premium, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(core_models.MutationLog, models.DO_NOTHING, related_name='premiums')

    class Meta:
        managed = True
        db_table = "contribution_PremiumMutation"

class PaymentServiceProviderMutation(core_models.UUIDModel, core_models.ObjectMutation):
    payment_service_provider  = models.ForeignKey(PaymentServiceProvider, models.DO_NOTHING,
                              related_name='mutations')
    mutation = models.ForeignKey(
        core_models.MutationLog, models.DO_NOTHING, related_name='payment_service_provider')

    class Meta:
        managed = True
        db_table = "PaymentServiceProviderMutation"