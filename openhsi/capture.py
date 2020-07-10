# AUTOGENERATED! DO NOT EDIT! File to edit: 01_capture.ipynb (unless otherwise specified).

__all__ = ['OpenHSI']

# Cell
import numpy as np
import matplotlib.pyplot as plt
from ximea import xiapi

# Cell
class OpenHSI(object):
    """XIMEA camera class to take images"""

    def __init__(self, serialnumber:str = None, xbinwidth:int = 896, xbinoffset:int = 528,
                exposure_ms:int = 1000, gain:int = 0):
        """Init the camera"""
        self.xicam = xiapi.Camera()
        self.xicam.open_device_by_SN(serialnumber) if serialnumber else self.xicam.open_device()

        print(f'Connected to device {self.xicam.get_device_sn()}')

        self.xbinwidth  = xbinwidth
        self.xbinoffset = xbinoffset
        self.exposure   = exposure_ms # ms?
        self.gain       = 0

        self.xicam.set_width(self.xbinwidth)
        self.xicam.set_offsetX(self.xbinoffset)
        self.xicam.set_exposure_direct(1000*self.exposure)
        self.xicam.set_gain_direct(self.gain)

        # What other settings are there?, can we make these *args, **kwargs? and check
        # them using getattr()
        self.xicam.set_imgdataformat("XI_RAW16")
        self.xicam.set_output_bit_depth("XI_BPP_12")
        self.xicam.enable_output_bit_packing()
        self.xicam.disable_aeag() # what is this?

        self.xicam.set_binning_vertical(2)
        self.xicam.set_binning_vertical_mode("XI_BIN_MODE_SUM")

        self.rows, self.cols = self.xicam.get_height(), self.xicam.get_width()

        self.img = xiapi.Image()
        self.xicam.start_acquisition()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.xicam.stop_acquisition()
        self.xicam.close_device()

    @property
    def exposure(self) -> float: # or int?
        """Current exposure in ms."""
        return self.xicam.get_exposure() / 1000

    @exposure.setter
    def exposure(self, val):
        """Update exposure in ms."""
        self.xicam.set_exposure_direct(val * 1000)

    @property
    def gain(self) -> float: # or int?
        """Current exposure property in dB from 0 to 24 dB."""
        return self.xicam.get_gain()

    @gain.setter
    def gain(self, val):
        """Update gain in dB."""
        self.xicam.set_gain_direct(val)

    def get_img(self, n:int = 1) -> np.ndarray:
        """Take `n` images"""
        data = np.zeros((self.cols,self.rows,n), dtype = np.uint16)
        for i in range(n):
            self.xicam.get_image(self.img)
            data[...,i] = np.rot90(self.img.get_image_data_numpy(), -1)
        return data

    def take_show(self):
        """Grab a single image using `get_img` and plot it"""
        with OpenHSI(xbinwidth=896,xbinoffset=528,exposure_ms=1000,gain=0) as cam:
            img = cam.start().get_img()
            plt.imshow(img)
            plt.xlabel('Wavelength (nm)')
            plt.ylabel('Line pixels')
            plt.show()