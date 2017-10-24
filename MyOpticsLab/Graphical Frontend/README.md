# Python module for [Ocean Optics](http://www.oceanoptics.com/) spectrometers

[![Github All Releases](https://img.shields.io/github/downloads/ap--/python-seabreeze/total.svg?style=flat-square)](https://github.com/ap--/python-seabreeze/releases)
[![GitHub issues](https://img.shields.io/github/issues/ap--/python-seabreeze.svg?style=flat-square)](https://github.com/ap--/python-seabreeze/issues)

This Graphical frontend is based on [python-seabreeze](https://github.com/ap--/python-seabreeze) and [PyQtGraph](https://github.com/pyqtgraph/pyqtgraph) and was designed with the open source version of [Qt designer](https://info.qt.io/download-qt-for-application-development).

## Usage

Just run MyLabOptica_Qt.py using python3: 
```
python3 Directory_containing/MyLabOptica_Qt.py
```


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





