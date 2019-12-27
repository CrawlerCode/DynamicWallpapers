import time, psutil, requests, urllib, os, socket, shutil
from bs4 import BeautifulSoup
from PIL import Image, ImageFont, ImageDraw
from pythontools.core import config

BASE_PATH = os.getenv('APPDATA') + '\Dynamic-Wallpapers\\'

class BaseModule:

    def __init__(self, wallpaper, name, default_font="segoeuil.ttf", default_color="#ffffff", default_position=[0, 0], default_settings={}):
        self.wallpaper = wallpaper
        self.cfg = config.getConfig()
        self.name = name
        self.updateTime = 5
        self.lastUpdate = 0
        self.settings = {"Active": False, "Position": default_position, "Font": default_font, "Color": default_color}
        self.settings.update(default_settings)
        cfgData = self.cfg.getConfig()
        for mod in cfgData["Modules"]:
            if mod["name"] == self.name:
                self.settings = mod["settings"]
        self.fontDraw = ImageDraw.Draw(Image.new('RGB', (1920, 1080), color='black'))

    def handle(self, img, draw):
        if time.time() - self.lastUpdate >= self.updateTime:
            self.onUpdate()
            self.lastUpdate = time.time()
        self.onDraw(img, draw, self.settings["Position"])

    def update(self):
        cfgData = self.cfg.getConfig()
        for mod in cfgData["Modules"]:
            if mod["name"] == self.name:
                mod["settings"] = self.settings
                self.cfg.saveConfig()
                self.onUpdate()
                self.wallpaper.menu.update()
                return
        cfgData["Modules"].append({"name": self.name, "settings": self.settings})
        self.cfg.saveConfig()
        self.onUpdate()
        self.wallpaper.menu.update()

    def getFont(self, size):
        return ImageFont.truetype('/Library/Fonts/' + self.settings["Font"], size)

    def getFontHeight(self, size):
        return self.fontDraw.textsize(text="text", font=self.getFont(size))[1]

    def getFontWidth(self, text, size):
        return self.fontDraw.textsize(text=text, font=self.getFont(size))[0]

    def drawCenteredText(self, draw, pos, text, color, fontSize):
        font = self.getFont(fontSize)
        w, h = draw.textsize(text=text, font=font)
        draw.text((pos[0] - w / 2, pos[1] - h / 2), text=text, fill=color, font=font)

    def drawText(self, draw, pos, text, color, fontSize):
        draw.text(pos, text=text, fill=color, font=self.getFont(fontSize))

    def drawBackground(self, img, x, y, width, height):
        black = Image.new('RGBA', (width, height), color=(0, 0, 0, 120))
        img.paste(black, (x, y), black)

    def onUpdate(self):
        pass

    def onDraw(self, img, draw, position):
        pass

class TimeModule(BaseModule):

    def __init__(self, wallpaper):
        BaseModule.__init__(self, wallpaper, "Time", default_position=[int(1920/2), int(1080/2)])
        self.updateTime = 3
        self.time = ""

    def onUpdate(self):
        self.time = time.strftime("%H:%M", time.localtime())

    def onDraw(self, img, draw, position):
        self.drawCenteredText(draw, pos=position, text=self.time, color=self.settings["Color"], fontSize=80)

class DateModule(BaseModule):

    def __init__(self, wallpaper):
        BaseModule.__init__(self, wallpaper, "Date", default_position=[int(1920/2), int(1080/2+80)])
        self.updateTime = 60
        self.date = ""

    def onUpdate(self):
        self.date = time.strftime("%Y/%m/%d", time.localtime())

    def onDraw(self, img, draw, position):
        self.drawCenteredText(draw, pos=position, text=self.date, color=self.settings["Color"], fontSize=30)

