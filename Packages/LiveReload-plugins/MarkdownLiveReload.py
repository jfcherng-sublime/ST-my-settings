import os

import sublime_plugin
from LiveReload.server.PluginAPI import PluginInterface as Plugin


class MarkdownLiveReload(Plugin, sublime_plugin.EventListener):
    title = "Markdown Preview"
    description = "Generate preview in real-time"
    file_types = ".md,.markdown,.mdown"

    def on_post_save(self, view):
        self.refresh(os.path.basename(view.file_name()))


"""
Plugins for LiveReload should provide the following attributes:

description (string) describing your plugin
title (string) naming your plugin
file_types (string) file_types which should trigger refresh for this plugin

Public methods:

self.refresh(filename, settings):

    (string) filename; file to refresh (.css, .js, jpg ...)
    (object) settings; how to reload(entire page or just parts)

self.sendCommand(plugin, command, settings):

    (instance) plugin; instance
    (string) command; to trigger in livereload.js (refresh, info, or one of the plugins)
    (object) settings; additional data that gets passed to command (should be json parsable)

self.addResource(req_path, buffer, content_type='text/plain'):

    (string) req_path;  browser path to file you want to serve. Ex: /yourfile.js
    (string/file) buffer; string or file instance to file you want to serve
    (string) content_type; Mime-type of file you want to serve

self.listClients():

    returns list with all connected clients with their req_url and origin

    """
