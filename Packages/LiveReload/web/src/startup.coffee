# CoffeeScript: bare: true 

#= require customevents
#= require livereload
#= require socketPluginAPI
#= require less
#
LiveReload = window.LiveReload = new LiveReload window

for k of window when k.match(/^LiveReloadPlugin/)
  LiveReload.log "Adding plugin: #{k}"
  LiveReload.addPlugin window[k]

LiveReload.on 'shutdown', -> delete window.LiveReload
LiveReload.on 'connect', ->
  CustomEvents.fire document, 'LiveReloadConnect'
LiveReload.on 'disconnect', ->
  CustomEvents.fire document, 'LiveReloadDisconnect'

CustomEvents.bind document, 'LiveReloadShutDown', -> LiveReload.shutDown()
