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
from paths import move_paths
pygame.init()
x= 1

def show_game(port, pat_id, sess, max_emg, framepass, no_motor=False, no_emg=False):
    ### motor needs ### 

    print("in game")
    #****should be all speeds = 175
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

    if(max_emg==0):
        max_emg=.5

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
        "display_success": False if sess in [1,2,3] else True,
        "pre_max": max_emg*.20,
        "pre_min": max_emg*.05
    }
    )
    print("frame")
    frame = framepass

    ### from previous motor #####

    def plot_emg(yacc, yemg,v1 = None, v2 = None, h1 = None, duration = None):

        yemg = yemg[400:1600]
        yacc = yacc[400:1600]

        _, ax = plt.subplots()

        ax.plot(yemg, 'r', label="EMG")
        ax.legend(loc=2)

        # Display vertical lines
        if v1 and v2 and h1:
            ax.axhline(h1)
            ax.axvline(v1)
            ax.axvline(v2)

        ax2 = ax.twinx()
        ax2.plot(yacc,'b', label="ACC")
        ax2.legend(loc=1)

        # Format plot
        plt.title('Most Recent Trial Readings')
        plt.ion()
        plt.legend()
        if duration:
            plt.show()
            plt.pause(duration)
            plt.close()
        else:
            plt.show(block= True)


    ### game prep keep ####

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
        # Loads the instances
        load_bars()
        load_lilypads()
        move(i)
       # load_tongue()
        load_score()
        logo()
        load_combo()
        load_info()
        load_pause_button(flash)
        load_start_button(flash)
        load_stop_button(flash)
        load_option_button()
        load_player(player_x, player_y)
        if combo > COMBO_MAX_1:
            load_border()
            load_golden()
        load_fly_score()
        
    def refresh2():
              # Loads the instances
        load_bars()
        load_lilypads()
        move(i)
        load_player(player_x, player_y)
        if combo > COMBO_MAX_1:
            load_border()
            load_golden()
  
    print("root build")
    # ROOT BUILD
    WINDOW_W = 1090
    WINDOW_H = 490 
    root = pygame.display.set_mode((WINDOW_W, WINDOW_H))

    def on_closing():
        #running = False
        pygame.display.exit()
        frame.exit()
    #####root.protocol("WM_DELETE_WINDOW", on_closing)
        # for event in pygame.event.get():
        # if event.type == pygame.QUIT:
        #     running = False
                # on_closing()


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
    ROWS = 15
    COLUMNS = 5

    # Maximum number of trials
    TRIAL_MAX = 75

    # Score types
    SCORE_IMAGE = (image("fail"), image("win"), image("bruh"))

    # Score multiplier
    SCORE_MULTIPLIER = 100

    # Combo maxima
    COMBO_MAX_1 = 3
    COMBO_MAX_2 = 14

    # Full combo bonus
    FULL_SCORE = 100000
    FULL_BONUS = 4100

    # Reflex success range   ??
    REFLEX_MIN = 0.15
    REFLEX_MAX = 0.85

    # Reflex zone dimensions
    REFLEX_ZONE_WIDTH = 42
    REFLEX_ZONE_HEIGHT = 282

    FLY_PAD_Y = 4
    FLY_HEIGHT = WINDOW_H / 4
    FLY_BUZZ = 24
    FLY_SPEED = 1.25

    # Border
    BORDER_PAD = 8
    BORDER_SHRINK = 3

    # Interpolation for lerp
    LERP_INTERP = 0.015

    ###############################################################################
    # INSTANCES
    print("bars")
    # Bars
    bars_image = image("bars_win")
    bars_x = 218
    bars_y = 0
    global last_zone
    last_zone = 1

    def load_bars():
        global last_zone
        if player_xcenter <= ZONE_LEFT:
            bars_image = image("yellow-background")
            if last_zone != 0:
                last_zone = 0
                play_sound("zone_bad")
        elif player_xcenter >= ZONE_RIGHT:
            bars_image = image("background-red")
            if last_zone != 2:
                last_zone = 2
                play_sound("zone_bad")
        else:
            bars_image = image("basic-background")
            if last_zone != 1:
                last_zone = 1
                play_sound("zone_good")
        root.blit(bars_image, (bars_x, bars_y))

    # Lilypads
    lilypads_image = image("new_lilypad")
    lilypads_x = 218
    lilypads_y = 303
    def load_lilypads():
        root.blit(lilypads_image, (lilypads_x, lilypads_y))

    #flies
    fly_image = image("fly")
    clock = pygame.time.Clock() 
    angle, ship_pos = move_paths()
    def move(i):
        clock.tick(100)
        rotimage = pygame.transform.rotate(fly_image, angle[i])
        rect = rotimage.get_rect(center=ship_pos[i])
        #print(ship_pos[i])
        root.blit(rotimage,rect)


    # Tongue
    global tongue_image 
    tongue_image = image("tongue")

    def load_tongue():
        global tongue_image
        for t in range(0,350,1):
            #t = pygame.time.get_ticks() /4  # scale and loop time
            clock.tick(350)
            y = -(t+1) + 400
            x = math.sin((t+1)/50.0) * 50 + player_x + (player_image.get_width()/2)   #sine + frog current location
            x = int(x)                            
            pygame.draw.circle(root, (222,165,164), (x, y), 10)
            pygame.display.update()

        root.fill((0,0,0),(400, 100, 300, 390)) 

        for m in range(350,0,-10):
            refresh2()
            for t in range(m):
                y = -(t+1) + 400
                x = math.sin((t+1)/50.0) * 50 + player_x + (player_image.get_width()/2)   #sine + frog current location
                x = int(x)                   
                pygame.draw.circle(root, (222,165,164), (x, y), 10)
                if t == m -1:
                    root.blit(fly_image, (x-10,y))
            pygame.display.update((230, 0, 600, 490))
            clock.tick(100)

    print("score")
    # Score
    score = 0
    score_font = pygame.font.Font(FONT, 32)
    score_x = 109
    score_y = 416
    global score_color
    score_color = (0, 0, 0)

    def load_score():
        global score_color
        if score >= (FULL_SCORE * 0.8):
            score_color = (0, 255, 0)
        score_text = score_font.render("{:,}".format(score), True, score_color)
        centerblit(score_text, score_x, score_y)

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
            clock.tick(2)
            pygame.draw.rect(root, button_flash, [890,235,180,50])
            centerblit(pause_text, button_x, button_y- (pause_text.get_rect().height / 2))
            pygame.display.update((890,235,180,50))
            clock.tick(2)
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

    def option_button():
        show_more_options(options)

    def logo():
        logo_image = image("LETREP23_LOGO")
        centerblit(logo_image,980,20)

    print("combo")
    # Combo
    combo = 1
    combo_font = pygame.font.Font(FONT, 18)
    combo_x = 109
    combo_y = 448
    combo_color = (0, 0, 0)
    def load_combo():
        if combo <= math.floor(COMBO_MAX_2 / 3):
            combo_color = (0, 0, 0)
        elif combo <= math.floor((COMBO_MAX_2 / 3) * 2):
            combo_color = (255, 255, 0)
        else:
            combo_color = (0, 255, 0)
        combo_text = combo_font.render("x" + str(combo), True, combo_color)
        centerblit(combo_text, combo_x, combo_y)

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

    # Golden fly
    golden_image = image("golden")
    golden_x = 0
    golden_y = 0
    def load_golden():
        root.blit(golden_image, (golden_x, golden_y))

    print("score")
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
    print("pre-loop")
    max = []

    i=0
    while running:
        print ("running loop")
        mouse = pygame.mouse.get_pos()
        pressed = pygame.key.get_pressed()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                on_closing()

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
                    


                player_xcenter = player_x + (player_image.get_width() / 2)
                span = 218/(.15 * max_emg)
                player_x = (torque_value * span) + 363
                if player_x < BOUNDARY_LEFT:
                    player_x += BOUNDARY_LEFT - player_x
                if (player_x + player_image.get_width()) > BOUNDARY_RIGHT:
                    player_x -= (player_x + player_image.get_width()) - BOUNDARY_RIGHT
                player_xcenter = player_x + (player_image.get_width() / 2)
                
                           
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
            # OG PRELOAD SOUND HERE
            #check if 1st trial
            if frame.trial_count == 0:
                options["block_count"] = frame.block_count
                Num_of_success = 0

            #preload display
            frame.starting_trial = False



        # This happens when after a trial
        if frame.finished_trial:
            
            # Remove DC Offset for finding peak
            emg_dc_offset = sum(frame.current_trial.emg_data[0:400])/400
            emg = [sample-emg_dc_offset if sample -
                    emg_dc_offset > 0 else 0 for sample in frame.current_trial.emg_data]


            # Check if we are to show_emg
            if options["show_emg"]:
                plot_thread = Process(
                    target=plot_emg,args = (frame.current_trial.acc_data, emg, None, None, None, 4) )
                plot_thread.start()

            # Update successs display
            if options["display_success"]:
                
                frame.current_trial.peak, frame.current_trial.max_delay_ms = peak.condition_peak(
                    emg,options["avg_peak_delay"], options["m1_noise_factor"])

                # Add check for no peak found
                if not (frame.current_trial.peak and frame.current_trial.max_delay_ms) and frame.emg:
                    frame.pause_block()
                    json_dir = os.path.join(os.path.join(
                    os.environ['USERPROFILE']), f'Desktop\\LETREP2\\Logs\\')
                    if not os.path.exists(json_dir):
                        os.makedirs(json_dir)
                    with open(json_dir+f'Failed Trial_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json', "w") as file:

                        JSONTrialMaker(frame.current_trial, file)

                    M1_avg = int((options["avg_peak_delay"]*1925/1000)+100)
                    plot_thread = Process(target=plot_emg, args=(frame.current_trial.acc_data, emg,  M1_avg - 20,  M1_avg + 20, peak.find_peak_min_thresh(emg, options["m1_noise_factor"]),  None,))
                    plot_thread.start()
                    
                    retake_trial = messagebox.askyesno(
                        "EMG Error", "Program failed to find a peak in specified range, retake trial?")
                    
                    if retake_trial:
                        frame.retake_trial()
                else:

                    m1_size = frame.current_trial.peak if frame.emg else random.random() * (options["m1_max"] - options["m1_min"]) + options["m1_min"]


                    
                    if frame.current_trial.success:
                        frame.current_trial.success = m1_size <= options["m1_thresh"]
                        reflex_fail = False
                        tongue_x = player_xcenter - (tongue_image.get_width() / 2)
                        if m1_size <= options["m1_thresh"]:
                            Num_of_success +=1
                            play_sound("success")  
                            fly_board[trial] = 2
                            trial += 1
                        else:
                            #handles failure
                            reflex_fail = True
                            fly_board[trial] = 1
                            combo = 1
                            play_sound("fail")
                            trial += 1
                          
            else:
                frame.current_trial.peak, frame.current_trial.max_delay_ms = peak.base_peak(
                    emg, options["m1_noise_factor"])
                
                fly_board[trial] = 3
                successes += 1
                trial += 1
                score += (combo * SCORE_MULTIPLIER)
                  # Plays the success sound effect
                preloading = True

                tongue_x = player_xcenter - (tongue_image.get_width() / 2)
                play_sound("tongue")
                load_tongue()

                if score >= (FULL_SCORE - FULL_BONUS):
                    score = FULL_SCORE
                
                if combo <= COMBO_MAX_1:
                    combo += 1
                else:
                    if (player_xcenter >= border_x) and (player_xcenter <= (border_x + border_w)):
                        if (combo < COMBO_MAX_2):
                            combo += 1
                    else:
                        score -= SCORE_MULTIPLIER
                                        # Updates the border's position
                border_w = ((BOUNDARY_LEFT - (BORDER_PAD * 2)) / 2) - (BORDER_SHRINK * (combo - COMBO_MAX_1))
                border_x = ZONE_LEFT + BORDER_PAD + (BOUNDARY_LEFT - (BORDER_PAD * 2) - border_w) * random.random()
                if (combo > COMBO_MAX_1):
                    border_y_goal = 0
                    border_y = WINDOW_H
                    border_y_goal = 0
                    # Updates the golden fly's position
                    golden_x = border_x + (border_w / 2) - (golden_image.get_width() / 2)
                    golden_y = FLY_PAD_Y + (FLY_HEIGHT * random.random())
                    
                  

            # Check if we can do another trial
            if frame.trial_count+1 == 75 :
                logging.warning("Trial count meets success display limit... Ending block")
                new_thresh = frame.block.compute_avg_peak()
                messagebox.showinfo(
                    "M1 Threshold Update", f"Average M1 Peak From Previous Block: {new_thresh}\n New M1 Thresh: {.9*new_thresh}")
                #general_info_lbl.configure(text=f"Success Rate:{frame.block.compute_avg_success()*100:.2f}")
                #general_info_lbl.last_updated = time.time()
                options["m1_thresh"] = .9*new_thresh
                options["updates"] = True
                frame.stop_block()
            
            # Reset trial bit
            frame.finished_trial = False

        

        
        # Sets the background color
        root.fill(BG_COLOR)
        
        refresh()

        # Updates the window
        pygame.display.update()
        i = i +1
        if i == len(angle):
            i = 0



if __name__ == "__main__":

    show_game(None, 1234, 1, no_motor=True, no_emg=True)
