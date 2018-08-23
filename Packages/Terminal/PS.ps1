$pshost = get-host
$pswindow = $pshost.ui.rawui

$newsize = $pswindow.buffersize
$newsize.height = 3000
$newsize.width = 120
$pswindow.buffersize = $newsize

$newsize = $pswindow.windowsize
$newsize.height = 50
$newsize.width = 120
$pswindow.windowsize = $newsize

$pswindow.windowtitle = "Windows Powershell"
$pswindow.foregroundcolor = "DarkYellow"
$pswindow.backgroundcolor = "DarkMagenta"

cls

###################
# my own settings #
###################
$p = $host.privatedata
$p.ErrorForegroundColor    = "Red"
$p.ErrorBackgroundColor    = "Black"
$p.WarningForegroundColor  = "Yellow"
$p.WarningBackgroundColor  = "Black"
$p.DebugForegroundColor    = "Yellow"
$p.DebugBackgroundColor    = "Black"
$p.VerboseForegroundColor  = "Yellow"
$p.VerboseBackgroundColor  = "Black"
$p.ProgressForegroundColor = "Yellow"
$p.ProgressBackgroundColor = "DarkCyan"

$console = $host.UI.RawUI
$console.ForegroundColor = "white"
$console.BackgroundColor = "black"

clear-host
