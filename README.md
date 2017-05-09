# imagey - ImageJ with CPython REPL

Note that this requires the imagey branch of imglyb, currently.

![Matplotlib inline plot from ImagePlus](https://gist.githubusercontent.com/hanslovsky/4e0ec6dbb64d01186ac7f9f2a942257c/raw/79d7789172afb128ca913b207e89b59e04291814/imagej-qtconsole.png)

![IPython code completion](https://gist.githubusercontent.com/hanslovsky/4e0ec6dbb64d01186ac7f9f2a942257c/raw/79d7789172afb128ca913b207e89b59e04291814/imagej-qtconsole-autocomplete.png)

## Dependencies
 - PyJNIus
 - imglyb
 - PyQt5
 - QtConsole
 
## Run
```bash
python /path/to/imagey/imagey/imagey.py [-j '<java options>'] /path/to/Fiji.app
```
To start the CPython repl, navigate the Fiji menu to
```
Plugins > Scripting > CPython REPL
```
