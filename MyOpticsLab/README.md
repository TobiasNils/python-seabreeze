# Python modules for unified laboratory device control

[![Github All Releases](https://img.shields.io/github/downloads/ap--/python-seabreeze/total.svg?style=flat-square)](https://github.com/ap--/python-seabreeze/releases)
[![GitHub issues](https://img.shields.io/github/issues/ap--/python-seabreeze.svg?style=flat-square)](https://github.com/ap--/python-seabreeze/issues)

These python classes make use of [python-seabreeze](https://github.com/ap--/python-seabreeze) to control [Ocean Optics](http://www.oceanoptics.com/) spectrometers and implement an adapted version of [Micos.py](https://gist.github.com/pklaus/3955382) to control the [Corvus Eco](https://www.physikinstrumente.com/en/products/controllers-and-drivers/motion-controllers-for-motor-screw-drives/smc-corvus-eco-smc-series-1204800/) microstep-controller system by [PI|Micos](https://www.physikinstrumente.com/en/) with the aim to create a unified platform for laboratory use. 

## Usage

Recommended use is via the [Spyder-IDE](https://github.com/spyder-ide) using python3.x

After executing MyOpticsLab.py with
```
>>> runfile(MyOpticsLab.py)
```
by default an animated Graph should pop up to give visual feedback of spectra registered by up to two Ocean Optics devices connected, which are iniciated as "sp" or "sp1" and "sp2", respectively. 
Running
```
>>> help(MyOpticsLab)
```
and 
```
>>> help(MySpectrometer)
```
should give you an overview of the functions already defined, among them e.g.: 
```
>>> sp.light_on()
>>> sp.light_off()
```
triggers the serial out of the spectrometer initiated as "sp", which in essence gives you control over a ~ 5V output between the serial pins "GND_SIGNAL" and "LampEnable" (compare with the datasheet of your Ocean Optics device). This works to control Ocean Optics Lamps via their TTL implementation as well as for other lightsources (e.g. LEDs, wired directly with an appropriate resistance in place).   


## Supported Devices

| Spectrometer | cseabreeze | 
|:-------------|:----------:|
| HR4000       |     x      |
| MAYA2000     |     x      | 
| MAYA2000PRO  |     x      | 
| NIRQUEST256  |     x      | 
| NIRQUEST512  |     x      |
| QE65000      |     x      |
| QE-PRO       |     x      | 
| USB2000      |     x      | 
| USB2000PLUS  |     x      | 
| Flame        |     x      |


## Known Issues

- No conda packages for armv6 (RPI version 1) [Issue #46](https://github.com/ap--/python-seabreeze/issues/46)

## Contributing Guidelines

If you run into any problems, file an issue and be sure to include the
following in your report:

- Operating system (Linux distribution, Windows version, OSX version) and
  archictecture (32bit, 64bit, arm)
- Python version and arch (i.e. Python 2.7.10 64bit)
- python-seabreeze version

If you want a feature implemented, please file an issue, or create a pull
request when you implement it yourself. And if you would like to support me via
paypal, click on the paypal donate button on top of this README.

 
## License

Files in this repository are released under the [MIT license](LICENSE.md).


## Related Repositories

If you want me to add your project here, let me know. Happy to add it.

- [SeaBreeze](https://sourceforge.net/projects/seabreeze/) - Ocean Optics' SeaBreeze C library.
- [libseabreeze](https://github.com/ap--/libseabreeze) - github clone of the C library. _internal use only_ (has pre-built libraries if you know what you're doing)
- [python-seabreeze-feedstock](https://github.com/ap--/python-seabreeze) - anaconda feedstock for automated package deployment. _internal use only_





