# CoffeeScript: bare: true 

class SocketPlugin
  @identifier = 'socket'
  @version = '1.0'

  constructor: (@window, @host) ->

  processCommand: (msg) =>
    console.log msg
  sendCommand:(msg)=>
    @host._connector.sendCommand msg
  analyze: ->
    { disable: false }

LiveReloadPluginSocket = window.LiveReloadPluginSocket = SocketPlugin