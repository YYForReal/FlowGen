// $Id = DriveFile.js,v 1.12 2010-01-02 09 =45 =14 gaudenz Exp $
// Copyright (c) 2006-2014, JGraph Ltd
/**
 * Constructs a new point for the optional x and y coordinates. If no
 * coordinates are given, then the default values for <x> and <y> are used.
 * @constructor
 * @class Implements a basic 2D point. Known subclassers = {@link mxRectangle}.
 * @param {number} x X-coordinate of the point.
 * @param {number} y Y-coordinate of the point.
 */
LocalLibrary = function(ui, data, title)
{
	LocalFile.call(this, ui, data, title);
};

//Extends mxEventSource
mxUtils.extend(LocalLibrary, LocalFile);


LocalLibrary.prototype.getHash = function()
{
	return 'F' + this.getTitle();
};


LocalLibrary.prototype.isAutosave = function()
{
	return false;
};


LocalLibrary.prototype.saveAs = function(title, success, error)
{
	this.saveFile(title, false, success, error);
};


LocalLibrary.prototype.updateFileData = function()
{
	// Do nothing
};

/**
 * Returns the location as a new object.
 * @type mx.Point
 */
LocalLibrary.prototype.open = function()
{
	// Do nothing - this should never be called
};
