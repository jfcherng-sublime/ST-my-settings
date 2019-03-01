
augroup IndentFinder
    au! IndentFinder
    au BufRead *.* let b:indent_finder_result = system('python -c "import indent_finder; indent_finder.main()" --vim-output "' . expand('%') . '"' )
    au BufRead *.* execute b:indent_finder_result

    " Uncomment the next line to see which indentation is applied on all your loaded files
    " au BufRead *.* echo "Indent Finder: " . b:indent_finder_result
augroup End

