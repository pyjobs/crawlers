# -*- coding: utf-8 -*-
import re
import parsedatetime

from datetime import datetime

from pyjobs_crawlers.spiders import JobSpider, JobSource, Tag


class BlueCodersSpider(JobSpider):
    name = u'bluecoders'
    start_urls = [u'http://bluecoders.io/search?search=python']
    label = u'Bluecoders'
    url = u'http://bluecoders.io/'
    logo_url = u'http://bluecoders.io/resources/images/logo_banneer.svg'

    _crawl_parameters = {
        'from_list__jobs_lists__xpath': '/html/body/main/div/div[@class="job-list"]/ul',
        'from_list__jobs__xpath': 'a',
        'from_list__url__xpath': '@href',
        'from_list__title__xpath': "li/div/div[contains(@class,'job-title-container')]/h4/text()",
        'from_list__publication_datetime__xpath': "li/div/div[contains(@class,'job-infos')]/p[contains(@class,'duration')]/span/text()",
        'from_list__tags__xpath': "li/div/div[contains(@class,'job-title-container')]/div/ul/li/img/@alt",

        'from_page__container__xpath': "/html/body/main/div/div/div[contains(@class,'card')]/div",
        'from_page__description__xpath': "div[contains(@class,'white-background')]/div/div[contains(@class,'adbody')]"
    }


    def _strip_HTML(self, data):
        return re.sub('<[^<]+?>', '', data)

    def _get_from_page__description(self, node):
        html_description = self._extract_first(node, 'from_page__description')
        if html_description:
            return self._strip_HTML(html_description)

    def _get_from_list__url(self, node):
        extracted_url = self._extract_first(node, 'from_list__url', required=True)
        return self._get_absolute_url(extracted_url.encode('utf-8'))

    def _get_from_list__tags(self, node):
        """
        Tags are hidden in img/alt ('alt="recrutement développeur python"')
        TODO : Must find another way to create tag instead of creating obj
        """

        raw_tags = self._extract_all(node, 'from_list__tags')

        if raw_tags:
            return [Tag(tag.split()[-1]) for tag in raw_tags]

        return True

    def _get_from_list__publication_datetime(self, node):
        """
            The datetime is humanized/natural (ex: "2 days ago")
            Our goal here is to parse to a datetime object
        """
        raw_date = self._extract_first(node, 'from_list__publication_datetime')
        if raw_date:
            cal = parsedatetime.Calendar()
            time_struct, parse_status = cal.parse(raw_date)
            return datetime(*time_struct[:6])


source = JobSource.from_job_spider(BlueCodersSpider)
