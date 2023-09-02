import gc
# enable garbage collection and set the threshold
gc.enable()
gc.threshold((gc.mem_free() + gc.mem_alloc()) // 4)

# excessive gc after modules load to reduce fragmentation of memory
from machine import Timer, Pin, reset
gc.collect()
from micropython import schedule
gc.collect()
import micropython
gc.collect()
import math
gc.collect()
import time
gc.collect()
from random import random, randint
gc.collect()
import array
gc.collect()
from os import stat
gc.collect()
from is31fl3737 import is31fl3737, rgb_value
gc.collect()

micropython.alloc_emergency_exception_buf(100)

TOUCH_PINS = (4, 5, 6, 7, 22, 23, 24, 25)
from touch import TouchController
gc.collect()

def file_exists(filename):
    try:
        return (stat(filename)[0] & 0x4000) == 0
    except OSError:
        return False

def pallet_rainbow(target):
    print("rainbow")
    for i in range(len(target)):
        target[i][0] = i/len(target)
        target[i][1] = 1.0
        target[i][2] = 255

def pallet_set_colour(target, hue, hue_spread, sat, sat_spread):
    offset = 0.0
    start = 0
    end   = 0
    count = int(len(target)/16)
    for i in range(16):
        dir_change = random() * 0.1
        if offset + dir_change >  hue_spread/2:
            dir_change = -dir_change
        if offset - dir_change < -hue_spread/2:
            dir_change = -dir_change
        offset += dir_change
        if offset >  hue_spread/2:
            offset =  hue_spread/2
        if offset < -hue_spread/2:
            offset = -hue_spread/2

        end   = offset
        step_size = (start - end)/count
        for j in range(count):
            pos = j / count
            offset = (step_size * pos) + start
            target[i*count + j][0] = hue+offset
            target[i*count + j][1] = sat
            target[i*count + j][2] = 255
        start = end
    end   = 0
    step_size = (start - end)/count
    for j in range(count):
        pos = j / count
        offset = (step_size * pos) + start
        target[len(target)-count+j][0] = hue+offset
        target[len(target)-count+j][1] = sat
        target[len(target)-count+j][2] = 255

def pallet_blue(target):
    pallet_set_colour(target, 0.5, 0.3, 0.8, 0.4)
    print("blue")

def pallet_red(target):
    pallet_set_colour(target, 0.0, 0.3, 0.8, 0.4)
    print("red")

def pallet_yellow(target):
    pallet_set_colour(target, 0.07, 0.3, 0.8, 0.4)
    print("yellow")

def pallet_green(target):
    pallet_set_colour(target, 0.25, 0.3, 0.8, 0.4)
    print("green")

def pallet_purple(target):
    pallet_set_colour(target, 0.75, 0.3, 0.8, 0.4)
    print("purple")

def pallet_magenta(target):
    pallet_set_colour(target, 0.85, 0.3, 0.8, 0.4)
    print("magenta")

class animation_rainbow_around:
    def __init__(self, badge):
        self.badge = badge
        self.offset = 0.0

    def update(self):
        self.offset += 0.5
        for i in range(46):
            self.badge.disp.clockwise[i].hsv(self.badge.pallet[int(1024*((i+self.offset)/60))&0x3FF][0], 1.0, 100)
        self.badge.disp.eye1.hsv(self.badge.pallet[int(1024*((i+self.offset)/46))&0x3FF][0], 1.0, 200)
        self.badge.disp.eye2.hsv(self.badge.pallet[int(1024*((i+self.offset)/46))&0x3FF][0], 1.0, 200)

class animation_rainbow_down:
    def __init__(self, badge):
        self.badge = badge
        self.offset = 0.0

    def update(self):
        self.offset -= 0.5
        for i in range(48):
            self.badge.disp.downward[i].hsv(self.badge.pallet[int(1024*(i+self.offset)/100)&0x3FF][0], 1.0, 100)
        self.badge.disp.eye1.hsv(self.badge.pallet[int(1024*((i+self.offset)/46))&0x3FF][0], 1.0, 200)
        self.badge.disp.eye2.hsv(self.badge.pallet[int(1024*((i+self.offset)/46))&0x3FF][0], 1.0, 200)

class animation_chasers:
    def __init__(self, badge):
        self.badge = badge
        self.traces = []
        self.last = time.ticks_ms()
        self.next = time.ticks_add(self.last, int(random() * 1000))
        self.max_traces = 3
        self.decay = 0.95
        self.brightness = 255
        self.buffer = [rgb_value() for i in range(46)]
        self.eye_offset = 0.0

    def update(self):
        if time.ticks_diff(self.next, time.ticks_ms()) <= 0:
            colour = self.badge.pallet[int(1024*random())][0]
            speed = (0.5-((random()-0.5)**2))*1.2*(1 if (random()>0.5) else 0)

            #                      0      1               2            3            4         5
            #                   colour  speed           position    life_rate      life      record
            self.traces.append([colour, speed, float(random()*46), (random()*0.07), 1.0,  array.array("f", [0]*46)])
            self.next = time.ticks_add(time.ticks_ms(), int(random()*3500))

            # if traces are not dying off increase life_rate decay
            if len(self.traces) > self.max_traces:
                for i in range(len(self.traces)):
                    self.traces[i][3] += 0.01

        for trace in self.traces:
            if trace[4] <= 0:
                self.traces.remove(trace)

        for i in range(46):
            self.buffer[i].r = 0.0
            self.buffer[i].g = 0.0
            self.buffer[i].b = 0.0

        for trace in self.traces:
            trace[4] -= trace[3]
            if trace[4] < 0:
                trace[4] = 0
            if trace[4] > 0.1:
                end_gain = 1.0
            else:
                end_gain = trace[4] * 10.0
            for i in range(46):
                trace[5][i] *= (self.decay * end_gain)

            trace[2] += trace[1]
            trace[5][int(trace[2])%46] = self.brightness * end_gain

            for i in range(46):
                r,g,b = self.buffer[0].hsv(trace[0],1.0,trace[5][i],1.0,ret_value=True)
                self.buffer[i].value[0] += r
                self.buffer[i].value[1] += g
                self.buffer[i].value[2] += b

        for i in range(46):
            if self.buffer[i].r > self.brightness:
                self.buffer[i].r = self.brightness
            if self.buffer[i].g > self.brightness:
                self.buffer[i].g = self.brightness
            if self.buffer[i].b > self.brightness:
                self.buffer[i].b = self.brightness
            if self.buffer[i].r < 0:
                self.buffer[i].r = 0
            if self.buffer[i].g < 0:
                self.buffer[i].g = 0
            if self.buffer[i].b < 0:
                self.buffer[i].b = 0
            self.badge.disp.clockwise[i].value[0] = int(self.buffer[i].r)
            self.badge.disp.clockwise[i].value[1] = int(self.buffer[i].g)
            self.badge.disp.clockwise[i].value[2] = int(self.buffer[i].b)

        self.eye_offset += 0.5
        self.badge.disp.eye1.hsv((i+self.eye_offset)/46, 1.0, self.brightness)
        self.badge.disp.eye2.hsv((i+self.eye_offset)/46, 1.0, self.brightness)

class animation_sparkle:
    def __init__(self, badge):
        self.badge = badge
        self.offset = 0.0
        self.last = time.ticks_ms()
        self.next = time.ticks_add(self.last, int(random() * 1000))
        self.decay = [0.0 for i in range(48)]
        self.buffer = [0.0 for i in range(48)]

    def update(self):
        if time.ticks_diff(self.next, time.ticks_ms()) <= 0:
            pixel = randint(0,47)
            decay = (random()*10.0 + 1.0)
            self.buffer[pixel] = 100
            self.decay[pixel] = decay

            self.next = time.ticks_add(time.ticks_ms(), int(random()*200))

        for i in range(48):
            self.buffer[i] -= self.decay[i]
            if self.buffer[i] < 0:
                self.buffer[i] = 0
                self.decay[i] = 0

        self.offset -= 0.5
        for i in range(48):
            self.badge.disp.downward[i].hsv(self.badge.pallet[int(1024*(i+self.offset)/100)&0x3FF][0], 1.0, self.buffer[i])
        self.badge.disp.eye1.hsv(self.badge.pallet[int(1024*((i+self.offset)/46))&0x3FF][0], 1.0, 200)
        self.badge.disp.eye2.hsv(self.badge.pallet[int(1024*((i+self.offset)/46))&0x3FF][0], 1.0, 200)

class badge(object):
    def __init__(self):
        self.disp = is31fl3737()
        self.touch = TouchController(TOUCH_PINS)
        self.touch.channels[0].level_lo = 15000
        self.touch.channels[0].level_hi = 20000
        self.touch.channels[1].level_lo = 15000
        self.touch.channels[1].level_hi = 20000
        self.touch.channels[2].level_lo = 15000
        self.touch.channels[2].level_hi = 20000
        self.touch.channels[3].level_lo = 15000
        self.touch.channels[3].level_hi = 20000
        self.anim_index = 1
        self.half_bright = False
        self.animations = [animation_rainbow_around(self),animation_rainbow_down(self),animation_chasers(self),animation_sparkle(self)]
        self.animation_names = ["rainbow around", "rainbow_down", "chasers", "sparkle"]
        self.pallet_index = 0
        self.pallet_functions = [pallet_rainbow, pallet_blue, pallet_red, pallet_yellow, pallet_green, pallet_purple, pallet_magenta]
        self.blush_mix = 0.0
        self.ear1_mix = 0.0
        self.ear2_mix = 0.0
        self.blush_count = 0
        self.ear1_count = 0
        self.ear2_count = 0
        self.boop_debounce = 0
        self.booped = False
        self.ear1_touch = False
        self.ear2_touch = False

        self.wink_mix = 0.0
        self.wink_count = 0
        self.wink_flag = False

        self.sw4 = Pin(10)
        self.sw5 = Pin(11)

        self.sw4_state = 0xFF
        self.sw5_state = 0xFF

        self.sw4_count = 0
        self.sw5_count = 0
        self.sw4_last  = 0
        self.sw5_last  = 0

        self.pallet = [[0.0,0.0,0.0] for i in range(1024)]
        self.pallet_functions[self.pallet_index](self.pallet)

        self.read_config()

        self.mem_info_count = 0

        print("Dreams are messages from the deep.")
        self.timer = Timer(mode=Timer.PERIODIC, freq=15, callback=self.isr_update) # <== Comment out to use the polled method

    def save_config(self):
        with open("config", "w") as file:
            file.write("half_bright=")
            if self.half_bright:
                file.write("true\n")
            else:
                file.write("false\n")
            file.write("anim_index="+str(self.anim_index)+"\n")
            file.write("pallet_index="+str(self.pallet_index)+"\n")

    def read_config(self):
        if file_exists("config"):
            with open("config", "r") as file:
                data = file.read().splitlines()
            for line in data:
                if line == "half_bright=true":
                    self.half_bright = True

                if line[:11] == "anim_index=":
                    self.anim_index = int(line[11:])

                if line[:13] == "pallet_index=":
                    self.pallet_index = int(line[13:])
                    self.pallet_functions[self.pallet_index](self.pallet)

    def blush(self, mix):
        if mix > 1.0: mix = 1.0
        if mix < 0.0: mix = 0.0

        for l in self.disp.cheak1:
            l.r = (l.r *  (1-mix)) + (mix * 255)
            l.g = (l.g *  (1-mix)) + (mix * 10)
            l.b = (l.b *  (1-mix)) + (mix * 10)

        for l in self.disp.cheak2:
            l.r = (l.r *  (1-mix)) + (mix * 255)
            l.g = (l.g *  (1-mix)) + (mix * 10)
            l.b = (l.b *  (1-mix)) + (mix * 10)

    def ear1_blush(self, mix):
        if mix > 1.0: mix = 1.0
        if mix < 0.0: mix = 0.0

        for l in self.disp.ear1:
            l.r = (l.r *  (1-mix)) + (mix * 255)
            l.g = (l.g *  (1-mix)) + (mix * 10)
            l.b = (l.b *  (1-mix)) + (mix * 10)

    def ear2_blush(self, mix):
        if mix > 1.0: mix = 1.0
        if mix < 0.0: mix = 0.0

        for l in self.disp.ear2:
            l.r = (l.r *  (1-mix)) + (mix * 255)
            l.g = (l.g *  (1-mix)) + (mix * 10)
            l.b = (l.b *  (1-mix)) + (mix * 10)

    def eye2_wink(self, mix):
        if mix > 1.0: mix = 1.0
        if mix < 0.0: mix = 0.0

        self.disp.eye2.r = (self.disp.eye2.r * (1-mix)) + (mix * 0)
        self.disp.eye2.g = (self.disp.eye2.g * (1-mix)) + (mix * 0)
        self.disp.eye2.b = (self.disp.eye2.b * (1-mix)) + (mix * 0)

    def isr_update(self,*args):
        try:
            schedule(self.update, self)
        except:
            # don't complain about the warnings saying the schedule queue is full. It's fine.
            pass

    def update(self,*args):
        try:
            self.touch.update()
            if (self.touch.channels[0].level > 0.3) or (self.touch.channels[1].level > 0.3):
                self.boop_debounce += 1
                if not self.booped and self.boop_debounce > 3:
                    print("boop", end = "")
                    if (self.touch.channels[0].level > 0.3) and (self.touch.channels[1].level > 0.3):
                        print("!")
                        if randint(1,100) > 50:
                            self.wink_flag = True
                            self.wink_count = 6
                            self.wink_mix = 1

                    elif (self.touch.channels[0].level > 0.3) and not (self.touch.channels[1].level > 0.3):
                        print(".")
                    else:
                        print("'")
                    self.booped = True
                self.blush_count = 50
                if self.blush_mix < 1.0:
                    self.blush_mix += 0.5
            else:
                self.booped = False
                self.boop_debounce = 0
                if self.blush_count > 0:
                    self.blush_count -= 1
                else:
                    if self.blush_mix > 0.0:
                        self.blush_mix -= 0.05

            gc.collect()

            if self.wink_count > 0:
                self.wink_count -= 1
            elif self.wink_mix > 0.0:
                self.wink_flag = False
                self.wink_mix -= 0.1

            if (self.touch.channels[3].level > 0.3):
                if not self.ear1_touch:
                    print("ear1")
                    self.ear1_touch = True
                self.ear1_count = 12
                if self.ear1_mix < 1.0:
                    self.ear1_mix += 0.5
            else:
                self.ear1_touch = False
                if self.ear1_count > 0:
                    self.ear1_count -= 1
                else:
                    if self.ear1_mix > 0.0:
                        self.ear1_mix -= 0.05

            if (self.touch.channels[2].level > 0.3):
                if not self.ear2_touch:
                    print("ear2")
                    self.ear2_touch = True
                self.ear2_count = 12
                if self.ear2_mix < 1.0:
                    self.ear2_mix += 0.5
            else:
                self.ear2_touch = False
                if self.ear2_count > 0:
                    self.ear2_count -= 1
                else:
                    if self.ear2_mix > 0.0:
                        self.ear2_mix -= 0.05

            gc.collect()

            self.sw4_state <<= 1
            self.sw4_state |= self.sw4()
            self.sw5_state <<= 1
            self.sw5_state |= self.sw5()
            if (self.sw4_state & 0x3) == 0x0:
                self.sw4_count += 1
            else:
                self.sw4_count = 0
            if (self.sw5_state & 0x3) == 0x0:
                self.sw5_count += 1
            else:
                self.sw5_count = 0

            if self.sw4_count == 0 and self.sw4_last > 0:
                if self.sw4_last > 10: # long press
                    self.half_bright = not self.half_bright
                    if self.half_bright:
                        print("Half bright")
                    else:
                        print("Full bright")
                else:
                    self.anim_index += 1
                    if self.anim_index >= len(self.animations):
                        self.anim_index = 0
                    print(self.animation_names[self.anim_index])
                self.save_config()
            elif self.sw5_count == 0 and self.sw5_last > 0:
                if self.sw5_last > 10:
                    self.pallet_index += 1
                    if self.pallet_index >= len(self.pallet_functions):
                        self.pallet_index = 0
                    self.pallet_functions[self.pallet_index](self.pallet)
                else:
                    self.anim_index -= 1
                    if self.anim_index < 0:
                        self.anim_index = len(self.animations)-1
                    print(self.animation_names[self.anim_index])
                self.save_config()

            self.sw4_last = self.sw4_count
            self.sw5_last = self.sw5_count

            if self.half_bright:
                self.disp.brightness = 50
            else:
                self.disp.brightness = 255

            self.animations[self.anim_index].update()
            if self.blush_mix:
                self.blush(self.blush_mix)
            if self.ear1_mix:
                self.ear1_blush(self.ear1_mix)
            if self.ear2_mix:
                self.ear2_blush(self.ear2_mix)
            if self.wink_mix:
                self.eye2_wink(self.wink_mix)
            self.disp.update()

            # memory reporting
            #self.mem_info_count += 1
            #if self.mem_info_count > 450:
            #    self.mem_info_count = 0
            #    print(micropython.mem_info())

            gc.collect()

        except MemoryError as error:
            # gc didn't do it's job, so just reset
            print(error)
            time.sleep(3)
            reset()

    def run(self):
        while True:
            self.update()
            time.sleep(1/15)


global t
t = badge()
# t.run() <== to use the poled method
