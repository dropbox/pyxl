" Pyxl indent file
"
" This file is the unholy spawn of a python indent file from the vim script
" database and the standard, html, and xml indent files.
"
" BUG: atrociously slow; takes about four seconds to reindent 200 lines.
"
" Language:		Pyxl
" Maintainer:		Josiah Boning <jboning@gmail.com>
" Last Change:		2012 Sep 16
" Credits:
" 			Python credits:
" 			  Eric Mc Sween <em@tomcom.de>
" 			  David Bustos <bustos@caltech.edu>
" 			HTML and XML credits:
" 			  Johannes Zellner <johannes@zellner.org>

" Only load this indent file when no other was loaded.
if exists("b:did_indent")
    finish
endif
let b:did_indent = 1

setlocal expandtab
setlocal nolisp
setlocal autoindent
setlocal indentexpr=GetPyxlIndent(v:lnum)
setlocal indentkeys=!^F,o,O,<:>,0),0],0},=elif,=except,<>>,<<>,/,{,},*<Return>

let s:maxoff = 50

" Find backwards the closest open parenthesis/bracket/brace.
function! s:SearchParensPair()
    let line = line('.')
    let col = col('.')

    " Skip strings and comments and don't look too far
    let skip = "line('.') < " . (line - s:maxoff) . " ? dummy :" .
                \ 'synIDattr(synID(line("."), col("."), 0), "name") =~? ' .
                \ '"string\\|comment"'

    " Search for parentheses
    call cursor(line, col)
    let parlnum = searchpair('(', '', ')', 'bW', skip)
    let parcol = col('.')

    " Search for brackets
    call cursor(line, col)
    let par2lnum = searchpair('\[', '', '\]', 'bW', skip)
    let par2col = col('.')

    " Search for braces
    call cursor(line, col)
    let par3lnum = searchpair('{', '', '}', 'bW', skip)
    let par3col = col('.')

    " Get the closest match
    if par2lnum > parlnum || (par2lnum == parlnum && par2col > parcol)
        let parlnum = par2lnum
        let parcol = par2col
    endif
    if par3lnum > parlnum || (par3lnum == parlnum && par3col > parcol)
        let parlnum = par3lnum
        let parcol = par3col
    endif

    " Put the cursor on the match
    if parlnum > 0
        call cursor(parlnum, parcol)
    endif
    return parlnum
endfunction

" Find the start of a multi-line statement
function! s:StatementStart(lnum)
    let lnum = a:lnum
    while 1
        if getline(lnum - 1) =~ '\\$'
            let lnum = lnum - 1
        else
            call cursor(lnum, 1)
            let maybe_lnum = s:SearchParensPair()
            if maybe_lnum < 1
                return lnum
            else
                let lnum = maybe_lnum
            endif
        endif
    endwhile
endfunction

" Find the block starter that matches the current line
function! s:BlockStarter(lnum, block_start_re)
    let lnum = a:lnum
    let maxindent = 10000       " whatever
    while lnum > 1
        let lnum = prevnonblank(lnum - 1)
        if indent(lnum) < maxindent
            if getline(lnum) =~ a:block_start_re
                return lnum
            else
                let maxindent = indent(lnum)
                " It's not worth going further if we reached the top level
                if maxindent == 0
                    return -1
                endif
            endif
        endif
    endwhile
    return -1
endfunction

let s:cpo_save = &cpo
set cpo-=C

if !exists('b:xml_indent_open')
    let b:xml_indent_open = '.\{-}<\a'
    " pre tag, e.g. <address>
    " let b:xml_indent_open = '.\{-}<[/]\@!\(address\)\@!'
endif

if !exists('b:xml_indent_close')
    let b:xml_indent_close = '.\{-}</'
    " end pre tag, e.g. </address>
    " let b:xml_indent_close = '.\{-}</\(address\)\@!'
endif

fun! <SID>XmlIndentWithPattern(line, pat)
    let s = substitute('x'.a:line, a:pat, "\1", 'g')
    return strlen(substitute(s, "[^\1].*$", '', ''))
endfun

" [-- return the sum of indents of a:lnum --]
fun! <SID>XmlIndentSum(lnum, style)
    let line = getline(a:lnum)
    if a:style == match(line, '^\s*</')
        return (
            \  (<SID>XmlIndentWithPattern(line, b:xml_indent_open)
            \ - <SID>XmlIndentWithPattern(line, b:xml_indent_close)
            \ - <SID>XmlIndentWithPattern(line, '.\{-}/>')))
    else
        return 0
    endif
endfun

fun! <SID>XmlIndentSumLines(startnum, endnum, style)
    let sum = 0
    for lnum in range(a:startnum, a:endnum)
        let sum = sum + <SID>XmlIndentSum(lnum, a:style)
    endfor
    return sum
endfun

