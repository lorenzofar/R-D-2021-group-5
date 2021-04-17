from threading import Thread

import zbar

from camera.FrameHandler import FrameHandler
from camera.QRCodeHandler import QRCodeHandler


class CodeReader(Thread, FrameHandler):
    __code_handler: QRCodeHandler
    __scanner: zbar.Scanner

    __alive: bool

    # TODO: Add reference to code handlers

    def __init__(self):
        super().__init__()
        self._frames_buffer = []
        self.__alive = True

        self.__scanner = zbar.Scanner()

    def run(self) -> None:
        super().run()
        while self.__alive:
            # Get the next frame from the buffer
            ret, frame = self.get_next_frame()
            if ret and frame is not None:
                result = self.__scanner.scan(frame)
                # TODO: Emit the code when something is detected

    def stop(self):
        self.__alive = False
