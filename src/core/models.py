from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, List
from uuid import uuid4

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.template.loader import get_template
from django.utils.timezone import localdate
from django.utils.translation import activate, deactivate
from django.utils.translation import gettext_lazy as _
from weasyprint import CSS, HTML

from .signals import cv_generated

# Create your models here.

class UserManager(BaseUserManager):
    def create(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password=None, **extra_fields):
        user = self.create(email, password, **extra_fields)
        user.is_superuser = False
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create(email, password, **extra_fields)
        user.is_superuser = True
        user.save()
        return user


class User(PermissionsMixin, AbstractBaseUser):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    first_name = models.CharField(_('first name'), max_length=50)
    middle_name = models.CharField(_('middle name'), max_length=50)
    last_name = models.CharField(_('last name'), max_length=50)
    birth_date = models.DateField(_('birth date'))
    email = models.EmailField(_('email address'), unique=True)
    tel = models.CharField(_('tel'), max_length=14, unique=True)
    social_networks = models.ManyToManyField('SocialNetwork', related_name='+', through='UserSocialNetwork')
    city = models.ForeignKey('City', on_delete=models.CASCADE, related_name='+', null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'middle_name', 'last_name', 'birth_date', 'tel']
    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.middle_name[0]}. {self.last_name}'

    @property
    def age(self):
        return (localdate() - self.birth_date).days // 365

    @property
    def is_staff(self):
        return self.is_superuser

    def is_active(self):
        return True

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'core_users'

    def generate_cv(self, language: 'CVLanguage', role: 'Role', brief: str, skills: List['Skill'], company_name: str, company_brief: str):
        tel = self.tel
        self.tel = f'({tel[3:5]}) {tel[5]} {tel[6:10]}-{tel[10:]}'

        activate(language.language)
        template = get_template('cv/index.html')
        html = template.render({
            'user': self,
            'brief': brief,
            'role': role,
            'skills': skills.values_list('skill__name', flat=True),
            'socials': UserSocialNetwork.objects.filter(user=self),
            'experiences': self.experiences.all(),
            'educations': self.educations.all(),
            'languages': self.languages.all(),
        })

        company, _ = Company.objects.get_or_create(name=company_name, defaults={'brief': company_brief})
        user_brief, _ = Brief.objects.get_or_create(user_role=role, company=company, defaults={'brief': brief})
        try:
            Cv.objects.create(user=self, cv_language=language, role=role, brief=user_brief, skills=skills)
        except:
            pass

        html = HTML(string=html)
        css = Path(__file__).parent / 'static/css/styles_out.css'
        css = CSS(filename=css)
        cv_path = NamedTemporaryFile(suffix='.pdf', delete=True)
        cv = cv_path.name
        html.write_pdf(cv, stylesheets=[css])
        deactivate()
        cv_generated.send(sender=self, cv=cv)
        return cv_path


