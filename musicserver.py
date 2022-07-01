#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  4 17:15:20 2022

@author: franciscojjimenezh
"""
import socket

from selenium import webdriver 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.options import Options
from parsel import Selector
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
 
from pynput.keyboard import Controller

class Music:
    
    def __init__(self):
        
        self.last_song = ''
        self.reproduc = None
        self.reproduc_v = True
        self.current = 0
        
        self.host = socket.gethostname()
        self.port = 12345
        self.BUFFER_SIZE = 1024
        
        self.keyboard = Controller()
        
        self.opts = Options()
        self.opts.add_argument("--headless")
    
    def volume(self, v):
        if not self.reproduc_v: 
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate( IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
             
            volume.SetMasterVolumeLevel(v, None)
            self.current = v
            
    def fetch_url(self, song):
        
        song2 = song.replace(" ", "+")
        
        url_base = "https://www.youtube.com"
    
        url = url_base + '/results?search_query=' + song2
        
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.opts)
        driver.get(url)
        
        sel = Selector(driver.page_source)
        result1 = sel.xpath('//div/h3/a[@class="yt-simple-endpoint style-scope ytd-video-renderer"]/@href').extract_first()
        url_res = url_base + result1
        driver.close()
        
        return url_res
    
    def get_data(self, data):
        
        res = data.decode('utf-8')
        res2 = res.split(sep='///')

        return res2[0], float(res2[1])
        
    def server(self):
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        
        while True:
            sock.listen(5) 
            conn, addr = sock.accept() 

            while True:
                data = conn.recv(self.BUFFER_SIZE)
   
                if data:
                    try: 
                        song, v = self.get_data(data)
                        
                        if song != 'stop':
                        
                            url = self.fetch_url(song)
                        
                            self.reproduc_v = False if self.current != v else True
                            self.volume(v)
                            
                            if self.last_song != song:
                                self.reproduc = False

                            if self.last_song != song or not self.last_song:
                                driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.opts)
                                driver.get(url)
                                
                                video = driver.find_element_by_id('movie_player')
                                video.send_keys(Keys.SPACE)

                                self.last_song = song
                                self.reproduc = True
                                
                                conn.send('Reproducida'.encode('utf-8')) 
                                
                        else:
                            conn.send('Pausada'.encode('utf-8')) 
                            
                            video = driver.find_element_by_id('movie_player')
                            video.send_keys(Keys.SPACE)
                            
                    except Exception as e: 
                        conn.send(str(e).encode('utf-8')) 
                else: break
                conn.send(bytes('','utf-8')) 

if '__name__' == '__main__':
    
    music = Music()
    music.server()