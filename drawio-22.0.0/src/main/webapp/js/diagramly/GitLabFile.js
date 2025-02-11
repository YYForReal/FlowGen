/**
 * Copyright (c) 2006-2017, JGraph Ltd
 * Copyright (c) 2006-2017, Gaudenz Alder
 */
GitLabFile = function(ui, data, meta)
{
	GitHubFile.call(this, ui, data, meta);
	
	this.peer = this.ui.gitLab;
};

//Extends mxEventSource
mxUtils.extend(GitLabFile, GitHubFile);

/**
 * Returns true if copy, export and print are not allowed for this file.
 */
GitLabFile.prototype.getFileUrl = function()
{
	return this.meta.html_url;
};

/**
 * Returns true if copy, export and print are not allowed for this file.
 */
GitLabFile.prototype.getFolderUrl = function()
{
	var url = this.getFileUrl();

	return url.substring(0, url.lastIndexOf('/'));
};


GitLabFile.prototype.share = function()
{
	this.ui.editor.graph.openLink(DRAWIO_GITLAB_URL + '/' +
		encodeURIComponent(this.meta.org) + '/' +
		encodeURIComponent(this.meta.repo) +'/-/project_members');
};


GitLabFile.prototype.getId = function()
{
	return this.meta.org + '/' +
		((this.meta.repo != null) ? encodeURIComponent(this.meta.repo) + '/' +
		((this.meta.ref != null) ? this.meta.ref +
		((this.meta.path != null) ? '/' + this.meta.path : '') : '') : '');
};


GitLabFile.prototype.getHash = function()
{
	return encodeURIComponent('A' + this.getId());
};

/**
 * Adds the listener for automatically saving the diagram for local changes.
 */
GitLabFile.prototype.isConflict = function(err)
{
	return err != null && err.status == 400;
};


GitLabFile.prototype.getMode = function()
{
	return App.MODE_GITLAB;
};

/**
 * Adds all listeners.
 */
GitLabFile.prototype.getDescriptorEtag = function(desc)
{
	return desc.last_commit_id;
};

/**
 * Adds the listener for automatically saving the diagram for local changes.
 */
GitLabFile.prototype.setDescriptorEtag = function(desc, etag)
{
	desc.last_commit_id = etag;
};
