# The Super Duper Script Editor 2

A script editor for _Super Danganronpa 2: So Long, Despair Academy_.

## DISCLAIMER

**This code is incomplete, and will not be of any use to the average user. It is _only_ provided for educational purposes, as a way to document the research we did on SDR2 before the translation project was canceled. This code is provided _completely unsupported_, and with no guarantees it will operate correctly.**

If you want to set up a workspace, check out the code in `extract/cpk.py`. If someone wants to take the reins on this and finish it up, you're more than welcome to fork the repo and have at it.

## Dependencies

### Primary dependencies

* Python 2.7
    * <http://www.python.org/download/>
    * Not the 64-bit version
* PyQt4
    * <http://www.riverbankcomputing.co.uk/software/pyqt/download>
* PyEnchant
    * <http://packages.python.org/pyenchant/download.html>
* Sony ATRAC3 Codec
    * <http://www.codecs.com/Sony_ATRAC3_Audio_Codec_download.htm>
    * Required to play voices.
* Java
    * <http://www.java.com>
    * Must be available on PATH on Windows

### Other dependencies

* mkisofs
    * Used to build the completed ISO.
    * A Windows binary is included in `tools`.
* pngquant
    * <http://pngquant.org/>
    * Used to quantize PNGs before converting them to GIM files.
    * A Windows binary is included in `tools`.

# Note:
   * You will need to download some required files to get this to work. Check "Releases", Download those files and place them in "data" folder.


## Licensing and legal stuff

The Super Duper Script Editor 2 is released under the GNU GPL, Version 3. A list of attributions can be found under `Help` -> `About` from within the editor.
