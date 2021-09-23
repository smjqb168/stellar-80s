import threading
import time
import bs4
import requests
import StellarPlayer
import re
import urllib.parse
import urllib.request
import math
import json

eighty_url = 'https://www.1680s.com'

class eightysplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        super().__init__(player)
        self.menuall = []
        self.secmenu = []
        self.medias = []
        self.firstpage = ''
        self.lastpage = ''
        self.nextpage = ''
        self.previouspage = ''
        self.cur_page = ''
        self.allmovidesdata = {}

    
    def start(self):
        super().start()
        res = requests.get(eighty_url,verify=False)
        if res.status_code == 200:
            bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
            selector = bs.find_all('a', class_='fed-navs-title fed-font-xvi fed-hide-xs fed-hide-sm fed-show-md-block')
            for item in selector:
                menuname = item.string
                menuurl = eighty_url + item.get('href')
                self.menuall.append({'title':menuname,'url':menuurl}) 
        searchurl = eighty_url + '/map.html'
        self.loadMedias(searchurl)
    
    def show(self):
        controls = self.makeLayout()
        self.doModal('main',800,600,'',controls)
    
    def makeLayout(self):   
        mainmenu = []
        for cat in self.menuall:
            mainmenu.append({'type':'link','name':cat['title'],'@click':'onMenuMainClick','width':60})
        
        mediagrid_layout = [
            [
                {
                    'group': [
                        {'type':'image','name':'picture', '@click':'on_grid_click'},
                        {'type':'link','name':'title','textColor':'#ff7f00','fontSize':15,'height':0.2, '@click':'on_grid_click'}
                    ],
                    'dir':'vertical'
                }
            ]
        ]
        controls = [
            {'type':'space','height':5},
            {
                'group':[
                    {'type':'edit','name':'search_edit','label':'搜索','width':0.4},
                    {'type':'button','name':'搜索','@click':'onSearch','width':80}
                ],
                'width':1.0,
                'height':30
            },
            {'type':'space','height':10},
            {'group':mainmenu,'height':30},
            {'type':'space','height':5},
            {'group':[],'height':30,'name':'secmenugroup'},
            {'type':'grid','name':'mediagrid','itemlayout':mediagrid_layout,'value':self.medias,'separator':True,'itemheight':200,'itemwidth':120},
            {'group':
                [
                    {'type':'space'},
                    {'group':
                        [
                            {'type':'label','name':'cur_page',':value':'cur_page'},
                            {'type':'link','name':'首页','@click':'onClickFirstPage'},
                            {'type':'link','name':'上一页','@click':'onClickFormerPage'},
                            {'type':'link','name':'下一页','@click':'onClickNextPage'},
                            {'type':'link','name':'末页','@click':'onClickLastPage'},
                        ]
                        ,'width':0.45
                    },
                    {'type':'space'}
                ]
                ,'height':30
            },
            {'type':'space','height':5}
        ]
        return controls
    
    def onSearch(self, *args):
        search_word = self.player.getControlValue('main','search_edit')
        if len(search_word) > 0:
            searchurl = eighty_url + '/vodsearch/' + urllib.parse.quote(search_word,encoding='utf-8') + '-1.html'
            self.loadMedias(searchurl)
    
    def onMenuMainClick(self,pageId,control,*args):
        controls = []
        self.secmenu = []
        self.player.removeControl('main','canremovemenugroup')
        secmenuurl = ''
        for item in self.menuall:
            if item['title'] == control:
                secmenuurl = item['url']
        if secmenuurl != '':
            res = requests.get(secmenuurl,verify=False)
            if res.status_code == 200:
                bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
                selector = bs.find_all('div', class_='fed-list-head fed-part-rows fed-padding')
                for item in selector:
                    nameinfo = item.select('h2')
                    urlinfo = item.select('ul > li > a')
                    if nameinfo and urlinfo:
                        name = nameinfo[0].string
                        url = eighty_url + urlinfo[0].get('href')
                        self.secmenu.append({'title':name,'url':url})
            self.loadMedias(secmenuurl) 
        for cat in self.secmenu:
            controls.append({'type':'link','name':cat['title'],'width':60,'@click':'onSecondMenuClick'})
        row = {'group':controls,'name':'canremovemenugroup'}
        self.player.addControl('main','secmenugroup',row)
          
    def onSecondMenuClick(self,pageId,control,*args):
        selecturl = ''
        for item in self.secmenu:
            if item['title'] == control:
                selecturl = item['url']
        print(selecturl)
        if selecturl != '':
            self.loadMedias(selecturl)
    
    def loadMedias(self,url):
        self.loading()
        self.medias = []
        res = requests.get(url,verify=False)
        if res.status_code == 200:
            bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
            selector = bs.find_all('li', class_='fed-list-item fed-padding fed-col-xs4 fed-col-sm3 fed-col-md2')
            if selector:
                for item in selector:
                    picinfo = item.select('a.fed-list-pics.fed-lazy.fed-part-2by3')
                    urlinfo = item.select('a.fed-list-title.fed-font-xiv.fed-text-center.fed-text-sm-left.fed-visible.fed-part-eone')
                    if picinfo and urlinfo:
                        pic = picinfo[0].get('data-original')
                        print(pic)
                        name = urlinfo[0].string
                        mediaurl = eighty_url + urlinfo[0].get('href')
                        self.medias.append({'url':mediaurl,'picture':pic,'title':name})
            else:
                selector = bs.find_all('dl', class_='fed-list-deta fed-deta-padding fed-line-top fed-margin fed-part-rows fed-part-over')
                if selector:
                    for item in selector:
                        picinfo = item.select('dt > a')
                        urlinfo = item.select('dd.fed-deta-content.fed-col-xs7.fed-col-sm8 > h3 > a')
                        if picinfo and urlinfo:
                            pic = picinfo[0].get('data-original')
                            name = urlinfo[0].string
                            mediaurl = eighty_url + urlinfo[0].get('href')
                            self.medias.append({'url':mediaurl,'picture':pic,'title':name})
            pageselector = bs.find_all('div',class_='fed-page-info fed-text-center')
            if pageselector:
                pages = pageselector[0].select('a')
                n = len(pages)
                self.firstpage =  eighty_url + pages[0].get('href')
                self.lastpage = eighty_url + pages[n - 1].get('href')
                self.nextpage = eighty_url + pages[n - 2].get('href')
                self.previouspage = eighty_url + pages[1].get('href')
                self.cur_page = '第' + pages[n - 3].getText() + '页'
                print(self.firstpage)
                print(self.nextpage)
                print(self.lastpage)
                print(self.previouspage)
            else:
                self.cur_page = '第1/1页'
        self.player.updateControlValue('main','mediagrid',self.medias)
        self.loading(True)
               
    def onClickFirstPage(self, *args):
        if self.firstpage == '':
            return 
        self.loadMedias(self.firstpage)
        
    def onClickFormerPage(self, *args):
        if self.previouspage == '':
            return 
        self.loadMedias(self.previouspage)
    
    def onClickNextPage(self, *args):
        if self.nextpage == '':
            return 
        self.loadMedias(self.nextpage)
        
    def onClickLastPage(self, *args):
        if self.lastpage == '':
            return 
        self.loadMedias(self.lastpage)
     
    def getPlayPageUrl(self,pageurl):
        res = requests.get(pageurl,verify=False)
        if res.status_code == 200:
            bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
            selector = bs.find_all('a', class_='fed-deta-play fed-rims-info fed-btns-info fed-btns-green fed-col-xs4')
            print(selector[0])
            playpageurl = eighty_url + selector[0].get('href')
            return playpageurl
        return ''
        
    def on_grid_click(self, page, listControl, item, itemControl):
        self.loading()
        mediapageurl = self.medias[item]['url']
        res = requests.get(mediapageurl)
        xls = []
        playurls = []
        picurl = ''
        medianame = ''
        infostr = ''
        if res.status_code == 200:
            bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
            selector = bs.find_all('dt', class_='fed-deta-images fed-list-info fed-col-xs3')[0]
            if selector:
                picinfo = selector.select('a')[0]
                if picinfo:
                    picurl = picinfo.get('data-original')
            
            selector = bs.find_all('dd', class_='fed-deta-content fed-col-xs7 fed-col-sm8')[0]
            if selector:
                nameinfo = selector.select('h3 > a')[0]
                if nameinfo:
                    medianame = nameinfo.string
                actorinfo = selector.select('ul > li')
                for item in  actorinfo:
                    span = item.select('span')[0]
                    infostr = infostr + item.getText() + '\\n'                
            
            selector = bs.find_all('div', class_='fed-tabs-foot')
            xlselector = selector[0]
            playurlselector = selector[1]
            if xlselector:
                xllist = xlselector.select('ul > li')
                n = 0
                for item in xllist:
                    n = n + 1
                    xls.append({'index':n,'title':item.select('a.fed-tabs-btn.fed-btns-info.fed-rims-info.fed-part-eone')[0].string})
                    
            if playurlselector:
                urls = playurlselector.select('ul')
                n = 0
                for itemurls in urls:
                    n = n + 1
                    urllist = itemurls.select('li')
                    listurl = []
                    for urlitem in urllist:
                        info = urlitem.select('a')[0]
                        name = info.string
                        pageurl = eighty_url + info.get('href')
                        listurl.append({'playname':name,'url':pageurl})
                    playurls.append(listurl)
        
        allmovies = playurls
        actmovies = []
        if len(playurls) > 0:
            actmovies = playurls[0]
        self.allmovidesdata[medianame] = {'allmovies':allmovies,'actmovies':actmovies}
        
        xl_list_layout = {'type':'link','name':'title','textColor':'#ff0000','width':0.6,'@click':'on_xl_click'}
        movie_list_layout = {'type':'link','name':'playname','@click':'on_movieurl_click'}
        controls = [
            {'type':'space','height':5},
            {'group':[
                    {'type':'image','name':'mediapicture', 'value':picurl,'width':0.35},
                    {'type':'label','name':'info','value':infostr,'width':0.65}
                ],
                'width':1.0,
                'height':240
            },
            {'group':
                {'type':'grid','name':'xllist','itemlayout':xl_list_layout,'value':xls,'separator':True,'itemheight':25,'itemwidth':80},
                'height':30
            },
            {'type':'space','height':5},
            {'group':
                {'type':'grid','name':'movielist','itemlayout':movie_list_layout,'value':actmovies,'separator':True,'itemheight':25,'itemwidth':120},
                'height':200
            }
        ]
        self.loading(True)
        result,controls = self.player.doModal(medianame,400,470,medianame,controls)
    
    def on_xl_click(self, page, listControl, item, itemControl):
        if len(self.allmovidesdata[page]['allmovies']) > item:
            self.allmovidesdata[page]['actmovies'] = self.allmovidesdata[page]['allmovies'][item]
        self.player.updateControlValue(page,'movielist',self.allmovidesdata[page]['actmovies'])
        
    def on_movieurl_click(self, page, listControl, item, itemControl):
        if len(self.allmovidesdata[page]['actmovies']) > item:
            playurl = self.allmovidesdata[page]['actmovies'][item]['url']
            print(playurl)
            self.playMovieUrl(playurl)
            
    def playMovieUrl(self,playpageurl):
        res = requests.get(playpageurl)
        if res.status_code == 200:
            bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
            try:
                selector = bs.find_all('div', class_='fed-play-player')[0]
                item = selector.select('div')[0]
                scriptitem = item.select('script')[0]
                print(scriptitem)
                jsonstr = re.findall(r"var player_aaaa=(.+)",scriptitem.string)[0]
                playerjson = json.loads(jsonstr)
                print(playerjson)
                playurl  = playerjson['url']
                self.player.play(playurl)
            except:
                selector = bs.find_all('p', class_='copyright_notice')
                if len(selector) > 0:
                    self.player.toast('mediaframe',selector[0].string)
            
    def loading(self, stopLoading = False):
        if hasattr(self.player,'loadingAnimation'):
            self.player.loadingAnimation('main', stop=stopLoading)
        
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = eightysplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()