import pyray as pr
import numpy as np
import math
from copy import copy
from entity import Entity
from resource_type import ResourceType

MAX_METEORS = 30
# MAX_SHOTS = 5

class Game:
    def __init__(self, screen_width, screen_height):
        self.resources = {}
        self.meteors = []
        self.shots = []
        self.player = Entity()
        self.screen_width = screen_width
        self.screen_height = screen_height

    # Loads all the resources
    def startup(self):
        pr.init_audio_device()

        image = pr.load_image("assets/meteor.png")
        self.resources[ResourceType.TEXTURE_METEOR_SMALL] = pr.load_texture_from_image(image)
        pr.unload_image(image)

        image = pr.load_image("assets/meteor_med.png")
        self.resources[ResourceType.TEXTURE_METEOR_MED] = pr.load_texture_from_image(image)
        pr.unload_image(image)

        image = pr.load_image("assets/meteor_large.png")
        self.resources[ResourceType.TEXTURE_METEOR_LARGE] = pr.load_texture_from_image(image)
        pr.unload_image(image)

        image = pr.load_image("assets/player.png")
        self.resources[ResourceType.TEXTURE_PLAYER] = pr.load_texture_from_image(image)
        pr.unload_image(image)

        self.resources[ResourceType.SOUND_LASER_SHOOT] = pr.load_sound("assets/laser-shoot.wav")
        self.resources[ResourceType.SOUND_LASER_EXPLOSION] = pr.load_sound("assets/laser-explosion.wav")

        self.reset()

    # Updates the game
    def update(self):
        # Player Movement Keys
        if pr.is_key_down(pr.KEY_LEFT):
            self.player.heading -= 5.0
        elif pr.is_key_down(pr.KEY_RIGHT):
            self.player.heading += 5.0
        elif pr.is_key_down(pr.KEY_UP):
            if self.player.acceleration < 1.0:
                self.player.acceleration += 0.04
        elif pr.is_key_down(pr.KEY_DOWN):
            if self.player.acceleration > -1.0:
                self.player.acceleration -= 0.04

        # Shooting Bullet Keys
        if pr.is_key_pressed(pr.KEY_SPACE):
            shot = Entity()
            shot.active = True
            shot.position.x = copy(self.player.position.x)
            shot.position.y = copy(self.player.position.y)
            shot.heading = copy(self.player.heading)
            shot.acceleration = 1.0
            shot.speed.x = math.cos(np.deg2rad(self.player.heading)) * 10.0
            shot.speed.y = math.sin(np.deg2rad(self.player.heading)) * 10.0

            self.shots.append(shot)
            pr.play_sound(self.resources[ResourceType.SOUND_LASER_SHOOT])

        # Move the player
        self.player.speed.x = math.cos(np.deg2rad(self.player.heading)) * 6.0
        self.player.speed.y = math.sin(np.deg2rad(self.player.heading)) * 6.0

        self.player.position.x += (self.player.speed.x * self.player.acceleration)
        self.player.position.y += (self.player.speed.y * self.player.acceleration)

        # Player Offscreen handling
        if self.player.position.x < 0:
            self.player.position.x = self.screen_width
        elif self.player.position.x > self.screen_width:
            self.player.position.x = 0

        if self.player.position.y < 0:
            self.player.position.y = self.screen_height
        elif self.player.position.y > self.screen_height:
            self.player.position.y = 0

        # Move the meteors
        for meteor in self.meteors:
            meteor.position.x += math.cos(np.deg2rad(meteor.heading)) * meteor.speed.x
            meteor.position.y += math.sin(np.deg2rad(meteor.heading)) * meteor.speed.y

            # Offscreen handling
            if meteor.position.x < 0:
                meteor.position.x = self.screen_width
            elif meteor.position.x > self.screen_width:
                meteor.position.x = 0

            if meteor.position.y < 0:
                meteor.position.y = self.screen_height
            elif meteor.position.y > self.screen_height:
                meteor.position.y = 0

        # Move the shots
        for shot in self.shots:
            if shot.active == True:
                shot.position.x += (shot.speed.x * shot.acceleration)
                shot.position.y += (shot.speed.y * shot.acceleration)

                # Offscreen handling
                if shot.position.x < 0 or shot.position.x > self.screen_width:
                    shot.active = False
                if shot.position.y < 0 or shot.position.y > self.screen_height:
                    shot.active = False

        # Shots collisions with meteors
        for shot in self.shots:
            if shot.active == True:
                for meteor in self.meteors:
                    if meteor.active == True:
                        texture = ResourceType(meteor.type)
                        if pr.check_collision_circles(shot.position, 1, meteor.position, self.resources[texture].width):
                            shot.active = False
                            meteor.active = False
                            pr.play_sound(self.resources[ResourceType.SOUND_LASER_EXPLOSION])
                            break

        # Player collisions with meteors (Game Over)
        for meteor in self.meteors:
            if meteor.active == True:
                texture = ResourceType(meteor.type)
                if pr.check_collision_circles(self.player.position, 1, meteor.position, self.resources[texture].width):
                    pr.play_sound(self.resources[ResourceType.SOUND_LASER_EXPLOSION])
                    self.reset()
                    break

        # Remove inactive shots and meteors
        active_shots = filter(lambda x: (x.active == True), self.shots)
        self.shots = list(active_shots)

        active_meteors = filter(lambda x: (x.active == True), self.meteors)
        self.meteors = list(active_meteors)

    # Render things on screen
    def render(self):
        # Rendering Meteors
        for meteor in self.meteors:
            texture = ResourceType(meteor.type)
            pr.draw_texture_pro(
                self.resources[texture],
                pr.Rectangle(
                    0, 0, self.resources[texture].width, self.resources[texture].height
                ),
                pr.Rectangle(
                    meteor.position.x,
                    meteor.position.y,
                    self.resources[texture].width,
                    self.resources[texture].height
                ),
                pr.Vector2(
                    self.resources[texture].width // 2,
                    self.resources[texture].height // 2
                ),
                meteor.heading,
                pr.WHITE
            )

        # Rendering shots
        for shot in self.shots:
            pr.draw_circle(
                int(shot.position.x),
                int(shot.position.y),
                1.0,
                pr.YELLOW
            )

        # Rendering player
        pr.draw_texture_pro(
            self.resources[ResourceType.TEXTURE_PLAYER],
            pr.Rectangle(0, 0,self.resources[ResourceType.TEXTURE_PLAYER].width, self.resources[ResourceType.TEXTURE_PLAYER].height),
            pr.Rectangle(self.player.position.x, self.player.position.y, self.resources[ResourceType.TEXTURE_PLAYER].width // 2, self.resources[ResourceType.TEXTURE_PLAYER].height // 2),
            pr.Vector2(self.resources[ResourceType.TEXTURE_PLAYER].width // 4, self.resources[ResourceType.TEXTURE_PLAYER].height // 4),
            self.player.heading,
            pr.WHITE
        )

    # Reset the game
    def reset(self):
        self.shots.clear()
        self.meteors.clear()

        self.player.heading = 0.00
        self.player.acceleration = 0.00
        self.player.active = True
        self.player.speed = pr.Vector2(0, 0)
        self.player.position = pr.Vector2(self.screen_width // 2, self.screen_height // 2)

        for i in range(MAX_METEORS):
            meteor = Entity()
            meteor.active = True
            meteor.heading = float(pr.get_random_value(0, 360))
            meteor.position = pr.Vector2(
                float(pr.get_random_value(0, self.screen_width)),
                float(pr.get_random_value(0, self.screen_height)),
            )
            meteor.type = pr.get_random_value(ResourceType.TEXTURE_METEOR_SMALL.value, ResourceType.TEXTURE_METEOR_LARGE.value)
            meteor.speed = pr.Vector2(
                float(pr.get_random_value(-5, 5)),
                float(pr.get_random_value(-5, 5)),
            )
            self.meteors.append(meteor)

    # Shutdown the game
    def shutdown(self):
        pr.unload_texture(self.resources[ResourceType.TEXTURE_METEOR_SMALL])
        pr.unload_texture(self.resources[ResourceType.TEXTURE_METEOR_MED])
        pr.unload_texture(self.resources[ResourceType.TEXTURE_METEOR_LARGE])
        pr.unload_texture(self.resources[ResourceType.TEXTURE_PLAYER])

        pr.unload_sound(self.resources[ResourceType.SOUND_LASER_SHOOT])
        pr.unload_sound(self.resources[ResourceType.SOUND_LASER_EXPLOSION])

        pr.close_audio_device()
