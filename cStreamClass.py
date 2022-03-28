class circularStream:

    def __init__(self, camID='door', nsec=15, mediaPath='/home/pi/cam/mess/media/'):
        import picamera
        import notiClass as noti
        import wsAsync_client as ws
        import asyncio
        import os

        self.camID = camID
        self.nsec = nsec
        cam_props = {'door': {'res' : (240, 320), 'rot': 90, 'led': False}}

        print('Initialising camera')
        self.cam = picamera.PiCamera()
        self.cam.resolution = cam_props[camID]['res']
        self.cam.rotation = cam_props[camID]['rot']
        self.cam.led = cam_props[camID]['led']
        self.stream = picamera.PiCameraCircularIO(self.cam, seconds=nsec)

        if not mediaPath.endswith(os.path.sep):
            mediaPath += os.path.sep
        self.mediaPath = mediaPath

        self.mail = noti.eNotification()
        self.ws_loop = asyncio.get_event_loop()
        self.ws_main_cap = ws.main_cap
        self.ws_main_ret = ws.main_ret

    def run(self, pinID=24, nImages=15):
        import time
        import datetime as dt
        import RPi.GPIO as GPIO
        import multiprocessing as mp
        import asyncio
        mp.set_start_method('fork')

        print('start circular stream')
        self.cam.start_recording(self.stream, format='h264')

        print('setting pin mode')
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pinID, GPIO.IN)
        print(f'pin value at init {GPIO.input(pinID)}')

        print('\n\n')
        try:
            while True:
                signal = GPIO.input(pinID)
                if signal == 1:
                    t1 = time.time()
                    dtime = dt.datetime.now().strftime("%H:%M:%S_%y-%m-%d")
                    print('signal received ' + dtime)

                    fname = dtime +'.h264'
                    self.cam.capture(self.mediaPath + 'still_'+dtime+'.jpg', format='jpeg', use_video_port=True)
                    self.cam.split_recording(self.mediaPath + 'after_'+fname)
                    self.stream.copy_to(self.mediaPath + 'before_'+fname, seconds=self.nsec)
                    self.stream.clear()

                    # capture photo and send email in new process
                    print('capturing image sequence ')
                    fnameStill = [
                        f'{self.mediaPath}image%02d_{dtime}.jpg' % i
                        for i in range(1, nImages + 1)
                    ]
                    self.cam.capture_sequence(fnameStill)

                    # send capture request to cam 2
                    print('request to record video via ws cam 2')
                    self.ws_loop.run_until_complete(self.ws_main_cap())

                    betr = 'security alert ' + self.camID + ' (' + dtime + ')'
                    msg = 'detector went off ' + dtime + ' - video recording is currently in progress, h264 will be sent shortly.'

                    print('emailing sequence')
                    p = mp.Process(group=None, target=self.mail.notify_wImage, args=(betr, msg, fnameStill))
                    p.start()
                    t2 = time.time()

                    # send capture request to cam 2
                    print('request video via ws cam 2')
                    self.ws_loop.run_until_complete(self.ws_main_ret(self.mediaPath + 'cam2.h264'))

                    print('emailing videos')
                    # send videos
                    vids = [self.mediaPath + 'after_' + fname, self.mediaPath + 'before_' + fname, self.mediaPath + 'cam2.h264']
                    msg = 'detector went off ' + dtime + ' - appended are video files.'
                    p1 = mp.Process(group=None, target=self.mail.notify_wImage, args=(betr, msg, vids))
                    p1.start()
                    t3 = time.time()

                    # remove video files
                    t4 = time.time()
                    while GPIO.input(pinID) == 1:
                        self.cam.wait_recording(2)
                    t5 = time.time()
                    print('---')
                    print(f'time full cycle (vigil to vigil): {round(t3 - t1)}')
                    print(f'time from signal received to emailing photos: {round(t2 - t1)}')
                    print(f'time from signal received to emailing videos: {round(t3 - t1)}')
                    print(f'time idle due to continuing signal: {t5-t4}')

                    print('\n\n')

        finally:
            self.cam.stop_recording()