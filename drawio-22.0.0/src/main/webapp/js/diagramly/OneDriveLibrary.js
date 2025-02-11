/**
 * Copyright (c) 2006-2017, JGraph Ltd
 * Copyright (c) 2006-2017, Gaudenz Alder
 */
OneDriveLibrary = function(ui, data, meta)
{
	OneDriveFile.call(this, ui, data, meta);
};

//Extends mxEventSource
mxUtils.extend(OneDriveLibrary, OneDriveFile);


OneDriveLibrary.prototype.isAutosave = function()
{
	return true;
};


OneDriveLibrary.prototype.save = function(revision, success, error)
{
	this.ui.oneDrive.saveFile(this, mxUtils.bind(this, function(resp)
	{
		this.desc = resp;
		
		if (success != null)
		{
			success(resp);
		}
	}), error);
};

/**
 * Returns the location as a new object.
 * @type mx.Point
 */
OneDriveLibrary.prototype.open = function()
{
	// Do nothing - this should never be called
};
