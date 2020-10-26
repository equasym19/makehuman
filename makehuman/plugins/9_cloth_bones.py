nope
from core import G
import events3d

class ClothBones(events3d.EventHandler):
    def __init__(self, app):
        super(ClothBones, self).__init__()
        self.app=app
        self.human=app.selectedHuman
    def onHumanChanging(self,event):
        if event.change == 'reset':
            print(self.app)
            print(self.human)
    def onHumanChanged(self,event):
        if event.change == 'proxyChange':
            if event.proxy != 'clothes':
                return
            proxy = event.proxy_obj
            if not proxy:
                return
            print("NL")
            if proxy.uuid=="b9c8ba49-005f-497e-abe0-62efc8cdfc7c":
                doThing(proxy)
    def doThing(proxy):
        proxy.vertexBoneWeights=

def load(app):
    handler=ClothBones(app)
    app.addEventHandler(handler,6000)
    print("NL",app.selectedHuman)
def unload(app):
    pass

