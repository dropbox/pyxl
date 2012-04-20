;;; pyxl-mode.el --- major mode for editing pyxl enabled Python
;;;
;;; @author Akhil Wable
;;;
;;; To install, drop this anywhere on your load path, and add the following to
;;; your ~/.emacs file (GNU Emacs) or ~/.xemacs/init.el file (XEmacs):
;;;
;;; (autoload 'pyxl-mode "pyxl-mode" "Major mode for editing pyxl" t)
;;; (setq auto-mode-alist
;;;      (cons '("\\.py\\'" . pyxl-mode) auto-mode-alist))
;;;

(require 'cl)
(require 'python)

(defcustom pyxl-mode-hook nil
  "list of functions to be executed on entry to pyxl-mode."
  :type 'hook
  :group 'python)

(defun pyxl-context-p ()
  "Does the range include some HTML?"
  (let ((start-rexp "([ \n\t]*<")
        (end-rexp ">[ \n\t]*)"))
    (let ((backward-start (save-excursion (re-search-backward start-rexp nil t)))
          (backward-end (save-excursion (re-search-backward end-rexp nil t))))
      (if (and backward-start
               (or (not backward-end) (< backward-end backward-start)))
          backward-start
        nil))))

(defun pyxl-back-to-indentation ()
  (let ((first-non-indent
         (save-excursion
           (back-to-indentation)
           (point))))
    (if (< (point) first-non-indent)
        (back-to-indentation))))

(defun pyx-indent-line-helper ()
  "Indent a line containing html."
  ;; nesting regex matches either an opening tag OR a closing tag
  (let ((nesting-regex "\\(<[:a-zA-Z][:a-zA-Z0-9_]*\\)\\|\\(</\\|/>\\)")
        (indent-from (line-beginning-position))
        (depth 1))
    (save-excursion
      (re-search-backward "([ \n\t]*<" nil t)
      (let ((starting-indent (current-indentation)))
        (while (and (< (point) indent-from)
                    (re-search-forward nesting-regex indent-from t))
          (if (match-string 1) (incf depth))
          (if (match-string 2) (decf depth)))
        (goto-char indent-from)
        (indent-line-to
         (+ starting-indent
            (* 4 depth)
            (if (looking-at "[ \t]*\\(?:</\\|/>\\)") -4 0)))))
    (pyxl-back-to-indentation)))

(defun pyxl-indent-line ()
  "Modify indent for a line of html."
  (interactive)
  (save-excursion
    (if (pyxl-context-p)
     ;; If a line is inside html, use the custom indent function
        (pyx-indent-line-helper)
    ;; Fall back to regular python indentation for no html
    (python-indent-line)))

  (pyxl-back-to-indentation))

(defun pyxl-indent-region (start end)
  (save-excursion
    (goto-char end)
    (setq end (point-marker))
    (goto-char start)
    (or (bolp) (forward-line 1))
    (while (< (point) end)
      (or (and (bolp) (eolp))
          (pyxl-indent-line))
      (forward-line 1))
    (move-marker end nil)))

(defcustom pyxl-default-face 'default
  "Default face in pyxl-mode buffers."
  :type 'face
  :group 'pyxl-mode)

(defconst pyxl-font-lock-keywords
  (append
   (list
    ;; tags
    '("\\(</?\\)\\([:a-zA-Z0-9_]+\\)" (1 pyxl-default-face) (2 font-lock-function-name-face))

    ;; comments
    '("<!--[^>]*-->" (0 font-lock-comment-face))

    ;; XML entities
    '("&\\w+;" . font-lock-constant-face)
    )
   python-font-lock-keywords)
  "Font Lock for pyxl mode.")

;;;###autoload
(define-derived-mode pyxl-mode python-mode "pyxl"
  "Major mode for editing Python code with pyxl."

  ;; Adapted from python-mode.el
  (set (make-local-variable 'font-lock-defaults)
       '(pyxl-font-lock-keywords
         nil
         nil
         nil
         nil
         '(font-lock-syntactic-keywords . python-font-lock-syntactic-keywords)
         ;; This probably isn't worth it.
         ;; (font-lock-syntactic-face-function
         ;;  . python-font-lock-syntactic-face-function)
         ))

  (setq indent-line-function 'pyxl-indent-line)
  (setq indent-region-function 'pyxl-indent-region)
  (run-hooks 'pyxl-mode-hook))

(provide 'pyxl-mode)

;; In python-mode.el RET is bound to newline-and-indent, which indents the next line if necessary.
;; In python.el which we're extending, this is bound to C-j instead.
;; This binds RET to newline-and-indent
(add-hook
 'python-mode-hook
 '(lambda () (define-key python-mode-map "\C-m" 'newline-and-indent)))
