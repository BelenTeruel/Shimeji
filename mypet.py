import tkinter as tk
import random, os, multiprocessing
from PIL import Image, ImageTk
from utils import get_pet_paths, load_img_from, parse_args

class Mypet: 
    
    def __init__(self, args):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        pet_path = paths[args.pet]

        self.animations = {
            "left": load_img_from(os.path.join(pet_path, "Left")),
            "right": load_img_from(os.path.join(pet_path, "Right")),
            "standing": load_img_from(os.path.join(pet_path, "Standing")),
            "dragging": load_img_from(os.path.join(pet_path, "Dragging"))
            # "up": [load("climbing1.png"), load("climbing2.png")],
        }
        self.current_frame = 0
        self.frame_delay = 0  
        self.frame_hold = 5   
        
        self.label = tk.Label(self.root, image=self.animations["standing"][0], bg="black")
        self.root.wm_attributes("-transparentcolor", "black")
        self.label.pack()

        self.label.bind("<ButtonPress-1>", self.on_drag_start)
        self.label.bind("<B1-Motion>", self.on_drag_motion)
        self.label.bind("<ButtonRelease-1>", self.on_drag_end)
        self.dragging = False

        self.directions = ["right", "up", "left", "down", "up_l", "down_l", "up_r", "down_r"]
        # self.root.geometry(f"+{self.x}+{self.y}")

        self.dx = 3  #bajarlo p/"pasos mas cortos"
        self.dy = 3 
        self.steps_remaining = random.randint(10, 50)
        
        if args.mode == "square":
            self.x, self.y = 0, random.randint(0, self.screen_height -64)
            self.direction = random.choice(["up", "down"])
            self.square_move()
            
        elif args.mode == "random":
            self.x = random.randint(0, self.screen_width - 64)
            self.y = random.randint(0, self.screen_height - 64)
            self.direction = random.choice(self.directions)
            self.random_move()    
        
        self.root.mainloop()

    # @property
    # def x_bounds(self): ...
    def get_x_bounds(self):
        return {
            "left" : max(self.x - self.dx, 0),
            "right" : min(self.x + self.dx, self.screen_width - 64)
        }

    def get_y_bounds(self):
        return{
            "up": max(self.y - self.dy, 0),
            "down": min(self.y + self.dy, self.screen_height - 64)
        }
    
    def update_sprite(self):
        if self.dragging:
            key = "dragging"
        elif  self.direction in ("left", "up_l", "down_l"): 
            key = "left"
        elif self.direction in ("right", "up_r", "down_r"):
            key = "right"
        else: 
            key = "standing"
        
        frames = self.animations.get(key, self.animations["standing"]) 

        if key in ("standing", "dragging"):
            self.frame_delay += 1
            if self.frame_delay < self.frame_hold:
                return
            self.frame_delay = 0

        self.current_frame = (self.current_frame + 1) % len(frames)
        self.label.config(image=frames[self.current_frame])

    def square_move(self):
        if not self.dragging:
            x_bounds = self.get_x_bounds()
            y_bounds = self.get_y_bounds()

            at_left   = self.x <= 0
            at_right  = self.x >= self.screen_width - 64
            at_top    = self.y <= 0
            at_bottom = self.y >= self.screen_height - 64

            if self.steps_remaining <= 0:
                possible_dirs = []
                if at_left or at_right:
                    possible_dirs.extend(["up", "down"])
                if at_top or at_bottom:
                    possible_dirs.extend(["left", "right"])
                if possible_dirs:
                    self.direction = random.choice(possible_dirs)
                self.steps_remaining = random.randint(10, 50)

            move_map = {
                "right": (x_bounds["right"], self.y),
                "left": (x_bounds["left"], self.y),
                "up": (self.x, y_bounds["up"]),
                "down": (self.x, y_bounds["down"]),
            }

            if self.direction in move_map:
                self.x, self.y = move_map[self.direction]

            self.steps_remaining -=1
            self.root.geometry(f"+{self.x}+{self.y}")

        self.update_sprite()
        self.root.after(70, self.square_move)
   

    def random_move(self):
        if not self.dragging:
            x_bounds = self.get_x_bounds()
            y_bounds = self.get_y_bounds()
            
            if self.steps_remaining <= 0:
                self.direction = random.choice(self.directions)
                self.steps_remaining = random.randint(10,50)

            move_map = {
                "right": (x_bounds["right"], self.y),
                "left": (x_bounds["left"], self.y),
                "up": (self.x, y_bounds["up"]),
                "down":(self.x, y_bounds["down"]),
                "up_l": (x_bounds["left"], y_bounds["up"]),
                "up_r": (x_bounds["right"], y_bounds["up"]),
                "down_l": (x_bounds["left"], y_bounds["down"]),
                "down_r": (x_bounds["right"], y_bounds["down"])
            }
            
            if self.direction in move_map:
                self.x, self.y = move_map[self.direction]

            self.steps_remaining -= 1

        self.update_sprite()
        self.root.geometry(f"+{self.x}+{self.y}")
        self.root.after(70, self.random_move)  #para que sea mas fluido bajarlo

    def on_drag_start(self, event):
        self.dragging = True
        self.drag_offset_x = event.x
        self.drag_offset_y = event.y

    def on_drag_motion(self, event):
        new_x = self.root.winfo_pointerx() - self.drag_offset_x
        new_y = self.root.winfo_pointery() - self.drag_offset_y
        self.x = new_x
        self.y = new_y
        self.root.geometry(f"+{self.x}+{self.y}")

    def on_drag_end(self, event):
        self.dragging = False


paths = get_pet_paths()

def run_pet(args):
    Mypet(args)

if __name__ == "__main__":
    args = parse_args(list(paths.keys()))

    processes = []  
    for _ in range(args.quantity):
        p = multiprocessing.Process(target=run_pet, args=(args,))
        p.start()
        processes.append(p)
    for p in processes:
        p.join
