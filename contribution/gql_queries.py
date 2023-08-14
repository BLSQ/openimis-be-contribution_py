import graphene
from graphene_django import DjangoObjectType
from .models import Premium, PremiumMutation, PaymentServiceProvider
from core import prefix_filterset, ExtendedConnection
from policy.schema import PolicyGQLType


class PaymentServiceProviderGQLType(DjangoObjectType):

    """
    create a category with a label in the slug field
    """

    class Meta:
        model = PaymentServiceProvider
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id":["exact"],
            "uuid": ["exact"], 
            "PSPName":["exact"],
            "PSPAccount":["exact"],
            "Pin":["exact"],
        }
        connection_class = ExtendedConnection


class PremiumGQLType(DjangoObjectType):
    client_mutation_id = graphene.String()

    class Meta:
        model = Premium
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "uuid": ["exact"],
            "amount": ["exact", "lt", "lte", "gt", "gte"],
            "pay_date": ["exact", "lt", "lte", "gt", "gte"],
            "pay_type": ["exact"],
            "remarks" : ["exact"],
            "is_photo_fee": ["exact"],
            "receipt": ["exact", "icontains"],
            **prefix_filterset("policy__", PolicyGQLType._meta.filter_fields)
        }
        connection_class = ExtendedConnection

    def resolve_client_mutation_id(self, info):
        premium_mutation = self.mutations.select_related(
            'mutation').filter(mutation__status=0).first()
        return premium_mutation.mutation.client_mutation_id if premium_mutation else None


class PremiumMutationGQLType(DjangoObjectType):
    class Meta:
        model = PremiumMutation
