import cv2
import numpy as np
import hashlib

def rewind(file, frame_number):
    i = 0
    cap = cv2.VideoCapture(file)
    if frame_number <= 0:
        return cap
    while cap.isOpened() and frame_number != i:
        cap.read()
        i += 1
    return cap


def fix_buffer(dic, key):
    for a, b in dic.items():
        if np.array_equal(b, key):
            del dic[a]
            return


def track_ball(file):
    global memory_buffer, waiting, org_frame
    memory_buffer = {}
    frame_count = 0
    cap = cv2.VideoCapture(file)
    cv2.namedWindow("Clip")
    cv2.setMouseCallback("Clip", draw_circle)
    waiting = True
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (1280, 720))
            fix_buffer(memory_buffer, frame)
            org_frame = frame.copy()

            for x, y in [eval(i) for i in memory_buffer.keys()]:
                cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)

            cv2.imshow('Clip', frame)
            frame_count += 1

            key = cv2.waitKey(1)
            while key != ord("n"):
                key = cv2.waitKey(1)
                if not waiting:
                    break
                if key == ord("p"):
                    frame_count -= 2
                    cap = rewind(file, frame_count)
                    break
                elif key == ord("s"):
                    break
                elif key == ord("q"):
                    cv2.destroyAllWindows()
                    return False
            if key == ord("s"):
                break

            waiting = True

    cv2.destroyAllWindows()
    images = []
    for frame in memory_buffer:
        img_hash = hashlib.sha256(np.array(memory_buffer[frame])).hexdigest()
        images.append((img_hash, memory_buffer[frame], frame))

    return memory_buffer, images

# import cv2
#
# img = cv2.imread('9e838e1065d1dabd298d3b1bb88dbafd7740700af0654d509945578e808d2b8a.jpg')
# cv2.circle(img, (683, 362), 1, (0, 0, 255), -1)
# cv2.imshow('image', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
