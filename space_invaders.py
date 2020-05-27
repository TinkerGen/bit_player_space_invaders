from microbit import *
import random

JoyStick_X = pin1
JoyStick_Y = pin2

DIR = {
    'NONE': 0,
    'L': 3,
    'R': 4,
}

class DisplayBuf:
    def __init__(self, val="00000:00000:00000:00000:00000"):
        self.buffer = list(val)
    def set(self, x, y, val, add=False, clamp=False):
        x = round(x)
        y = round(y)
        if not clamp and (x>2 or x<-2 or y>2 or y<-2):
            return
        x=min(2, max(-2,x))
        y=min(2, max(-2,y))
        pos = 14+x+6*y
        if add:
            val = val+int(self.buffer[pos])
        val = min(9, max(0, val))
        self.buffer[pos] = str(val)
        return (x,y,val)

    def render(self):
        display.show(Image(''.join(self.buffer)))

class Mover:
    def __init__(self, x, y, dy):
        self.x = x
        self.y = y
        self.dy = dy
        self.bright = 9
    def move(self):
        self.y = self.y+self.dy
    def render(self, dispBuf):
        dispBuf.set(self.x, self.y, self.bright)
        
    
class Bullet(Mover):
    def __init__(self, x):
        super(Bullet, self).__init__(x, 1, -0.1)

        
class Invader(Mover):
    def __init__(self, x):
        super(Invader, self).__init__(x, -2, 0.02)
        self.bright = 6
        
class JOYSTICK():
    def __init__(self):
        self.Read_X = JoyStick_X.read_analog()

    def Listen_Dir(self, Dir):
        Get_Rocker = DIR['NONE']
        New_X = JoyStick_X.read_analog()

        Right = New_X - self.Read_X
        Left = self.Read_X - New_X

        # max = 1023
        Precision = 150

        if Right > Precision:
            Get_Rocker = DIR['R']
        elif Left > Precision:
            Get_Rocker = DIR['L']
        else:
            Get_Rocker = DIR['NONE']

        if Dir == Get_Rocker:
            return True
        else:
            return False

score = 0
health = 100
shield = 90
bpressed = False
bullets = []
vaders = []
levels = [(2,30,100)]
level = 0
game_over = False
x = 3
JoyStick = JOYSTICK()

while not game_over:
    (maxvaders, vaderchance, levelup) = levels[level]
    
    if JoyStick.Listen_Dir(DIR['R']) == 1:
        x = x + 1
    if JoyStick.Listen_Dir(DIR['L']) == 1:
        x = x - 1
        
    if x > 2:
        x = 2
    if x < -2:
        x = -2

    dispBuf = DisplayBuf()
    dispBuf.set(x,2,7,clamp=True)
    shieldon = button_a.is_pressed() and shield>0
    if shieldon:
        shield = shield - 0.1
        for sx in range(5):
            dispBuf.set(sx-2,1,round(shield/10),clamp=True)
    if button_b.is_pressed():
        if not bpressed:
            score = max(0, score-1)
            if len(bullets)<4:
                bullets.append(Bullet(x))
        bpressed = True
    else:
        bpressed = False
        
    if len(vaders)<maxvaders and random.randint(1, vaderchance)==1:
        vaders.append(Invader(random.randint(-2, 2)))

    for b in bullets:
        b.render(dispBuf)
    for v in vaders:
        v.render(dispBuf)
        
    dispBuf.render()

    for b in bullets:
        b.move()
        for v in vaders:
            if round(b.y)==round(v.y) and round(b.x)==round(v.x):
                b.y=-100
                v.y=100
                score = score+10

    for v in vaders:
        v.move()
        if round(v.y)>=1:
            if shieldon:
                v.y=100
                shield = shield - 5
            elif round(v.y)==2:
                game_over = True
        
    bullets = [b for b in bullets if round(b.y)>=-2]
    vaders = [v for v in vaders if round(v.y)<=2]

    sleep(20)

display.scroll("Game Over... %d"%score)
sleep(1000)
display.clear()