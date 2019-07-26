Snockets = require('snockets')
fs = require('fs')
path = require('path')

#global module:false
module.exports = (grunt) ->
  
  # Project configuration.
  grunt.initConfig
    
    # Metadata.
    pkg: grunt.file.readJSON("package.json")
    banner: '/*! <%= pkg.name %> - v<%= pkg.version %> - ' +
          '<%= grunt.template.today("yyyy-mm-dd") %>\n' +
          '<%= pkg.homepage ? "* " + pkg.homepage + "\\n" : "" %>' +
          '* Copyright (c) <%= grunt.template.today("yyyy") %> <%= pkg.author %>;' +
          ' Licensed <%= pkg.license %> */\n',
    # Task configuration.
    uglify:
      options:
        banner: "<%= banner %>"

      dist:
        src: "<%= snockets.dist.dest %>"
        dest: "dist/<%= pkg.name %>.min.js"

    snockets:
      dist:
        src: 'src/startup.coffee'
        dest: "dist/<%= pkg.name %>.js"

    qunit:
      files: ["test/**/*.html"]

  grunt.registerMultiTask "snockets", "Building js files with snockets.js.", ->
    
    snockets = new Snockets

    # It doesn't run with empty src and dest parameters.    
    if typeof @data.src is "undefined" or typeof @data.dest is "undefined"
      grunt.log.error "Missing Options: src and dest options necessary"
      return false
    if fs.existsSync(path.resolve(@data.src))
      try
        js = snockets.getConcatenation(@data.src,
          async: false
        )
        js = """
        (function() {
        #{js}
        }).call(this);
        """
        fs.writeFileSync path.resolve(@data.dest), js
        grunt.log.write @data.src + " snocket to " + @data.dest
        return true
      catch e
        grunt.log.error e
        return false
    else
      grunt.log.error "Missing File: " + @data.src
      false

  # These plugins provide necessary tasks.
  grunt.loadNpmTasks "grunt-contrib-uglify"
  grunt.loadNpmTasks "grunt-contrib-qunit"
  grunt.loadNpmTasks "grunt-contrib-watch"
  
  # Default task.
  grunt.registerTask "default", ["snockets", "uglify"]
