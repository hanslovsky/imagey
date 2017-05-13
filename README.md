# imagey - ImageJ with CPython REPL

This uses ImageJ2 because shared memory would not be possible with ImageJ1 `ImageProcessor` data structures.

![Matplotlib inline plot from ImagePlus](https://gist.githubusercontent.com/hanslovsky/4e0ec6dbb64d01186ac7f9f2a942257c/raw/f8f97fa0981503815b195efd8f64874228eda992/imagey.png)

![IPython code completion](https://gist.githubusercontent.com/hanslovsky/4e0ec6dbb64d01186ac7f9f2a942257c/raw/79d7789172afb128ca913b207e89b59e04291814/imagej-qtconsole-autocomplete.png)

## Dependencies
 - [imglyb](https://github.com/hanslovsky/imglib2-imglyb)
   - Follow build instructions, or
   - install from conda: `conda install -c hanslovsky imglib2-imglyb`
 - [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro)
   - Install through your package manager, or
   - `pip install pyqt5`
 - [QtConsole](https://github.com/jupyter/qtconsole)
   - Install through your package manager, or
   - `pip install qtconsole`

## Run
```bash
python /path/to/imagey/imagey/imagey.py [-j '<java options>'] /path/to/Fiji.app
```
To start the CPython repl, navigate the Fiji menu to
```
Plugins > Scripting > CPython REPL
```
