# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import reverse
from django.db import models
from django.contrib.auth.models import User
import json
from django.core.mail import send_mail

class frequently_asked_question(models.Model):
    heading = models.CharField(max_length = 50)
    displayOrder = models.IntegerField()
    text = models.TextField(max_length = 2000,verbose_name ="HTML text")
    published = models.BooleanField(default=False)
    def __unicode__(self):
        return self.heading
    class Meta:
        ordering=["displayOrder"]
        verbose_name ="Frequently Asked Question"

class school(models.Model):
    name = models.CharField(max_length = 100, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
            db_table = 'school'
            ordering = ['name']

class specialization(models.Model):
    name=models.CharField(max_length=100)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']

class PhD(models.Model):
    firstName = models.CharField(max_length=100,  null=True, verbose_name="First Name")
    lastName = models.CharField(max_length=100, null=True,  verbose_name="Last Name")
    year = models.IntegerField(max_length=4, blank=True, null=True, verbose_name="Year PhD Awarded")
    school = models.ForeignKey(school)
    advisor = models.ManyToManyField("self", null=True, blank=True, symmetrical=False)
    specialization = models.ManyToManyField(specialization, null=True, blank=True)
    URL_for_detail = models.CharField(max_length=200, null=True, blank=True)
    validated = models.NullBooleanField(default=False, blank=True)
    submitter_email = models.EmailField(verbose_name="Your Email Address")
    submitter_user = models.ForeignKey(User, null=True, blank=True, verbose_name="Submitter username")
    source_of_info = models.CharField(max_length=300, verbose_name="What's the source of this info?")

    def __unicode__(self):
        name = self.firstName + " " + self.lastName
        return name

    def get_absolute_url(self):
        return reverse('PhD-detail-view', kwargs={'URL_for_detail': self.URL_for_detail})

    def save(self):  # custom save method for person to update detail URL
        self.URL_for_detail = (self.firstName + "_" + self.lastName).replace(" ", "_")
        if not self.pk: #only do this if object doesn't exist yet
            try:
                ob = self.submitter_user.userprofile
                profile = UserProfile.objects.get(pk=ob.id)
                profile.reputation_points = profile.reputation_points + 10
                profile.save()
            except:
                pass

        # call the normal PhD save method
        super(PhD, self).save()


    @property
    def network_edges_formatted(self):
        arrowSettings = {"from":{"scaleFactor":1.3}}
        edge_list = []

        for child in PhD.objects.filter(advisor=self):
            for advisor in child.advisor.all():
                edge_list.append({"to":advisor.pk, "from":child.pk, "arrows":arrowSettings})

        for advisor in self.advisor.all():
            edge_list.append({"to":advisor.pk, "from":self.pk, "arrows":arrowSettings})
            for sibling in PhD.objects.filter(advisor=advisor).exclude(pk=self.pk):
                edge_list.append({"to": advisor.pk, "from": sibling.pk, "arrows": arrowSettings})

        return json.dumps(edge_list)

    @property
    def network_nodes_formatted(self):
        selectedNodeColor = "#1e88e5"
        baseNodeColor = "#ffecb3"
        baseNodeColorHasNonVisibleAdvisees = "#ffca28"
        nodes = []

        nodes.append({"id": self.pk,
                      "label": " ".join((self.firstName, self.lastName)),
                      "color": selectedNodeColor,
                      "shape": "ellipse",
                      "font" : {"color":"white"},
                      "size": 20})
        advisors = self.advisor.all()
        for advisor in advisors:
            if PhD.objects.filter(advisor=advisor).count() > 0:
                color = baseNodeColorHasNonVisibleAdvisees
            else:
                color = baseNodeColor
            nodes.append({"id": advisor.pk,
                          "label": " ".join((advisor.firstName, advisor.lastName)),
                          "color":color})
            for sibling in PhD.objects.filter(advisor=advisor).exclude(pk=self.pk):
                if PhD.objects.filter(advisor=sibling).count() > 0:
                    color = baseNodeColorHasNonVisibleAdvisees
                else:
                    color = baseNodeColor
                nodes.append({"id": sibling.pk,
                              "label": " ".join((sibling.firstName, sibling.lastName)),
                              "color":color})

        children = PhD.objects.filter(advisor=self)
        for child in children:
            if PhD.objects.filter(advisor=child).count() > 0:
                color = baseNodeColorHasNonVisibleAdvisees
            else:
                color = baseNodeColor
            nodes.append({"id": child.pk,
                          "label": " ".join((child.firstName, child.lastName)),
                          "color":color})

        return json.dumps(nodes)

    @property
    def find_root_ancestors(self):
        parents = []
        current_advisor = [advisor for advisor in self.advisor.all()]
        while current_advisor is not None:
            next_advisor = []
            for eachAdvisor in current_advisor:
                parents.append(eachAdvisor)
                for each in eachAdvisor.advisor.all():
                    next_advisor.append(each)
            if next_advisor:
                current_advisor = next_advisor
            else:
                current_advisor = None
        #get parents that are roots for their tree
        roots = []
        for parent in parents:
            if parent.advisor.all():
                pass
            else:
                roots.append(parent)
        return roots

    @property
    def get_nested_tree_dict(self):
        theDict = {}
        theDict["name"]=self.__unicode__()
        theDict["children"]=[]
        for each in PhD.objects.filter(advisor=self):
            theDict["children"].append(each.get_nested_tree_dict)
        if len(theDict["children"])==0:
            del theDict["children"]
        return theDict

    class Meta:
        db_table = 'PhD'
        unique_together = (("firstName", "lastName"),)
        ordering = ['lastName']
        verbose_name_plural = 'PhDs'
        verbose_name = "PhD"



class PhDupdate(models.Model):
    PhD = models.ForeignKey(PhD)
    moderator_approved = models.BooleanField(default=False)
    approver = models.ForeignKey(User, null=True, blank=True)
    suggested_update_fixture = models.TextField()
    submitter_email = models.EmailField(verbose_name="Your Email Address")
    submitter_user = models.ForeignKey(User, null=True, blank=True, related_name="submitter_user", verbose_name="Submitter username")
    source_of_info = models.CharField(max_length=300,verbose_name="What's the source of this info?")
    date_sent = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "Suggested Update"
        verbose_name_plural = "Suggested Updates"

    def save(self):
        if not self.pk: #only do this next part if self is not already in DB
            if self.submitter_user.userprofile:
                profile = UserProfile.objects.get(pk=self.submitter_user.userprofile.id)
                profile.reputation_points = profile.reputation_points + 10
                profile.save()
        # call the normal save method
        super(PhDupdate, self).save()

class userContact(models.Model):
    email = models.EmailField(verbose_name="Your Email Address")
    first_name = models.CharField(max_length=100,verbose_name="Your First Name")
    last_name = models.CharField(max_length=100,verbose_name="Your Last Name")
    affiliation = models.CharField(max_length=100,verbose_name="Your Institutional Affiliation")
    message = models.TextField(max_length=2000,verbose_name="Your message")
    dealt_with = models.BooleanField(default=False)
    admin_notes = models.TextField(max_length=1000)
    date_sent = models.DateTimeField(auto_now_add=True)
    date_last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('dealt_with','-date_sent')

    def __unicode__(self):
        display = "%s %s - (sent on %s)" % (self.first_name, self.last_name, self.date_sent.strftime("%Y-%m-%d")
)
        return display

class UserProfile(models.Model):
    user = models.OneToOneField(to=User)
    moderator_approved = models.BooleanField(default=False)
    alert_email_sent = models.BooleanField(default=False)
    associated_PhD = models.OneToOneField(to=PhD)
    current_position = models.CharField(max_length=100, null=True, blank=True)
    current_affiliation = models.CharField(max_length=100, null=True, blank=True)
    reputation_points = models.IntegerField(default=10)
    research_website = models.URLField(null=True, blank=True)
    research_blurb = models.TextField(max_length=2000,verbose_name="Describe your research program (2000 characters max)", null=True, blank=True)

    def __unicode__(self):
        return "%s = %s" %(self.user, self.associated_PhD.firstName + " " + self.associated_PhD.lastName)

    def save(self):
        #custom save method to send email when moderator has approved the user profile
        if self.moderator_approved:
            if not self.alert_email_sent:
                send_mail(
                    'Your Phys Anth Phylogeny profile account has been approved',
                    '''Hi %s,

Your account on physanthphylogeny.org has been approved by a moderator. You can now directly update the information that appears on the site using this link.

http://physanthphylogeny.org/detail/%s/

Thanks,
The physanthphylogeny.org team''' %(self.user,self.associated_PhD.URL_for_detail,),
                    'do-not-reply@physanthphylogeny.org',
                    [self.user.email,],
                    fail_silently=False,
                )
                self.alert_email_sent = True
        super(UserProfile, self).save()

class socialMediaPosts(models.Model):
    PhD = models.ForeignKey(PhD)
    date_posted = models.DateTimeField(auto_now_add=True)
    facebook = models.BooleanField(default=True)
    twitter = models.BooleanField(default=True)
    def __unicode__(self):
        return str(self.PhD) + " " + str(self.date_posted.date())
    class Meta:
        verbose_name_plural = "social media posts"
        verbose_name = "social media post"

#######BELOW IS DEPRECATED###########
############################
CHOICES_editable_fields = [("firstName", "firstName"), ("lastName", "lastName"), ("year", "year")]

class suggestedPhDTextUpdate(models.Model):
    ## deals with user suggested updates for fields that can be stored as text
    PhD = models.ForeignKey(PhD)
    field = models.CharField(choices=CHOICES_editable_fields, max_length=100)
    value = models.CharField(max_length=100)
    moderator_approved = models.BooleanField(default=False)
    approver = models.ForeignKey(User, default=1)

class person(models.Model):
    firstName = models.CharField(max_length = 100,blank=True,null=True)
    middleName = models.CharField(max_length = 100,blank=True,null=True)
    lastName = models.CharField(max_length = 100,blank=True,null=True)
    yearOfPhD = models.IntegerField(max_length= 4, blank=True,null=True)
    school = models.ForeignKey(school)
    specialization = models.ManyToManyField(specialization,null=True,blank=True)
    URL_for_detail = models.CharField(max_length = 200,null=True)
    #shareImageURL = models.URLField(max_length=200, null=True, blank=True)
    featureImage = models.FileField(max_length=255, blank=True, upload_to="people/images/", null=True)
    featureBlurb = models.TextField(max_length=2000, null=True, blank=True, help_text="formatted with with <\p> tags")
    isFeatured = models.NullBooleanField()
    dateFeatured = models.DateField(null=True, blank=True)
    def get_absolute_url(self):
        return reverse('academicPhylogeny.views.detail', args=[self.URL_for_detail])

    def __unicode__(self):
            name = self.firstName + " " + self.lastName
            return name

    def save(self):#custom save method for person to update detail URL
        self.URL_for_detail = (self.firstName + "_" + self.lastName).replace(" ","_")

        #call the normal person save method
        super(person, self).save()

    class Meta:
            db_table = 'person'
            unique_together = (("firstName", "lastName"),)
            ordering = ['lastName']
            verbose_name_plural = 'people'



class connection(models.Model):
    advisor = models.ManyToManyField(person,related_name="a+")
    student = models.ForeignKey(person)

    def student_First_Name(self):
        return(self.student.firstName)
    student_First_Name.admin_order_field = 'student__firstName'

    def student_Last_Name(self):
        return(unicode(self.student.lastName))
    student_Last_Name.admin_order_field = 'student__lastName'

    def student_Year_Of_PhD(self):
        return(str(self.student.yearOfPhD))
    student_Year_Of_PhD.admin_order_field = 'student__yearOfPhD'

    def advisor_name(self):
        allAdvisors = []
        for each in self.advisor.all():
            allAdvisors.append(unicode(each.lastName))

        advisorNames = "/".join(allAdvisors)
        return(unicode(advisorNames))
    advisor_name.admin_order_field = 'advisor__lastName'

    def connectionJSON(self):
        allAdvisors = []
        try:
            for each in self.advisor.all():
                allAdvisors.append(unicode(each.firstName) + " " +  unicode(each.lastName))
            to_be_formatted = '{"source":"' + allAdvisors[0] + '", "target":"' + unicode(self.student.firstName) + " " + unicode(self.student.lastName) + '"}'
        except IndexError:
            to_be_formatted = '{"source":"' + "Unknown" + '", "target":"' + unicode(self.student.firstName) + " " + unicode(self.student.lastName) + '"}'
        return to_be_formatted.replace("None","Unknown")
    def __unicode__(self):
        return self.advisor_name() + "-->>" + self.student.firstName + " " + self.student.lastName + " (" + str(self.student.yearOfPhD) + ")"

    class Meta:
        db_table = "connection"
        unique_together = ('student',)
        ordering = ('student',)
#######ABOVE IS DEPRECATED###########
############################
