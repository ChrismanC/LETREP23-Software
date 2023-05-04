###############################################################################
# INITIALIZATION

# Libraries
import pygame
from pygame.locals import *
import sys
import math
import random
from framework import framework

from datetime import datetime
from multiprocessing import Process
import os
from tkinter import *
import time
import random
from tkinter import messagebox
import winsound

from M1Display import M1Display

from create_json import JSONTrialMaker
from PreloadDisplay import PreloadDisplay
from global_funcs import *
from framework import framework
from more_options import *
import peak
import matplotlib.pyplot as plt
from SuccessRecordDisplay import SuccessRecordDisplay
from PIL import ImageTk, Image
import logging
from more_options import show_more_options
pygame.init()

from BaselineMaxDisplay import BaselineMaxDisplay
from datetime import datetime
import os
from tkinter import *
import time
from global_funcs import *
from framework import framework
from more_options import *
from PIL import ImageTk, Image
import logging
from r_app import r_app
from game import show_game

x= 1

#not implemented
#would replace max.py if implemented
#currently has issues

def show_max_game(port, pat_id, sess, no_motor=False, no_emg=False):
   
    speed_arr = [[0 for i in range(2)] for j in range(1)]

    for i in range(0,1):
        speed_arr [i][0] = 175 #85+(i*10)
        speed_arr [i][1] = 75

    #new log directory 
    log_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop\\LETREP2\\Logs\\')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    #configs a new Run .log file that logging statements can write to
    logging.basicConfig(filename=log_dir+datetime.now().strftime('Run_%Y-%m-%d_%H-%M.log'), level=logging.DEBUG,
                    format='%(asctime)s:%(filename)s:%(levelname)s:%(message)s')
    
    cease=False

    options = get_default_options()
    # Give defaults for options not set in get_default_options before loading from file
    options.update(
    {
        "m1_thresh": 0.06
    }
    )
    options.update(load_options_from_file(pat_id))
    options.update(
    {
        "pat_id": pat_id, 
        "sess": sess, 
        "display_success": False if sess in [1,2,3] else True
    }
    )

    #frame = None

    # Directory constants
    ASSETS = "SUB3/resources/"
    IMAGES = ASSETS + "gameimages/"
    SOUNDS = ASSETS + "gamesounds/"
    global flash
    flash = 1
    
    # Function for loading images
    def image(image_new):
        return pygame.image.load(IMAGES + image_new + ".png")

    # Function for drawing centered text
    def centerblit(text, x, y):
        root.blit(text, (x - (text.get_rect().width / 2), y))

    # Function for playing a sound effect
    def play_sound(sound_name):
        pygame.mixer.Sound.play(pygame.mixer.Sound(SOUNDS + sound_name + ".wav"))

