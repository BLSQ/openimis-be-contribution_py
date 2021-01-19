from django.db.models import Q
from django.core.exceptions import PermissionDenied
from graphene_django.filter import DjangoFilterConnectionField
import graphene_django_optimizer as gql_optimizer

from .apps import ContributionConfig
from location.apps import LocationConfig
from django.utils.translation import gettext as _
from core.schema import signal_mutation_module_before_mutating, OrderedDjangoFilterConnectionField
from policy import models as policy_models
from .models import Premium, PremiumMutation
# We do need all queries and mutations in the namespace here.
from .gql_queries import *  # lgtm [py/polluting-import]
from .gql_mutations import *  # lgtm [py/polluting-import]


class Query(graphene.ObjectType):
    premiums = OrderedDjangoFilterConnectionField(
        PremiumGQLType,
        show_history=graphene.Boolean(),
        parent_location=graphene.String(),
        parent_location_level=graphene.Int(),
        orderBy=graphene.List(of_type=graphene.String),
    )
    premiums_by_policies = OrderedDjangoFilterConnectionField(
        PremiumGQLType,
        policy_uuids=graphene.List(graphene.String, required=True),
        orderBy=graphene.List(of_type=graphene.String),
    )

    def resolve_premiums(self, info, **kwargs):
        if not info.context.user.has_perms(ContributionConfig.gql_query_premiums_perms):
            raise PermissionDenied(_("unauthorized"))
        filters = []
        show_history = kwargs.get('show_history', False)
        if not show_history and not kwargs.get('uuid', None):
            filters += filter_validity(**kwargs)
        parent_location = kwargs.get('parent_location')
        if parent_location is not None:
            parent_location_level = kwargs.get('parent_location_level')
            if parent_location_level is None:
                raise NotImplementedError("Missing parentLocationLevel argument when filtering on parentLocation")
            f = "uuid"
            for i in range(len(LocationConfig.location_types) - parent_location_level - 1):
                f = "parent__" + f
            family_location = "policy__family__location__" + f
            filters.append(Q(**{family_location: parent_location}))
        return gql_optimizer.query(Premium.objects.filter(*filters).all(), info)


    def resolve_premiums_by_policies(self, info, **kwargs):
        if not info.context.user.has_perms(ContributionConfig.gql_query_premiums_perms):
            raise PermissionDenied(_("unauthorized"))
        policies = policy_models.Policy.objects.values_list('id').filter(Q(uuid__in=kwargs.get('policy_uuids')))
        return Premium.objects.filter(Q(policy_id__in=policies), *filter_validity(**kwargs))


def set_premium_deleted(premium):
    try:
        premium.delete_history()
        return []
    except Exception as exc:
        return {
            'title': premium.uuid,
            'list': [{
                'message': _("premium.mutation.failed_to_delete_premium") % {'premium': str(premium)},
                'detail': premium.uuid
            }]
        }


class Mutation(graphene.ObjectType):
    delete_premium = DeletePremiumsMutation.Field()
    create_premium = CreatePremiumMutation.Field()
    update_premium = UpdatePremiumMutation.Field()


def on_policy_mutation(sender, **kwargs):
    errors = []
    if kwargs.get("mutation_class") == 'DeletePoliciesMutation':
        uuids = kwargs['data'].get('uuids', [])
        policies = policy_models.Policy.objects.prefetch_related("premiums").filter(uuid__in=uuids).all()
        for policy in policies:
            for premium in policy.premiums.all():
                errors += set_premium_deleted(premium)
    return errors

def on_premium_mutation(sender, **kwargs):
    uuids = kwargs['data'].get('uuids', [])
    if not uuids:
        uuid = kwargs['data'].get('premium_uuid', None)
        uuids = [uuid] if uuid else []
    if not uuids:
        return []
    impacted_premiums = Premium.objects.filter(uuid__in=uuids).all()
    for premium in impacted_premiums:
        PremiumMutation.objects.create(
            premium=premium, mutation_id=kwargs['mutation_log_id'])
    return []

def bind_signals():
    signal_mutation_module_before_mutating["policy"].connect(on_policy_mutation)
    signal_mutation_module_before_mutating["contribution"].connect(on_premium_mutation)