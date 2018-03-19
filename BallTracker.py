from PIL import Image as PIL_Image
from PIL import ImageTk
import cv2
from tkinter import *
from tkinter import ttk
import numpy as np
from tkinter.filedialog import askopenfilename
from helper_code import track_ball
import time
import os

NORM_FONT = ("Helvetica", 12)


class Application(Frame):
    def __init__(self):
        self.homepage = Tk()
        Frame.__init__(self, self.homepage)
        self.homepage.geometry("1480x720")
        self.homepage.wm_title("Ball Tracker")
        self.current_frame_number = 0
        self.memory_buffer = {}
        self.line_width = 8
        self.saving = False
        self.images = ()

        image = np.zeros((720, 1280, 3), np.uint8)
        image = PIL_Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        self.image_panel = Label(image=image)
        self.image_panel.image = image
        self.image_panel.pack(side="left")

        ttk.Button(self.homepage, text="Open New Clip", command=lambda: self.OpenFile()).pack(padx="10", pady="40",
                                                                                              fill=X)
        ttk.Label(self.homepage, text="Ball Size", font=NORM_FONT).pack(pady="10")

        self.ball_size = ttk.Entry(self.homepage)
        self.ball_size.pack(padx="10", pady="10", fill=X)

        ttk.Button(self.homepage, text="Update Line Width", command=lambda: self.update_line_width()).pack(padx="10",
                                                                                                           pady="40",
                                                                                                           fill=X)

        ttk.Button(self.homepage, text="Save Clip", command=lambda: self.save2disk()).pack(padx="10", pady="40",
                                                                                           fill=X)

        self.pool()

    def pool(self):
        if not self.saving and self.memory_buffer:
            if self.current_frame_number >= len(self.memory_buffer):
                self.current_frame_number = 0
            not_a_frame = self.memory_buffer.copy()
            not_a_frame, _ = self.draw(not_a_frame, self.current_frame_number, draw=True)
            self.update_image(cv2.cvtColor(not_a_frame, cv2.COLOR_BGR2RGB))
            self.current_frame_number += 1
        else:
            self.update_image(np.zeros((720, 1280, 3), np.uint8))

        self.after(500, self.pool)

    def update_image(self, image):
        image = PIL_Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        self.image_panel.configure(image=image)
        self.image_panel.image = image

    def OpenFile(self):
        name = askopenfilename(filetypes=(("MP4", "*.mp4"), ("AVI", "*.avi"), ("All Files", "*.*")),
                               title="Choose a file.", initialdir="./")

        memory_buffer, self.images = track_ball(name)
        # for i in range(len(memory_buffer)):
        #     frame, _ = self.draw(memory_buffer, i, draw=False)
        #     cv2.imshow('Frame', frame)
        #     cv2.waitKey(100)
        if memory_buffer:
            self.memory_buffer = memory_buffer.copy()

    def update_line_width(self):
        if self.ball_size.get().isdigit() and int(self.ball_size.get()) > 0:
            self.line_width = int(self.ball_size.get())
        else:
            self.line_width = 8
        self.update_image(np.zeros((720, 1280, 3), np.uint8))
        self.current_frame_number = 0

    def save2disk(self):
        self.saving = True
        if not os.path.isdir('images'):
            os.mkdir('images')
        for image in self.images:
            if not os.path.exists('images/{}.jpg'.format(image[0])):
                cv2.imwrite('images/{}.jpg'.format(image[0]), image[1])
                with open('images/data.csv', 'a') as f:
                    f.write('{},{}\n'.format(image[0], image[2]))

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('{}.avi'.format(int(time.time())), fourcc, 20, (1280, 720))

        for i in range(len(self.memory_buffer)):
            frame, _ = self.draw(self.memory_buffer.copy(), i, draw=True)
            for _ in range(4):
                out.write(frame)
        out.release()

        # for i in range(len(memory_buffer)):
        #     frame, _ = self.draw(memory_buffer, i, draw=False)
        #     cv2.imshow('Frame', frame)
        #     cv2.waitKey(100)
        self.saving = False

    # @staticmethod
    # def draw(buffer, frame_number, draw=True):
    #     frame = list(buffer.values())[frame_number].copy()
    #     n = frame_number + 1
    #     points = None
    #     if draw:
    #         for i in range(1, n):
    #             points = [eval(i) for i in buffer.keys()]
    #             if points[i - 1] is None or points[i] is None:
    #                 continue
    #             overlay = frame.copy()
    #             cv2.line(overlay, points[i - 1], points[i], (255, 0, 10), app.line_width)
    #             cv2.addWeighted(overlay, get_alpha(i, n), frame, 1 - get_alpha(i, n), 0, frame)
    #     return frame, points

    @staticmethod
    def draw(buffer, frame_number, draw=True):
        frame = list(buffer.values())[frame_number].copy()
        n = frame_number + 1
        points = None
        if draw:
            overlay = frame.copy()
            for i in range(1, n):
                points = [eval(i) for i in buffer.keys()]
                if points[i - 1] is None or points[i] is None:
                    continue
                cv2.line(overlay, points[i - 1], points[i], (10, 0, 255), app.line_width)
            cv2.addWeighted(overlay, 0.5, frame, 1 - 0.5, 0, frame)
        return frame, points

    @staticmethod
    def preview(buffer, frame_number, draw=True):
        frame_ = list(buffer.values())[frame_number].copy()
        n = frame_number + 1
        points = None
        if draw:
            for i in range(1, n):
                points = [eval(i) for i in buffer.keys()]
                if points[i - 1] is None or points[i] is None:
                    continue
                cv2.line(frame_, points[i - 1], points[i], (10, 0, 255), app.line_width)
        return frame_, points

def get_alpha(i, n):
    alpha = ((0.7 * i) / n) + 0.2
    return alpha


app = Application()
app.homepage.mainloop()
