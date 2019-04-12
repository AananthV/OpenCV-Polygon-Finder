import cv2
import numpy as np

class Scanner:
    def __init__(self, image):
        self.image = image

    def rectify(self, h):
        h = h.reshape((4,2))
        hnew = np.zeros((4,2),dtype = np.float32)

        add = h.sum(1)
        hnew[0] = h[np.argmin(add)]
        hnew[2] = h[np.argmax(add)]

        diff = np.diff(h,axis = 1)
        hnew[1] = h[np.argmin(diff)]
        hnew[3] = h[np.argmax(diff)]

        return hnew

    def findPolyL(self, img):
        im2 = img.copy()
        #imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(img, (5,5), 0)
        #_,timg = cv2.threshold(blurred, 95, 255, cv2.THRESH_BINARY_INV)
        timg = np.invert(blurred)
        contours, heirarchy = cv2.findContours(timg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        '''
        hull = cv2.convexHull(contours[0])
        cv2.fillConvexPoly(timg, hull, 255)
        contours, heirarchy = cv2.findContours(timg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        '''

        if len(contours) == 0:
            return 0, im2

        pmt = cv2.arcLength(contours[0], True)
        approx = cv2.approxPolyDP(contours[0], 0.02*pmt, True)

        '''cv2.imshow("Before", timg)
        for a in approx:
            cv2.circle(timg, tuple(a[0]), 5, (127, 0, 0), -1)
        cv2.imshow(f"Timg{np.random.rand(1)}",timg)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(im2, str(len(approx)), (im2.shape[1]*48//100, im2.shape[0]*98//100), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.imshow("im2", timg)
        return len(approx), im2
        '''
        return len(approx)

    def findPolyR(self, img):
        im2 = img.copy()
        #imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(img, (5,5), 0)
        #_,timg = cv2.threshold(blurred, 95, 255, cv2.THRESH_BINARY_INV)
        timg = np.invert(blurred)
        contours, heirarchy = cv2.findContours(timg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        hull = cv2.convexHull(contours[0])
        cv2.fillConvexPoly(timg, hull, 255)
        contours, heirarchy = cv2.findContours(timg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if len(contours) == 0:
            return 0, im2

        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        pmt = cv2.arcLength(contours[0], True)
        approx = cv2.approxPolyDP(contours[0], 0.02*pmt, True)

        '''
        for a in hull:
            cv2.circle(timg, tuple(a[0]), 5, (127, 0, 0), -1)
        cv2.imshow(f"Timg{np.random.rand(1)}",timg)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(im2, str(len(approx)), (im2.shape[1]*48//100, im2.shape[0]*98//100), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.imshow("im2", timg)
        return len(approx), im2
        '''
        return len(approx)

    def preProcessing(self, threshValue):
        # resize image so it can be processed
        # choose optimal dimensions such that important content is not lost
        image = cv2.resize(self.image, (400,225))

        # creating copy of original image
        orig = image.copy()

        # convert to grayscale and blur to smooth
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, threshValue, 255, cv2.THRESH_BINARY)
        blurred = cv2.GaussianBlur(thresh, (5, 5), 0)
        #blurred = cv2.medianBlur(gray, 5)

        # apply Canny Edge Detection
        edged = cv2.Canny(blurred, 0, 50)
        orig_edged = edged.copy()

        # find the contours in the edged image, keeping only the
        # largest ones, and initialize the screen contour
        (contours, _) = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        #x,y,w,h = cv2.boundingRect(contours[0])
        #cv2.rectangle(image,(x,y),(x+w,y+h),(0,0,255),0)

        # get approximate contour
        target = None

        for c in contours:
            p = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * p, True)

            if len(approx) == 4:
                target = approx
                break

        if target is None:
            return orig, edged, orig, orig

        # mapping target points to 800x800 quadrilateral
        approx = self.rectify(target)
        pts2 = np.float32([[0,0],[480,0],[480,200],[0,200]])

        M = cv2.getPerspectiveTransform(approx,pts2)
        dst = cv2.warpPerspective(orig,M,(480,200))

        cv2.drawContours(image, [target], -1, (0, 255, 0), 2)
        dst = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

        # using thresholding on warped image to get scanned effect (If Required)
        ret,th1 = cv2.threshold(dst,threshValue,255,cv2.THRESH_BINARY)
        '''
        th2 = cv2.adaptiveThreshold(dst,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
                    cv2.THRESH_BINARY,11,2)
        th3 = cv2.adaptiveThreshold(dst,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                    cv2.THRESH_BINARY,11,2)
        ret2,th4 = cv2.threshold(dst,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        '''

        '''cv2.imshow("Original.jpg", orig)
        cv2.imshow("Original Gray.jpg", gray)
        cv2.imshow("Original Blurred.jpg", blurred)
        cv2.imshow("Original Edged.jpg", orig_edged)
        cv2.imshow("Outline.jpg", image)
        cv2.imshow("Thresh Binary.jpg", th1)
        cv2.imshow("Thresh mean.jpg", th2)
        cv2.imshow("Thresh gauss.jpg", th3)
        cv2.imshow("Otsu's.jpg", th4)
        cv2.imshow("dst.jpg", dst)
        '''

        # other thresholding methods
        """
        ret,thresh1 = cv2.threshold(dst,127,255,cv2.THRESH_BINARY)
        ret,thresh2 = cv2.threshold(dst,127,255,cv2.THRESH_BINARY_INV)
        ret,thresh3 = cv2.threshold(dst,127,255,cv2.THRESH_TRUNC)
        ret,thresh4 = cv2.threshold(dst,127,255,cv2.THRESH_TOZERO)
        ret,thresh5 = cv2.threshold(dst,127,255,cv2.THRESH_TOZERO_INV)

        cv2.imshow("Thresh Binary", thresh1)
        cv2.imshow("Thresh Binary_INV", thresh2)
        cv2.imshow("Thresh Trunch", thresh3)
        cv2.imshow("Thresh TOZERO", thresh4)
        cv2.imshow("Thresh TOZERO_INV", thresh5)
        """

        imgL = th1[0:dst.shape[0], 0:dst.shape[1]//2]
        imgR = th1[0:dst.shape[0], dst.shape[1]//2:dst.shape[1]]

        '''
        cv2.imshow("Left", imgL)
        cv2.imshow("Right", imgR)
        '''
        return image, orig_edged, imgL, imgR;

    def scan(self, threshValue):
        _, __, imgL, imgR = self.preProcessing(threshValue)

        lc = self.findPolyL(imgL)
        rc = self.findPolyR(imgR)
        '''
        lc, til = self.findPoly(imgL)
        rc, tir = self.findPoly(imgR)
        cv2.imshow("TLeft", til)
        cv2.imshow("TRight", tir)
        finalImg = np.concatenate((til, tir), axis=1)
        cv2.imshow("Final", finalImg)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        '''
        return lc, rc
