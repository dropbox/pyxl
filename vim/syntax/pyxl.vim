" Pyxl syntax file
"
" This file is the unholy spawn of the standard python and html syntax files.
"
" Language:	Python with Pyxl support
" Maintainer:	Josiah Boning <jboning@gmail.com>
" Last Change:	2012 Sep 04
" Credits:
"
"		Python credits:
"		  Neil Schemenauer <nas@python.ca>
"		  Zvezdan Petkovic <zpetkovic@acm.org>
"		  Neil Schemenauer <nas@python.ca>
"		  Dmitry Vasiliev
"
"		  This version is a major rewrite by Zvezdan Petkovic.
"
"		  - introduced highlighting of doctests
"		  - updated keywords, built-ins, and exceptions
"		  - corrected regular expressions for
"
"		    * functions
"		    * decorators
"		    * strings
"		    * escapes
"		    * numbers
"		    * space error
"
"		  - corrected synchronization
"		  - more highlighting is ON by default, except
"		  - space error highlighting is OFF by default
"
"		HTML credits:
"		  Claudio Fleiner <claudio@fleiner.com>
"
"
"
"
" Optional highlighting can be controlled using these variables.
"
"   let python_no_builtin_highlight = 1
"   let python_no_doctest_code_highlight = 1
"   let python_no_doctest_highlight = 1
"   let python_no_exception_highlight = 1
"   let python_no_number_highlight = 1
"   let python_space_error_highlight = 1
"
" All the options above can be switched on together.
"
"   let python_highlight_all = 1
"

" For version 5.x: Clear all syntax items.
" For version 6.x: Quit when a syntax file was already loaded.
if version < 600
  syntax clear
elseif exists("b:current_syntax")
  finish
endif

if !exists("main_syntax")
  let main_syntax = 'pyxl'
endif


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" Python
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

" We need nocompatible mode in order to continue lines with backslashes.
" Original setting will be restored.
let s:cpo_save = &cpo
set cpo&vim

" Keep Python keywords in alphabetical order inside groups for easy
" comparison with the table in the 'Python Language Reference'
" http://docs.python.org/reference/lexical_analysis.html#keywords.
" Groups are in the order presented in NAMING CONVENTIONS in syntax.txt.
" Exceptions come last at the end of each group (class and def below).
"
" Keywords 'with' and 'as' are new in Python 2.6
" (use 'from __future__ import with_statement' in Python 2.5).
"
" Some compromises had to be made to support both Python 3.0 and 2.6.
" We include Python 3.0 features, but when a definition is duplicated,
" the last definition takes precedence.
"
" - 'False', 'None', and 'True' are keywords in Python 3.0 but they are
"   built-ins in 2.6 and will be highlighted as built-ins below.
" - 'exec' is a built-in in Python 3.0 and will be highlighted as
"   built-in below.
" - 'nonlocal' is a keyword in Python 3.0 and will be highlighted.
" - 'print' is a built-in in Python 3.0 and will be highlighted as
"   built-in below (use 'from __future__ import print_function' in 2.6)
"
syn keyword pythonStatement	False, None, True
syn keyword pythonStatement	as assert break continue del exec global
syn keyword pythonStatement	lambda nonlocal pass print return with yield
syn keyword pythonStatement	class def nextgroup=pythonFunction skipwhite
syn keyword pythonConditional	elif else if
syn keyword pythonRepeat	for while
syn keyword pythonOperator	and in is not or
syn keyword pythonException	except finally raise try
syn keyword pythonInclude	from import

" Decorators (new in Python 2.4)
syn match   pythonDecorator	"@" display nextgroup=pythonFunction skipwhite
" The zero-length non-grouping match before the function name is
" extremely important in pythonFunction.  Without it, everything is
" interpreted as a function inside the contained environment of
" doctests.
" A dot must be allowed because of @MyClass.myfunc decorators.
syn match   pythonFunction
      \ "\%(\%(def\s\|class\s\|@\)\s*\)\@<=\h\%(\w\|\.\)*" contained

