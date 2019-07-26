# CoffeeScript: bare: true 

class Timer
  constructor: (@func) ->
    @running = no
    @id = null
    @_handler = =>
      @running = no
      @id = null
      @func()

  start: (timeout, func) ->
    # setTimeout func, timeout
    clearTimeout @id if @running
    handle = if func? then func else @_handler
    @id = setTimeout handle, timeout
    @running = yes

  stop: ->
    if @running
      clearTimeout @id
      @running = no; @id = null

