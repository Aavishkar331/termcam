import cv2
import os


RAMP = " .,:;i1tfLCG08@"
cap = cv2.VideoCapture(0)
tc,tr = os.get_terminal_size()
MODES = ["ascii", "pixel", "half"]
m = 0

def size_math(mode,h,w,tc,tr):
    if mode == "half":
        cols = tc
        rows = int(h*cols/(w))
        max_rows = 2 * (tr - 1)
    
        if rows > max_rows:
            rows = max_rows
            cols = int(w*rows/(h))
    
        rows -= rows % 2
    else:
        cols = tc
        rows = int(h*cols/(2*w))
    
        if rows > tr:
            rows = tr
            cols = int(2*w*rows/(h))
    return cols,rows
def renderer(mode,small_gray,boosted,rows):
    lines = []
    if mode == MODES[2]:
        for y in range(0, rows, 2):
            top    = boosted[y]
            bottom = boosted[y + 1]
            line = ""
            for (b1, g1, r1), (b2, g2, r2) in zip(top, bottom):
                line += f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀"
            lines.append(line + "\033[0m")            
    
    elif mode == MODES[0]:
        for gray_row, color_row in zip(small_gray, boosted):
            line = ""
            for px, (b, g, r) in zip(gray_row, color_row):
                idx = int((px/255)*(len(RAMP)-1))
                line += f"\033[38;2;{r};{g};{b}m" + RAMP[idx]
            lines.append(line+"\033[0m")
    
    else:
        for gray_row, color_row in zip(small_gray, boosted):
            line = ""
            for px, (b, g, r) in zip(gray_row, color_row):
                line += f"\033[48;2;{r};{g};{b}m" + " "
            lines.append(line+"\033[0m")

    return lines

print("\033[2J\033[?25l")
while True:
    sucess,frame = cap.read()
    if not sucess:
        break

    h,w = frame.shape[:2]

    cols,rows = size_math(MODES[m],h,w,tc,tr)
    
    small_color = cv2.resize(frame, ( cols, rows ))   # order yaad hai? (w, h)
    small_gray = cv2.cvtColor(small_color,cv2.COLOR_BGR2GRAY)
    small_gray = cv2.equalizeHist(small_gray)
    hsv = cv2.cvtColor(small_color, cv2.COLOR_BGR2HSV).astype("float32")
    hsv[..., 1] *= 2.5      # saturation boost
    hsv[..., 2] *= 1.3      # brightness boost
    hsv = hsv.clip(0, 255).astype("uint8")
    boosted = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    lines = renderer(MODES[m],small_gray,boosted,rows)
    
    print("\033[H" + "\n".join(lines), end="")

    cv2.imshow("controls",small_color)        # koi chhota image, jaise small_color
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    if key == ord('m'):
        m = (m+1)%len(MODES)
        print("\033[2J")
print("\033[0m\033[?25h")
cap.release()
cv2.destroyAllWindows()