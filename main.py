import os
from random import choice, random, randint

from kivy.animation import Animation
from kivy.app import App
from kivy.graphics import BorderImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, StringProperty 
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.utils import get_color_from_hex
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.core.window import Window

Window.clearcolor = get_color_from_hex('#101216')   
Window.size = (600,150)

import pygame
pygame.init()
pygame.mixer.init()
MUSIC_DIR = 'music/'

TTF_DIR = "ttf/"

LabelBase.register(
    name="Roboto",
    fn_regular = TTF_DIR + "Roboto-Regular.ttf",
    fn_bold = TTF_DIR + "Roboto-Bold.ttf",
    fn_italic = TTF_DIR + "Roboto-Italic.ttf",
    fn_bolditalic = TTF_DIR + "Roboto-BoldItalic.ttf")

animations = {
    0:'in_back',
    1:'in_bounce',
    2:'in_circ',
    3:'in_cubic',
    4:'in_elastic',
    5:'in_expo',
    6:'in_out_back',
    7:'in_out_bounce',
    8:'in_out_circ',
    9:'in_out_cubic',
    10:'in_out_elastic',
    11:'in_out_expo',
    12:'in_out_quad',
    13:'in_out_quart',
    14:'in_out_quint',
    15:'in_out_sine',
    16:'in_quad',
    17:'in_quart',
    18:'in_quint',
    19:'in_sine',
    20:'linear',
    21:'out_back',
    22:'out_bounce',
    23:'out_circ',
    24:'out_cubic',
    25:'out_elastic',
    26:'out_expo',
    27:'out_quad',
    28:'out_quart',
    29:'out_quint',
    30:'out_sine'
}

ATLAS_PATH = "atlas://images/star/"
stars = dict(zip([x for x in range(7)], [ATLAS_PATH + "star" + str(x) for x in range(1, 8)]))

class AnimWidget(Widget):
    image = StringProperty()
    def __init__(self, **kwargs):
        super(AnimWidget, self).__init__(**kwargs)
        self.pos = (random() * Window.width, Window.height)
        self.size = (50,50)
        self.fall_animation()
        self.image = stars[randint(0,6)]
           
    def fall_animation(self, *args):
        Animation.cancel_all(self)
        duration = randint(5,10)
        self.pos = (random() * Window.width, Window.height)
        x_destination = random() * (Window.width + self.width)
        y_destination = 0 - self.width
        
        
        
        anim = Animation(x=x_destination, y=y_destination,
                                                duration=duration,
                                                t = animations[randint(0,30)])
        anim.start(self)
        anim.bind(on_complete=lambda *args: self.fall_animation())
        
class AnimLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(AnimLayout, self).__init__(**kwargs)
        self.star = {}
        for i in range(30):
            self.star[i] = AnimWidget()
            self.add_widget(self.star[i])
        
        
class MusicButton(Button):
    
    def __init__(self, **kwargs):
        super(MusicButton, self).__init__(**kwargs)
        self.size_hint = (None, 0.7)
        self.background_down = ATLAS_PATH + 'button_pressed'
        self.background_normal = ATLAS_PATH + 'button_normal'
        self.border =  (0, 0, 0, 0)    
          
          
class MusicToggleButton(ToggleButton):
    
    image = StringProperty('')
    def __init__(self, **kwargs):
        super(MusicToggleButton, self).__init__(**kwargs)
        self.image = ATLAS_PATH + 'button_normal'
      
    def on_state(self, *args):
        if self.state == 'normal':
            self.image = ATLAS_PATH + 'button_normal'
        elif self.state == 'down':
            self.image = ATLAS_PATH + 'button_pressed'
        
       
class VolumeSlider(Slider):
    
    def __init__(self, **kwargs):
        super(VolumeSlider, self).__init__(**kwargs)
        self.sliderbackground = ATLAS_PATH + "slider_background3"
        self.sliderknob = ATLAS_PATH + "slider_button2"
        
class MusicLayout(BoxLayout):
    
    background_image = StringProperty('')
    
    def __init__(self, **kwargs):
        super(MusicLayout, self).__init__(**kwargs)
        self.song_list = MusicLayout.list_music_files()
        print(self.song_list)
        self.song_index = 0
        self.number_of_songs = len(self.song_list)
        self.paused = False
        self.volume = 0.5
        self.p = None
        self.shuffle = False
        self.repeat = False
        self.update_song_labels()
        self.background_image = ATLAS_PATH + "background"
   
    @staticmethod
    def list_music_files(directory="music/"):
        extensions = (".ogg")
        musicfiles = list(filter(lambda x: x.endswith(extensions), os.listdir(directory)))
        musicfiles.sort()
        
        return [x for x in musicfiles]            
       
    def toggle_repeat(self):
        if self.ids.repeat_toggle.state == 'down':
            self.repeat = True
        elif self.ids.repeat_toggle.state == 'normal':
            self.repeat = False
        print(self.repeat)
       
    def toggle_shuffle(self):
        if self.ids.shuffle_toggle.state =='down':
            self.shuffle = True
        elif self.ids.shuffle_toggle.state == 'normal':
            self.shuffle = False
        print(self.shuffle)      
       
    def update_song_labels(self):
        self.current_song = self.song_list[self.song_index]
        self.next_song = self.song_list[(self.song_index + 1)% self.number_of_songs]
        self.ids.currentLabel.text = "[b]Current:[/b] [i]{}[/i]".format(self.current_song)

    def change_song_index(self, inc):
        self.song_index = (self.song_index + inc) % self.number_of_songs
     
    def play(self):
        self.paused = False
        self.update_song_labels()
        pygame.mixer.music.load(MUSIC_DIR + self.song_list[self.song_index])
        pygame.mixer.music.play()
        Clock.schedule_once(self.play_helper, 0)
        Clock.schedule_interval(self.auto_play, 2)
        
    def play_helper(self, dt):
        if pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        else:
            Clock.unschedule(self.player_helper)

    def auto_play(self, dt):
        if not pygame.mixer.music.get_busy() and not self.paused:
            if self.shuffle:
                self.song_index = randint(0, self.number_of_songs)
            elif not self.shuffle and not self.repeat:
                self.song_index = (self.song_index + 1) % self.number_of_songs
                
            self.play()
                
    def pause(self):
        if not self.paused:
            self.paused = True
            pygame.mixer.music.pause()
        else:
            self.paused = False
            pygame.mixer.music.unpause()           
        
    def stop(self):
        self.paused = True
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            Clock.unschedule(self.play_helper)
    
    def change_song(self, inc):
        self.stop()
        self.change_song_index(inc)
        self.update_song_labels()
        self.play()
        
    def change_volume(self):
        pygame.mixer.music.set_volume(self.ids.volumeSlider.value/100)

class musicApp(App):    
    def build(self):
        return MusicLayout()

if __name__ == '__main__':
    musicApp().run()
    