'''
All things computer vision. Isolates OpenCV from the rest of the system.
If you see another file using OpenCV directly, it should probably be using
this module instead.
'''

import cv2
import cv



class Camera(object):
    S_CAPTURE_OPEN_ERROR = 'Device #%d does not support video capture interface'
    S_CAPTURE_READ_ERROR = 'Error while capturing. Camera disconnected?'
    SEARCH_FOR_DEVICE=-1

    def __init__(self, device_index=SEARCH_FOR_DEVICE, width=400, height=300):
        self._device = self._new_capture_device(device_index)
        self.set_dimensions(width, height)

    @staticmethod
    def _new_capture_device(device_index):
        capture = cv2.VideoCapture(device_index)

        if not capture.isOpened():
            capture.release()

            raise IOError(S_CAPTURE_OPEN_ERROR % device_index)

        return capture

    def set_dimensions(self, width, height):
        self._device.set(cv.CV_CAP_PROP_FRAME_WIDTH, width)
        self._device.set(cv.CV_CAP_PROP_FRAME_HEIGHT, height)

    def read_image(self):
        ret, image = self._device.read()

        if not ret:
            raise IOError(S_CAPTURE_READ_ERROR)

        return Image(image)


class Image(object):
    def __init__(self, image_cv, is_grayscale=False):
        self._image_cv = image_cv
        self._is_grayscale = is_grayscale
        self._image_cv_grayscale = None
        if self._is_grayscale:
            self._image_cv_grayscale = self._image_cv

    def to_cv(self):
        return self._image_cv

    def to_cv_grayscale(self):
        if self._image_cv_grayscale is None:
            self._image_cv_grayscale = \
                    self._cv_rgb_to_cv_grayscale(self._image_cv)
        return self._image_cv_grayscale

    def get_width(self):
        return self._image_cv.shape[0]

    def get_height(self):
        return self._image_cv.shape[1]


    @staticmethod
    def _cv_rgb_to_cv_grayscale(image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


class HaarLoader(object):
    _haar_files = {
        "face": "haars/haarcascade_frontalface_default.xml",
        "nose": "haars/haarcascade_mcs_nose.xml",
    }

    _haar_cache = {}

    @staticmethod
    def from_name(name):
        if not name in HaarLoader._haar_files:
            # TODO: Throw an exception
            pass

        haar_file = HaarLoader._haar_files[name]

        haar = HaarLoader.from_file(haar_file, name)

        return haar

    @staticmethod
    def from_file(file_, cache_name=None):
        import os

        if cache_name in HaarLoader._haar_cache:
            return HaarLoader._haar_cache[cache_name]

        current_dir = os.path.dirname(os.path.realpath(__file__))

        haar_file = os.path.join(current_dir, file_)

        haar = cv2.CascadeClassifier(haar_file)

        if not cache_name is None:
            if not cache_name in HaarLoader._haar_cache:
                HaarLoader._haar_cache[cache_name] = haar

        return haar


class NoseLocator(object):
    def __init__(self):
        self._face_detector = FeatureDetector(
                'face', scale_factor=1.5, min_neighbors=5)
        self._nose_detector = FeatureDetector(
                'nose', scale_factor=1.1, min_neighbors=5)

    def locate(self, image):
        face = self._face_detector.detect(image)
        nose = self._nose_detector.detect(face['image'])
        return {
                'x': face['x'] + nose['center']['x'],
                'y': face['y'] + nose['center']['y'],
                }


class FeatureDetector(object):
    def __init__(self, name, scale_factor=1.1, min_neighbors=3):
        '''
        name - name of feature to detect

        scale_factor - how much the image size is reduced at each image scale
                while searching. Default 1.1.

        min_neighbors - how many neighbors each candidate rectangle should have
                to retain it. Default 3.
        '''
        self._name = name
        self._single = None
        self._plural = None
        self._image = None
        self._cascade = HaarLoader.from_name(name)
        self._scale_factor = scale_factor
        self._min_neighbors = min_neighbors

    def detect(self, image):
        self._image = image
        self._detect_plural()
        self._exit_if_none_detected()
        self._unpack_first()
        self._extract_image()
        self._calculate_center()
        return self._single

    def _detect_plural(self):
        self._plural = self._cascade.detectMultiScale(
                self._image.to_cv_grayscale(),
                self._scale_factor,
                self._min_neighbors)

    def _exit_if_none_detected(self):
        if len(self._plural) == 0:
            # FIXME: need custom exception
            raise Exception('No ' + self._name + 's detected.')

    def _unpack_first(self):
        self._single = dict(zip(['x', 'y', 'width', 'height'], self._plural[0]))

    def _calculate_center(self):
        self._single["center"] = {
                "x": (self._single["x"] + self._single["width"]) / 2,
                "y": (self._single["y"] + self._single["height"]) / 2,
                }

    def _extract_image(self):
        single = self._single
        from_y = single['y']
        to_y = single['y'] + single['height']
        from_x = single['x']
        to_x = single['x'] + single['width']
        image_cv_grayscale = self._image.to_cv_grayscale()
        single["image"] = Image(
                image_cv_grayscale[from_y:to_y, from_x:to_x],
                is_grayscale=True)
