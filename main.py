import cv2
import mediapipe as mp
import pyautogui
import math
import time


# Virtual Mouse - Subhabrata Pal

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True

screen_width, screen_height = pyautogui.size()
print("screen:", screen_width, screen_height)


# Camera

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


# MediaPipe

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


# Smooth cursor - Subhabrata Pal

class OneEuroFilter:

    def __init__(
        self,
        freq=30.0,
        min_cutoff=1.2,
        beta=0.6,
        d_cutoff=1.0
    ):
        self.freq = freq
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff

        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None

    def alpha(self, cutoff, dt):
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def reset(self):
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None

    def filter(self, x, t):

        if self.t_prev is None:
            self.t_prev = t
            self.x_prev = x
            self.dx_prev = 0.0
            return x

        dt = max(t - self.t_prev, 1e-6)

        dx = (x - self.x_prev) / dt

        a_d = self.alpha(
            self.d_cutoff,
            dt
        )

        dx_hat = (
            a_d * dx
            + (1 - a_d) * self.dx_prev
        )

        cutoff = (
            self.min_cutoff
            + self.beta * abs(dx_hat)
        )

        a = self.alpha(
            cutoff,
            dt
        )

        x_hat = (
            a * x
            + (1 - a) * self.x_prev
        )

        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t

        return x_hat


# Settings

SENSITIVITY = 2.2
DEADZONE = 0.0015

PINCH_ENTER = 0.032
PINCH_EXIT = 0.050

HOLD_TIME = 1.0

SCROLL_SENSITIVITY = 6000
SCROLL_DEADZONE = 0.002

HAND_LOST_GRACE_FRAMES = 5


# Filters

filter_x = OneEuroFilter(
    min_cutoff=1.2,
    beta=0.6
)

filter_y = OneEuroFilter(
    min_cutoff=1.2,
    beta=0.6
)

filter_scroll = OneEuroFilter(
    min_cutoff=1.0,
    beta=0.5
)


# Cursor

prev_x = None
prev_y = None

cursor_x, cursor_y = pyautogui.position()


# Gesture states

left_pinched = False
right_pinched = False

left_start_time = None
right_start_time = None

is_dragging = False

prev_scroll_y = None

hand_missing_frames = 0

status = "INDEX -> MOVE"


# Distance

def distance(a, b):

    return math.sqrt(
        (a.x - b.x) ** 2
        + (a.y - b.y) ** 2
        + (a.z - b.z) ** 2
    )


# Finger up

def finger_up(tip, pip):
    return tip.y < pip.y


# Rounded UI box

def rounded_rectangle(
    img,
    top_left,
    bottom_right,
    radius,
    color,
    thickness=-1
):

    x1, y1 = top_left
    x2, y2 = bottom_right

    if thickness == -1:

        cv2.rectangle(
            img,
            (x1 + radius, y1),
            (x2 - radius, y2),
            color,
            -1
        )

        cv2.rectangle(
            img,
            (x1, y1 + radius),
            (x2, y2 - radius),
            color,
            -1
        )

        cv2.circle(
            img,
            (x1 + radius, y1 + radius),
            radius,
            color,
            -1
        )

        cv2.circle(
            img,
            (x2 - radius, y1 + radius),
            radius,
            color,
            -1
        )

        cv2.circle(
            img,
            (x1 + radius, y2 - radius),
            radius,
            color,
            -1
        )

        cv2.circle(
            img,
            (x2 - radius, y2 - radius),
            radius,
            color,
            -1
        )

    else:

        cv2.rectangle(
            img,
            (x1 + radius, y1),
            (x2 - radius, y2),
            color,
            thickness
        )

        cv2.rectangle(
            img,
            (x1, y1 + radius),
            (x2, y2 - radius),
            color,
            thickness
        )


# UI - Subhabrata Pal

