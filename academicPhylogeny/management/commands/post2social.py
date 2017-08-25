# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from academicPhylogeny.models import PhD, socialMediaPosts
from academicPhylogeny.secrets import FACEBOOK_PHYSPHYLO_PAGE_ID,FACEBOOK_PHYSPHYLO_PAGE_ACCESS_TOKEN, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_KEY_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
import requests
import tweepy
from datetime import date

class Command(BaseCommand):
    help = 'posts to facebook'


    def debug(self, TWmsg, FBmsg):
        self.stdout.write("Tweet:" + TWmsg)
        self.stdout.write("\nFacebook:" + FBmsg)

    def post(self, selectedPhD, TWmsg=None, FBmsg=None, link=None):
        newPostDB = None
        if FBmsg:
            token = FACEBOOK_PHYSPHYLO_PAGE_ACCESS_TOKEN
            pageID = FACEBOOK_PHYSPHYLO_PAGE_ID
            dataDict = {"message": FBmsg, "link": link, "access_token": token}
            post_url = "https://graph.facebook.com/v2.10/%d/feed" % (pageID,)
            r = requests.post(url=post_url, data=dataDict)
            if r.status_code == 200:
                self.stdout.write(self.style.SUCCESS('Successfully posted to facebook!'))
                if not newPostDB:
                    newPostDB = socialMediaPosts(PhD=selectedPhD,facebook=True,twitter=False)
                    newPostDB.save()
                else:
                    newPostDB.facebook = True
                    newPostDB.save()
            else:
               self.stdout.write(self.style.ERROR("Facebook post failure."))

        if TWmsg:
            auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_KEY_SECRET)
            auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
            api = tweepy.API(auth)
            api.update_status(TWmsg)
            if not newPostDB:
                newPostDB = socialMediaPosts(PhD=selectedPhD, facebook=False, twitter=True)
                newPostDB.save()
            else:
                newPostDB.twitter = True
                newPostDB.save()


    def handle(self, *args, **options):

        prior_posts = socialMediaPosts.objects.all().values_list("PhD")
        unpostedCurrentYearPhDs = PhD.objects.filter(year=date.today().year, validated=True).exclude(id__in=prior_posts)
        legacyPhDs = PhD.objects.filter(validated=True, school__isnull=False, year__isnull=False, year__lte=2000).order_by("year").exclude(id__in=prior_posts)

        if unpostedCurrentYearPhDs.__len__() > 0:
            selectedPhD = unpostedCurrentYearPhDs[0]
            link = "https://www.physanthphylogeny.org%s" % (selectedPhD.get_absolute_url(),)
            FBmsg = ("Congratulations to Dr. %s, who recently completed a PhD at %s with %s."
                     " This information now appears in the academic genealogy network on our website!"
                     " Submit your own information if it isn't already in the database!") % (
                        selectedPhD.firstName + " " + selectedPhD.lastName,
                        selectedPhD.school,
                        (" and ").join(
                            [advisor.firstName + " " + advisor.lastName for advisor in selectedPhD.advisor.all()])
                    )
            TWmsg = "Congrats to Dr. %s for completing a PhD at %s! #bioanthphd %s" % (
                selectedPhD.firstName + " " + selectedPhD.lastName,
                selectedPhD.school,
                link)
        else:
            selectedPhD = legacyPhDs[0]
            link = "https://www.physanthphylogeny.org%s" % (selectedPhD.get_absolute_url(),)
            advisorPhrase = ""
            advisorPeriodOrNot = "."
            if(len(selectedPhD.advisor.all()) > 0):
                advisorsAnd = (" and ").join(
                            [advisor.firstName + " " + advisor.lastName for advisor in selectedPhD.advisor.all()]
                )
                advisorPhrase = "with " + advisorsAnd + "."
                advisorPeriodOrNot = ""
            studentsPhrase = ""
            students = PhD.objects.filter(validated=True, advisor = selectedPhD)
            if len(students) > 0:
                studentsPhrase = "%s advised at least %d PhD students including: %s." %(
                    selectedPhD.lastName,
                    len(students),
                    ", ".join([student.__unicode__().strip() for student in students])
                )
            FBmsg = ("%s completed a PhD at %s in %s%s %s %s\n\nLearn more on our website...") % (
                        selectedPhD.__unicode__().strip(),
                        selectedPhD.school,
                        selectedPhD.year,
                        advisorPeriodOrNot,
                        advisorPhrase,
                        studentsPhrase
                    )
            TWmsg = "%s completed a PhD at %s in %s #bioanthphd %s" % (
                selectedPhD.__unicode__().strip(),
                selectedPhD.school,
                selectedPhD.year,
                link)


        #self.debug(TWmsg, FBmsg)
        self.post(selectedPhD=selectedPhD, FBmsg=FBmsg, TWmsg=TWmsg, link=link)