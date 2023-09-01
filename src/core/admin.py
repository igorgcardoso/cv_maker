from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import (City, Country, CVLanguage, Education, EducationCourse,
                     EducationDegree, EducationInstitution, Experience,
                     ExperienceCompany, ExperienceRole, Language, Project,
                     Role, Skill, SocialNetwork, State, User, UserLanguage,
                     UserRole, UserSkill, UserSocialNetwork)


@admin.register(EducationCourse)
class EducationCourseAdmin(admin.ModelAdmin):
  list_display = ['name']
  exclude = ['id']


@admin.register(EducationDegree)
class EducationDegreeAdmin(admin.ModelAdmin):
  list_display = ['name']
  exclude = ['id']


@admin.register(EducationInstitution)
class EducationInstitutionAdmin(admin.ModelAdmin):
  list_display = ['name', 'acronym', 'city']
  exclude = ['id']


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
  list_display = ['user', 'company', 'role', 'description_display', 'start_date', 'end_date', 'created_at', 'updated_at']
  exclude = ['id', 'created_at', 'updated_at']

  @admin.display(description=_('Description'))
  def description_display(self, obj):
    return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description


@admin.register(ExperienceRole)
class ExperienceRoleAdmin(admin.ModelAdmin):
  list_display = ['name']
  exclude = ['id']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
  list_display = ['name']
  exclude = ['id']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
  list_display = ['name', 'description_display', 'start_date', 'end_date', 'created_at', 'updated_at']
  exclude = ['id', 'created_at', 'updated_at']

  @admin.display(description=_('Description'))
  def description_display(self, obj):
    return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
  list_display = ['name']
  exclude = ['id']


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
  list_display = ['name']
  exclude = ['id']


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
  list_display = ['user', 'skill', 'created_at', 'updated_at']
  exclude = ['id', 'created_at', 'updated_at']

  @admin.display
  def level(self, obj):
    return f'{obj.level}/5'


@admin.register(UserLanguage)
class UserLanguageAdmin(admin.ModelAdmin):
  list_display = ['user', 'language', 'level_display', 'created_at', 'updated_at']
  exclude = ['id', 'created_at', 'updated_at']

  @admin.display(description=_("Level"))
  def level_display(self, obj):
    return obj.get_level_display() if not obj.is_native else _('Native')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
  list_display = ['user', 'role', 'created_at', 'updated_at']
  exclude = ['id', 'created_at', 'updated_at']


@admin.register(UserSocialNetwork)
class UserSocialNetworkAdmin(admin.ModelAdmin):
  list_display = ['user', 'social_network', 'username']
  exclude = ['id']


@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
  list_display = ['name', 'base_url', 'icon_url']
  exclude = ['id']


@admin.register(ExperienceCompany)
class ExperienceCompanyAdmin(admin.ModelAdmin):
  list_display = ['name']
  exclude = ['id']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
  list_display = ['user', 'institution', 'degree', 'course', 'date_range', 'created_at', 'updated_at']
  exclude = ['id', 'created_at', 'updated_at']

  @admin.display(description=_('Date range'))
  def date_range(self, obj):
    return f'{obj.start_date.strftime("%b %Y")} - {obj.end_date.strftime("%b %Y") if obj.end_date else _("Present")}'


@admin.register(CVLanguage)
class CVLanguageAdmin(admin.ModelAdmin):
  list_display = ['language']
  exclude = ['id']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
  list_display = ['name']
  exclude = ['id']


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
  list_display = ['name', 'country', 'abbreviation']
  exclude = ['id']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
  list_display = ['name', 'state']
  exclude = ['id']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
  list_display = ['first_name', 'last_name', 'email', 'birth_date', 'city','created_at', 'updated_at']
  exclude = ['id', 'password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions', 'created_at', 'updated_at']
