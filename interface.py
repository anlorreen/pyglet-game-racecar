import pyglet
import random
import engine

pyglet.resource.path = ["resources"]
pyglet.resource.reindex()

class Game(pyglet.window.Window):
    def __init__(self):
        pyglet.window.Window.__init__(self, width=700, height=670)
        self.set_location(350,35)
        self.set_caption("Race Car")

        #Key Handlers
        self.key = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key)

        #batches
        self.main_batch = pyglet.graphics.Batch()
        self.intro_text_batch = pyglet.graphics.Batch()

        #loading image display for player's car
        race_car = pyglet.resource.image("Black_viper.png")
        self.player = pyglet.sprite.Sprite(race_car, x = 290, y = 80,batch = self.main_batch)
        self.player.scale = 0.4

        #load background
        road = pyglet.resource.image("road2.png")
        self.road = pyglet.sprite.Sprite(road, x = 0, y = 0)
        self.road_list = []   #list for infinite scroll of background
        for i in range(2):
            self.road_list.append(pyglet.sprite.Sprite(road, x = 0, y = i*670))

        #load boulder image
        self.boulder_image = pyglet.resource.image("boulder.png")
        self.boulder_list = []    #initiate list for multiple boulders

        #load explosion animation
        explosion = pyglet.resource.image("explosion.png")
        self.explosion_sequence = pyglet.image.ImageGrid(explosion, 4, 5, item_width = 96, item_height=96)
        self.explosion_textures = pyglet.image.TextureGrid(self.explosion_sequence)
        self.explosion_animation = pyglet.image.Animation.from_image_sequence(self.explosion_textures[0:], 0.05, loop=True)

        #load explosion sound
        self.explosion_sound = pyglet.resource.media("TorpedoExplosion.wav", streaming=False)
        self.explosion_list = []
        self.explode_time = 1

        #load sound effects
        # self.snd = pyglet.resource.media('bgm.wav')
        # self.looper = pyglet.media.SourceGroup(self.snd.audio_format, None)
        # self.looper.loop = True
        # self.looper.queue(self.snd)
        # self.sndplayer = pyglet.media.Player()
        # self.sndplayer.queue(self.looper)
        #reference: Mitchel Humpherys's comment on stackoverflow, full reference on documentation

        #intro Screen
        self.intro_text = pyglet.text.Label("press enter to start", x=145, y=320)
        self.intro_text.italic = True
        self.intro_text.bold = True
        self.intro_text.font_size = 35
        #reference: Attila Toth via GitHub, full reference link on documentation

        #score
        self.score_label = pyglet.text.Label(text="Score: 0        High Score: 0", x=0, y=650)
        self.score = 0
        self.high_score = int(engine.load_high_score("resources/high_score.txt"))

        #game over
        self.game_over_label = pyglet.text.Label(text="Game Over!", x=350, y=330)
        self.game_over_label.anchor_x = "center"
        self.game_over_label.anchor_y = "center"
        self.game_over_label.font_name = "Courier New"
        self.game_over_label.font_size = 50

        #retry
        self.retry_label = pyglet.text.Label(text="Retry Game? \nPress Y to retry, else N.", x=350, y=240)
        self.retry_label.anchor_x = 'center'
        self.retry_label.anchor_y = 'center'
        self.retry_label.font_name = "Arial"
        self.retry_label.font_size = 20

        #score if got high score
        self.your_high_score = pyglet.text.Label("", x=350, y=200)
        self.your_high_score.anchor_x = 'center'
        self.your_high_score.anchor_y = 'center'
        self.your_high_score.font_name = "Arial"
        self.your_high_score.font_size = 18

        #game conditions
        self.player_is_alive = True
        self.game_condition = False
        
        pyglet.clock.schedule_interval(self.game_update, 1/60.0)

    def on_draw(self):
        self.clear() 
        for road in self.road_list:
            road.draw()
        if self.game_condition == True and self.player_is_alive == True:
            self.main_batch.draw()
            self.player.draw()
            for boulder in self.boulder_list:
                boulder.draw()
            for exp in self.explosion_list:
                exp.draw()
            self.score_label.draw()
        elif self.game_condition == False and self.player_is_alive == True:
            self.intro_text.draw()
        elif self.player_is_alive == False:
            self.your_high_score.draw()
            self.main_batch.draw()
            self.player.draw()
            for boulder in self.boulder_list:
                boulder.draw()
            for exp in self.explosion_list:
                exp.draw()
            self.game_over_label.draw()
            self.retry_label.draw()
    
    def game_update(self,dt):
        self.update_road()
        if self.key[pyglet.window.key.ENTER]:
            self.game_condition = True
        if self.game_condition == True:
            self.update_road()
            self.update_player()
            self.update_boulder()
            self.update_explosion()
        if self.player_is_alive == True:
            self.update_score()
        if self.player_is_alive == False:
            self.game_over()
            self.retry()
            if self.key[pyglet.window.key.Y]:
                self.game_condition = True
                self.player_is_alive = True
                self.score = 0
            elif self.key[pyglet.window.key.N]:
                self.Game().close()        

    def update_player(self):
        if self.key[pyglet.window.key.RIGHT] and not self.player.x > 510:
            self.player.x += 5
        if self.key[pyglet.window.key.LEFT] and not self.player.x < 100:
            self.player.x -= 5

    def update_boulder(self):
        if random.randint(1, 47) == 4:
            self.boulder = pyglet.sprite.Sprite(img=self.boulder_image, x = random.randint(10,600), y = 670)
            self.boulder.scale = 0.3
            self.boulder_list.append(self.boulder)
        for boulder in self.boulder_list:
            boulder.y -= random.randint(10,23)
            if boulder.y <= 0:
                self.boulder_list.remove(boulder)
        for boulder in self.boulder_list:
            if self.sprite_collision(boulder, self.player):
                self.explosion_sound.play()
                x = boulder.x
                y = boulder.y
                self.explosion_list.append(pyglet.sprite.Sprite(self.explosion_animation,x,y))
                self.player_is_alive = False

    def update_explosion(self):
        self.explode_time -= 0.15
        if self.explode_time <= 0:
            for exp in self.explosion_list:
                self.explosion_list.remove(exp)
                exp.delete()
            self.explode_time += 2
    #reference: Attila Toth via GitHub, full reference link on documentation

    def update_road(self):
        for road in self.road_list:
            road.y -= 7
            if road.y <= -670:
                road.y = 670

    def sprite_collision(self, spr1, spr2):
        return (spr1.x-spr2.x)**2 + (spr1.y-spr2.y)**2 < (spr1.width/2 + spr2.width/2)**2
    #reference:Gokberk Yaltirakli via GitHub, full reference link on documentation

    def update_score(self):
        self.score += 1
        if self.score > self.high_score:
            self.high_score = self.score
        self.score_label.text = "Score: {}        High Score: {}".format(self.score, self.high_score)

    def game_over(self):
        if self.high_score > int(engine.load_high_score("resources/high_score.txt")):
            engine.save_high_score("resources/high_score.txt", self.high_score)
        self.your_high_score.text = "Your Score: {}  High Score: {}".format(self.score, self.high_score)

        player_is_alive = False
    #reference: Attila Toth via GitHub, full reference link on documentation

    def retry(self):
        self.high_score = int(engine.load_high_score("resources/high_score.txt"))

# if __name__=="__main__":
#     window = Game()
#     pyglet.app.run()