class ComputerModule(BaseModule):

    def __init__(self, wallpaper):
        BaseModule.__init__(self, wallpaper, "Computer", default_position=[1920-190, 20], default_settings={"CPU": True, "RAM": True, "IP": False, "Disk": False})
        self.updateTime = 3
        self.cpu = ""
        self.ram = ""
        self.ip = ""
        self.disk = ""

    def onUpdate(self):
        if self.settings["IP"]:
            self.ip = socket.gethostbyname(socket.gethostname())
        if self.settings["CPU"]:
            self.cpu = str(psutil.cpu_percent()) + "%"
        if self.settings["RAM"]:
            self.ram = str(psutil.virtual_memory()._asdict()["percent"]) + "%"
        if self.settings["Disk"]:
            self.disk = str(round(shutil.disk_usage("/")[1] // (2**30), 1)) + "GB/" + str(round(shutil.disk_usage("/")[0] // (2**30), 1)) + "GB"

    def onDraw(self, img, draw, position):
        start_x = position[0]
        start_y = position[1]
        space = 10
        widths = []
        height = space
        drawTasks = []
        if self.settings["CPU"]:
            drawTasks.append(((start_x + space, start_y + height), "CPU: " + self.cpu, self.settings["Color"], 20))
            widths.append(space * 2 + self.getFontWidth("CPU: " + self.cpu, 20))
            height += space + self.getFontHeight(20)
        if self.settings["RAM"]:
            drawTasks.append(((start_x + space, start_y + height), "RAM: " + self.ram, self.settings["Color"], 20))
            widths.append(space * 2 + self.getFontWidth("RAM: " + self.ram, 20))
            height += space + self.getFontHeight(20)
        if self.settings["IP"]:
            drawTasks.append(((start_x + space, start_y + height), "IP: " + self.ip, self.settings["Color"], 20))
            widths.append(space * 2 + self.getFontWidth("IP: " + self.ip, 20))
            height += space + self.getFontHeight(20)
        if self.settings["Disk"]:
            drawTasks.append(((start_x + space, start_y + height), "Disk: " + self.disk, self.settings["Color"], 20))
            widths.append(space * 2 + self.getFontWidth("Disk: " + self.disk, 20))
            height += space + self.getFontHeight(20)
        self.drawBackground(img, start_x, start_y, max(widths), height)
        for task in drawTasks:
            self.drawText(draw, task[0], task[1], task[2], task[3])

class YouTubeSubscriberModule(BaseModule):

    def __init__(self, wallpaper):
        BaseModule.__init__(self, wallpaper, "YouTubeSubscriber", default_position=[30, 1080-150], default_settings={'Url': 'https://www.youtube.com/channel/UCqVS1YFEYDW5wJ4sKegOcXA'})
        self.updateTime = 60*30
        self.subscriber = "0"
        self.profile = None
        self.username = ""

    def onUpdate(self):
        try:
            response = BeautifulSoup(requests.get(self.settings["Url"]).content, "html.parser")
            self.username = response.find_all("img", attrs={"class": "appbar-nav-avatar"})[0]["title"]
            urllib.request.urlretrieve(str(response.find_all("link", attrs={"rel": "image_src"})[0]["href"]), BASE_PATH + self.username + ".png")
            pixels = []
            self.profile = Image.open(BASE_PATH + self.username + ".png").resize((28, 28)).convert("RGBA")
            for item in self.profile.getdata():
                if item[0] >= 235 and item[1] >= 235 and item[2] >= 235:
                    pixels.append((255, 255, 255, 0))
                else:
                    pixels.append(item)
            self.profile.putdata(pixels)
            self.subscriber = str(response.find_all("span", attrs={"class": "yt-subscription-button-subscriber-count-branded-horizontal subscribed yt-uix-tooltip"})[0]["title"])
        except:
            pass

    def onDraw(self, img, draw, position):
        start_x = position[0]
        start_y = position[1]
        space = 12
        width1 = space*3 + 23 + self.getFontWidth(self.username, 23)
        width2 = space*2 + self.getFontWidth("Subscribers: " + self.subscriber, 23)
        height = space*3 + 23 + self.getFontHeight(20)
        self.drawBackground(img, start_x, start_y, max([width1, width2]), height)
        try:
            img.paste(self.profile, (start_x + space, start_y + space), self.profile)
        except:
            pass
        self.drawText(draw, (start_x + space*2 + 23, start_y + space), self.username, self.settings["Color"], 23)
        self.drawText(draw, (start_x + 10 + 23/2, start_y + space*2 + 23), "Subscribers: " + self.subscriber, self.settings["Color"], 20)

def getAllModules(wallpaper):
    return [TimeModule(wallpaper), DateModule(wallpaper), ComputerModule(wallpaper), YouTubeSubscriberModule(wallpaper)]