
from BaselineMaxDisplay import BaselineMaxDisplay
from datetime import datetime
import os
from tkinter import *
import time
import winsound
from global_funcs import *
from framework import framework
from more_options import *
from PIL import ImageTk, Image
import logging
from game import show_game


def max(port, pat_id, sess, no_motor=False, no_emg=False):
    
    log_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop\\LETREP23\\Logs\\')
    # log_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads\\LETREP2\\Logs\\')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(filename=log_dir+datetime.now().strftime('Run_%Y-%m-%d_%H-%M.log'), level=logging.DEBUG,
                        format='%(asctime)s:%(filename)s:%(levelname)s:%(message)s')

    cease=False
    root = Tk()
    root.configure(bg="white")
    root.running = True

    #print("options")
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

    frame = None

    def on_closing():
        root.running = False
        frame.exit()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    img = Image.open(logo_dir)
    img = img.resize((100, 100), Image.ANTIALIAS)
    logo = ImageTk.PhotoImage(img)
    logo_label = Label(root, image=logo, bg="white")
    logo_label.grid(row=0, column=0, padx=padx, pady=pady)
    
    #patient ID label
    patient_info_lbl = Label(root, text="PatID " + str(options["pat_id"]) + "\nSession #" + str(options["sess"]))
    patient_info_lbl.configure(bg="white", font=large_font)
    patient_info_lbl.grid(row=0, column=1)

    # Start, Pause, Trash, Stop, and Other button functions
    def r_start():
        frame.r_start() #***

    # paused = False
    def on_pause():
        frame.pause_block()
        # paused = -paused

    def on_trash_prev():
        pass

    def on_other_options():
        show_more_options(options)

    def continue_button(event=None):
        #max fn only, important for transition to app
        max_emg = frame.block.avg_max_emg
        print(max_emg)
        frame.r_block() 
        # frame.exit()
        root.destroy()
        no = port == None
        show_game(port, pat_id, sess, max_emg, frame, no_motor=no, no_emg=no)


    # Button configuration
    big_w = 11
    big_h = 3

    # start_btn
    start_btn = Button(root, text="Start Block", command=r_start, width=big_w, height=big_h,
                       bg="green", font=button_font, fg=button_font_color)
    start_btn.grid(row=1, column=0, padx=padx, pady=pady)

    # pause_btn
    pause_btn_color_swap = True
    swap_time = 0
    PAUSE_BLINK_RATE = .5
    pause_btn = Button(root, text="Pause Block", command=on_pause, width=big_w, height=big_h,
                       bg="red", font=button_font, fg=button_font_color)
    pause_btn['state'] = 'disabled'
    pause_btn.grid(row=2, column=0, padx=padx, pady=pady)

    # trash_btn
    trash_btn = Button(root, text="Trash Prev\nResult", command=on_trash_prev, width=big_w, height=big_h,
                       bg="blue", font=button_font, fg=button_font_color)
    trash_btn.grid(row=0, column=2)

    # other_opts_btn
    other_opts_btn = Button(root, text="More Options", command=on_other_options, width=big_w, height=big_h,
                        bg="gray", font=button_font, fg=button_font_color)
    other_opts_btn.grid(row=0, column=3)

    #continue btn
    cont = Button(root, text="Continue", command=continue_button,
                  width=17, height=0, bg=button_color, font=button_font, fg=button_font_color)
    cont['state'] = 'disabled'
    cont.grid(row=3, column=0, padx=padx, pady=pady)

    # Display Frame: widget to hold preload and record displays
    # display_frame

    # Large GRAY background: keep
    df_bg = "gray"
    display_frame = Frame(root, bg=df_bg, padx=padx, pady=pady)

    df_block = Label(display_frame, text="Current Block: N/A", 
                     bg=df_bg, font=small_font)
    df_block.grid(row=0, column=0)

    df_trial = Label(display_frame, text="Current Trial: N/A",
                     bg=df_bg, font=small_font)
    df_trial.grid(row=0, column=1)


    Num_of_success = 0
    df_success = Label(display_frame, text="Number of Successes: N/A",
                     bg=df_bg, font=small_font)
    df_success.grid(row=0, column=2)

    df_torque = Label(display_frame, text="",
                     bg=df_bg, font=small_font)
    df_torque.grid(row=1, column=0)

