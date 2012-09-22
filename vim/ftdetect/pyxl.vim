function! Detect_pyxl()
	let re = 'coding[:=]\s*pyxl\>'
	if getline(1) =~ re || getline(2) =~ re
		set ft=pyxl
	endif
endfunction

augroup filetypedetect
	au BufRead,BufNewFile *		call Detect_pyxl()
augroup END
