class circularStream:

    def __init__(self, camID='door', nsec=15, mediaPath='/home/pi/cam/mess/media/'):
        import picamera
        import notiClass as noti
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

        self.mail = noti.eNotification()

        if not mediaPath.endswith(os.path.sep):
            mediaPath += os.path.sep
        self.mediaPath = mediaPath

    def run(self, pinID=24, nImages=15):
        import os
        import time
        import datetime as dt
        import RPi.GPIO as GPIO
        import multiprocessing as mp
        mp.set_start_method('fork')

        self.cam.start_recording(self.stream, format='h264')

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pinID, GPIO.IN)

        try:
            while True:
                #self.cam.wait_recording(1)
                signal = GPIO.input(pinID)
                if signal == 1:
                    dtime = dt.datetime.now().strftime("%H:%M:%S_%y-%m-%d")
                    fname = dtime +'.h264'
                    self.cam.capture(self.mediaPath + 'still_'+dtime+'.jpg', format='jpeg', use_video_port=True)
                    self.cam.split_recording(self.mediaPath + 'after_'+fname)
                    self.stream.copy_to(self.mediaPath + 'before_'+fname, seconds=self.nsec)
                    self.stream.clear()

                    # capture photo and send email in new process
                    fnameStill = [
                        f'{self.mediaPath}image%02d_{dtime}.jpg' % i
                        for i in range(1, nImages + 1)
                    ]
                    self.cam.capture_sequence(fnameStill)

                    # send images via email
                    ddt = dt.datetime.now().strftime("%H:%M:%S %y-%m-%d")

                    betr = 'security alert ' + self.camID + ' (' + ddt + ')'
                    msg = 'detector went off ' + ddt + ' - video recording is currently in progress, h264 will be sent shortly.'

                    if __name__ == '__main__':
                        p = mp.Process(group=None, target=self.mail.notify_wImage, args=(betr, msg, imgs))
                        p.start()

                        time.sleep(self.nsec + 10)

                        # send videos
                        vids = [self.mediaPath + 'after_' + fname, self.mediaPath + 'before_' + fname]
                        msg = 'detector went off ' + ddt + ' - appended are video files.'
                        p1 = mp.Process(group=None, target=self.mail.notify_wImage, args=(betr, msg, vids))
                        p1.start()
                    #
                    # child_pid = os.fork()
                    #
                    # if child_pid == 0:
                    #     imgs = [self.mediaPath + 'still_'+dtime+'.jpg'] + fnameStill
                    #     self.mail.notify_wImage(betr, msg, img_path=imgs)
                    #
                    #     time.sleep(self.nsec+10)
                    #     # send videos
                    #     vids = [self.mediaPath + 'after_' + fname, self.mediaPath + 'before_' + fname]
                    #     msg = 'detector went off ' + ddt + ' - appended are video files.'
                    #     self.mail.notify_wImage(betr, msg, img_path=vids)

                        # remove video files

                    while signal == 1:
                        self.cam.wait_recording(2)
        finally:
            self.cam.stop_recording()