def draw_ui(
    frame,
    current_status,
    hand_detected,
    hold_progress
):

    h, w, _ = frame.shape

    # Top title

    overlay = frame.copy()

    rounded_rectangle(
        overlay,
        (15, 15),
        (245, 70),
        15,
        (25, 25, 25),
        -1
    )

    cv2.addWeighted(
        overlay,
        0.82,
        frame,
        0.18,
        0,
        frame
    )

    cv2.putText(
        frame,
        "VIRTUAL MOUSE",
        (30, 42),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Subhabrata Pal",
        (30, 61),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        (0, 220, 255),
        1
    )


    # Status panel

    panel_x1 = w - 280
    panel_y1 = 15
    panel_x2 = w - 15
    panel_y2 = 300

    overlay = frame.copy()

    rounded_rectangle(
        overlay,
        (panel_x1, panel_y1),
        (panel_x2, panel_y2),
        18,
        (22, 22, 22),
        -1
    )

    cv2.addWeighted(
        overlay,
        0.88,
        frame,
        0.12,
        0,
        frame
    )

    cv2.putText(
        frame,
        "GESTURE STATUS",
        (panel_x1 + 18, panel_y1 + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )

    cv2.line(
        frame,
        (panel_x1 + 15, panel_y1 + 42),
        (panel_x2 - 15, panel_y1 + 42),
        (0, 200, 255),
        1
    )


    # Current status

    cv2.putText(
        frame,
        "STATUS",
        (panel_x1 + 18, panel_y1 + 68),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        (150, 150, 150),
        1
    )

    status_color = (
        (0, 255, 200)
        if hand_detected
        else (0, 165, 255)
    )

    cv2.putText(
        frame,
        current_status,
        (panel_x1 + 18, panel_y1 + 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        status_color,
        2
    )


    # Hold progress

    if hold_progress > 0:

        bar_x1 = panel_x1 + 18
        bar_x2 = panel_x2 - 18

        bar_y1 = panel_y1 + 105
        bar_y2 = panel_y1 + 112

        cv2.rectangle(
            frame,
            (bar_x1, bar_y1),
            (bar_x2, bar_y2),
            (70, 70, 70),
            -1
        )

        progress_x = int(
            bar_x1
            + (bar_x2 - bar_x1)
            * min(hold_progress, 1.0)
        )

        cv2.rectangle(
            frame,
            (bar_x1, bar_y1),
            (progress_x, bar_y2),
            (0, 220, 255),
            -1
        )


    # Gesture guide

    guide_y = panel_y1 + 138

    guide = [
        "Index              Move",
        "Index + Thumb      Click",
        "Index + Thumb      Hold 1s = Double",
        "Middle + Thumb     Right Click",
        "Middle + Thumb     Hold 1s = Drag",
        "Fist               Scroll"
    ]

    for i, text in enumerate(guide):

        cv2.putText(
            frame,
            text,
            (panel_x1 + 18, guide_y + i * 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.31,
            (215, 215, 215),
            1
        )


    # Bottom bar

    bottom_y = h - 30

    overlay = frame.copy()

    rounded_rectangle(
        overlay,
        (120, h - 45),
        (520, h - 8),
        12,
        (20, 20, 20),
        -1
    )

    cv2.addWeighted(
        overlay,
        0.85,
        frame,
        0.15,
        0,
        frame
    )


    # Camera

    cv2.circle(
        frame,
        (140, bottom_y),
        5,
        (0, 255, 100),
        -1
    )

    cv2.putText(
        frame,
        "Camera",
        (152, bottom_y + 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.33,
        (220, 220, 220),
        1
    )


    # Hand

    cv2.circle(
        frame,
        (235, bottom_y),
        5,
        (0, 255, 100) if hand_detected else (0, 100, 255),
        -1
    )

    cv2.putText(
        frame,
        "Hand",
        (247, bottom_y + 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.33,
        (220, 220, 220),
        1
    )


    # Smoothing

    cv2.putText(
        frame,
        "Smoothing ON",
        (310, bottom_y + 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.33,
        (0, 220, 255),
        1
    )


# Reset

def reset_all():

    global left_pinched
    global right_pinched
    global left_start_time
    global right_start_time
    global is_dragging
    global prev_scroll_y
    global status

    if is_dragging:
        pyautogui.mouseUp()

    left_pinched = False
    right_pinched = False

    left_start_time = None
    right_start_time = None

    is_dragging = False

    prev_scroll_y = None

    status = "INDEX -> MOVE"

    filter_scroll.reset()


# Main loop - Subhabrata Pal

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    result = hands.process(rgb)

    hold_progress = 0.0


    # Hand detected

    if result.multi_hand_landmarks:

        hand_missing_frames = 0

        hand = result.multi_hand_landmarks[0]

        mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )


        # Landmarks

        thumb_tip = hand.landmark[4]

        index_pip = hand.landmark[6]
        index_tip = hand.landmark[8]

        middle_pip = hand.landmark[10]
        middle_tip = hand.landmark[12]

        ring_pip = hand.landmark[14]
        ring_tip = hand.landmark[16]

        pinky_pip = hand.landmark[18]
        pinky_tip = hand.landmark[20]

        middle_mcp = hand.landmark[9]

        wrist = hand.landmark[0]


        now = time.time()


        # Finger states

        index_up = finger_up(
            index_tip,
            index_pip
        )

        middle_up = finger_up(
            middle_tip,
            middle_pip
        )

        ring_up = finger_up(
            ring_tip,
            ring_pip
        )

        pinky_up = finger_up(
            pinky_tip,
            pinky_pip
        )


        # Pinch distances

        index_thumb_dist = distance(
            index_tip,
            thumb_tip
        )

        middle_thumb_dist = distance(
            middle_tip,
            thumb_tip
        )


        # Fist

        all_closed = (

            not index_up
            and not middle_up
            and not ring_up
            and not pinky_up
        )


        # SCROLL

        if all_closed:

            status = "SCROLL"

            if is_dragging:

                pyautogui.mouseUp()

                is_dragging = False

            left_pinched = False
            right_pinched = False

            left_start_time = None
            right_start_time = None

            palm_y = (
                wrist.y
                + middle_mcp.y
            ) / 2

            scroll_y = filter_scroll.filter(
                palm_y,
                now
            )

            if prev_scroll_y is None:

                prev_scroll_y = scroll_y

            dy = (
                scroll_y
                - prev_scroll_y
            )

            if abs(dy) > SCROLL_DEADZONE:

                pyautogui.scroll(
                    int(
                        -dy
                        * SCROLL_SENSITIVITY
                    )
                )

            prev_scroll_y = scroll_y


        # NORMAL

        else:

            prev_scroll_y = None
            filter_scroll.reset()


            # LEFT CLICK

            if not right_pinched:

                if (
                    not left_pinched
                    and index_thumb_dist < PINCH_ENTER
                ):

                    left_pinched = True

                    left_start_time = now


                elif (
                    left_pinched
                    and index_thumb_dist > PINCH_EXIT
                ):

                    left_pinched = False


                    if left_start_time is not None:

                        held_time = (
                            now
                            - left_start_time
                        )


                        # Double click

                        if held_time >= HOLD_TIME:

                            pyautogui.doubleClick(
                                interval=0.12
                            )

                            status = "DOUBLE CLICK"


                        # Left click

                        else:

                            pyautogui.click()

                            status = "LEFT CLICK"


                    left_start_time = None


            # Left hold

            if left_pinched:

                if left_start_time is None:

                    left_start_time = now

                held_time = (
                    now
                    - left_start_time
                )

                hold_progress = (
                    held_time
                    / HOLD_TIME
                )

                if held_time >= HOLD_TIME:

                    status = "DOUBLE CLICK READY"

                else:

                    status = "LEFT CLICK"


            # RIGHT CLICK / DRAG

            if not left_pinched:

                if (
                    not right_pinched
                    and middle_thumb_dist < PINCH_ENTER
                ):

                    right_pinched = True

                    right_start_time = now


                elif (
                    right_pinched
                    and middle_thumb_dist > PINCH_EXIT
                ):

                    right_pinched = False


                    if right_start_time is not None:

                        held_time = (
                            now
                            - right_start_time
                        )


                        # Drag end

                        if held_time >= HOLD_TIME:

                            if is_dragging:

                                pyautogui.mouseUp()

                                is_dragging = False

                            status = "DRAG END"


                        # Right click

                        else:

                            pyautogui.click(
                                button="right"
                            )

                            status = "RIGHT CLICK"


                    right_start_time = None


            # Right hold

            if right_pinched:

                if right_start_time is None:

                    right_start_time = now

                held_time = (
                    now
                    - right_start_time
                )

                hold_progress = (
                    held_time
                    / HOLD_TIME
                )

                if held_time >= HOLD_TIME:

                    if not is_dragging:

                        pyautogui.mouseDown()

                        is_dragging = True

                    status = "DRAGGING"

                else:

                    status = "RIGHT CLICK"


            # CURSOR

            if (
                not left_pinched
                and not right_pinched
            ):

                x = filter_x.filter(
                    index_tip.x,
                    now
                )

                y = filter_y.filter(
                    index_tip.y,
                    now
                )


                if prev_x is None:

                    prev_x = x
                    prev_y = y

                    cursor_x, cursor_y = pyautogui.position()


                dx = x - prev_x
                dy = y - prev_y


                if abs(dx) < DEADZONE:
                    dx = 0

                if abs(dy) < DEADZONE:
                    dy = 0


                cursor_x += (
                    dx
                    * screen_width
                    * SENSITIVITY
                )

                cursor_y += (
                    dy
                    * screen_height
                    * SENSITIVITY
                )


                cursor_x = max(
                    2,
                    min(
                        screen_width - 3,
                        cursor_x
                    )
                )

                cursor_y = max(
                    2,
                    min(
                        screen_height - 3,
                        cursor_y
                    )
                )


                pyautogui.moveTo(
                    int(cursor_x),
                    int(cursor_y)
                )


                prev_x = x
                prev_y = y


            # DRAG MOVEMENT

            elif is_dragging:

                x = filter_x.filter(
                    index_tip.x,
                    now
                )

                y = filter_y.filter(
                    index_tip.y,
                    now
                )


                if prev_x is None:

                    prev_x = x
                    prev_y = y


                dx = x - prev_x
                dy = y - prev_y


                if abs(dx) < DEADZONE:
                    dx = 0

                if abs(dy) < DEADZONE:
                    dy = 0


                cursor_x += (
                    dx
                    * screen_width
                    * SENSITIVITY
                )

                cursor_y += (
                    dy
                    * screen_height
                    * SENSITIVITY
                )


                cursor_x = max(
                    2,
                    min(
                        screen_width - 3,
                        cursor_x
                    )
                )

                cursor_y = max(
                    2,
                    min(
                        screen_height - 3,
                        cursor_y
                    )
                )


                pyautogui.moveTo(
                    int(cursor_x),
                    int(cursor_y)
                )


                prev_x = x
                prev_y = y


    # Hand lost

    else:

        hand_missing_frames += 1

        if (
            hand_missing_frames
            > HAND_LOST_GRACE_FRAMES
        ):

            prev_x = None
            prev_y = None

            reset_all()

            filter_x.reset()
            filter_y.reset()


    # UI

    draw_ui(
        frame,
        status,
        result.multi_hand_landmarks is not None,
        hold_progress
    )


    cv2.imshow(
        "Virtual Mouse",
        frame
    )


    # Press "q" to exit

    if cv2.waitKey(1) & 0xFF == ord("q"):

        if is_dragging:

            pyautogui.mouseUp()

        break


# Cleanup

cap.release()
cv2.destroyAllWindows()


