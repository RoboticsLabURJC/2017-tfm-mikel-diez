import cv2
import numpy as np


def drawlines(img1, img2, lines, pts1, pts2):
    ''' img1 - image on which we draw the epilines for the points in img2
        lines - corresponding epilines '''
    r, c = img1.shape
    img1 = cv2.cvtColor(img1, cv2.COLOR_GRAY2BGR)
    img2 = cv2.cvtColor(img2, cv2.COLOR_GRAY2BGR)
    for r, pt1, pt2 in zip(lines, pts1, pts2):
        color = tuple(np.random.randint(0, 255, 3).tolist())
        x0, y0 = map(int, [0, -r[2] / r[1]])
        x1, y1 = map(int, [c, -(r[2] + r[0] * c) / r[1]])
        img1 = cv2.line(img1, (x0, y0), (x1, y1), color, 1)
        #img1 = cv2.circle(img1, tuple(pt1), 5, color, -1)
        print(pt2)
        print(color)
        img2 = cv2.circle(img2, tuple(pt2[0]), 5, color, -1)
    return img1, img2


def imShowTwoImages(image1, image2, title):
    image = np.concatenate((cv2.resize(image1, (640, 480)), cv2.resize(image2, (640, 480))), axis=1)
    color = 0
    # for index, line in enumerate(range(image1.shape[0] / 10)):
    #
    #     if (color > 255):
    #         color = 0
    #     cv2.line(image, (0, line * 10), (1279, line * 10), (color), 1)
    #     color += 50
    cv2.imshow(title, image)
