/**
 * Copyright (c) 2006-2017, JGraph Ltd
 * Copyright (c) 2006-2017, Gaudenz Alder
 */
/**
 * Constructs a new point for the optional x and y coordinates. If no
 * coordinates are given, then the default values for <x> and <y> are used.
 * @constructor
 * @class Implements a basic 2D point. Known subclassers = {@link mxRectangle}.
 * @param {number} x X-coordinate of the point.
 * @param {number} y Y-coordinate of the point.
 */
UrlLibrary = function(ui, data, title)
{
	StorageFile.call(this, ui, data, title);
	
	var fname = title;
	var last = fname.lastIndexOf('/');
		
	if (last >= 0)
	{
		fname = fname.substring(last + 1);
	}
	
	this.fname = fname;
};

//Extends mxEventSource
mxUtils.extend(UrlLibrary, StorageFile);


UrlLibrary.prototype.getHash = function()
{
	return 'U' + encodeURIComponent(this.title);
};


UrlLibrary.prototype.getTitle = function()
{
	return this.fname;
};


UrlLibrary.prototype.isAutosave = function()
{
	return false;
};

/**
 * Overridden to avoid updating data with current file.
 */
UrlLibrary.prototype.isEditable = function(title, success, error)
{
	return false;
};

/**
 * Overridden to avoid updating data with current file.
 */
UrlLibrary.prototype.saveAs = function(title, success, error)
{
	// Cannot be saved
};

/**
 * Returns the location as a new object.
 * @type mx.Point
 */
UrlLibrary.prototype.open = function()
{
	// Do nothing - this should never be called
};
