import argparse
import pygame
import random
import carla
import math

from .hud import InfoBar
from .hero_with_controller import Hero
from .hero_with_controller2 import Hero2
from .hero_with_controller3 import Hero3
from .world import World
from .input_control import InputControl

from .color import *


def game_loop(args, target_speed, target_speed1, target_speed2):
    """Initialized, Starts and runs all the needed modules for No Rendering Mode"""
    try:

        # Init Pygame
        pygame.init()
        display = pygame.display.set_mode(
            (args.width, args.height), pygame.HWSURFACE | pygame.DOUBLEBUF
        )

        # Place a title to game window
        pygame.display.set_caption(args.description)

        # Show loading screen
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        text_surface = font.render("Rendering map...", True, COLOR_WHITE)
        display.blit(
            text_surface,
            text_surface.get_rect(center=(args.width / 2, args.height / 2)),
        )
        pygame.display.flip()

        # Init
        hud = InfoBar(args.width, args.height)
        input_control = InputControl()
        world = World(args)
        hero = Hero()
        hero2 = Hero2()
        hero3 = Hero3()

        # For each module, assign other modules that are going to be used inside that module
        hud.start(world)
        input_control.start(hud, world)
        world.start(input_control)

        hero.start(world, target_speed1)
        hero2.start(world, target_speed2)
        hero3.start(world, target_speed)

        # Game loop
        clock = pygame.time.Clock()
        while True:
            
            
            clock.tick_busy_loop(500)

            # Tick all modules
            world.tick(clock)
            hero.tick(clock)
            hero2.tick(clock)
            hero3.tick(clock)
            
            lateral_acceleration = lateral_calculator(Hero2, world.world.get_map())

            hud.tick(clock)
            input_control.tick(clock)

            # Render all modules
            display.fill(COLOR_ALUMINIUM_4)
            world.render(display)
            hud.render(display)
            input_control.render(display)

            pygame.display.flip()
        

    except KeyboardInterrupt:
        print("\nCancelled by user. Bye!")

    except RuntimeError:
        print("Simulation is complete.")

    finally:
        if hero is not None:
            hero.destroy()
        if hero2 is not None:
            hero2.destroy()
        if hero3 is not None:
            hero3.destroy()

def lateral_calculator(actor, map):

    waypoint = map.get_waypoint(actor.get_location(), project_to_road=True, lane_type=carla.LaneType.Driving)
    road_yaw = waypoint.transform.rotation.yaw
    actor_yaw = actor.get_transform().rotation.yaw

    curr_acc_vector = actor.get_acceleration()
    
    lateral_acceleration= (abs(curr_acc_vector.x * math.sin(road_yaw - actor_yaw))
                + abs(curr_acc_vector.y * math.cos(road_yaw - actor_yaw))
                )

    town_map = world.get_map()

    return lateral_acceleration


def main():
    """Parses the arguments received from commandline and runs the game loop"""

    # Define arguments that will be received and parsed
    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "--host",
        metavar="H",
        default="127.0.0.1",
        help="IP of the host server (default: 127.0.0.1)",
    )
    argparser.add_argument(
        "-p",
        "--port",
        metavar="P",
        default=2000,
        type=int,
        help="TCP port to listen to (default: 2000)",
    )
    argparser.add_argument(
        "--tm-port",
        metavar="P",
        default=8000,
        type=int,
        help="Port to communicate with TM (default: 8000)",
    )
    argparser.add_argument(
        "--timeout",
        metavar="X",
        default=2.0,
        type=float,
        help="Timeout duration (default: 2.0s)",
    )
    argparser.add_argument(
        "--res",
        metavar="WIDTHxHEIGHT",
        default="1280x720",
        help="window resolution (default: 1280x720)",
    )
    argparser.add_argument(
        "--filter",
        metavar="PATTERN",
        default="vehicle.audi.*",
        help='actor filter (default: "vehicle.audi.*")',
    )

    # Parse arguments
    args = argparser.parse_args()
    args.description = "BounCMPE CarlaSim 2D Visualizer"
    args.width, args.height = [int(x) for x in args.res.split("x")]

    

    # Run game loop
    i = 0
    while i < 25:
        
        #Creates 25 random scenarios
        target_speed = random.uniform(0, 5)
        target_speed1 = random.uniform(19.4, 25)
        target_speed2 = random.uniform(19.4, 25)
        
        print(target_speed)
        print(target_speed1)
        print(target_speed2)

        f = open("/home/emre/CMPE486-Term-Project/client/app/acceleration.txt", "a")

        f.write(str(target_speed2*3.6))
        f.write(str(", "))
        f.close

        game_loop(args, target_speed, target_speed1, target_speed2)

        
        

        i = i + 1