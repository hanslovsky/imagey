# imagey - ImageJ with CPython REPL

This uses ImageJ2 because shared memory would not be possible with ImageJ1 `ImageProcessor` data structures.

![Matplotlib inline plot from ImagePlus](https://gist.githubusercontent.com/hanslovsky/4e0ec6dbb64d01186ac7f9f2a942257c/raw/f8f97fa0981503815b195efd8f64874228eda992/imagey.png)

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
 - [Fiji](https://fiji.sc)
   - Download Fiji and run `Update...`
   - Add (http://sites.imagej.net/Hanslovsky/) to update sites and update `scifio.jar`.

## Run
```bash
python /path/to/imagey/imagey/imagey.py [-j '<java options>'] /path/to/Fiji.app
```
Switch to modern mode:
```
Help>Switch to Modern Mode
```
To start the CPython repl, navigate the Fiji menu to
```
Plugins>Scripting>CPython REPL
```

For conevenience, these variables are exposed to the IPython interpretor:

| Variable          | Description                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------- |
| `ij`              | `ImageJ` instance                                                                           |
| `factory`         | `ImgFactory` instance for numpy convertibale `Img`                                          |
| `opener`          | `ImgOpener` instance                                                                        |
| `display`         | `DisplayService` used by active `ImageJ` instance                                           |
| `open_imgs`       | Open all images at path through `ImgOpener`                                                 |
| `open_img`        | Open image at path through `ImgOpener`                                                      |
| `show_img`        | Show image (`numpy` or `imglib2`) through `DisplayService` used by active `ImageJ` instance |
| `imglyb`          | `imglib2-imglyb` module                                                                     |
| `util`            | `imglyb.util`                                                                               |
| `types`           | `imglyb.types`                                                                              |
| `np`              | `numpy` package                                                                             |
| `autoclass`       | `jnius.autoclass`                                                                           |
| `cast`            | `jnius.cast`                                                                                |
| `java_method`     | `jnius.java_method`                                                                         |
| `PythonJavaClass` | `jnius.PythonJavaClass`                                                                     |
| `jnius_config`    | config module for `jnius`                                                                   |

These keyboard shortcuts are available:

| Shortcut | Action                   |
| -------- | ------------------------ |
| C-+      | Increase font size       |
| C--      | Decrease font size       |
| C-0      | Reset font size          |
| C-p      | Reload initial variables |
