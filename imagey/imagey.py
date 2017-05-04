import glob
import os
import re
import subprocess
import sys
import time

from collections import defaultdict

from PyQt5 import QtGui, QtCore, QtWidgets
from qtconsole.rich_ipython_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager

class IPythonWidget( QtWidgets.QWidget ):
	def __init__( self, parent, kernel_manager, kernel_client, kernel ):
		super( IPythonWidget, self ).__init__( parent )
		self.layout = QtWidgets.QHBoxLayout( self )
		self.kernel_manager = kernel_manager
		self.kernel_client = kernel_client
		self.kernel = kernel
		self.current_widget = RichJupyterWidget( parent = self )
		self.current_widget.kernel_manager = kernel_manager
		self.layout.addWidget( self.current_widget )
		ipython_widget = self.current_widget
		self.kernel.shell.push({'widget':ipython_widget,'kernel':self.kernel, 'parent':self})
		self.layout.setContentsMargins( 0, 0, 0, 0 )
		try:
			self.current_widget.kernel_client = kernel_client
		except Exception as e:
			print( e )
			raise e
		self.geometry_memory = self.geometry()
		self.was_hiding = False

	def closeEvent( self, event ):
		toggleShow = False
		self.geometry_memory = self.geometry()
		self.current_widget.hide()
		self.hide()
		self.was_hiding = True

	def showEvent( self, event ):
		self.setVisible( True )
		self.current_widget.show()
		self.activateWindow()
		self.raise_()
		if self.was_hiding:
			self.setGeometry( self.geometry_memory )
			self.was_hiding = False


if __name__ == "__main__":

	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument( 'fiji_dir', metavar='FIJI_DIR', nargs=1, help='Fiji app directory containings plugins and jars directories.' )
	parser.add_argument( '--java-opts', '-j', required=False, default='' )
	parser.add_argument( '--ij-opts', '-i', required=False, default='' )

	args = parser.parse_args()
	
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

	pth = '/home/phil/local/tmp'
	jars += [ pth ]

	           
	           
	if 'CLASSPATH' in os.environ:
		os.environ['CLASSPATH'] = ':'.join( jars + os.environ['CLASSPATH'].split(':') )
	else:      
		os.environ['CLASSPATH'] = ':'.join( jars )
	           
	os.environ['JVM_OPTIONS'] = '{}{}'.format( 
		' '.join( [ '-Dplugins.dir={}'.format( FIJI_PLUGIN_DIR ), '-Dpython.cachedir.skip=true' ] ),
		'' if len( args.java_opts ) == 0 else ' {}'.format( args.java_opts )
		)

	print ( "JVM OPTIONS", os.environ[ 'JVM_OPTIONS' ] )

	ij_arguments = [] if len( args.ij_opts ) == 0 else args.ij_opts.split(' ')

	import imglyb
	from imglyb import util
	from jnius import autoclass, cast, PythonJavaClass, java_method
	
	class Command( PythonJavaClass ):

		__javainterfaces__ = [ 'org/scijava/command/Command' ]

		def __init__( self, command ):
			super( Command, self ).__init__()
			self.command = command

		@java_method( '()V' )
		def run( self ):
			self.command()
	           
	           
	kernel_manager = QtInProcessKernelManager()
	kernel_manager.start_kernel()
	kernel = kernel_manager.kernel
	kernel.gui = 'qt'
	           
	kernel_client = kernel_manager.client()
	kernel_client.start_channels()
	           
	app = QtWidgets.QApplication([])
	app.setQuitOnLastWindowClosed( False )
	widget = IPythonWidget( None, kernel_manager, kernel_client, kernel )
	widget.setWindowTitle( "IPYTHOOOOON" )
	           
	PythonCommandInfo = autoclass( 'net.imglib2.python.PythonCommandInfo' )
	command = Command( lambda : QtWidgets.QApplication.postEvent( widget, QtGui.QShowEvent() ) )
	command_info = PythonCommandInfo( 'ToggleQTConsoleWrapper', command )

	ImageJ = autoclass( 'ij.ImageJ' )
	ImageJ2 = autoclass( 'net.imagej.ImageJ' )
	CommandInfo = autoclass( 'org.scijava.command.CommandInfo' )
	MenuPath = autoclass( 'org.scijava.MenuPath' )

	ij2 = ImageJ2()

	kernel.shell.push( {'ij2' : ij2 } )

	command_info.setMenuPath( MenuPath( "Plugins>Scripting>CPython REPL" ) )
	ij2.module().addModule( command_info )

	ij2.launch()
	           
	app.exec_()

