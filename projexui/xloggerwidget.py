#!/usr/bin/python

""" Creates a widget for monitoring logger information. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

### Modified by BlackDragonHunt for use in the Super Duper Script Editor, 2013

#------------------------------------------------------------------------------

import logging
import re
import weakref

from PyQt4 import QtCore
from PyQt4.QtCore import QMutex, QMutexLocker

from PyQt4.QtGui import QColor, QTextCharFormat, QTextEdit

from projexui.xcolorset import XColorSet

class XLoggerColorSet(XColorSet):
    def __init__( self, *args, **defaults ):
        super(XLoggerColorSet, self).__init__(*args, **defaults)
        
        self.setColorGroups(['Default'])
        
        self.setColor('Standard',     QColor('black'))
        self.setColor('Debug',        QColor('gray'))
        self.setColor('Info',         QColor('blue'))
        self.setColor('Warning',      QColor('orange').darker(150))
        self.setColor('Error',        QColor('darkRed'))
        self.setColor('Critical',     QColor('darkRed').lighter(150))
        self.setColor('Background',   QColor(250, 250, 250))
        self.setColor('String',       QColor('darkRed'))
        self.setColor('Number',       QColor('orange').darker(150))
        self.setColor('Comment',      QColor('green'))
        self.setColor('Keyword',      QColor('blue'))
    
    @staticmethod
    def lightScheme():
        return XLoggerColorSet()
    
    @staticmethod
    def darkScheme():
        out = XLoggerColorSet()
        out.setColor('Standard',    QColor('white'))
        out.setColor('Debug',       QColor(220, 220, 220))
        out.setColor('Info',        QColor('cyan'))
        out.setColor('Warning',     QColor('yellow'))
        out.setColor('Error',       QColor('red'))
        out.setColor('Critical',    QColor('darkRed').lighter(150))
        out.setColor('Background',  QColor(40, 40, 40))
        out.setColor('String',      QColor('orange'))
        out.setColor('Number',      QColor('red'))
        out.setColor('Comment',     QColor(140, 255, 140))
        out.setColor('Keyword',     QColor('cyan'))
        
        return out

# needed for save/load using the datatype system
# XLoggerColorSet.registerToDataTypes()

class XLoggerHandler(logging.Handler):
    """ Custom class for handling error exceptions via the logging system,
        based on the logging level. """
    
    def __init__( self, widget, showLevel = True, showDetails = True ):
        logging.Handler.__init__(self)
        
        self._widgetRef     = weakref.ref(widget)
        self._showLevel     = showLevel
        self._showDetails   = showDetails
        self._formatter     = logging.Formatter()
    
    def emit( self, record ):
        """ 
        Throws an error based on the information that the logger reported,
        given the logging level.
        
        :param      record | <logging.LogRecord>
        """
        widget = self.widget()
        if ( widget ):
            widget.pythonMessageLogged.emit(record.levelno, 
                                            self.format(record) + '\n')
    
    def format( self, record ):
        """
        Formats the inputed log record into a return string.
        
        :param      record | <logging.LogRecord>
        """
        format= []
        
        if ( self._showLevel ):
            format.append(u'[%(levelname)s ― %(name)s]')
        
        if ( self._showDetails ):
            # details = 'PATH: %(filename)s LINE: %(lineno)s'
            # if ( 'funcName' in dir(record) ):
                # details = 'FN: %(funcName)s ' + details
            
            # format.append(details + ' ---')
            format.append("Line %(lineno)s:")
        
        format.append('%(message)s')
        
        self._formatter._fmt = ' '.join(format)
        return self._formatter.format(record)
    
    def setShowDetails( self, state ):
        """
        Sets whether or not to show detail information for this handler.
        
        :param      state | <bool>
        """
        self._showDetails = state
    
    def setShowLevel( self, state ):
        """
        Sets whether or not to show level information for this handler.
        
        :param      state | <bool>
        """
        self._showLevel = state
    
    def showDetails( self ):
        """
        Returns whether or not to show details for this logger.
        
        :return     <bool>
        """
        return self._showDetails
    
    def showLevel( self ):
        """
        Return whether ornot to show level information for this handler.
        
        :return     <bool>
        """
        return self._showLevel
    
    def widget( self ):
        """
        Returns the widget that is linked to this handler.
        
        :return     <QWidget>
        """
        return self._widgetRef()

#------------------------------------------------------------------------------

class XLoggerWidget(QTextEdit):
    
    LoggingMap = {
        logging.DEBUG:    'debug',
        logging.INFO:     'info',
        logging.WARN:     'warning',
        logging.ERROR:    'error',
        logging.CRITICAL: 'critical',
    }
    
    messageLogged       = QtCore.pyqtSignal(int, unicode)
    pythonMessageLogged = QtCore.pyqtSignal(int, unicode)
        
    """ Defines the main logger widget class. """
    def __init__( self, parent ):
        super(XLoggerWidget, self).__init__(parent)
        
        # set standard properties
        self.setReadOnly(True)
        # self.setLineWrapMode(XLoggerWidget.NoWrap)
        
        # define custom properties
        self._logger        = None
        self._clearOnClose  = True
        self._handler       = XLoggerHandler(self, True)
        self._currentMode   = 'standard'
        self._blankCache    = ''
        self._mutex         = QMutex()
        
        # determine whether or not to use the light or dark configuration
        palette = self.palette()
        # base    = palette.color(palette.Base)
        # avg     = (base.red() + base.green() + base.blue()) / 3.0
        
        # if ( avg < 160 ):
            # colorSet = XLoggerColorSet.darkScheme()
        # else:
            # colorSet = XLoggerColorSet.lightScheme()
        colorSet = XLoggerColorSet.darkScheme()
        
        self._colorSet      = colorSet
        palette.setColor(palette.Text, colorSet.color('Standard'))
        palette.setColor(palette.Base, colorSet.color('Background'))
        self.setPalette(palette)
        
        # setup the levels
        self._loggingEnabled = {
            'debug':        True,
            'info':         True,
            'warning':      True,
            'error':        True,
            'critical':     True,
            'fatal':        True,
        }
        
        # create connections
        self.pythonMessageLogged.connect( self.log )
    
    def clearOnClose( self ):
        """
        Returns whether or not this widget should clear the link to its \
        logger when it closes.
        
        :return     <bool>
        """
        return self._clearOnClose
    
    def closeEvent( self, event ):
        """
        Clear the handler from the logger when this widget closes.
        
        :param      event | <QCloseEvent>
        """
        if ( self.clearOnClose() ):
            self.setLogger(None)
            
        super(XLoggerWidget, self).closeEvent(event)
    
    def color( self, key ):
        """
        Returns the color value for the given key for this console.
        
        :param      key | <unicode>
        
        :return     <QColor>
        """
        return self._colorSet.color(str(key).capitalize())
    
    def colorSet( self ):
        """
        Returns the colors used for this console.
        
        :return     <XLoggerColorSet>
        """
        return self._colorSet
    
    def critical( self, msg ):
        """
        Logs a critical message to the console.
        
        :param      msg | <unicode>
        """
        self.log('critical', msg)
    
    def currentMode( self ):
        """
        Returns the current mode that the console is in for coloring.
        
        :return     <unicode>
        """
        return self._currentMode
    
    def debug( self, msg ):
        """
        Inserts a debug message to the current system.
        
        :param      msg | <unicode>
        """
        self.log('debug', msg)
    
    def error( self, msg ):
        """
        Inserts an error message to the current system.
        
        :param      msg | <unicode>
        """
        self.log('error', msg)
    
    def fatal( self, msg ):
        """
        Logs a fatal message to the system.
        
        :param      msg | <unicode>
        """
        self.log('fatal', msg)
    
    def handler( self ):
        """
        Returns the logging handler that is linked to this widget.
        
        :return     <XLoggerHandler>
        """
        return self._handler
    
    def information( self, msg ):
        """
        Inserts an information message to the current system.
        
        :param      msg | <unicode>
        """
        self.log( 'info', msg )
    
    def isLoggingEnabled( self, level ):
        """
        Returns whether or not logging is enabled for the given level.
        
        :param      level | <int>
        """
        if ( type(level) == int ):
            level = self.LoggingMap.get(level, 'info')
            
        return self._loggingEnabled.get(level, True)
    
    def log( self, level, msg ):
        """
        Logs the inputed message with the given level.
        
        :param      level | <int> | logging level value
                    msg   | <unicode>
        
        :return     <bool> success
        """
        locker = QMutexLocker(self._mutex)
        
        if ( not self.isLoggingEnabled(level) ):
            return False
        
        if isinstance(msg, QtCore.QString):
          msg = unicode(msg.toUtf8(), "UTF-8")
        
        msg = self._blankCache + msg
        if msg.endswith('\n'):
            self._blankCache = '\n'
            msg = msg[:-1]
        else:
            self._blankCache = ''
        
        self.setCurrentMode(level)
        self.insertPlainText(msg)
        
        if not self.signalsBlocked():
            self.messageLogged.emit(level, msg)
        
        self.scrollToEnd()
        
        return True
    
    def logger( self ):
        """
        Returns the logger instance that this widget will monitor.
        
        :return     <logging.Logger>
        """
        return self._logger
    
    def scrollToEnd( self ):
        """
        Scrolls to the end for this console edit.
        """
        vsbar = self.verticalScrollBar()
        vsbar.setValue(vsbar.maximum())
        
        hbar = self.horizontalScrollBar()
        hbar.setValue(0)
    
    def setClearOnClose( self, state ):
        """
        Sets whether or not this widget should clear the logger link on close.
        
        :param      state | <bool>
        """
        self._clearOnClose = state
    
    def setColor( self, key, value ):
        """
        Sets the color value for the inputed color.
        
        :param      key     | <unicode>
                    value   | <QColor>
        """
        key = str(key).capitalize()
        self._colorSet.setColor(key, value)
        
        # update the palette information
        if ( key == 'Background' ):
            palette = self.palette()
            palette.setColor( palette.Base, value )
            self.setPalette(palette)
    
    def setColorSet( self, colorSet ):
        """
        Sets the colors for this console to the inputed collection.
        
        :param      colors | <XLoggerColorSet>
        """
        self._colorSet = colorSet
        
        # update the palette information
        palette = self.palette()
        palette.setColor( palette.Text, colorSet.color('Standard') )
        palette.setColor( palette.Base, colorSet.color('Background') )
        self.setPalette(palette)
    
    def setCurrentMode( self, mode ):
        """
        Sets the current color mode for this console to the inputed value.
        
        :param      mode | <unicode>
        """
        if ( type(mode) == int ):
            mode = self.LoggingMap.get(mode, 'standard')
            
        if ( mode == self._currentMode ):
            return
            
        self._currentMode = mode
        
        color = self.color(mode)
        if ( not color.isValid() ):
            return
            
        format = QTextCharFormat()
        format.setForeground( color )
        self.setCurrentCharFormat( format )
    
    def setLoggingEnabled( self, level, state ):
        """
        Sets whether or not this widget should log the inputed level amount.
        
        :param      level | <int>
                    state | <bool>
        """
        if ( type(level) == int ):
            level = self.LoggingMap.get(level, 'standard')
            
        self._loggingEnabled[level] = state
        
    def setLogger( self, logger ):
        """
        Sets the logger instance that this widget will monitor.
        
        :param      logger  | <logging.Logger>
        """
        if ( self._logger == logger ):
            return
        
        if ( self._logger ):
            self._logger.removeHandler(self._handler)
        
        self._logger = logger
        
        if ( logger ):
            logger.addHandler(self._handler)
    
    def setShowDetails( self, state ):
        """
        Sets whether or not the level should be logged with the message in the \
        output.
        
        :param      state | <bool>
        """
        self._handler.setShowDetails(state)
        
    def setShowLevel( self, state ):
        """
        Sets whether or not the level should be logged with the message in the \
        output.
        
        :param      state | <bool>
        """
        self._handler.setShowLevel(state)
        
    def showDetails( self ):
        """
        Returns whether or not to show details for this logger.
        
        :return     <bool>
        """
        return self._handler.showDetails()
        
    def showLevel( self ):
        """
        Returns whether or not this logger should output the level when a \
        message is printed.
        
        :return     <bool>
        """
        return self._handler.showLevel()
    
    def warning( self, msg ):
        """
        Logs a warning message to the system.
        
        :param      msg | <unicode>
        """
        self.log('warning', msg)

__designer_plugins__ = [XLoggerWidget]