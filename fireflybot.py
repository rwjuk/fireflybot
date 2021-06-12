#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, datetime, logging
import pywikibot
import mwparserfromhell
import difflib

class FireflyBot():
    def task_permitted(self):
            if self.task_number < 1:
                return True
            shutoff_page_title = "User:FireflyBot/shutoff/{}".format(self.task_number)
            shutoff_page = pywikibot.Page(site, shutoff_page_title)

            return (shutoff_page.get().strip().lower() == "active")

    def allow_bots(self, raw_text, user="FireflyBot"):
            user = user.lower().strip()
            text = mwparserfromhell.parse(raw_text)
            for tl in text.filter_templates():
                    if tl.name.matches(['bots', 'nobots']):
                            break
            else:
                    return True
            for param in tl.params:
                    bots = [x.lower().strip() for x in param.value.split(",")]
                    if param.name == 'allow':
                            if ''.join(bots) == 'none': return False
                            for bot in bots:
                                    if bot in (user, 'all'):
                                            return True
                    elif param.name == 'deny':
                            if ''.join(bots) == 'none': return True
                            for bot in bots:
                                    if bot in (user, 'all'):
                                            return False
            if (tl.name.matches('nobots') and len(tl.params) == 0):
                    return False
            return True

    def save_edit(page, newtext, comment, minor=True):
            if not self.task_permitted():
                    raise Exception("Shutoff switch for task {} flipped!".format(self.task_number))

            oldtext = page.get()
            if self.allow_bots(oldtext):
                    page.put(newtext=newtext, comment=comment, minor=minor)

    def parse_wikitext(self, wikitext):
            parse_request = pywikibot.data.api.Request(site=self.site, parameters={'action':'parse','format':'json', 'text':wikitext, 'onlypst':1,'contentmodel': 'wikitext'})
            return parse_request.submit()["parse"]["text"]["*"]

    def generate_html_diff(self, old, new, table=False):
            if self.htmldiff == None:
                    self.htmldiff = difflib.HtmlDiff()

            old_l = old.splitlines()
            new_l = new.splitlines()
            if table:
                    retval = self.htmldiff.make_table(old_l, new_l, context=True, numlines=3)
            else:
                    retval =  self.htmldiff.make_file(old_l, new_l, context=True, numlines=3)

            return retval.replace("&nbsp;", " ").replace('nowrap="nowrap"',"")
    

    def __init__(self, task_number=-1):
            self.task_number=task_number
            self.site = pywikibot.Site()
            self.htmldiff = None
