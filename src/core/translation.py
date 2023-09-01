from modeltranslation.translator import TranslationOptions, register

from .models import (City, Country, EducationCourse, EducationDegree,
                     EducationInstitution, Experience, ExperienceRole,
                     Language, Project, Role, Skill, State)


@register(EducationCourse)
class EducationCourseTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Country)
class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(State)
class StateTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(City)
class CityTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(EducationInstitution)
class EducationInstitutionTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(EducationDegree)
class EducationDegreeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(ExperienceRole)
class ExperienceRoleTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Experience)
class ExperienceTranslationOptions(TranslationOptions):
    fields = ('description',)


@register(Skill)
class SkillTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Language)
class LanguageTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Role)
class RoleTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Project)
class ProjectTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