# success baubles: keep
     #box columns and rows for MAX collection
    bw = 5
    bh = 1
    baseline_display = BaselineMaxDisplay(
        display_frame, 600, 50, bw, bh, margin=15, squareSide=30, start_color=1 if options["display_success"] else 3)

    baseline_display.grid(row=1,column=0,rowspan=2,columnspan=3)
    baseline_display.configure(bg=df_bg)

    GI_CLEAR_TIME = 3
    general_info_lbl = Label(display_frame, text="", bg=df_bg, font=large_font)
    general_info_lbl.grid(row=4, column=0, columnspan=4)
    general_info_lbl.last_updated = time.time()

    display_frame.grid(row=1, column=1, rowspan=3, columnspan=3)


    center_window(root)

    # End gui
    #print("make frame")
    # # To launch with no_motor and no_emg, run sign_in.py and hold shift while you press continue
    frame = framework(port, patID=options["pat_id"], sess=options["sess"],
                      premin=options["pre_min"], premax=options["pre_max"], no_motor=no_motor, no_emg=no_emg)
    max = []
    center_window(root)
    # for i in range(bw*bh):
    #     baseline_display.set_record(i-1, 2)
    #print("after frame")
    while root.running:

        # Pause button flashing
        if not frame.paused and not frame.running:
            print("Illegal state: not frame.paused and not frame.running. Corrected to frame.paused and not frame.running.")
            frame.paused = True
        if frame.paused:
            if frame.running:
                # Running, but paused
                other_opts_btn['state'] = 'normal'
                start_btn['state'] = 'disabled'
                pause_btn['state'] = 'normal'
                cont['state'] = 'normal'

                if pause_btn_color_swap and time.time() - swap_time > PAUSE_BLINK_RATE:
                    pause_btn_color_swap = not pause_btn_color_swap
                    pause_btn.configure(bg="red")
                    swap_time = time.time()

                elif not pause_btn_color_swap and time.time() - swap_time > PAUSE_BLINK_RATE:
                    pause_btn_color_swap = not pause_btn_color_swap
                    pause_btn.configure(bg="green")
                    swap_time = time.time()
            else:
                # Not running; stopped
                other_opts_btn['state'] = 'normal'
                start_btn['state'] = 'normal'
                pause_btn['state'] = 'disabled'
                cont['state'] = 'disabled'

                pause_btn.configure(bg="red")
        else:
            # Running, not paused
            other_opts_btn['state'] = 'disabled'
            start_btn['state'] = 'disabled'
            pause_btn['state'] = 'normal'
            cont['state'] = 'normal'

            pause_btn.configure(bg="red")

        # Check for updates and then change values
        if options["updates"]:
            frame.update_options(options)

            # Update session value
            patient_info_lbl.configure(text="PatID " + str(options["pat_id"]) + "\nSession #" + str(options["sess"]))
            options["updates"] = False


        # Check if a trial is just starting
        if frame.starting_trial:
            if options["preload_audio"]:
                wav_file = "C:\\Program Files\\LETREP2\\resources\\preload_notification.wav"
                winsound.PlaySound(wav_file, winsound.SND_FILENAME | winsound.SND_ASYNC)

            df_trial.configure(text="Current Trial: " + str(frame.trial_count))
            #Check if this is a first trial
            if frame.trial_count == 0:
                options["block_count"] = frame.block_count
                df_block.configure(text="Current Block: " + str(frame.block_count))


            general_info_lbl.configure(text="Collect Max")
            general_info_lbl.last_updated = time.time()
            frame.starting_trial = False

        # Clear general info label after 3 seconds
        if time.time() - general_info_lbl.last_updated > GI_CLEAR_TIME:
            general_info_lbl.configure(text="")

        # This happens when after a trial

        if frame.finished_trial:
    #         # Check if we can do another trial
            baseline_display.set_record(frame.trial_count-1, 5)
            
            if frame.trial_count == bw * bh :
                logging.warning("Trial count meets success display limit... Ending block")
                
                max_emg = frame.block.avg_max_emg
                print(max_emg)
                frame.r_block() #***
                root.running = False
                # frame.exit()
                root.update()
                root.destroy()
                no = port == None
                show_game(port, pat_id, sess, max_emg, frame, no_motor=no, no_emg=no) #***
                cease=True
            
            # Reset trial bit
            if(not cease):
                frame.finished_trial = False
        if(not cease):
            root.update()
    if(not cease):        
        root.destroy()


if __name__ == "__main__":

    max(None, 1234, 1, no_motor=True, no_emg=True)