##TBK

    # Custom lerp function (rounds up)
    def chris_lerp(value, value_new, interpolation):
        do_ceil = value_new > value
        value_new = (value + ((value_new - value) * interpolation))
        if do_ceil:
            return math.ceil(value_new)
        else:
            return math.floor(value_new)

    def refresh():
        global flash
        load_bars()
        load_lilypads()
        logo()
        load_info()
        load_pause_button(flash)
        load_start_button(flash)
        load_stop_button(flash)
        load_continue_button()
        load_option_button()
        load_player(player_x, player_y)
        load_fly_score()
        
        
    def refresh2():
        # Loads the instances
        load_bars()
        load_lilypads()
        load_player(player_x, player_y)

  

    # ROOT BUILD
    WINDOW_W = 1090
    WINDOW_H = 490 
    root = pygame.display.set_mode((WINDOW_W, WINDOW_H))

    def on_closing():
        running = False
        pygame.display.exit()

    running = True



    ###############################################################################
    # GAME SETTINGS

    # Background color
    BG_COLOR = (96, 96, 96)
    # Font
    FONT = ASSETS + "arial.ttf"

    # Zone borders
    ZONE_LEFT = 436
    ZONE_RIGHT = 654
    # Game boundaries
    BOUNDARY_LEFT = 218
    BOUNDARY_RIGHT = 872

    # Fly score dimensions
    ROWS = 1
    COLUMNS = 5

    # Maximum number of trials
    TRIAL_MAX = 5

    # Score types
    SCORE_IMAGE = (image("fail"), image("win"), image("bruh"))

    # Border
    BORDER_PAD = 8
    BORDER_SHRINK = 3

    # Interpolation for lerp
    LERP_INTERP = 0.015

    ###############################################################################
    # INSTANCES

    # Bars
    bars_image = image("bars_win")
    bars_x = 218
    bars_y = 0
    global last_zone
    last_zone = 1

    def load_bars():
        global last_zone
        bars_image = image("basic-background")
        root.blit(bars_image, (bars_x, bars_y))

    # Lilypads
    lilypads_image = image("new_lilypad")
    lilypads_x = 218
    lilypads_y = 303
    def load_lilypads():
        root.blit(lilypads_image, (lilypads_x, lilypads_y))

    button_light = (255, 255, 0)
    button_dark = (1,44,118)
    button_flash = (100,100,100)

    def load_pause_button(flash):
        button_font = pygame.font.SysFont('Corbel', 30)
        button_x = 981
        button_y = 260
        if flash ==1:
            pygame.draw.rect(root, button_flash, [890,235,180,50])
        if flash ==3:
            pygame.draw.rect(root, button_dark, [890,235,180,50])
            pause_text = button_font.render('Pause', True, button_light)
            centerblit(pause_text, button_x, button_y- (pause_text.get_rect().height / 2))
            pygame.display.update((890,235,180,50))
            #clock.tick(2)
            pygame.draw.rect(root, button_flash, [890,235,180,50])
            centerblit(pause_text, button_x, button_y- (pause_text.get_rect().height / 2))
            pygame.display.update((890,235,180,50))
            #clock.tick(2)
        if flash ==2:
            pygame.draw.rect(root, button_dark, [890,235,180,50])
        pause_text = button_font.render('Pause', True, button_light)
        centerblit(pause_text, button_x, button_y- (pause_text.get_rect().height / 2))

   

    def pause():
        global flash
        frame.pause_block()
        if flash == 2:
            flash = 3
        else:
            if flash == 3:
                flash =2


    def load_start_button(flash):
       
        if flash ==1:
            pygame.draw.rect(root, button_dark, [890,160,180,50])
        if flash ==2:
            pygame.draw.rect(root, button_flash, [890,160,180,50])
        if flash ==3:
            pygame.draw.rect(root, button_flash, [890,160,180,50])
        button_font = pygame.font.SysFont('Corbel', 30)
        button_x = 981
        button_y = 185
        start_text = button_font.render('Start', True, button_light)
        centerblit(start_text, button_x, button_y- (start_text.get_rect().height / 2))

    def start():
        global flash
        frame.start_block(speed_arr)
        flash = 2

    def load_stop_button(flash):
        if flash ==1:
            pygame.draw.rect(root, button_flash, [890,310,180,50])
        if flash ==2:
            pygame.draw.rect(root, button_dark, [890,310,180,50])
        if flash ==3:
            pygame.draw.rect(root, button_dark, [890,310,180,50])
        button_font = pygame.font.SysFont('Corbel', 30)
        button_x = 981
        button_y = 335
        stop_text = button_font.render('Stop', True, button_light)
        centerblit(stop_text, button_x, button_y- (stop_text.get_rect().height / 2))

    def stop():
        new_thresh = frame.block.compute_avg_peak()
        messagebox.showinfo(
            "M1 Threshold Update", f"Average M1 Peak From Previous Block: {new_thresh}\n New M1 Thresh: {.9*new_thresh}")
        options["m1_thresh"] = new_thresh*.9
        options["updates"] = True
        frame.stop_block()

    def load_option_button():
        pygame.draw.rect(root, button_dark, [970,450,100,25])
        button_font = pygame.font.SysFont('Corbel', 20)
        button_x = 1020
        button_y = 465
        option_text = button_font.render('Options', True, button_light)
        centerblit(option_text, button_x, button_y- (option_text.get_rect().height / 2))

    def load_continue_button():
        pygame.draw.rect(root, button_dark, [10,310,180,50])
        button_font = pygame.font.SysFont('Corbel', 30)
        button_x = 100
        button_y = 335
        stop_text = button_font.render('Continue', True, button_light)
        centerblit(stop_text, button_x, button_y- (stop_text.get_rect().height / 2))

    def cont():
        #max fn only, important for transition to app
        max_emg = frame.block.avg_max_emg
        print(max_emg)
        frame.r_block() 
        # frame.exit()
        root.destroy()
        no = port == None
        show_game(port, pat_id, sess, max_emg, frame, no_motor=no, no_emg=no)

    def option_button():
        show_more_options(options)

    def logo():
        logo_image = image("LETREP23_LOGO")
        centerblit(logo_image,980,20)

    def display_max_prompt():
        pygame.draw.rect(root, button_dark, [300,150,500,150])
        prompt_font = pygame.font.SysFont('Corbel', 50)
        prompt_x = 325
        prompt_y = 200
        prompt_text = prompt_font.render('Push as hard you can', True, button_light)
        root.blit(prompt_text,(prompt_x, prompt_y))

    # Info
    trial = 0
    successes = 0
    info_font = pygame.font.Font(FONT, 18)
    info_x = 981
    info_y = 380
    info_color = (0, 0, 0)
    ## GAME need current patient data here ##
    def load_info():
        info_text_trial = info_font.render("Current Trial: " + str(min(trial + 1, TRIAL_MAX)), True, info_color)
        centerblit(info_text_trial, info_x, info_y)
        info_text_successes = info_font.render("Successful Trials: " + str(successes), True, info_color)
        centerblit(info_text_successes, info_x, info_y + info_text_trial.get_rect().height + 2)


    # Player
    player_image = image("smol_frog")
    player_x = 502
    player_y = 355
    player_xcenter = 0
    def load_player(x, y):
        root.blit(player_image, (x, y))

    # Border
    border_image = image("border")
    border_x = 0
    global border_y
    border_y_goal = WINDOW_H
    border_y = border_y_goal
    border_w = 0
    def load_border():
        global border_y
        border_y = chris_lerp(border_y, border_y_goal, LERP_INTERP)
        root.blit(border_image, (border_x, border_y))
        root.blit(border_image, (border_x + border_w, border_y))


    # Fly score
    fly_board = [0] * TRIAL_MAX
    fly_image = image("fly")
    fly_x = 5
    fly_y = 5
    fly_pad = 2
    def load_fly(x, y):
        root.blit(fly_image, (x, y))
    def load_fly_score():
        for i in range(ROWS):
            for j in range(COLUMNS):
                fly_x_new = fly_x + (j * (fly_image.get_width() + fly_pad))
                fly_y_new = fly_y + (i * (fly_image.get_height() + fly_pad))
                fly_board_index = (i * COLUMNS) + j
                load_fly(fly_x_new, fly_y_new)
                if fly_board[fly_board_index] > 0:
                    root.blit(SCORE_IMAGE[fly_board[fly_board_index] - 1], (fly_x_new, fly_y_new))

    ###############################################################################
    # GAME

    frame = framework(port, patID=options["pat_id"], sess=options["sess"],
                      premin=options["pre_min"], premax=options["pre_max"], no_motor=no_motor, no_emg=no_emg)
    max = []

    i=0
    while running:
        refresh()
        mouse = pygame.mouse.get_pos()
        pressed = pygame.key.get_pressed()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # pause
                if 890 <= mouse[0] <= 1070 and 235 <= mouse[1] <= 285:
                    pause()
                #start
                if 890 <= mouse[0] <= 1070 and 160 <= mouse[1] <= 210:
                    start()
                #stop 
                if 890 <= mouse[0] <= 1070 and 310 <= mouse[1] <= 360:
                    stop()

                #continue
                if 10 <= mouse[0] <= 190 and 310 <= mouse[1] <= 360:
                    cont()

                # options
                if 970 <= mouse[0] <= 1070 and 450 <= mouse[1] <= 475:
                    option_button()

 
        
        if frame.mot:
            if frame.mot.torque_update:
                torque_value = frame.mot._display_emgV       #grabs emg from motor object
                frame.mot.torque_update = False
                torque_value = frame.mot._display_emgV
                
                # 20 sample rolling torque average
                if options["torque_display"]:
                    max.append(abs(torque_value))
                    max = max[-20:]
                    avg_torque = sum(max)/len(max)
                           
        # Pause button flashing
        
        if not frame.paused and not frame.running:
            print("Illegal state: not frame.paused and not frame.running. Corrected to frame.paused and not frame.running.")
            frame.paused = True

        # Check for updates and then change values
        if options["updates"]:
            frame.update_options(options)
            options["updates"] = False

        # Check if a trial is just starting
        if frame.starting_trial:
            display_max_prompt()
            # OG PRELOAD SOUND HERE
            #check if 1st trial
            if frame.trial_count == 0:
                options["block_count"] = frame.block_count
                Num_of_success = 0

            

            #preload display
            frame.starting_trial = False
            
            
        # This happens when after a trial
        if frame.finished_trial:
            
            #baseline_display.set_record(frame.trial_count-1, 5)

            fly_board[trial] = 2
            successes += 1
            trial += 1
            pygame.display.update()
            if frame.trial_count == 5 :
                logging.warning("Trial count meets success display limit... Ending block")
                
                max_emg = frame.block.avg_max_emg
                print(max_emg)
                frame.r_block() #***
                root.running = False
                # frame.exit()
                root.update()
                root.destroy()
                no = port == None
                r_app(port, pat_id, sess, max_emg, frame, no_motor=no, no_emg=no) #***
                cease=True
            
            # Reset trial bit
            if(not cease):
                frame.finished_trial = False
        if(not cease):
            pygame.display.update()
            #refresh()
            #root.update()
    if(not cease):        
        root.destroy()

        
    # Sets the background color
    root.fill(BG_COLOR)
    
    

    # Updates the window
    pygame.display.update()




if __name__ == "__main__":

    show_game(None, 1234, 1, no_motor=True, no_emg=True)