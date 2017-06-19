import glob
import numpy as np
import os
import re
import subprocess
import sys
import time

from collections import defaultdict

from PyQt5 import QtGui, QtCore, QtWidgets
from qtconsole.rich_ipython_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager

class ResetVariablesDialog( QtWidgets.QWidget ):
	def __init__( self, parent, kernel, **variables ):
		super( ResetVariablesDialog, self ).__init__( parent )
		self.kernel = kernel
		self.variables = variables

		self.layout = QtWidgets.QGridLayout()

		self.checkbox_group = QtWidgets.QGroupBox( 'Reset variables' )
		self.checkbox_layout = QtWidgets.QGridLayout()
		self.checkbox_group.setFlat( True )

		num_rows = int( np.floor( np.sqrt( len( variables ) ) ) )
		num_cols = int( np.floor( len( variables ) * 1.0 / num_rows ) ) # Why floor?

		self.checkboxes = [ QtWidgets.QCheckBox( k ) for k, v in self.variables.items() ]
		for idx, box in enumerate( self.checkboxes ):
			box.setChecked( True )
			self.checkbox_layout.addWidget( box, idx / num_rows, idx % num_cols )

		self.checkbox_group.setLayout( self.checkbox_layout )
		self.layout.addWidget( self.checkbox_group, 0, 0 )

		self.button_group = QtWidgets.QGroupBox( '' )
		self.button_layout = QtWidgets.QHBoxLayout()
		self.button_group.setFlat( True )

		self.ok_button = QtWidgets.QPushButton( "&Push selection" )
		def push_variables_and_close( kernel, variables, checkboxes ):
			pushable_variables = {
				box.text().replace( '&', '' ) : variables[ box.text().replace( '&', '' ) ] for box in checkboxes if box.isChecked()
				}
			kernel.shell.push( pushable_variables )
			self.close()
		self.ok_button.clicked.connect( lambda : push_variables_and_close( self.kernel, self.variables, self.checkboxes ) )

		self.cancel_button = QtWidgets.QPushButton( "&Cancel" )
		self.cancel_button.clicked.connect( self.close )

		self.button_layout.addWidget( self.ok_button )
		self.button_layout.addWidget( self.cancel_button )
		self.button_group.setLayout( self.button_layout )
		self.layout.addWidget( self.button_group, 1, 0 )

		self.setLayout( self.layout )

class IPythonWidget( QtWidgets.QWidget ):
	def __init__( self, parent, kernel_manager, kernel_client, kernel, **reserved_variables ):
		super( IPythonWidget, self ).__init__( parent )
		self.layout = QtWidgets.QHBoxLayout( self )
		self.kernel_manager = kernel_manager
		self.kernel_client = kernel_client
		self.kernel = kernel
		self.reserved_variables = reserved_variables
		self.current_widget = RichJupyterWidget( parent = self )
		self.current_widget.kernel_manager = kernel_manager
		self.layout.addWidget( self.current_widget )
		self.layout.setContentsMargins( 0, 0, 0, 0 )

		try:
			self.current_widget.kernel_client = kernel_client
		except Exception as e:
			print( e )
			raise e
		self.geometry_memory = self.geometry()
		self.was_hiding = False

		self.kernel.shell.push( self.reserved_variables )

		self.push_action = QtWidgets.QAction(
			"Push variables",
			self,
			shortcut="Ctrl+p",
			shortcutContext=QtCore.Qt.WidgetWithChildrenShortcut,
			statusTip="Restore the Normal font size",
			triggered=lambda : ResetVariablesDialog( None, self.kernel, **self.reserved_variables ).show() )
		self.addAction( self.push_action )

	def closeEvent( self, event ):
		toggleShow = False
		self.geometry_memory = self.geometry()
		self.current_widget.hide()
		self.hide()
		self.was_hiding = True

	def showEvent( self, event ):
		# self.kernel.shell.push( self.reserved_variables )
		self.setVisible( True )
		self.current_widget.show()
		self.activateWindow()
		self.raise_()
		if self.was_hiding:
			self.setGeometry( self.geometry_memory )
			self.was_hiding = False

	def add_more_variables( self,  **variables ):
		self.reserved_variables.update( variables )
		self.kernel.shell.push( variables )



