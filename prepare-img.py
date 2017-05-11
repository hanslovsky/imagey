import imglyb
from imglyb import util

from jnius import autoclass

from imglyb.imglib_ndarray import ImgLibReferenceGuard

Factory = autoclass( 'net/imglib2/python/ArrayImgWithUnsafeStoreFactory'.replace( '/', '.' ) )
factory = cast( 'net.imglib2.img.ImgFactory', Factory() )
ImgOpener = autoclass( 'io.scif.img.ImgOpener' )
opener = ImgOpener( ij.getContext() )
url = 'http://www.nerdtests.com/mq/testimages/167138_4f49b66c0cb4a87cc906.jpg'
img = opener.openImgs( url, factory ).get( 0 )
display = ij.display()
d = display.createDisplay( 'unsafe', img )
ndarray = ImgLibReferenceGuard( img.getImg() )

