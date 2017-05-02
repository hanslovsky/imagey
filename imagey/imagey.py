import glob
import os
import re
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

	def closeEvent( self, event ):
		toggleShow = False
		self.geometry_memory = self.geometry()
		self.current_widget.hide()
		self.hide()

	def showEvent( self, event ):
		self.setVisible( True )
		self.current_widget.show()
		self.activateWindow()
		self.raise_()
		self.setGeometry( self.geometry_memory )

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
	           
	match_string = r'(imglib2-([0-9]|algorithm-[0-9])|bigdataviewer|imagej-legacy)'
	matcher = re.compile( match_string )
	           
	libs = [ jar for jar in sorted( glob.glob( '{}/*.jar'.format( FIJI_JARS_DIR ) ) ) if not matcher.search( jar ) ]
	plugin_jars = [ jar for jar in sorted( glob.glob( '{}/*.jar'.format( FIJI_PLUGIN_DIR ) ) ) if not matcher.search( jar ) ]
	bioformats_jars = [ jar for jar in sorted( glob.glob( '{}/*.jar'.format( FIJI_JARS_BIOFORMATS_DIR ) ) ) if not matcher.search( jar ) ]
	           
	jars = libs + plugin_jars + bioformats_jars
	           
	           
	if 'CLASSPATH' in os.environ:
		os.environ['CLASSPATH'] = ':'.join( jars + os.environ['CLASSPATH'].split(':') )
	else:      
		os.environ['CLASSPATH'] = ':'.join( jars )
	           
	os.environ['JVM_OPTIONS'] = '{} {}'.format( 
		' '.join( [ '-Dplugins.dir={}'.format( FIJI_PLUGIN_DIR ), '-Dpython.cachedir.skip=true' ] ),
		args.java_opts
		)

	ij_arguments = [] if len( args.ij_opts ) == 0 else args.ij_opts.split(' ')

	
	# import jnius_config
	
	# PYJNIUS_JAR_STR = 'PYJNIUS_JAR'

	# try:
	# 	PYJNIUS_JAR=os.environ[ PYJNIUS_JAR_STR ]
	# except KeyError as e:
	# 	print( "Path to pyjnius.jar not defined! Use environment variable {} to define it.".format( PYJNIUS_JAR_STR ) )
	# 	raise e

	# jnius_config.add_classpath( PYJNIUS_JAR )
	# CLASSPATH_STR='CLASSPATH'
	# if CLASSPATH_STR in os.environ:
	# 	for path in os.environ[ CLASSPATH_STR ].split( jnius_config.split_char ):
	# 		jnius_config.add_classpath( path )

	# jnius_config.add_options( *os.environ[ 'JVM_OPTIONS' ].split(' ') )

	import imglyb
	from imglyb import util
	from jnius import autoclass, cast, PythonJavaClass, java_method
	           
	class ActionListener( PythonJavaClass ):
	           
		__javainterfaces__ = [ 'java/awt/event/ActionListener' ]
		       
		def __init__( self, func ):
			super( ActionListener, self ).__init__()
			self.func = func
	           
		@java_method('(Ljava/awt/event/ActionEvent;)V')
		def actionPerformed( self, e ):
			try:
			    self.func( e )
			except Exception as e:
			    print (e)
			    raise e
	           
	class WindowListener( PythonJavaClass ):
	           
		__javainterfaces__ = [ 'java/awt/event/WindowListener' ]
	           
		def __init__( self, func_dic ):
			super( WindowListener, self ).__init__()
			self.func_dict = func_dict
	           
		@java_method( '(Ljava/awt/event/WindowEvent;)V' )
		def windowActivated( self, event ):
			self.func_dict[ 'activated' ]( event )
	           
		@java_method( '(Ljava/awt/event/WindowEvent;)V' )
		def windowClosed( self, event ):
			self.func_dict[ 'closed' ]( event )
	           
		@java_method( '(Ljava/awt/event/WindowEvent;)V' )
		def windowClosing( self, event ):
			self.func_dict[ 'closing' ]( event )
	           
		@java_method( '(Ljava/awt/event/WindowEvent;)V' )
		def windowDeactivated( self, event ):
			self.func_dict[ 'deactivated' ]( event )
	           
		@java_method( '(Ljava/awt/event/WindowEvent;)V' )
		def windowDeiconified( self, event ):
			self.func_dict[ 'deiconified' ]( event )
	           
		@java_method( '(Ljava/awt/event/WindowEvent;)V' )
		def windowIconified( self, event ):
			self.func_dict[ 'iconified' ]( event )
	           
		@java_method( '(Ljava/awt/event/WindowEvent;)V' )
		def windowOpened( self, event ):
			self.func_dict[ 'opened' ]( event )

			
	class PythonRunnable( PythonJavaClass ):

		__javainterfaces__ = [ 'java/lang/Runnable' ]

		def __init__( self, command ):
			super( PythonRunnable, self ).__init__()
			self.command = command

		@java_method( '()V' )
		def run( self ):
			self.command()



			
	PythonCommand = autoclass( 'net.imglib2.python.PythonCommand' )
	pr = PythonRunnable( lambda : print( "I am a command!" ) )
	pr.run()
	dummy_command = PythonCommand( pr )

	# class PythonModuleInfo( PythonJavaClass ):
	ImageJ = autoclass( 'ij.ImageJ' )
	ImageJ2 = autoclass( 'net.imagej.ImageJ' )
	CommandInfo = autoclass( 'org.scijava.command.CommandInfo' )
	MenuPath = autoclass( 'org.scijava.MenuPath' )
	ij2 = ImageJ2()

	# command_info = CommandInfo( cast( util.Helpers.className( dummy_command ), dummy_command ).getClass() )
	print( 'cls name', util.Helpers.className( dummy_command) )
	command_info = CommandInfo( 'net.imglib2.python.PythonCommand' ) # util.Helpers.className( dummy_command ) )
	command_info.setMenuPath( MenuPath( "Plugins>Scripting>CPython REPL" ) )
	ij2.module().addModule( command_info )
	
	ij2.launch()# ij_arguments )

	def get_or_add_menu( root_menu, name ):
		children_list = root_menu.getChildren()
		children = [ children_list.get( i ) for i in range( children_list.size() ) if children_list.get( i ).getName() == name ]
		return None if len( children ) == 0 else children[ 0 ]
	
	# Menu = autoclass( 'java.awt.Menu' )
	# MenuItem = autoclass( 'java.awt.MenuItem' )
	# ij = ImageJ()
	# title = 'ImageY'
	window_service = ij2.window()
	main_menu = window_service.getMenuService().getMenu()
	plugins_menu = get_or_add_menu( main_menu, 'Plugins' )
	scripting_menu = get_or_add_menu( plugins_menu, 'Scripting' )
	# print( scripting_menu.getMenuPath() )
	
	# ij.setTitle( title )
	# menu_bar = ij.getMenuBar()
	# menu_count = menu_bar.getMenuCount()
	# menu_name = 'Plugins'
	# scripting_name = 'Scripting'
	# menus = [ menu_bar.getMenu( i ) for i in range( menu_count ) if menu_name == menu_bar.getMenu( i ).getLabel() ]
	# menu = menus[ 0 ] if len( menus ) > 0 else menu_bar.add( Menu( menu_name ) )
	# items = [ menu.getItem( i ) for i in range( menu.getItemCount() ) if scripting_name == menu.getItem( i ).getLabel() ]
	# created = Menu( scripting_name )
	           
	# sub_menu = cast( 'java.awt.Menu', items[0] if len(items) > 0 else menu.add( cast( 'java.awt.MenuItem', Menu( scripting_name ) ) ) )
	# cpython_entry = sub_menu.add( MenuItem( "CPython REPL" ) )
	           
	           
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
	           
	# listener = ActionListener( lambda e : QtWidgets.QApplication.postEvent( widget, QtGui.QShowEvent() ) )
	# cpython_entry.addActionListener( listener )
	           
	# func_dict = defaultdict( lambda : lambda event : None )
	# func_dict[ 'closed' ] = lambda event : app.quit()
	           
	# hook = WindowListener( func_dict )
	           
	# ij.addWindowListener( hook )
	           
	app.exec_()

