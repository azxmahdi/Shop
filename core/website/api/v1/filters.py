import django_filters

from website.models import TeamMembers


class TeamMemberFilter(django_filters.FilterSet):
    status = django_filters.BooleanFilter(
        method="getting_team_members_based_on_status"
    )

    class Meta:
        model = TeamMembers
        fields = []

    def getting_team_members_based_on_status(self, queryset, name, value):
        return queryset.filter(status=value)