fun! <SID>GetMarkupIndent(lnum)
    " Find a non-empty line above the current line.
    let lnum = prevnonblank(a:lnum - 1)

    " Hit the start of the file, use zero indent.
    if lnum == 0
        return 0
    endif

    let restore_ic = &ic
    setlocal ic " ignore case

    " [-- special handling for <pre>: no indenting --]
    if getline(a:lnum) =~ '\c</pre>'
        \ || 0 < searchpair('\c<pre>', '', '\c</pre>', 'nWb')
        \ || 0 < searchpair('\c<pre>', '', '\c</pre>', 'nW')
    " we're in a line with </pre> or inside <pre> ... </pre>
    if restore_ic == 0
      setlocal noic
    endif
    return -1
    endif

    "" The javascript indentation doesn't really work, since curly braces are
    "" handled by the python indentation.

    "" [-- special handling for <javascript>: use cindent --]
    "let js = '<script.*type\s*=\s*.*java'
    "
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    "" by Tye Zdrojewski <zdro@yahoo.com>, 05 Jun 2006
    "" ZDR: This needs to be an AND (we are 'after the start of the pair' AND
    ""      we are 'before the end of the pair').  Otherwise, indentation
    ""      before the start of the script block will be affected; the end of
    ""      the pair will still match if we are before the beginning of the
    ""      pair.
    ""
    "if   0 < searchpair(js, '', '</script>', 'nWb')
    "\ && 0 < searchpair(js, '', '</script>', 'nW')
    "" we're inside javascript
    "if getline(lnum) !~ js && getline(a:lnum) != '</script>'
    "    if restore_ic == 0
    "      setlocal noic
    "    endif
    "    return cindent(a:lnum)
    "endif
    "endif

    if getline(lnum) =~ '\c</pre>'
    " line before the current line a:lnum contains
    " a closing </pre>. --> search for line before
    " starting <pre> to restore the indent.
    let preline = prevnonblank(search('\c<pre>', 'bW') - 1)
    if preline > 0
        if restore_ic == 0
          setlocal noic
        endif
        return indent(preline)
    endif
    endif

    if restore_ic == 0
    setlocal noic
    endif

    let ind = <SID>XmlIndentSum(lnum, -1)
    let ind = ind + <SID>XmlIndentSum(a:lnum, 0)

    if ind > 0
        return indent(lnum) + &sw
    elseif ind < 0
        return indent(lnum) - &sw
    else
        return indent(lnum)
    endif
endfun

function! GetPyxlIndent(lnum)

    " First line has indent 0
    if a:lnum == 1
        return 0
    endif

    " Examine previous line
    let plnum = a:lnum - 1
    let pline = getline(plnum)
    let sslnum = s:StatementStart(plnum)

    " If we can find an open parenthesis/bracket/brace, line up with it, then
    " apply any XML indentation.
    call cursor(a:lnum, 1)
    let parlnum = s:SearchParensPair()
    if parlnum > 0
        let parcol = col('.')
        let closing_paren = match(getline(a:lnum), '^\s*[])}]') != -1
        if match(getline(parlnum), '[([{]\s*$', parcol - 1) != -1
            if closing_paren
                return indent(parlnum)
            else
                if plnum == parlnum
                    return indent(parlnum) + &shiftwidth
                else
                    let ind = <SID>XmlIndentSumLines(parlnum, a:lnum, -1)
                    let ind = ind + <SID>XmlIndentSumLines(parlnum, a:lnum, 0)
                    if ind > 0
                        return <SID>GetMarkupIndent(a:lnum)
                    else
                        return indent(parlnum) + &sw
                    end
                endif
            endif
        else
            if closing_paren
                return parcol - 1
            else
                if plnum == parlnum
                    let ind = <SID>XmlIndentSum(plnum, -1)
                    let ind = ind + <SID>XmlIndentSum(a:lnum, 0)
                    return parcol + (&sw * ind)
                else
                    let ind = <SID>XmlIndentSumLines(parlnum, a:lnum, -1)
                    let ind = ind + <SID>XmlIndentSumLines(parlnum, a:lnum, 0)
                    if ind > 0
                        return <SID>GetMarkupIndent(a:lnum)
                    else
                        return parcol
                    endif
                endif
            endif
        endif
    endif

    " Examine this line
    let thisline = getline(a:lnum)
    let thisindent = indent(a:lnum)

    " If the line starts with 'elif' or 'else', line up with 'if' or 'elif'
    if thisline =~ '^\s*\(elif\|else\)\>'
        let bslnum = s:BlockStarter(a:lnum, '^\s*\(if\|elif\)\>')
        if bslnum > 0
            return indent(bslnum)
        else
            return -1
        endif
    endif

    " If the line starts with 'except' or 'finally', line up with 'try'
    " or 'except'
    if thisline =~ '^\s*\(except\|finally\)\>'
        let bslnum = s:BlockStarter(a:lnum, '^\s*\(try\|except\)\>')
        if bslnum > 0
            return indent(bslnum)
        else
            return -1
        endif
    endif

    " If the previous line is blank, keep the same indentation
    if pline =~ '^\s*$'
        return -1
    endif

    " If this line is explicitly joined, try to find an indentation that looks
    " good.
    if pline =~ '\\$'
        let compound_statement = '^\s*\(if\|while\|for\s.*\sin\|except\)\s*'
        let maybe_indent = matchend(getline(sslnum), compound_statement)
        if maybe_indent != -1
            return maybe_indent
        else
            return indent(sslnum) + &sw * 2
        endif
    endif

    " If the previous line ended with a colon, indent relative to
    " statement start.
    if pline =~ ':\s*$'
        return indent(sslnum) + &sw
    endif

    " If the previous line was a stop-execution statement or a pass
    if getline(sslnum) =~ '^\s*\(break\|continue\|raise\|return\|pass\)\>'
        " See if the user has already dedented
        if indent(a:lnum) > indent(sslnum) - &sw
            " If not, recommend one dedent
            return indent(sslnum) - &sw
        endif
        " Otherwise, trust the user
        return -1
    endif

    " If the previous line closed a statement, match the beginning of that
    " statement.
    if pline =~ '[])}]$'
        return indent(sslnum)
    endif

    "" In all other cases, line up with the start of the previous statement.
    return indent(sslnum)

endfun

let &cpo = s:cpo_save
unlet s:cpo_save

" for debugging
"map yy :echo GetPyxlIndent(line('.'))<ENTER>
