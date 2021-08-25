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


def concatUrl(url1, url2):
    splits = re.split(r'/+',url1)
    url = splits[0] + '//'
    if url2.startswith('/'):
        url = url + splits[1] + url2
    else:
        url = url + '/'.join(splits[1:-1]) + '/' + url2
    return url

class eightysplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        super().__init__(player)
        self.menuall = ['最新更新','电影','电视剧','动漫','综艺','体育']
        self.menudianying = ['动作片','喜剧片','爱情片','科幻片','恐怖片','剧情片','战争片','记录片','动画电影']
        self.menudianshiju = ['国产剧','欧美剧','日韩剧','港台剧','海外剧']
        self.menudongman = ['国产','日本','欧美','其它']
        self.menuzongyi = ['内地','港台','日韩','欧美']
        self.menutiyu = ['mma','wwe','ufc','足球']
        self.menu1 = self.menuall[0]
        self.menu2 = ''
        self.gridmenu = []
        self.medias = []
        self.playurl = ''
        self.searchtype = False
        self.firstpage = ''
        self.lastpage = ''
        self.nextpage = ''
        self.previouspage = ''
        self.cur_page = ''
        self.allmovidesdata = {}

    
    def show(self):
        controls = self.makeLayout()
        self.doModal('main',800,600,'',controls)
    
    def makeLayout(self):
        mainmenu = []
        for cat in self.menuall:
            mainmenu.append({'type':'link','name':cat,'@click':'onMenuMainClick'})
        secmenu = []
        
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
        self.menu2 = '搜索'
        self.search_word = self.player.getControlValue('main','search_edit')
        self.loadMediaList(1)
    
    def onMenuMainClick(self,pageId,control,*args):
        controls = []
        self.player.removeControl('main','canremovemenugroup')
        if control == '最新更新' or control == '动漫' or control == '综艺':
            self.menu2 = control
            self.loadMediaList(0)
        
        if control == '电影':
            for cat in self.menudianying:
                controls.append({'type':'link','name':cat,'width':60,'@click':'onSecondMenuClick'})
        elif control == '电视剧':
            self.menu2 = '最新剧集'
            for cat in self.menudianshiju:
                controls.append({'type':'link','name':cat,'width':60,'@click':'onSecondMenuClick'})     
        elif control == '体育':
            self.menu2 = '最近更新'
            for cat in self.menutiyu:
                controls.append({'type':'link','name':cat,'width':60,'@click':'onSecondMenuClick'})                 
        print(controls)
        row = {'group':controls,'name':'canremovemenugroup'}
        self.player.addControl('main','secmenugroup',row)
          
    def onSecondMenuClick(self,pageId,control,*args):
        self.menu2 = control
        self.loadMediaList(1)
        
    def loadMediaList(self,pageindex):
        searchurl = ''
        self.searchtype = False
        if self.menu2 == '搜索':
            self.searchtype = True
            search_word = self.player.getControlValue('main','search_edit')
            if len(search_word) > 0:
                searchurl = eighty_url + '/vodsearch/' + urllib.parse.quote(search_word,encoding='utf-8') + '-' + str(pageindex) + '.html'
        elif self.menu2 == '最新更新':
            searchurl = eighty_url + '/map.html'
        elif self.menu2 == '动作片':
            searchurl = eighty_url + '/vodtype/dongzuopian-' + str(pageindex) + '.html'
        elif self.menu2 == '喜剧片':
            searchurl = eighty_url + '/vodtype/xijupian-' + str(pageindex) + '.html'
        elif self.menu2 == '爱情片':
            searchurl = eighty_url + '/vodtype/aiqingpian-' + str(pageindex) + '.html'
        elif self.menu2 == '科幻片':
            searchurl = eighty_url + '/vodtype/kehuanpian-' + str(pageindex) + '.html'
        elif self.menu2 == '恐怖片':
            searchurl = eighty_url + '/vodtype/kongbupian-' + str(pageindex) + '.html'
        elif self.menu2 == '剧情片':
            searchurl = eighty_url + '/vodtype/juqingpian-' + str(pageindex) + '.html'
        elif self.menu2 == '战争片':
            searchurl = eighty_url + '/vodtype/zhanzhengpian-' + str(pageindex) + '.html'
        elif self.menu2 == '记录片':
            searchurl = eighty_url + '/vodtype/jilupian-' + str(pageindex) + '.html'
        elif self.menu2 == '动画电影':
            searchurl = eighty_url + '/vodtype/donghua-' + str(pageindex) + '.html'
        elif self.menu2 == '国产剧':
            searchurl = eighty_url + '/vodtype/guochanju-' + str(pageindex) + '.html'
        elif self.menu2 == '欧美剧':
            searchurl = eighty_url + '/vodtype/oumeiju-' + str(pageindex) + '.html'
        elif self.menu2 == '日韩剧':
            searchurl = eighty_url + '/vodtype/rihanju-' + str(pageindex) + '.html'
        elif self.menu2 == '港台剧':
            searchurl = eighty_url + '/vodtype/gangtaiju-' + str(pageindex) + '.html'
        elif self.menu2 == '海外剧':
            searchurl = eighty_url + '/vodtype/haiwaiju-' + str(pageindex) + '.html'
        elif self.menu2 == '动漫':
            searchurl = eighty_url + '/vodtype/dongman-' + str(pageindex) + '.html'
        elif self.menu2 == '综艺':
            searchurl = eighty_url + '/vodtype/zongyi-' + str(pageindex) + '.html'
        elif self.menu2 == 'mma':
            searchurl = eighty_url + '/vodtype/mma-' + str(pageindex) + '.html'
        elif self.menu2 == 'wwe':
            searchurl = eighty_url + '/vodtype/wwe-' + str(pageindex) + '.html'
        elif self.menu2 == 'ufc':
            searchurl = eighty_url + '/vodtype/ufc-' + str(pageindex) + '.html'
        elif self.menu2 == '足球':
            searchurl = eighty_url + '/vodtype/zhuqiu-' + str(pageindex) + '.html'
        print(searchurl)
        self.reloadPage(searchurl)
        
    def onClickFirstPage(self, *args):
        if self.firstpage == '':
            return 
        self.reloadPage(self.firstpage)
        
    def onClickFormerPage(self, *args):
        if self.previouspage == '':
            return 
        self.reloadPage(self.previouspage)
    
    def onClickNextPage(self, *args):
        if self.nextpage == '':
            return 
        self.reloadPage(self.nextpage)
        
    def onClickLastPage(self, *args):
        if self.lastpage == '':
            return 
        self.reloadPage(self.lastpage)
        
    def reloadPage(self,url):    
        medialist = []
        self.firstpage = ''
        self.lastpage = ''
        self.nextpage = ''
        self.previouspage = ''
        self.loading()
        if url != '':
            res = requests.get(url,verify=False)
            if res.status_code == 200:         
                bs = bs4.BeautifulSoup(res.content.decode('UTF-8','ignore'),'html.parser')
                if self.searchtype:
                    selector = bs.find_all('dd', class_='fed-deta-content fed-col-xs7 fed-col-sm8')
                    for item in selector:
                        urlinfo = item.parent.select('dd.fed-deta-button.fed-col-xs7.fed-col-sm8.fed-part-rows > a')[0]
                        picinfo = item.parent.select('dt.fed-deta-images.fed-list-info.fed-col-xs3 > a')[0]
                        nameinfo = item.select('h3.fed-part-eone')[0].select('a')[0]
                        url = eighty_url + urlinfo.get('href')
                        pic = eighty_url + picinfo.get('data-original')
                        name = nameinfo.getText()
                        medialist.append({'url':url,'picture':pic,'title':name})
                        
                    pageselector = bs.find_all('div',class_='fed-page-info fed-text-center')
                    if pageselector:
                        pages = pageselector[0].select('a')
                        n = len(pages)
                        self.firstpage =  eighty_url + pages[0].get('href')
                        self.lastpage = eighty_url + pages[n - 1].get('href')
                        self.nextpage = eighty_url + pages[n - 2].get('href')
                        self.previouspage = eighty_url + pages[1].get('href')
                        self.cur_page = '第' + pages[n - 3].getText() + '页'
                    else:
                        self.cur_page = '第1/1页'
                else:
                    selector = bs.select('body > div.fed-main-info.fed-min-width > div > div.fed-list-new.fed-part-layout.fed-back-whits > ul > li')
                    for item in selector:
                        urlinfo = item.select('a.fed-list-pics.fed-lazy.fed-part-2by3')[0]
                        nameinfo = item.select('a.fed-list-title.fed-font-xiv.fed-text-center.fed-text-sm-left.fed-visible.fed-part-eone')[0]
                        url = eighty_url + urlinfo.get('href')
                        pic = eighty_url + urlinfo.get('data-original')
                        name = nameinfo.getText()
                        medialist.append({'url':url,'picture':pic,'title':name})
                        
                    pageselector = bs.find_all('div',class_='fed-page-info fed-text-center')
                    if pageselector:
                        pages = pageselector[0].select('a')
                        n = len(pages)
                        self.firstpage =  eighty_url + pages[0].get('href')
                        self.lastpage = eighty_url + pages[n - 1].get('href')
                        self.nextpage = eighty_url + pages[n - 2].get('href')
                        self.previouspage = eighty_url + pages[1].get('href')
                        self.cur_page = '第' + pages[n - 3].getText() + '页'
                    else:
                        self.cur_page = '第1/1页'
                    
        print(self.firstpage)
        print(self.lastpage)
        print(self.nextpage)
        print(self.previouspage)
        self.medias = medialist
        self.player.updateControlValue('main','mediagrid',self.medias)
        self.loading(True)
        
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
                    picurl = eighty_url + picinfo.get('data-original')
            
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
                {'type':'grid','name':'movielist','itemlayout':movie_list_layout,'value':actmovies,'separator':True,'itemheight':25,'itemwidth':60},
                'height':150
            }
        ]
        self.loading(True)
        self.player.doModal(medianame,400,420,medianame,controls)

    
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
                jsonstr = re.findall(r"var player_data=(.+)",scriptitem.string)[0]
                playerjson = json.loads(jsonstr)
                self.playurl  = playerjson['url']
                self.player.play(self.playurl)
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