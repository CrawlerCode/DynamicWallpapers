import time, psutil, requests, urllib, os, PySimpleGUI
from bs4 import BeautifulSoup
from PIL import Image

BASE_PATH = os.getenv('APPDATA') + '\Dynamic-Wallpapers\\'

class BaseModule:

    def __init__(self, wallpaper, cfg, cfgData, name):
        self.wallpaper = wallpaper
        self.cfg = cfg
        self.name = name
        self.updateTime = 3
        self.lastUpdate = 0
        self.active = False
        self.data = {}
        for mod in cfgData["Modules"]:
            if mod["name"] == self.name:
                self.active = mod["active"]
                self.data = mod["data"]
        self.settings = []

    def handle(self, img, draw, height):
        if time.time() - self.lastUpdate >= self.updateTime:
            self.onUpdate()
            self.lastUpdate = time.time()
        h = self.onDraw(img, draw, height)
        if h is not None and h > 0:
            return h
        else:
            return 0

    def update(self, cfg, cfgData):
        for mod in cfgData["Modules"]:
            if mod["name"] == self.name:
                mod["active"] = self.active
                mod["data"] = self.data
                cfg.saveConfig()
                self.wallpaper.menu.update()
                return
        cfgData["Modules"].append({"name": self.name, "active": self.active, "data": self.data})
        cfg.saveConfig()
        self.wallpaper.menu.update()

    def onUpdate(self):
        pass

    def onDraw(self, img, draw, height):
        pass

class TimeModule(BaseModule):

    def __init__(self, wallpaper, cfg, cfgData):
        BaseModule.__init__(self, wallpaper, cfg, cfgData, "Time")
        self.updateTime = 1
        self.time = ""

    def onUpdate(self):
        self.time = time.strftime("%H:%M", time.localtime())

    def onDraw(self, img, draw, height):
        self.wallpaper.drawCenteredText(draw, pos=(1920 / 2, 1080 / 2), text=self.time, color=(255, 255, 255), fontSize=80)

class DateModule(BaseModule):

    def __init__(self, wallpaper, cfg, cfgData):
        BaseModule.__init__(self, wallpaper, cfg, cfgData, "Date")
        self.updateTime = 60
        self.date = ""

    def onUpdate(self):
        self.date = time.strftime("%Y/%m/%d", time.localtime())

    def onDraw(self, img, draw, height):
        self.wallpaper.drawCenteredText(draw, pos=(1920 / 2, 1080 / 2 + self.wallpaper.getFontHeight(80)), text=self.date, color=(255, 255, 255), fontSize=30)

class CPUandRAMModule(BaseModule):

    def __init__(self, wallpaper, cfg, cfgData):
        BaseModule.__init__(self, wallpaper, cfg, cfgData, "CPU/RAM")
        self.cpu = ""
        self.ram = ""

    def onUpdate(self):
        self.cpu = str(psutil.cpu_percent()) + "%"
        self.ram = str(psutil.virtual_memory()._asdict()["percent"]) + "%"

    def onDraw(self, img, draw, start_height):
        start_x = 1920 - 150
        start_y = start_height
        space = 10
        width1 = space*2 + self.wallpaper.getFontWidth("CPU: " + self.cpu, 20)
        width2 = space*2 + self.wallpaper.getFontWidth("RAM: " + self.ram, 20)
        height = space*3 + self.wallpaper.getFontHeight(20)*2
        black = Image.new('RGBA', (width1 if width1 > width2 else width2, height), color=(0, 0, 0, 160))
        img.paste(black, (start_x, start_y), black)

        self.wallpaper.drawText(draw, (start_x + space, start_y + space), "CPU: " + self.cpu, (255, 255, 255), 20)
        self.wallpaper.drawText(draw, (start_x + space, start_y + self.wallpaper.getFontHeight(20) + space*2), "RAM: " + self.ram, (255, 255, 255), 20)
        return height

class YouTubeSubscriberModule(BaseModule):

    def __init__(self, wallpaper, cfg, cfgData):
        BaseModule.__init__(self, wallpaper, cfg, cfgData, "YouTubeSubscriber")
        self.updateTime = 60*30
        self.channel = ""
        if "channel" in self.data:
            self.channel = self.data["channel"]
        self.subscriber = "0"
        self.profile = None
        self.username = ""
        def openChannel():
            PySimpleGUI.theme("DarkGrey")
            window = PySimpleGUI.Window("YouTube Subscriber Channel", [[PySimpleGUI.Text("Channel: "), PySimpleGUI.InputText(self.channel)], [PySimpleGUI.Button("Cancel"), PySimpleGUI.Button("OK")]], icon=b'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')
            while True:
                event, values = window.read()
                if event in (None, 'Cancel'):
                    break
                if event == "OK":
                    self.channel = values[0]
                    self.data["channel"] = self.channel
                    self.settings = [("Active: " + str(self.active), toggle), ("Channel: " + self.channel, openChannel)]
                    self.update(cfg, cfgData)
                    break
            window.close()
            self.onUpdate()
        def toggle():
            self.active = not self.active
            self.settings = [("Active: " + str(self.active), toggle), ("Channel: " + self.channel, openChannel)]
            self.update(cfg, cfgData)
        self.settings = [("Active: " + str(self.active), toggle), ("Channel: " + self.channel, openChannel)]

    def onUpdate(self):
        response = BeautifulSoup(requests.get('https://www.youtube.com/channel/' + self.channel).content, "html.parser")
        try:
            urllib.request.urlretrieve(str(response.find_all("link", attrs={"rel": "image_src"})[0]["href"]), BASE_PATH + self.channel + ".png")
            pixels = []
            self.profile = Image.open(BASE_PATH + self.channel + ".png").resize((28, 28)).convert("RGBA")
            for item in self.profile.getdata():
                if item[0] >= 235 and item[1] >= 235 and item[2] >= 235:
                    pixels.append((255, 255, 255, 0))
                else:
                    pixels.append(item)
            self.profile.putdata(pixels)
        except:
            pass
        self.username = response.find_all("img", attrs={"class": "appbar-nav-avatar"})[0]["title"]
        self.subscriber = str(response.find_all("span", attrs={"class": "yt-subscription-button-subscriber-count-branded-horizontal subscribed yt-uix-tooltip"})[0]["title"])

    def onDraw(self, img, draw, start_height):
        start_x = 30
        start_y = 1080 - 150
        space = 12
        width1 = space*3 + 23 + self.wallpaper.getFontWidth(self.username, 23)
        width2 = space*2 + self.wallpaper.getFontWidth("Subscribers: " + self.subscriber, 23)
        height = space*3 + 23 + self.wallpaper.getFontHeight(20)
        black = Image.new('RGBA', (width1 if width1 > width2 else width2, height), color=(0, 0, 0, 120))
        img.paste(black, (start_x, start_y), black)
        try:
            img.paste(self.profile, (start_x + space, start_y + space), self.profile)
        except:
            pass
        self.wallpaper.drawText(draw, (start_x + space*2 + 23, start_y + space), self.username, (140, 217, 255), 23)
        self.wallpaper.drawText(draw, (start_x + 10 + 23/2, start_y + space*2 + 23), "Subscribers: " + self.subscriber, (201, 237, 255), 20)
        return self.wallpaper.getFontHeight(20) + 5

def getAllModules(wallpaper, cfg, cfgData):
    return [TimeModule(wallpaper, cfg, cfgData), DateModule(wallpaper, cfg, cfgData), CPUandRAMModule(wallpaper, cfg, cfgData), YouTubeSubscriberModule(wallpaper, cfg, cfgData)]