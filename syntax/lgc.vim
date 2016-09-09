" Vim syntax file for Logicode
" https://github.com/LogicodeLang/Logicode
" Author: TuxCrafting
"
" Installation instructions:
" 1. Copy this file to ~/.vim/syntax/lgc.vim
" 2. Create the file ~/.vim/ftdetect/lgc.vim
" 3. Write 'au BufRead,BufNewFile *.lgc set filetype=lgc' in the ftdetect file
" 4. ???
" 5. Profit!

if exists("b:current_syntax")
    finish
endif

syn keyword lgcTodo TODO FIXME XXX NOTE
syn match lgcComment "#.*$" contains=lgcTodo
syn keyword lgcKeyword circ cond out var
syn match lgcNumber "[01]\+"

let b:current_syntax = "lgc"

hi def link lgcTodo Todo
hi def link lgcComment Comment
hi def link lgcKeyword Statement
hi def link lgcNumber Constant
