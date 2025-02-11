/**
 * Copyright (c) 2006-2017, JGraph Ltd
 * Copyright (c) 2006-2017, Gaudenz Alder
 */
DropboxLibrary = function(ui, data, stat)
{
	DropboxFile.call(this, ui, data, stat);
};

//Extends mxEventSource
mxUtils.extend(DropboxLibrary, DropboxFile);


DropboxLibrary.prototype.isAutosave = function()
{
	return true;
};

/**
 * Overridden to avoid updating data with current file.
 */
DropboxLibrary.prototype.doSave = function(title, success, error)
{
	this.saveFile(title, false, success, error);
};

/**
 * Returns the location as a new object.
 * @type mx.Point
 */
DropboxLibrary.prototype.open = function()
{
	// Do nothing - this should never be called
};
