import cv2, sys, os, time
import numpy as np

try:
    import msvcrt
except ImportError:
    msvcrt = None

os.system("")
sys.stdout.reconfigure(encoding="utf-8")

CHARS = np.array(list(" .:-=+*#%@"))
SAT = 1.9
MAX_CAMS = 5
mode = 2  # 0 = plain ascii, 1 = color ascii, 2 = half-block

V = [i * 255 // 31 for i in range(32)]
FG = [f"\033[38;2;{V[i >> 10]};{V[(i >> 5) & 31]};{V[i & 31]}m" for i in range(32768)]
BG = [s.replace("[38;", "[48;") for s in FG]
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4))

def boost(img):
    h, s, v = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2HSV))
    v = clahe.apply(v)
    s = cv2.convertScaleAbs(s, alpha=SAT)
    return cv2.cvtColor(cv2.merge([h, s, v]), cv2.COLOR_HSV2BGR)

def to_idx(img):
    b = img[:, :, 0] >> 3
    g = img[:, :, 1] >> 3
    r = img[:, :, 2] >> 3
    return (r.astype(np.int32) << 10) | (g.astype(np.int32) << 5) | b.astype(np.int32)

def changed(key):
    flags = np.ones(key.shape, dtype=bool)
    flags[:, 1:] = key[:, 1:] != key[:, :-1]
    return flags.tolist()

def render(frame, cols, rows):
    if mode == 2:
        idx = to_idx(boost(cv2.resize(frame, (cols, (rows - 1) * 2))))
        top, bot = idx[0::2], idx[1::2]
        flags = changed(top * 32768 + bot)
        lines = []
        for t, b, f in zip(top.tolist(), bot.tolist(), flags):
            lines.append("".join(
                [FG[p] + BG[q] + "▀" if c else "▀" for p, q, c in zip(t, b, f)]
            ) + "\033[0m")
        return "\n".join(lines)

    small = boost(cv2.resize(frame, (cols, rows - 1)))
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    chars = CHARS[gray.astype(np.int32) * len(CHARS) // 256].tolist()

    if mode == 0:
        return "\n".join("".join(row) for row in chars)

    idx = to_idx(small)
    lines = []
    for t, ch, f in zip(idx.tolist(), chars, changed(idx)):
        lines.append("".join(
            [FG[p] + c if g else c for p, c, g in zip(t, ch, f)]
        ) + "\033[0m")
    return "\n".join(lines)

def open_cam(i):
    cam = cv2.VideoCapture(i, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(i)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    ok, _ = cam.read()
    if not ok:
        cam.release()
        return None
    return cam

def next_cam(current):
    for step in range(1, MAX_CAMS + 1):
        i = (current + step) % MAX_CAMS
        cam = open_cam(i)
        if cam:
            return cam, i
    return None, current

cam_index = 0
cap = open_cam(cam_index)
if not cap:
    sys.exit("no camera found")

sys.stdout.write("\033[2J\033[?25l")
last = time.perf_counter()
fps = 0.0
try:
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame = cv2.flip(frame, 1)
        cols, rows = os.get_terminal_size()

        sys.stdout.write("\033[H" + render(frame, cols, rows))
        sys.stdout.flush()

        now = time.perf_counter()
        fps = fps * 0.9 + (1 / (now - last)) * 0.1
        last = now
        sys.stdout.write(
            f"\033]0;ascii cam | cam {cam_index} | {fps:.0f} fps | c = mode | m = camera | q = quit\007"
        )

        if msvcrt and msvcrt.kbhit():
            key = msvcrt.getwch().lower()
            if key == "c":
                mode = (mode + 1) % 3
                sys.stdout.write("\033[2J")
            elif key == "m":
                cap.release()
                cap, cam_index = next_cam(cam_index)
                if not cap:
                    break
                sys.stdout.write("\033[2J")
            elif key == "q":
                break
except KeyboardInterrupt:
    pass
finally:
    if cap:
        cap.release()
    sys.stdout.write("\033[?25h\033[0m\n")





    