syn match   pythonComment	"#.*$" contains=pythonTodo,@Spell
syn keyword pythonTodo		FIXME NOTE NOTES TODO XXX contained

" Triple-quoted strings can contain doctests.
syn region  pythonString
      \ start=+[uU]\=\z(['"]\)+ end="\z1" skip="\\\\\|\\\z1"
      \ contains=pythonEscape,@Spell
syn region  pythonString
      \ start=+[uU]\=\z('''\|"""\)+ end="\z1" keepend
      \ contains=pythonEscape,pythonSpaceError,pythonDoctest,@Spell
syn region  pythonRawString
      \ start=+[uU]\=[rR]\z(['"]\)+ end="\z1" skip="\\\\\|\\\z1"
      \ contains=@Spell
syn region  pythonRawString
      \ start=+[uU]\=[rR]\z('''\|"""\)+ end="\z1" keepend
      \ contains=pythonSpaceError,pythonDoctest,@Spell

syn match   pythonEscape	+\\[abfnrtv'"\\]+ contained
syn match   pythonEscape	"\\\o\{1,3}" contained
syn match   pythonEscape	"\\x\x\{2}" contained
syn match   pythonEscape	"\%(\\u\x\{4}\|\\U\x\{8}\)" contained
" Python allows case-insensitive Unicode IDs: http://www.unicode.org/charts/
syn match   pythonEscape	"\\N{\a\+\%(\s\a\+\)*}" contained
syn match   pythonEscape	"\\$"

if exists("python_highlight_all")
  if exists("python_no_builtin_highlight")
    unlet python_no_builtin_highlight
  endif
  if exists("python_no_doctest_code_highlight")
    unlet python_no_doctest_code_highlight
  endif
  if exists("python_no_doctest_highlight")
    unlet python_no_doctest_highlight
  endif
  if exists("python_no_exception_highlight")
    unlet python_no_exception_highlight
  endif
  if exists("python_no_number_highlight")
    unlet python_no_number_highlight
  endif
  let python_space_error_highlight = 1
endif

" It is very important to understand all details before changing the
" regular expressions below or their order.
" The word boundaries are *not* the floating-point number boundaries
" because of a possible leading or trailing decimal point.
" The expressions below ensure that all valid number literals are
" highlighted, and invalid number literals are not.  For example,
"
" - a decimal point in '4.' at the end of a line is highlighted,
" - a second dot in 1.0.0 is not highlighted,
" - 08 is not highlighted,
" - 08e0 or 08j are highlighted,
"
" and so on, as specified in the 'Python Language Reference'.
" http://docs.python.org/reference/lexical_analysis.html#numeric-literals
if !exists("python_no_number_highlight")
  " numbers (including longs and complex)
  syn match   pythonNumber	"\<0[oO]\=\o\+[Ll]\=\>"
  syn match   pythonNumber	"\<0[xX]\x\+[Ll]\=\>"
  syn match   pythonNumber	"\<0[bB][01]\+[Ll]\=\>"
  syn match   pythonNumber	"\<\%([1-9]\d*\|0\)[Ll]\=\>"
  syn match   pythonNumber	"\<\d\+[jJ]\>"
  syn match   pythonNumber	"\<\d\+[eE][+-]\=\d\+[jJ]\=\>"
  syn match   pythonNumber
	\ "\<\d\+\.\%([eE][+-]\=\d\+\)\=[jJ]\=\%(\W\|$\)\@="
  syn match   pythonNumber
	\ "\%(^\|\W\)\@<=\d*\.\d\+\%([eE][+-]\=\d\+\)\=[jJ]\=\>"
endif

" Group the built-ins in the order in the 'Python Library Reference' for
" easier comparison.
" http://docs.python.org/library/constants.html
" http://docs.python.org/library/functions.html
" http://docs.python.org/library/functions.html#non-essential-built-in-functions
" Python built-in functions are in alphabetical order.
if !exists("python_no_builtin_highlight")
  " built-in constants
  " 'False', 'True', and 'None' are also reserved words in Python 3.0
  syn keyword pythonBuiltin	False True None
  syn keyword pythonBuiltin	NotImplemented Ellipsis __debug__
  " built-in functions
  syn keyword pythonBuiltin	abs all any bin bool chr classmethod
  syn keyword pythonBuiltin	compile complex delattr dict dir divmod
  syn keyword pythonBuiltin	enumerate eval filter float format
  syn keyword pythonBuiltin	frozenset getattr globals hasattr hash
  syn keyword pythonBuiltin	help hex id input int isinstance
  syn keyword pythonBuiltin	issubclass iter len list locals map max
  syn keyword pythonBuiltin	min next object oct open ord pow print
  syn keyword pythonBuiltin	property range repr reversed round set
  syn keyword pythonBuiltin	setattr slice sorted staticmethod str
  syn keyword pythonBuiltin	sum super tuple type vars zip __import__
  " Python 2.6 only
  syn keyword pythonBuiltin	basestring callable cmp execfile file
  syn keyword pythonBuiltin	long raw_input reduce reload unichr
  syn keyword pythonBuiltin	unicode xrange
  " Python 3.0 only
  syn keyword pythonBuiltin	ascii bytearray bytes exec memoryview
  " non-essential built-in functions; Python 2.6 only
  syn keyword pythonBuiltin	apply buffer coerce intern
endif

" From the 'Python Library Reference' class hierarchy at the bottom.
" http://docs.python.org/library/exceptions.html
if !exists("python_no_exception_highlight")
  " builtin base exceptions (only used as base classes for other exceptions)
  syn keyword pythonExceptions	BaseException Exception
  syn keyword pythonExceptions	ArithmeticError EnvironmentError
  syn keyword pythonExceptions	LookupError
  " builtin base exception removed in Python 3.0
  syn keyword pythonExceptions	StandardError
  " builtin exceptions (actually raised)
  syn keyword pythonExceptions	AssertionError AttributeError BufferError
  syn keyword pythonExceptions	EOFError FloatingPointError GeneratorExit
  syn keyword pythonExceptions	IOError ImportError IndentationError
  syn keyword pythonExceptions	IndexError KeyError KeyboardInterrupt
  syn keyword pythonExceptions	MemoryError NameError NotImplementedError
  syn keyword pythonExceptions	OSError OverflowError ReferenceError
  syn keyword pythonExceptions	RuntimeError StopIteration SyntaxError
  syn keyword pythonExceptions	SystemError SystemExit TabError TypeError
  syn keyword pythonExceptions	UnboundLocalError UnicodeError
  syn keyword pythonExceptions	UnicodeDecodeError UnicodeEncodeError
  syn keyword pythonExceptions	UnicodeTranslateError ValueError VMSError
  syn keyword pythonExceptions	WindowsError ZeroDivisionError
  " builtin warnings
  syn keyword pythonExceptions	BytesWarning DeprecationWarning FutureWarning
  syn keyword pythonExceptions	ImportWarning PendingDeprecationWarning
  syn keyword pythonExceptions	RuntimeWarning SyntaxWarning UnicodeWarning
  syn keyword pythonExceptions	UserWarning Warning
endif

if exists("python_space_error_highlight")
  " trailing whitespace
  syn match   pythonSpaceError	display excludenl "\s\+$"
  " mixed tabs and spaces
  syn match   pythonSpaceError	display " \+\t"
  syn match   pythonSpaceError	display "\t\+ "
endif

" Do not spell doctests inside strings.
" Notice that the end of a string, either ''', or """, will end the contained
" doctest too.  Thus, we do *not* need to have it as an end pattern.
if !exists("python_no_doctest_highlight")
  if !exists("python_no_doctest_code_higlight")
    syn region pythonDoctest
	  \ start="^\s*>>>\s" end="^\s*$"
	  \ contained contains=ALLBUT,pythonDoctest,@Spell
    syn region pythonDoctestValue
	  \ start=+^\s*\%(>>>\s\|\.\.\.\s\|"""\|'''\)\@!\S\++ end="$"
	  \ contained
  else
    syn region pythonDoctest
	  \ start="^\s*>>>" end="^\s*$"
	  \ contained contains=@NoSpell
  endif
endif

" Sync at the beginning of class, function, or method definition.
syn sync match pythonSync grouphere NONE "^\s*\%(def\|class\)\s\+\h\w*\s*("


" The Pyxl special sauce.
syn cluster pythonGroup contains=pythonStatement,pythonOperator,pythonConditional,pythonString,pythonEscape,pythonNumber,pythonBuiltin
syn region pyxlPythonNormal contained start="{\@<=" end="}\@=" contains=@pythonGroup
syn region pyxlPython start="[^\\]\@<={" end="}" contains=pyxlPythonNormal


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" HTML
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

" don't use standard HiLink, it will not work with included syntax files
if version < 508
  command! -nargs=+ HtmlHiLink hi link <args>
else
  command! -nargs=+ HtmlHiLink hi def link <args>
endif

syntax spell toplevel

syn case ignore

" mark illegal characters
"syn match htmlError "[<>&]"


" tags
syn region  htmlString   contained start=+"+ end=+"+ contains=htmlSpecialChar,javaScriptExpression,@htmlPreproc,pyxlPython
syn region  htmlString   contained start=+'+ end=+'+ contains=htmlSpecialChar,javaScriptExpression,@htmlPreproc
syn match   htmlValue    contained "=[\t ]*[^'" \t>][^ \t>]*"hs=s+1   contains=javaScriptExpression,@htmlPreproc
syn region  htmlEndTag             start=+</+      end=+>+ contains=htmlTagN,htmlTagError
syn region  htmlTag                start=+<[^/<= \t]+   end=+>+ contains=htmlTagN,htmlString,htmlArg,htmlValue,htmlTagError,htmlEvent,htmlCssDefinition,@htmlPreproc,@htmlArgCluster
syn match   htmlTagN     contained +<\s*[-a-zA-Z0-9_]\++hs=s+1 contains=htmlTagName,htmlSpecialTagName,@htmlTagNameCluster
syn match   htmlTagN     contained +</\s*[-a-zA-Z0-9_]\++hs=s+2 contains=htmlTagName,htmlSpecialTagName,@htmlTagNameCluster
"syn match   htmlTagError contained "[^>]<"ms=s+1


" tag names
syn keyword htmlTagName contained address applet area a base basefont
syn keyword htmlTagName contained big blockquote br caption center
syn keyword htmlTagName contained cite code dd dfn dir div dl dt font
syn keyword htmlTagName contained form frag hr html if img
syn keyword htmlTagName contained input isindex kbd li link map menu
syn keyword htmlTagName contained meta ol option param pre p samp span
syn keyword htmlTagName contained select small strike sub sup
syn keyword htmlTagName contained table td textarea th tr tt ul var xmp
syn match htmlTagName contained "\<\(b\|i\|u\|h[1-6]\|em\|strong\|head\|body\|title\)\>"

" new html 4.0 tags
syn keyword htmlTagName contained abbr acronym bdo button col label
syn keyword htmlTagName contained colgroup del fieldset iframe ins legend
syn keyword htmlTagName contained object optgroup q s tbody tfoot thead

" legal arg names
syn keyword htmlArg contained action
syn keyword htmlArg contained align alink alt archive background bgcolor
syn keyword htmlArg contained border bordercolor cellpadding
syn keyword htmlArg contained cellspacing checked class clear code codebase color
syn keyword htmlArg contained cols colspan content coords enctype face
syn keyword htmlArg contained gutter height hspace id
syn keyword htmlArg contained link lowsrc marginheight
syn keyword htmlArg contained marginwidth maxlength method name prompt
syn keyword htmlArg contained rel rev rows rowspan scrolling selected shape
syn keyword htmlArg contained size src start target text type url
syn keyword htmlArg contained usemap ismap valign value vlink vspace width wrap
syn match   htmlArg contained "\<\(http-equiv\|href\|title\)="me=e-1

" Netscape extensions
syn keyword htmlTagName contained frame noframes frameset nobr blink
syn keyword htmlTagName contained layer ilayer nolayer spacer
syn keyword htmlArg     contained frameborder noresize pagex pagey above below
syn keyword htmlArg     contained left top visibility clip id noshade
syn match   htmlArg     contained "\<z-index\>"

" Microsoft extensions
syn keyword htmlTagName contained marquee

" html 4.0 arg names
syn match   htmlArg contained "\<\(accept-charset\|label\)\>"
syn keyword htmlArg contained abbr accept accesskey axis char charoff charset
syn keyword htmlArg contained cite classid codetype compact data datetime
syn keyword htmlArg contained declare defer dir disabled for frame
syn keyword htmlArg contained headers hreflang lang language longdesc
syn keyword htmlArg contained multiple nohref nowrap object profile readonly
syn keyword htmlArg contained rules scheme scope span standby style
syn keyword htmlArg contained summary tabindex valuetype version

" special characters
syn match htmlSpecialChar "&#\=[0-9A-Za-z]\{1,8};"

" Comments (the real ones or the old netscape ones)
if exists("html_wrong_comments")
  syn region htmlComment                start=+<!--+    end=+--\s*>+
else
  syn region htmlComment                start=+<!+      end=+>+   contains=htmlCommentPart,htmlCommentError
  syn match  htmlCommentError contained "[^><!]"
  syn region htmlCommentPart  contained start=+--+      end=+--\s*+  contains=@htmlPreProc
endif
syn region htmlComment                  start=+<!DOCTYPE+ keepend end=+>+

" server-parsed commands
syn region htmlPreProc start=+<!--#+ end=+-->+ contains=htmlPreStmt,htmlPreError,htmlPreAttr
syn match htmlPreStmt contained "<!--#\(config\|echo\|exec\|fsize\|flastmod\|include\|printenv\|set\|if\|elif\|else\|endif\|geoguide\)\>"
syn match htmlPreError contained "<!--#\S*"ms=s+4
syn match htmlPreAttr contained "\w\+=[^"]\S\+" contains=htmlPreProcAttrError,htmlPreProcAttrName
syn region htmlPreAttr contained start=+\w\+="+ skip=+\\\\\|\\"+ end=+"+ contains=htmlPreProcAttrName keepend
syn match htmlPreProcAttrError contained "\w\+="he=e-1
syn match htmlPreProcAttrName contained "\(expr\|errmsg\|sizefmt\|timefmt\|var\|cgi\|cmd\|file\|virtual\|value\)="he=e-1

if !exists("html_no_rendering")
  " rendering
  syn cluster htmlTop contains=@Spell,htmlTag,htmlEndTag,htmlSpecialChar,htmlPreProc,htmlComment,htmlLink,javaScript,@htmlPreproc

  syn region htmlBold start="<b\>" end="</b>"me=e-4 contains=@htmlTop,htmlBoldUnderline,htmlBoldItalic
  syn region htmlBold start="<strong\>" end="</strong>"me=e-9 contains=@htmlTop,htmlBoldUnderline,htmlBoldItalic
  syn region htmlBoldUnderline contained start="<u\>" end="</u>"me=e-4 contains=@htmlTop,htmlBoldUnderlineItalic
  syn region htmlBoldItalic contained start="<i\>" end="</i>"me=e-4 contains=@htmlTop,htmlBoldItalicUnderline
  syn region htmlBoldItalic contained start="<em\>" end="</em>"me=e-5 contains=@htmlTop,htmlBoldItalicUnderline
  syn region htmlBoldUnderlineItalic contained start="<i\>" end="</i>"me=e-4 contains=@htmlTop
  syn region htmlBoldUnderlineItalic contained start="<em\>" end="</em>"me=e-5 contains=@htmlTop
  syn region htmlBoldItalicUnderline contained start="<u\>" end="</u>"me=e-4 contains=@htmlTop,htmlBoldUnderlineItalic

  syn region htmlUnderline start="<u\>" end="</u>"me=e-4 contains=@htmlTop,htmlUnderlineBold,htmlUnderlineItalic
  syn region htmlUnderlineBold contained start="<b\>" end="</b>"me=e-4 contains=@htmlTop,htmlUnderlineBoldItalic
  syn region htmlUnderlineBold contained start="<strong\>" end="</strong>"me=e-9 contains=@htmlTop,htmlUnderlineBoldItalic
  syn region htmlUnderlineItalic contained start="<i\>" end="</i>"me=e-4 contains=@htmlTop,htmlUnderlineItalicBold
  syn region htmlUnderlineItalic contained start="<em\>" end="</em>"me=e-5 contains=@htmlTop,htmlUnderlineItalicBold
  syn region htmlUnderlineItalicBold contained start="<b\>" end="</b>"me=e-4 contains=@htmlTop
  syn region htmlUnderlineItalicBold contained start="<strong\>" end="</strong>"me=e-9 contains=@htmlTop
  syn region htmlUnderlineBoldItalic contained start="<i\>" end="</i>"me=e-4 contains=@htmlTop
  syn region htmlUnderlineBoldItalic contained start="<em\>" end="</em>"me=e-5 contains=@htmlTop

  syn region htmlItalic start="<i\>" end="</i>"me=e-4 contains=@htmlTop,htmlItalicBold,htmlItalicUnderline
  syn region htmlItalic start="<em\>" end="</em>"me=e-5 contains=@htmlTop
  syn region htmlItalicBold contained start="<b\>" end="</b>"me=e-4 contains=@htmlTop,htmlItalicBoldUnderline
  syn region htmlItalicBold contained start="<strong\>" end="</strong>"me=e-9 contains=@htmlTop,htmlItalicBoldUnderline
  syn region htmlItalicBoldUnderline contained start="<u\>" end="</u>"me=e-4 contains=@htmlTop
  syn region htmlItalicUnderline contained start="<u\>" end="</u>"me=e-4 contains=@htmlTop,htmlItalicUnderlineBold
  syn region htmlItalicUnderlineBold contained start="<b\>" end="</b>"me=e-4 contains=@htmlTop
  syn region htmlItalicUnderlineBold contained start="<strong\>" end="</strong>"me=e-9 contains=@htmlTop

  syn region htmlLink start="<a\>\_[^>]*\<href\>" end="</a>"me=e-4 contains=@Spell,htmlTag,htmlEndTag,htmlSpecialChar,htmlPreProc,htmlComment,javaScript,@htmlPreproc
  syn region htmlH1 start="<h1\>" end="</h1>"me=e-5 contains=@htmlTop
  syn region htmlH2 start="<h2\>" end="</h2>"me=e-5 contains=@htmlTop
  syn region htmlH3 start="<h3\>" end="</h3>"me=e-5 contains=@htmlTop
  syn region htmlH4 start="<h4\>" end="</h4>"me=e-5 contains=@htmlTop
  syn region htmlH5 start="<h5\>" end="</h5>"me=e-5 contains=@htmlTop
  syn region htmlH6 start="<h6\>" end="</h6>"me=e-5 contains=@htmlTop
  syn region htmlHead start="<head\>" end="</head>"me=e-7 end="<body\>"me=e-5 end="<h[1-6]\>"me=e-3 contains=htmlTag,htmlEndTag,htmlSpecialChar,htmlPreProc,htmlComment,htmlLink,htmlTitle,javaScript,cssStyle,@htmlPreproc
  syn region htmlTitle start="<title\>" end="</title>"me=e-8 contains=htmlTag,htmlEndTag,htmlSpecialChar,htmlPreProc,htmlComment,javaScript,@htmlPreproc
endif

syn keyword htmlTagName         contained noscript
syn keyword htmlSpecialTagName  contained script style
if main_syntax != 'java' || exists("java_javascript")
  " JAVA SCRIPT
  syn include @htmlJavaScript syntax/javascript.vim
  unlet b:current_syntax
  syn region  javaScript start=+<script[^>]*>+ keepend end=+</script>+me=s-1 contains=@htmlJavaScript,htmlCssStyleComment,htmlScriptTag,@htmlPreproc
  syn region  htmlScriptTag     contained start=+<script+ end=+>+       contains=htmlTagN,htmlString,htmlArg,htmlValue,htmlTagError,htmlEvent
  HtmlHiLink htmlScriptTag htmlTag

  " html events (i.e. arguments that include javascript commands)
  if exists("html_extended_events")
    syn region htmlEvent        contained start=+\<on\a\+\s*=[\t ]*'+ end=+'+ contains=htmlEventSQ
    syn region htmlEvent        contained start=+\<on\a\+\s*=[\t ]*"+ end=+"+ contains=htmlEventDQ
  else
    syn region htmlEvent        contained start=+\<on\a\+\s*=[\t ]*'+ end=+'+ keepend contains=htmlEventSQ
    syn region htmlEvent        contained start=+\<on\a\+\s*=[\t ]*"+ end=+"+ keepend contains=htmlEventDQ
  endif
  syn region htmlEventSQ        contained start=+'+ms=s+1 end=+'+me=s-1 contains=@htmlJavaScript
  syn region htmlEventDQ        contained start=+"+ms=s+1 end=+"+me=s-1 contains=@htmlJavaScript
  HtmlHiLink htmlEventSQ htmlEvent
  HtmlHiLink htmlEventDQ htmlEvent

  " a javascript expression is used as an arg value
  syn region  javaScriptExpression contained start=+&{+ keepend end=+};+ contains=@htmlJavaScript,@htmlPreproc
endif

if main_syntax != 'java' || exists("java_vb")
  " VB SCRIPT
  syn include @htmlVbScript syntax/vb.vim
  unlet b:current_syntax
  syn region  javaScript start=+<script [^>]*language *=[^>]*vbscript[^>]*>+ keepend end=+</script>+me=s-1 contains=@htmlVbScript,htmlCssStyleComment,htmlScriptTag,@htmlPreproc
endif

syn cluster htmlJavaScript      add=@htmlPreproc

if main_syntax != 'java' || exists("java_css")
  " embedded style sheets
  syn keyword htmlArg           contained media
  syn include @htmlCss syntax/css.vim
  unlet b:current_syntax
  syn region cssStyle start=+<style+ keepend end=+</style>+ contains=@htmlCss,htmlTag,htmlEndTag,htmlCssStyleComment,@htmlPreproc
  syn match htmlCssStyleComment contained "\(<!--\|-->\)"
  syn region htmlCssDefinition matchgroup=htmlArg start='style="' keepend matchgroup=htmlString end='"' contains=css.*Attr,css.*Prop,cssComment,cssLength,cssColor,cssURL,cssImportant,cssError,cssString,@htmlPreproc
  HtmlHiLink htmlStyleArg htmlString
endif

if main_syntax == "pyxl"
  " synchronizing (does not always work if a comment includes legal
  " html tags, but doing it right would mean to always start
  " at the first line, which is too slow)
  syn sync match htmlHighlight groupthere NONE "<[/a-zA-Z]"
  syn sync match htmlHighlight groupthere javaScript "<script"
  syn sync match htmlHighlightSkip "^.*['\"].*$"
  syn sync minlines=10
endif

" The default highlighting.
if version >= 508 || !exists("did_html_syn_inits")
  if version < 508
    let did_html_syn_inits = 1
  endif
  HtmlHiLink htmlTag                     Function
  HtmlHiLink htmlEndTag                  Identifier
  HtmlHiLink htmlArg                     Type
  HtmlHiLink htmlTagName                 htmlStatement
  HtmlHiLink htmlSpecialTagName          Exception
  HtmlHiLink htmlValue                     String
  HtmlHiLink htmlSpecialChar             Special

  if !exists("html_no_rendering")
    HtmlHiLink htmlH1                      Title
    HtmlHiLink htmlH2                      htmlH1
    HtmlHiLink htmlH3                      htmlH2
    HtmlHiLink htmlH4                      htmlH3
    HtmlHiLink htmlH5                      htmlH4
    HtmlHiLink htmlH6                      htmlH5
    HtmlHiLink htmlHead                    PreProc
    HtmlHiLink htmlTitle                   Title
    HtmlHiLink htmlBoldItalicUnderline     htmlBoldUnderlineItalic
    HtmlHiLink htmlUnderlineBold           htmlBoldUnderline
    HtmlHiLink htmlUnderlineItalicBold     htmlBoldUnderlineItalic
    HtmlHiLink htmlUnderlineBoldItalic     htmlBoldUnderlineItalic
    HtmlHiLink htmlItalicUnderline         htmlUnderlineItalic
    HtmlHiLink htmlItalicBold              htmlBoldItalic
    HtmlHiLink htmlItalicBoldUnderline     htmlBoldUnderlineItalic
    HtmlHiLink htmlItalicUnderlineBold     htmlBoldUnderlineItalic
    HtmlHiLink htmlLink                    Underlined
    if !exists("html_my_rendering")
      hi def htmlBold                term=bold cterm=bold gui=bold
      hi def htmlBoldUnderline       term=bold,underline cterm=bold,underline gui=bold,underline
      hi def htmlBoldItalic          term=bold,italic cterm=bold,italic gui=bold,italic
      hi def htmlBoldUnderlineItalic term=bold,italic,underline cterm=bold,italic,underline gui=bold,italic,underline
      hi def htmlUnderline           term=underline cterm=underline gui=underline
      hi def htmlUnderlineItalic     term=italic,underline cterm=italic,underline gui=italic,underline
      hi def htmlItalic              term=italic cterm=italic gui=italic
    endif
  endif

  HtmlHiLink htmlPreStmt            PreProc
  HtmlHiLink htmlPreError           Error
  HtmlHiLink htmlPreProc            PreProc
  HtmlHiLink htmlPreAttr            String
  HtmlHiLink htmlPreProcAttrName    PreProc
  HtmlHiLink htmlPreProcAttrError   Error
  HtmlHiLink htmlSpecial            Special
  HtmlHiLink htmlSpecialChar        Special
  HtmlHiLink htmlString             String
  HtmlHiLink htmlStatement          Statement
  HtmlHiLink htmlComment            Comment
  HtmlHiLink htmlCommentPart        Comment
  HtmlHiLink htmlValue              String
  HtmlHiLink htmlCommentError       htmlError
  HtmlHiLink htmlTagError           htmlError
  HtmlHiLink htmlEvent              javaScript
  HtmlHiLink htmlError              Error

  HtmlHiLink javaScript             Special
  HtmlHiLink javaScriptExpression   javaScript
  HtmlHiLink htmlCssStyleComment    Comment
  HtmlHiLink htmlCssDefinition      Special
endif

delcommand HtmlHiLink

if version >= 508 || !exists("did_python_syn_inits")
  if version <= 508
    let did_python_syn_inits = 1
    command -nargs=+ HiLink hi link <args>
  else
    command -nargs=+ HiLink hi def link <args>
  endif

  " The default highlight links.  Can be overridden later.
  HiLink pythonStatement	Statement
  HiLink pythonConditional	Conditional
  HiLink pythonRepeat		Repeat
  HiLink pythonOperator		Operator
  HiLink pythonException	Exception
  HiLink pythonInclude		Include
  HiLink pythonDecorator	Define
  HiLink pythonFunction		Function
  HiLink pythonComment		Comment
  HiLink pythonTodo		Todo
  HiLink pythonString		String
  HiLink pythonRawString	String
  HiLink pythonEscape		Special
  if !exists("python_no_number_highlight")
    HiLink pythonNumber		Number
  endif
  if !exists("python_no_builtin_highlight")
    HiLink pythonBuiltin	Function
  endif
  if !exists("python_no_exception_highlight")
    HiLink pythonExceptions	Structure
  endif
  if exists("python_space_error_highlight")
    HiLink pythonSpaceError	Error
  endif
  if !exists("python_no_doctest_highlight")
    HiLink pythonDoctest	Special
    HiLink pythonDoctestValue	Define
  endif

  HiLink pyxlPython Special
  HiLink pyxlPythonNormal Normal

  delcommand HiLink
endif

let b:current_syntax = "pyxl"

if main_syntax == 'pyxl'
  unlet main_syntax
endif

let &cpo = s:cpo_save
unlet s:cpo_save

" vim:set sw=2 sts=2 ts=8 noet:
