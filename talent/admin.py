from django.contrib import admin

from . import models

admin.site.register([models.Status, models.Feedback])


@admin.register(models.BountyClaim)
class BountyClaimAdmin(admin.ModelAdmin):
    list_display = [
        "pk",
        "bounty",
        "person",
        "expected_finish_date",
        "status",
    ]
    search_fields = [
        "bounty__title",
        "person__user__username",
        "expected_finish_date",
        "status",
    ]


@admin.register(models.Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "parent"]


@admin.register(models.Expertise)
class ExpertiseAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "skill", "parent"]


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ["pk", "full_name", "user"]


@admin.register(models.PersonSkill)
class PersonSkillAdmin(admin.ModelAdmin):
    list_display = ["pk", "person", "skill", "expertise"]
