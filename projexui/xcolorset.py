#!/usr/bin/python

""" Defines a color set that will be used to define color relationships. """

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

from PyQt4.QtGui import QColor, QPalette

class XColorSet(object):
    def __init__( self, *args, **defaults ):
        # load another color set
        if ( args and isinstance(args[0], XColorSet) ):
            self._name        = args[0]._name
            self._colors      = args[0]._colors.copy()
            self._colorGroups = args[0]._colorGroups
        else:
            self._name        = defaults.get('name',        'Colors')
            self._colorGroups = defaults.get('colorGroups', ['Default'])
            self._colors      = {}
        
    def color( self, name, colorGroup = None ):
        """
        Returns the color for the given name at the inputed group.  If no \
        group is specified, the first group in the list is used.
        
        :param      name        | <str>
                    colorGroup  | <str> || None
            
        :return     <QColor>
        """
        if ( not colorGroup and self._colorGroups ):
            colorGroup = self._colorGroups[0]
        
        if ( not colorGroup ):
            return QColor()
        
        return self._colors.get(str(name), {}).get(str(colorGroup), QColor())
    
    def colors( self, name ):
        """
        Returns all the colors in order for the inputed color name.
        
        :return     [<QColor>, ..]
        """
        output = []
        colors = self._colors.get(name, {})
        for colorType in self._colorGroups:
            output.append(colors.get(colorType, QColor()))
        return output
    
    def colorGroups( self ):
        """
        Returns the list of color groups that are used for this set.
        
        :return     [<str>, ..]
        """
        return self._colorGroups[:]
    
    def colorNames( self ):
        """
        Returns a list of all the color names that are used for this set.
        
        :return     [<str>, ..]
        """
        return sorted(self._colors.keys())
    
    def name( self ):
        """
        Returns the name of this particular color set instance.
        
        :return     <str>
        """
        return self._name
    
    def setColor( self, name, color, colorGroup = None ):
        """
        Sets the color for the inputed name in the given color group.  If no \
        specific color group is found then the color will be set for all \
        color groups.
        
        :param      name        | <str>
                    color       | <QColor>
                    colorGroup  | <str> || None
        """
        self._colors.setdefault(str(name), {})
        cmap = self._colors.get(str(name))
        
        if ( not colorGroup ):
            for colorGroup in self._colorGroups:
                cmap[colorGroup] = color
        else:
            cmap[colorGroup] = color
    
    def setColorGroups( self, colorGroups ):
        """
        Defines the different color groups that can be used to work with \
        the color set system.  This could be things like, Active, Inactive, \
        Disabled, or you own custom grouping types.
        
        :param      colorGroups | [<str>, ..]
        """
        self._colorGroups = colorGroups[:]
    
    def setName( self, name ):
        """
        Sets the name of this particular color set instance to the given name.
        
        :param      name | <str
        """
        self._name = str(name)
    
    def toString( self ):
        """
        Saves the color set information out to string format.  The data is \
        returned as xml data.
        
        :return     <str>
        """
        # convert the element tree information
        from xml.etree import ElementTree
        
        xelem = ElementTree.Element('colorset')
        xelem.set('name', self.name())
        xelem.set('colorGroups', ','.join(self.colorGroups()))
        
        for colorName, colors in self._colors.items():
            xcolor = ElementTree.SubElement(xelem, 'color')
            xcolor.set('name', colorName)
            
            for colorGroup, color in colors.items():
                xcolorval = ElementTree.SubElement(xcolor, 'value')
                xcolorval.set('group', colorGroup)
                xcolorval.set('red',    str(color.red()))
                xcolorval.set('green',  str(color.green()))
                xcolorval.set('blue',   str(color.blue()))
                xcolorval.set('alpha',  str(color.alpha()))
        
        # save the text
        return ElementTree.tostring(xelem)
    
    @classmethod
    def fromString( cls, strdata ):
        """
        Restores a color set instance from the inputed string data.
        
        :param      strdata | <str>
        """
        if ( not strdata ):
            return None
            
        from xml.etree import ElementTree
        
        xelem = ElementTree.fromstring(str(strdata))
        output = cls(xelem.get('name'), xelem.get('colorGroups').split(','))
        
        for xcolor in xelem:
            colorName = xcolor.get('name')
            
            for xcolorval in xcolor:
                color = QColor( int(xcolorval.get('red')),
                                int(xcolorval.get('green')),
                                int(xcolorval.get('blue')),
                                int(xcolorval.get('alpha')) )
                
                output.setColor(colorName, color, xcolorval.get('group'))
        
        return output