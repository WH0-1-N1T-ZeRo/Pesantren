# scrap
import requests
from bs4 import BeautifulSoup

from odoo import http
from odoo.http import request,Response
from odoo.models import check_method_name
from odoo.api import call_kw
from odoo.tools import date_utils

API_URL = '/api/v1'

class IbsAlhamraApi(http.Controller):
    @http.route(API_URL+'/news', auth='none', type='json', method=['POST'])
    def api_news(self):
        req = requests.get('https://ibsalhamra.sch.id/category/uncategorized/page/1')
        if req.status_code != 200: return False
        soup = BeautifulSoup(req.content, 'html.parser')
        point = soup.find('div',class_='posts-layout')
        items = point.find_all('div',class_='entry-inner')

        news = []
        for item in items:
            title = item.find('h2',class_='entry-title')
            excerpt = item.find('div',class_='entry-excerpt')
            thumbnail = item.find('div',class_='entry-thumbnail')
            href = title.a.get('href')
            news.append({
                'title': title.a.text,
                'id': href[len('https://ibsalhamra.sch.id/'):len(href)],
                'text' : excerpt.p.text,
                'image' : thumbnail.img.get('src')
            })
        return news
    @http.route(API_URL+'/article', auth='none', type='json', method=['POST'])
    def api_article(self,**kwargs):
        news = kwargs.get('id')
        if not news: return None
        req = requests.get('https://ibsalhamra.sch.id/'+news)
        if req.status_code != 200: return False
        soup = BeautifulSoup(req.content,'html.parser')
        point = soup.find('article',class_='entry-single')
        return {
            'title':point.find('h1',class_='entry-title').text,
            'thumbnail':point.find('div',class_='entry-thumbnail').img.get('src'),
            'content':point.find('div',class_='entry-content').text,
            'image_tree':[img.get('src') for img in point.find_all('img',class_='alignnone')]
        }
    @http.route(API_URL+'/gallery', auth='none', type='json', method=['POST'])
    def api_gallery(self):
        req = requests.get('https://ibsalhamra.sch.id/')
        if req.status_code != 200: return False
        soup = BeautifulSoup(req.content,'html.parser')
        return  [img.get('src') for img in soup.find_all('img',class_='swiper-slide-image')]