class Country(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        db_table = 'core_countries'
        ordering = ['name']

class State(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=100, unique=True)
    abbreviation = models.CharField(_('abbreviation'), max_length=2, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('state')
        verbose_name_plural = _('states')
        db_table = 'core_states'
        constraints = [
            models.UniqueConstraint(fields=['name', 'country'], name='unique_state')
        ]
        ordering = ['name']


class City(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=100, unique=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name

    @property
    def country(self):
        return self.state.country

    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        db_table = 'core_cities'
        constraints = [
            models.UniqueConstraint(fields=['name', 'state'], name='unique_city')
        ]
        ordering = ['name']


class EducationInstitution(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=100)
    acronym = models.CharField(_('acronym'), max_length=10)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='+')

    def __str__(self):
        return self.name

    @property
    def country(self):
        return self.name

    class Meta:
        verbose_name = _('education institution')
        verbose_name_plural = _('education institutions')
        db_table = 'core_education_institutions'
        constraints = [
            models.UniqueConstraint(fields=['name', 'city'], name='unique_education_institution')
        ]
        ordering = ['name']


class EducationDegree(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('education degree')
        verbose_name_plural = _('education degrees')
        db_table = 'core_education_degrees'
        ordering = ['name']


class EducationCourse(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('education course')
        verbose_name_plural = _('education courses')
        db_table = 'core_education_courses'
        ordering = ['name']


class Education(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='educations')
    institution = models.ForeignKey(EducationInstitution, on_delete=models.CASCADE, related_name='+')
    course = models.ForeignKey(EducationCourse, on_delete=models.CASCADE, related_name='+')
    degree = models.ForeignKey(EducationDegree, on_delete=models.CASCADE, related_name='+')
    start_date = models.DateField(_('start date'), help_text=_('The year when you started the course'))
    end_date = models.DateField(_('end date'), null=True, blank=True, help_text=_('The year when you finished the course'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f'{self.course} - {self.institution.name}'

    @property
    def is_completed(self):
        return not self.end_date

    class Meta:
        verbose_name = _('education')
        verbose_name_plural = _('education')
        db_table = 'core_education'
        constraints = [
            models.UniqueConstraint(fields=['user', 'institution', 'course', 'degree'], name='unique_education')
        ]
        ordering = ['-start_date__year', '-end_date__year']


class ExperienceCompany(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('experience company')
        verbose_name_plural = _('experience companies')
        db_table = 'core_experience_companies'
        ordering = ['name']


class ExperienceRole(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('experience role')
        verbose_name_plural = _('experience roles')
        db_table = 'core_experience_roles'
        ordering = ['name']


class Experience(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experiences')
    company = models.ForeignKey(ExperienceCompany, on_delete=models.CASCADE, related_name='+')
    role = models.ForeignKey(ExperienceRole, on_delete=models.CASCADE, related_name='+')
    description = models.TextField(_('description'), null=True, blank=True)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f'{self.role} - {self.company.name}'

    class Meta:
        verbose_name = _('experience')
        verbose_name_plural = _('experiences')
        db_table = 'core_experiences'
        constraints = [
            models.UniqueConstraint(fields=['user', 'company', 'role'], name='unique_experience')
        ]
        ordering = ['-start_date', '-end_date']


class Skill(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('skill')
        verbose_name_plural = _('skills')
        db_table = 'core_skills'
        ordering = ['name']


class UserSkill(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='+')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f'{self.skill}'

    class Meta:
        verbose_name = _('user skill')
        verbose_name_plural = _('user skills')
        db_table = 'core_user_skills'
        constraints = [
            models.UniqueConstraint(fields=['user', 'skill'], name='unique_user_skill')
        ]


class Language(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('language')
        verbose_name_plural = _('languages')
        db_table = 'core_languages'
        ordering = ['name']


class UserLanguageManager(models.Manager):
    def create(self, user, language, level, is_native, **kwargs: Any) -> Any:
        model = super().create(user=user, language=language, level=level, is_native=is_native, **kwargs)
        if model.is_native:
            model.level = model.LevelEnum.C2
            model.save()
        return model


class UserLanguage(models.Model):
    class LevelEnum(models.enums.TextChoices):
        A1 = 'A1', _('Beginner')
        A2 = 'A2', _('Elementary')
        B1 = 'B1', _('Intermediate')
        B2 = 'B2', _('Upper Intermediate')
        C1 = 'C1', _('Advanced')
        C2 = 'C2', _('Proficient')
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='languages')
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='+')
    level = models.CharField(_('level'), max_length=2, choices=LevelEnum.choices)
    is_native = models.BooleanField(_('is native'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = UserLanguageManager()

    def __str__(self):
        return f'{self.language}'

    @property
    def level_display(self):
        if self.is_native:
            return _('native')
        return f'{self.level}/5'

    class Meta:
        verbose_name = _('user language')
        verbose_name_plural = _('user languages')
        db_table = 'core_user_languages'
        constraints = [
            models.UniqueConstraint(fields=['user', 'language'], name='unique_user_language')
        ]
        ordering = ['-is_native', '-level', 'language__name']


class Role(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=100, unique=True)
    users = models.ManyToManyField(User, related_name='+', through='UserRole')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        db_table = 'core_roles'
        ordering = ['name']


class UserRole(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='+')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f'{self.role}'

    class Meta:
        verbose_name = _('user role')
        verbose_name_plural = _('user roles')
        db_table = 'core_user_roles'
        constraints = [
            models.UniqueConstraint(fields=['user', 'role'], name='unique_user_role')
        ]
        ordering = ['role__name']

class CVLanguage(models.Model):
    class LanguageEnum(models.enums.TextChoices):
        EN = 'en-us', _('English')
        PT_BR = 'pt-br', _('Portuguese (Brazil)')

    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    language = models.CharField(_('language'), max_length=5, unique=True, choices=LanguageEnum.choices)

    def __str__(self):
        return self.get_language_display()

    class Meta:
        verbose_name = _('cv language')
        verbose_name_plural = _('cv languages')
        db_table = 'core_cv_languages'
        ordering = ['language']


class SocialNetwork(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=100, unique=True)
    base_url = models.URLField(_('base url'), unique=True)
    icon_url = models.URLField(_('icon url'), unique=True)
    suffix = models.CharField(_('suffix'), max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('social network')
        verbose_name_plural = _('social networks')
        db_table = 'core_social_networks'
        ordering = ['name']


class UserSocialNetwork(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    social_network = models.ForeignKey(SocialNetwork, on_delete=models.CASCADE, related_name='+')
    username = models.CharField(_('username'), max_length=100)

    def __str__(self):
        return f'{self.social_network} - {self.username}'

    @property
    def url(self):
        url = self.social_network.base_url
        if not url.endswith('/'):
            url += '/'
        if self.social_network.suffix:
            suffix = self.social_network.suffix
            url += suffix.replace('/', '')
        return f'{url}/{self.username}'

    @property
    def icon_url(self):
        return self.social_network.icon_url

    @property
    def name(self):
        return self.social_network.name

    class Meta:
        verbose_name = _('user social network')
        verbose_name_plural = _('user social networks')
        db_table = 'core_user_social_networks'
        constraints = [
            models.UniqueConstraint(fields=['user', 'social_network'], name='unique_user_social_network'),
            models.UniqueConstraint(fields=['username', 'social_network'], name='unique_username_social_network'),
        ]
        ordering = ['social_network__name']


class Project(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), null=True, blank=True)
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'), null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def __str__(self):
        return f'{self.name}'

    @property
    def is_completed(self):
        return not self.end_date

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        db_table = 'core_projects'
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_project')
        ]
        ordering = ['-start_date', '-end_date']


class Company(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    name = models.CharField(_('name'), max_length=100, unique=True)
    brief = models.CharField(_('brief'), max_length=255)

    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')
        db_table = 'core_companies'
        ordering = ['name']


class Brief(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    user_role = models.ForeignKey(UserRole, on_delete=models.CASCADE, related_name='+')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='+')
    brief = models.CharField(_('user brief'), max_length=255)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def __str__(self):
        return f'{self.user_role}'

    class Meta:
        verbose_name = _('brief')
        verbose_name_plural = _('briefs')
        db_table = 'core_briefs'
        ordering = ['-created_at']


class Cv(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    cv_language = models.ForeignKey(CVLanguage, on_delete=models.CASCADE, related_name='+')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='+')
    brief = models.ForeignKey(Brief, on_delete=models.CASCADE, related_name='+')
    skills = models.ManyToManyField(Skill, related_name='+')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    def __str__(self):
        return f'{self.user}'

    class Meta:
        verbose_name = _('cv')
        verbose_name_plural = _('cvs')
        db_table = 'core_cvs'
        ordering = ['-created_at']