if __name__ == "__main__":

	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument( 'fiji_dir', metavar='FIJI_DIR', nargs=1, help='Fiji app directory containings plugins and jars directories.' )
	parser.add_argument( '--java-opts', '-j', required=False, default='' )
	parser.add_argument( '--ij-opts', '-i', required=False, default='' )

	args = parser.parse_args()

	from jnius_config import split_char
	
	FIJI_JARS_DIR= '{}/jars'.format( args.fiji_dir[ 0 ] )
	FIJI_PLUGIN_DIR = '{}/plugins'.format( args.fiji_dir[ 0 ] )
	FIJI_JARS_BIOFORMATS_DIR = '{}/bio-formats'.format( FIJI_JARS_DIR )

	try:
		JAVA_HOME = os.environ[ 'JAVA_HOME' ]
	except KeyError as e:
		print( 'JAVA_HOME not in environment' )
		raise e

	javac = '{}/bin/javac'.format( JAVA_HOME )
	           
	match_string = r'(imglib2-([0-9]|algorithm-[0-9])|bigdataviewer|imagej-legacy)'
	matcher = re.compile( match_string )
	           
	libs = [ jar for jar in sorted( glob.glob( '{}/*.jar'.format( FIJI_JARS_DIR ) ) ) if not matcher.search( jar ) ]
	plugin_jars = [ jar for jar in sorted( glob.glob( '{}/*.jar'.format( FIJI_PLUGIN_DIR ) ) ) if not matcher.search( jar ) ]
	bioformats_jars = [ jar for jar in sorted( glob.glob( '{}/*.jar'.format( FIJI_JARS_BIOFORMATS_DIR ) ) ) if not matcher.search( jar ) ]

	
	           
	jars = libs + plugin_jars + bioformats_jars
	           
	if 'CLASSPATH' in os.environ:
		os.environ['CLASSPATH'] = split_char.join( jars + os.environ['CLASSPATH'].split( split_char ) )
	else:      
		os.environ['CLASSPATH'] = split_char.join( jars )
	           
	os.environ['JVM_OPTIONS'] = '{}{}'.format( 
		' '.join( [ '-Dplugins.dir={}'.format( FIJI_PLUGIN_DIR ), '-Dpython.cachedir.skip=true' ] ),
		'' if len( args.java_opts ) == 0 else ' {}'.format( args.java_opts )
		)

	print ( "JVM OPTIONS", os.environ[ 'JVM_OPTIONS' ] )

	ij_arguments = [] if len( args.ij_opts ) == 0 else args.ij_opts.split(' ')

	import imglyb
	import jnius_config

	from imglyb import util, types
	from jnius import autoclass, cast, PythonJavaClass, java_method
	
	class Runnable( PythonJavaClass ):

		__javainterfaces__ = [ 'java/lang/Runnable' ]

		def __init__( self, r ):
			super( Runnable, self ).__init__()
			self.r = r

		@java_method( '()V' )
		def run( self ):
			self.r()
	           
	           
	kernel_manager = QtInProcessKernelManager()
	kernel_manager.start_kernel()
	kernel = kernel_manager.kernel
	kernel.gui = 'qt'
	           
	kernel_client = kernel_manager.client()
	kernel_client.start_channels()

	           
	app = QtWidgets.QApplication([])
	app.setQuitOnLastWindowClosed( False )

	
	reserved_variables = dict (
		np=np,
		imglyb=imglyb,
		util=util,
		types=types,
		autoclass=autoclass,
		cast=cast,
		java_method=java_method,
		PythonJavaClass=PythonJavaClass,
		jnius_config=jnius_config
		)

	widget = IPythonWidget( None, kernel_manager, kernel_client, kernel, **reserved_variables )
	widget.setWindowTitle( "IPYTHOOOOON" )
	           
	def run_on_start():
		print( 'single shot in event loop' )
		ImageJ2 = autoclass( 'net.imagej.ImageJ' )
		CommandInfo = autoclass( 'org.scijava.command.CommandInfo' )
		MenuPath = autoclass( 'org.scijava.MenuPath' )
		ij = ImageJ2()

		Factory = autoclass( 'net/imglib2/python/ArrayImgWithUnsafeStoreFactory'.replace( '/', '.' ) )
		factory = cast( 'net.imglib2.img.ImgFactory', Factory() )
		ImgOpener = autoclass( 'io.scif.img.ImgOpener' )
		opener = ImgOpener( ij.getContext() )
		display = ij.display()

		PythonCommandInfo = autoclass( 'net.imglib2.python.PythonCommandInfo' )
		RunnableCommand = autoclass( 'net.imglib2.python.PythonCommandInfo$RunnableCommand' )
		runnable = Runnable( lambda : QtWidgets.QApplication.postEvent( widget, QtGui.QShowEvent() ) )
		command = RunnableCommand( runnable )
		command_info = PythonCommandInfo( command )

		command_info.setMenuPath( MenuPath( "Plugins>Scripting>CPython REPL" ) )
		ij.module().addModule( command_info )



		def open_imgs( path ):
			"""Open all images at location specified by path.

			Parameters
			----------
			path : str
			Location of images.
			"""
			return opener.openImgs( path, factory )

		def open_img( path ):
			"""Open one image at location specified by path.

			Parameters
			----------
			path : str
			Location of image.
			"""
			return open_imgs( path ).get( 0 )

		def show_img( img, title='' ):
			"""Show image using DisplayService of current ImageJ instance.

			Parameters
			----------
			img : numpy.ndarray or net.imglib2.RandomAccessibleInterval
			Image to be displayed.
			title : str
			Title of display.
			"""
			return display.createDisplay( title, imglyb.to_imglib( img ) if isinstance( img, ( np.ndarray, ) ) else img )

		widget.add_more_variables( ij=ij, factory=factory, opener=opener, display=display, open_imgs=open_imgs, open_img=open_img, show_img=show_img )

		ij.launch()
		

	QtCore.QTimer.singleShot( 0, run_on_start )

	print ( "Entering qt event loop" )
	app.exec_()

