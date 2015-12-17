#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#------------------------------------------------------------------------------
# Meowkdown viewer
# Kazuei HIRONAKA <kzh@nyacom.net> 2015 (C)
#------------------------------------------------------------------------------

import wx
import wx.html2
import gettext
import os
import time
import subprocess
import sys
import re
import math

# import frame1

#------------------------------------------------------------------------------
# Constant valuess

#------------------------------------------------------------------------------
TOK_HR		= 0
TOK_PRE1	= 1
TOK_PRE2	= 2
TOK_SETEXH2	= 3
TOK_SETEXH1	= 4

TOK_ATHXH6	= 5
TOK_ATHXH5	= 6
TOK_ATHXH4	= 7
TOK_ATHXH3	= 8 
TOK_ATHXH2	= 9
TOK_ATHXH1	= 10

TOK_LSTSPC0	= 11
TOK_LSTSPC1	= 12
TOK_LSTSPC2	= 13
TOK_LSTSPC3	= 14
TOK_LSTSPC4	= 15

TOK_LSTTAB1	= 16
TOK_LSTTAB2	= 17
TOK_LSTTAB3	= 18
TOK_LSTTAB4	= 19

TOK_NLSTSPC0	= 20
TOK_NLSTSPC1	= 21
TOK_NLSTSPC2	= 22
TOK_NLSTSPC3	= 23
TOK_NLSTSPC4	= 24

TOK_NLSTTAB1	= 25
TOK_NLSTTAB2	= 26
TOK_NLSTTAB3	= 27
TOK_NLSTTAB4	= 28

TOK_TABLE	= 29
TOK_QUOTE	= 30

TOK_REF		= 31

TOK_BRANK	= 32
TOK_PLAIN	= 33

#------------------------------------------------------------------------------
# Class .md parser
#------------------------------------------------------------------------------
class mdParseClass:
	def __init__(self):
		self.toks = []

		# ^^^^^ Upper is match high priolity ^^^^^
		self.toks.append(mdToken(r'^\s*-+()\s*$', TOK_SETEXH2))	# setex h2
		self.toks.append(mdToken(r'^\s*=+()\s*$', TOK_SETEXH1))	# setex h1
		self.toks.append(mdToken(r'^\s*([_\-\*])\s*\1\s*\1\s*\1*$', TOK_HR))	# hr

		self.toks.append(mdToken(r'^\s{,4}######\s*(.*)[#\s\t]*$', TOK_ATHXH6))	# atx h6
		self.toks.append(mdToken(r'^\s{,4}#####\s*(.*)[#\s\t]*$', TOK_ATHXH5))	# atx h5
		self.toks.append(mdToken(r'^\s{,4}####\s*(.*)[#\s\t]*$', TOK_ATHXH4))	# atx h4
		self.toks.append(mdToken(r'^\s{,4}###\s*(.*)[#\s\t]*$', TOK_ATHXH3))	# atx h3
		self.toks.append(mdToken(r'^\s{,4}##\s*(.*)[#\s\t]*$', TOK_ATHXH2))	# atx h2
		self.toks.append(mdToken(r'^\s{,4}#\s*(.*)[#\s\t]*$',	TOK_ATHXH1))	# atx h1


		self.toks.append(mdToken(r'^[0-9]+\.[\s\t]+(.*)$', TOK_NLSTSPC0))		# num list
		self.toks.append(mdToken(r'^\t[0-9]+\.[\s\t]+(.*)$', TOK_NLSTTAB1))		# num list
		self.toks.append(mdToken(r'^\s[0-9]+\.[\s\t]+(.*)$', TOK_NLSTSPC1))		# num list
		self.toks.append(mdToken(r'^\t\t[0-9]+\.[\s\t]+(.*)$', TOK_NLSTTAB2))		# num list
		self.toks.append(mdToken(r'^\s\s[0-9]+\.[\s\t]+(.*)$', TOK_NLSTSPC2))		# num list
		self.toks.append(mdToken(r'^\t\t\t[0-9]+\.[\s\t]+(.*)$', TOK_NLSTTAB3))		# num list
		self.toks.append(mdToken(r'^\s\s\s[0-9]+\.[\s\t]+(.*)$', TOK_NLSTSPC3))		# num list
		self.toks.append(mdToken(r'^\t\t\t\t[0-9]+\.[\s\t]+(.*)$', TOK_NLSTTAB4))	# num list
		self.toks.append(mdToken(r'^\s\s\s\s[0-9]+\.[\s\t]+(.*)$', TOK_NLSTSPC4))	# num list

		self.toks.append(mdToken(r'^[\*\-\+][\s\t]+(.*)$', TOK_LSTSPC0))		# disk list
		self.toks.append(mdToken(r'^\t[\*\-\+][\s\t]+(.*)$', TOK_LSTTAB1))		# disk list
		self.toks.append(mdToken(r'^\s[\*\-\+][\s\t]+(.*)$', TOK_LSTSPC1))		# disk list
		self.toks.append(mdToken(r'^\t\t[\*\-\+][\s\t]+(.*)$', TOK_LSTTAB2))		# disk list
		self.toks.append(mdToken(r'^\s\s[\*\-\+][\s\t]+(.*)$', TOK_LSTSPC2))		# disk list
		self.toks.append(mdToken(r'^\t\t\t[\*\-\+][\s\t]+(.*)$', TOK_LSTTAB3))		# disk list
		self.toks.append(mdToken(r'^\s\s\s[\*\-\+][\s\t]+(.*)$', TOK_LSTSPC3))		# disk list
		self.toks.append(mdToken(r'^\t\t\t\t[\*\-\+][\s\t]+(.*)$', TOK_LSTTAB4))	# disk list
		self.toks.append(mdToken(r'^\s\s\s\s[\*\-\+][\s\t]+(.*)$', TOK_LSTSPC4))	# disk list

		self.toks.append(mdToken(r'^\s{,4}\|(.*)\|[\s\t]*$', TOK_TABLE))	# table
		self.toks.append(mdToken(r'^\s{,4}>(.*)$', TOK_QUOTE))			# quote

		self.toks.append(mdToken(r'^\s{,3}```!*(.*)$',		TOK_PRE1))	# pre 1
		self.toks.append(mdToken(r'^\s{3}(.*)$',		TOK_PRE2))	# pre 2

		self.toks.append(mdToken(r'^\s{,4}\[(.*)\]:.*$',		TOK_REF))	# ref
		self.toks.append(mdToken(r'^\s{,4}\[(.*)\]:.*\s+".*"$',		TOK_REF))	# ref

		self.toks.append(mdToken(r'^\n()$',			TOK_BRANK))	# brank
		self.toks.append(mdToken(r'^.*$',			TOK_PLAIN))	# plain


		for t in self.toks:	# compile all regex patterns
			t.compile()


	def line_parse(self, line):
		for t in self.toks:
			m = t.p.search(line)
			if m:
				if m.lastindex != None:
					return (line, m.group(m.lastindex), t.token)
				else:
					return (line, None, t.token)

		return (line, None, "plain")	# nothing matched


#------------------------------------------------------------------------------
# Class mdToken for parsing
#------------------------------------------------------------------------------
class mdToken:
	def __init__(self, pat, token):
		self.pat = pat 
		self.token = token 
		self.p = None

	def compile(self):
		self.p = re.compile(self.pat) 	# regex pattern compile

#------------------------------------------------------------------------------
# Device context class
#------------------------------------------------------------------------------
class md2HTML:
	def __init__(self):
		self.css = ""
		self.ref = {}	# reference dict

		self.apppath = ""
		self.filepath = ""

	def appendHeader(self, s):
		s.append('<html>\n')
		s.append('<head>\n')

		s.append('<style type="text/css">\n')
		s.append('<!--\n')
		s.append(self.css)
		s.append('-->\n')
		s.append('</style>\n')

		#s.append('<link rel="stylesheet" type="text/css" href="default.css">\n')
		s.append('<meta http-equiv="Pragma" content="no-cache">\n')
		s.append('<meta http-equiv="Cache-Control" content="no-cache">\n')
		s.append('<meta http-equiv="Expires" content="0">\n')
		s.append('</head>\n')

	def refline2html(self, m):
		if (m.lastindex > 1):
			return r'<a href="' + self.ref[m.group(2)] + '">' + m.group(1) + '</a>'

		return r'<a href="' + self.ref[m.group(1)] + '">' + m.group(1) + '</a>'

	def img2html(self, m):
		ret = ''

		if (m.lastindex > 5):
			ret += r'<img src="' + m.group(3) + '?' + str(time.time()) + r'" alt="' + m.group(1) + r'" title="' + m.group(4) + r'" ' + m.group(2) + r'>'

		elif (m.lastindex > 4):
			ret += r'<img src="' + m.group(2) + '?' + str(time.time()) + '" alt="' + m.group(1) + '" ' + m.group(3) + r'>'	# src + option + title

		elif (m.lastindex > 3):
			ret += r'<img src="' + m.group(3) + '?' + str(time.time()) + '"' + m.group(2) + r'>'	# src + option

		elif (m.lastindex > 2):
			ret += r'<img src="' + m.group(2) + '?' + str(time.time()) + '">'	# src

		return ret

	def img2html_r(self, m):
		ret = r'<div style="text-align:right;">'

		if (m.lastindex > 5):
			ret += r'<img src="' + m.group(3) + '?' + str(time.time()) + r'" alt="' + m.group(1) + r'" title="' + m.group(4) + r'" ' + m.group(2) + r'>'

		elif (m.lastindex > 4):
			ret += r'<img src="' + m.group(2) + '?' + str(time.time()) + '" alt="' + m.group(1) + '" ' + m.group(3) + r'>'	# src + option + title

		elif (m.lastindex > 3):
			ret += r'<img src="' + m.group(3) + '?' + str(time.time()) + '"' + m.group(2) + r'>'	# src + option

		elif (m.lastindex > 2):
			ret += r'<img src="' + m.group(2) + '?' + str(time.time()) + '">'	# src

		ret += r'</div>'

		return ret

	def img2html_c(self, m):
		ret = r'<div style="text-align:center;">'

		if (m.lastindex > 5):
			ret += r'<img src="' + m.group(3) + '?' + str(time.time()) + r'" alt="' + m.group(1) + r'" title="' + m.group(4) + r'" ' + m.group(2) + r'>'

		elif (m.lastindex > 4):
			ret += r'<img src="' + m.group(2) + '?' + str(time.time()) + '" alt="' + m.group(1) + '" ' + m.group(3) + r'>'	# src + option + title

		elif (m.lastindex > 3):
			ret += r'<img src="' + m.group(3) + '?' + str(time.time()) + '"' + m.group(2) + r'>'	# src + option

		elif (m.lastindex > 2):
			ret += r'<img src="' + m.group(2) + '?' + str(time.time()) + '">'	# src

		ret += r'</div>'

		return ret


	def imgref2html(self, m):
		if (m.lastindex > 2):
			return r'<img src="' + self.ref[m.group(1)] + '"' + m.group(2) + '>'

		return r'<img src="' + self.ref[m.group(1)] + '">'

	def imgref2html_r(self, m):
		if (m.lastindex > 2):
			return r'<div style="text-align:right;"><img src="' + self.ref[m.group(1)] + '"' + m.group(2) + '></div>'

		return r'<div style="text-align:right;><img src="' + self.ref[m.group(1)] + '"></div>'

	def imgref2html_c(self, m):
		if (m.lastindex > 2):
			return r'<div style="text-align:center;"><img src="' + self.ref[m.group(1)] + '"' + m.group(2) + '></div>'

		return r'<div style="text-align:center;"><img src="' + self.ref[m.group(1)] + '"></div>'
	

	def plain2html(self, s):
		s = re.sub(r'<', r'&lt;', s)
		s = re.sub(r'>', r'&gt;', s)

		return s
		
	def line2html(self, s):
		s = re.sub(r'\\[#*-_+](.*)', r'\1', s)	# escape

		s = re.sub(r'<(http://.*)>(\s|$)', r'<a href="\1" target="_blank">\1</a> ', s)		# auto link (URI)
		s = re.sub(r'<(.*@.*)>(\s|$)', r'<a href="mailto:\1" target="_blank">\1</a> ', s)	# auto link (mail)

		s = re.sub(r'!\[\s(.*)@(.*)\s\]\((.*)\s+"(.*)"\)(\s|$)', self.img2html_c, s)	# centered img with name and tag
		s = re.sub(r'!\[\s(.*)@(.*)\]\((.*)\s+"(.*)"\)(\s|$)', self.img2html_r, s)	# rightered img with name and tag
		s = re.sub(r'!\[(.*)@(.*)\]\((.*)\s+"(.*)"\)(\s|$)', self.img2html, s)		# img with name and tag

		s = re.sub(r'!\[\s(.*)\s\]\((.*)\s+"(.*)"\)(\s|$)', self.img2html_c, s)		# centered img with name
		s = re.sub(r'!\[\s(.*)\]\((.*)\s+"(.*)"\)(\s|$)', self.img2html_r, s)		# rightered img with name
		s = re.sub(r'!\[(.*)\]\((.*)\s+"(.*)"\)(\s|$)',	self.img2html, s)		# img with name

		s = re.sub(r'!\[\s(.*)@(.*)\s\]\((.*)\)(\s|$)', self.img2html_c, s)		# img
		s = re.sub(r'!\[\s(.*)@(.*)\]\((.*)\)(\s|$)', self.img2html_r, s)		# img
		s = re.sub(r'!\[(.*)@(.*)\]\((.*)\)(\s|$)', self.img2html, s)			# img

		s = re.sub(r'!\[\s(.*)\s\]\((.*)\)(\s|$)', self.img2html_c, s)			# img
		s = re.sub(r'!\[\s(.*)\]\((.*)\)(\s|$)', self.img2html_r, s)			# img
		s = re.sub(r'!\[(.*)\]\((.*)\)(\s|$)', self.img2html, s)			# img

		s = re.sub(r'!\[\s(.*)@(.*)\s\](\s|$)',	self.imgref2html_c, s)			# img with ref
		s = re.sub(r'!\[\s(.*)@(.*)\](\s|$)',	self.imgref2html_r, s)			# img with ref
		s = re.sub(r'!\[(.*)@(.*)\](\s|$)',	self.imgref2html, s)			# img with ref

		s = re.sub(r'!\[\s(.*)\s\](\s|$)',	self.imgref2html_c, s)			# img with ref
		s = re.sub(r'!\[\s(.*)\](\s|$)',	self.imgref2html_r, s)			# img with ref
		s = re.sub(r'!\[(.*)\](\s|$)',		self.imgref2html, s)			# img with ref

		s = re.sub(r'\[(.*)\]\((.*)\s+"(.*)"\)(\s|$)',	r'<a href="\2" target="_blank" title="\3">\1</a>', s)	# link with name
		s = re.sub(r'\[(.*)\]\((.*)\)(\s|$)',		r'<a href="\2" target="_blank">\1</a>', s)	# link

		s = re.sub(r'\[(.*)\]\[\](\s|$)',	self.refline2html, s)	# ref link
		s = re.sub(r'\[(.*)\]\[(.*)\](\s|$)',	self.refline2html, s)	# ref link

		s = re.sub(r'\s__(.*)__(\s|$)', 	r'<strong> \1</strong>', s)	# bold
		s = re.sub(r'\s\*\*(.*)\*\*(\s|$)', 	r'<strong> \1</strong>', s)	# bold
		s = re.sub(r'\s_(.*)_(\s|$)', 		r'<em> \1</em>', s)		# italic
		s = re.sub(r'\s\*(.*)*(\s|$)', 		r'<em> \1</em>', s)		# italic
		s = re.sub(r'\s\`(.*)\`(\s|$)',		r'<code> \1</code>', s)		# code
		s = re.sub(r'\s~~(.*)~~(\s|$)', 	r'<s> \1</s>', s)		# strike
		s = re.sub(r'\s\s$', 			r'<br> \n', s)			# nr

		return s.rstrip('\n\r')

	def numlist(self, lines, s):
		i = 0
		s.append("<ol>\n")

		last_lv = TOK_NLSTSPC0

		while (i < len(lines)):
			l, v, t = lines[i]	# current

			if ((t >= TOK_NLSTSPC0 and t <= TOK_NLSTTAB4) or t == TOK_BRANK):
				if (i+1 < len(lines)):
					if (t != TOK_BRANK):
						s.append("<li>" + self.line2html(v) + "</li>\n")
						last_lv = t

					ll, vv, tt = lines[i+1]	# lookup next level

					if (tt >= TOK_NLSTSPC0 and tt <= TOK_NLSTTAB4):
						if (tt > last_lv):	# deeper level
							i += self.numlist(lines[i+1:], s) + 1
							break
						elif (tt < last_lv):	# less level
                                                        s.append("</ol>\n")

					elif (tt == TOK_BRANK):
						if (t == TOK_BRANK):
							break

						s.append("<br>\n")

					elif (tt >= TOK_LSTSPC0 and tt <= TOK_LSTTAB4):
						if (tt > (last_lv-9)): # more deeper
							i += self.disklist(lines[i:], s) + 1
						else:
							break;

					else:
						break
				else:
					s.append("<li>" + self.line2html(v) + "</li>\n")

			else:
				break

			i += 1

		s.append("</ol>\n")
		
		return i


	def disklist(self, lines, s):
		i = 0
		s.append("<ul>\n")

		last_lv = TOK_NLSTSPC0

		while (i < len(lines)):
			l, v, t = lines[i]	# current

			if ((t >= TOK_LSTSPC0 and t <= TOK_LSTTAB4) or t == TOK_BRANK):
				if (i+1 < len(lines)):
					if (t != TOK_BRANK):
						s.append("<li>" + self.line2html(v) + "</li>\n")
						last_lv = t

					ll, vv, tt = lines[i+1]	# lookup next level

					if (tt >= TOK_LSTSPC0 and tt <= TOK_LSTTAB4):
						if (tt > last_lv):	# deeper level
							i += self.disklist(lines[i+1:], s) + 1
							break
						elif (tt < last_lv):	# less level
                                                        s.append("</ul>\n")

					elif (tt == TOK_BRANK):
						if (t == TOK_BRANK):
							break

						s.append("<br>\n")

					elif (tt >= TOK_NLSTSPC0 and tt <= TOK_NLSTTAB4):
						if (tt > (last_lv+9)): # more deeper
							i += self.numlist(lines[i+1:], s) + 1

						else:
							break

					else:
						break
				else:
					s.append("<li>" + self.line2html(v) + "</li>\n")

			else:
				break

			i += 1

		s.append("</ul>\n")
		
		return i


	def paragraph(self, lines, s):
		i = 0
		s.append("<p>")

		while (i < len(lines)):
			l, v, t = lines[i]
			if (t == TOK_PLAIN):
				s.append(self.line2html(l))
			else:
				i -= 1
				break
			i += 1

		s.append("</p>\n")

		return i

	
	def quotedpreblock(self, lines, s):
		i = 0
		l, v, t = lines[i]

		# left lines are enough?
		if (1 >= len(lines)):
			s.append("<pre>" + l + "</pre>\n")
			return 1


		i += 1
		# is pipe command?
		if (v != ''):
			cwd = os.getcwd()	# for revert
			os.chdir(self.apppath)

			cmd = v + ' "' + self.filepath + '"'
#			cmd = 'pwd'
			pipebuf = ""

			while (i < len(lines)):
				l, v, t = lines[i]

				if (t == TOK_PRE1):
					i += 1
					break

				else:
					pipebuf = pipebuf + l

				i += 1

			print "ExtCmd: " + cmd
			proc = subprocess.Popen(cmd,
				shell = True,
				stdin = subprocess.PIPE,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE)

#			print "pipe: " + pipebuf

			proc_stdout, proc_stderr = proc.communicate(pipebuf)
			print proc_stdout
			print proc_stderr

			if (proc.returncode != 0):
				s.append("<pre>\n")
				print proc_stderr
				s.append("</pre>\n")

			os.chdir(cwd)

		else:
			s.append("<pre>\n")
			while (i < len(lines)):
				l, v, t = lines[i]

				if (t == TOK_PRE1):
					i += 1
					break

				else:
					s.append(self.plain2html(l) + "\n")

				i += 1

			s.append("</pre>\n")

		return i


	def spacedpreblock(self, lines, s):
		i = 0
		s.append("<pre>\n")

		while (i < len(lines)):
			l, v, t = lines[i]

			if (t == TOK_PRE2):
				s.append(self.plain2html(v) + "\n")

			else:
				i -= 1
				break

			i += 1

		s.append("</pre>\n")

		return i


	def tablealign(self, tc):
		align = []

		for td in tc:
			if (re.search(r":---*:", td)):
				align.append("center")

			elif (re.search(r":---", td)):
				align.append("left")

			elif (re.search(r"---:", td)):
				align.append("right")

			else:
				align.append("left")

		return align

				
	def tableblock(self, lines, s):
		i = 0
		align = []

		# left lines are not sufficent to make a valid table
		if (i+1 >= len(lines)):
			l, v, t = lines[i]
			s.append("<p>" + self.line2html(l) + "</p>\n")
			return 1

		else:
			l, v, t = lines[i]
			ll, vv, tt = lines[i+1]

			if (tt != TOK_TABLE):
				s.append("<p>" + self.line2html(l) + "</p>\n")
				s.append("<p>" + self.line2html(ll) + "</p>\n")
				return 2

		s.append("<table>\n")

		while (i < len(lines)):
			l, v, t = lines[i]

			if (t != TOK_TABLE):
				break


			tc = re.split(r"\|", l)[1:-1]   # take slice
			tcl = len(tc)

			if (re.search(r":*---:*\|", l)):	# Table align line
				# s.append("sc:" + str(tc) + str(tcl))
				align = self.tablealign(tc)

			else:					# normal line
				s.append("<tr>\n")
				# s.append("tc:" + str(tc) + str(tcl))

				if (i == 0):	# if normal line and it is 1st line, the line is a header
					j = 0
					for v in tc:          # table header
						a = align[j] if j < len(align) else "left"
						s.append("<th align=" + a + ">" + v + "</th>\n")
						j += 1

				else:
					j = 0
					for v in tc:          # table content
						a = align[j] if j < len(align) else "left"
						s.append("<td align=" + a + ">" + v + "</td>\n")
						j += 1

				s.append("</tr>\n")

			i += 1

		s.append("</table>\n")

		return i


	def blockquote(self, lv, lines, s):
		i = 0

		s.append("<blockquote>\n")

		l, v, t = lines[i]
		quot = re.split(r">", l)
		llv = len(quot)

		if (lv < llv):
			i += self.blockquote(lv+1, lines[i:], s)

		while (i < len(lines)):
			l, v, t = lines[i]

			if (t != TOK_QUOTE):
				i -= 1
				break

			quot = re.split(r">", l)
			llv = len(quot)

			if (lv < llv):		# to deeper level
				i += self.blockquote(lv+1, lines[i:], s)

			elif (lv > llv):	# to upper level
				i -= 1
				break;

			else:
				s.append(self.line2html(quot[lv-1]) + "<br>\n")

			i += 1

		s.append("</blockquote>\n")

		return i

	def reference(self, l):

		m = re.match(r'\[(.*)\]:(.*)\s+"(.*)"$', l)
		if (m):
			print m.group(0)
			print m.group(1)
			self.ref[m.group(1)] = m.group(2)


		m = re.match(r'\[(.*)\]:(.*)$', l)
		if (m):
			self.ref[m.group(1)] = m.group(2)

		return
		

	def toHtml(self, lines):
		htmlbuf = []
		self.appendHeader(htmlbuf)			# Append header

		# refsearch
		i = 0
		while (i < len(lines)):
			l, v, t = lines[i]

			if (t == TOK_REF):
				self.reference(l)

			i += 1

		# normal token
		i = 0
		while (i < len(lines)):

			l, v, t = lines[i]

			if (t == TOK_HR):			# Holizontal line
				htmlbuf.append("<hr>\n")

			if (t == TOK_SETEXH1):
				htmlbuf.append("<hr class='h1'>\n")

			if (t == TOK_SETEXH2):
				htmlbuf.append("<hr class='h2'>\n")

			if (t == TOK_ATHXH1):
				htmlbuf.append("<h1>" + self.line2html(v) + "</h1>\n")

			if (t == TOK_ATHXH2):
				htmlbuf.append("<h2>" + self.line2html(v) + "</h2>\n")

			if (t == TOK_ATHXH3):
				htmlbuf.append("<h3>" + self.line2html(v) + "</h3>\n")

			if (t == TOK_ATHXH4):
				htmlbuf.append("<h4>" + self.line2html(v) + "</h4>\n")

			if (t == TOK_ATHXH5):
				htmlbuf.append("<h5>" + self.line2html(v) + "</h5>\n")

			if (t == TOK_ATHXH6):
				htmlbuf.append("<h6>" + self.line2html(v) + "</h6>\n")

			if (t == TOK_PRE1):	# quoted pre block
				i += self.quotedpreblock(lines[i:], htmlbuf)

			if (t == TOK_PRE2):	# spaced pre block
				if (i+1 < len(lines)):
					i += self.spacedpreblock(lines[i:], htmlbuf)
				else:	# EOF
					htmlbuf.append("<pre>" + l + "</pre>\n")


			if (t >= TOK_LSTSPC0 and t <= TOK_LSTTAB4):	# Disk list
				i += self.disklist(lines[i:], htmlbuf)

			if (t >= TOK_NLSTSPC0 and t <= TOK_NLSTTAB4):	# Num list
				i += self.numlist(lines[i:], htmlbuf)

			if (t == TOK_TABLE):
				i += self.tableblock(lines[i:], htmlbuf)

			if (t == TOK_QUOTE):
				i += self.blockquote(1, lines[i:], htmlbuf)

			if (t == TOK_PLAIN):
				if (i+1 < len(lines)):		# Look ahead..
					ll, vv, tt = lines[i+1]
					if (tt == TOK_SETEXH1):
						htmlbuf.append("<h1>" + self.line2html(l) + "</h1>\n")
					elif (tt == TOK_SETEXH2):
						htmlbuf.append("<h2>" + self.line2html(l) + "</h2>\n")
					else:
						i += self.paragraph(lines[i:], htmlbuf)
				else: # EOF
					htmlbuf.append("<p>" + self.line2html(l) + "</p>\n")

	
			#if (t == TOK_BRANK):
			#	block = True
			#	htmlbuf.append("<h4>" + v + "</h4>\n")
			#	continue

			i += 1

		htmlbuf.append("</html>\n")

#		print ''.join(htmlbuf)

		return ''.join(htmlbuf)

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
class mdview:
	def __init__(self):

		self.apppath = os.path.dirname(os.path.realpath(__file__)) # application path

		self.filepath = ""		# openfile path
		self.filename = ""

		self.cssfile = self.apppath + "/default.css"
		self.html = ""

	def arguments(self):
		argvs = sys.argv		# arguments
		argc = len(argvs)		# arguments

		if (argc < 2 or argvs[1] == ''):
			print "Usage: python %s filename\n" % argvs[0]
			quit()

		self.filename = os.path.basename(argvs[1])
		self.filepath = os.path.dirname(os.path.abspath(argvs[1]))
		
		print self.filename
		print self.filepath

	def openfile(self):
		fullpath = self.filepath + '/' + self.filename

		try:
			f = open(fullpath)	# open file

		except IOError:
			print "Can not open %s\n" % fullpath
			quit()

		p = mdParseClass()

		# Parse lines
		lines = [];			# line buffer
		line = f.readline()

		while line:
			lines.append(p.line_parse(line))
			line = f.readline()	# next line

		f.close				# close file

		h = md2HTML()			# markdown to html class

		h.apppath = self.apppath
		h.filepath = self.filepath
		
		# read css class
		try:
			f = open(self.cssfile)	# default
			h.css += f.read()
			f.close()
		
		except IOError:
			h.css = ""

		self.html = h.toHtml(lines)

		return
	
	def savefile(self, path):
		try:
			f = open(path,"w+")	# open file

		except IOError:
			print "Can not open %s\n" % path
			quit()

		f.write(self.html)

		f.close()

		return 

#------------------------------------------------------------------------------
class frame_1(wx.Frame):
	def __init__(self, *args, **kwds):
		kwds["style"] = wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, *args, **kwds)

		self.panel_1 = wx.Panel(self, wx.ID_ANY)

		self.html_1 = wx.html2.WebView.New(self)	# webview
		self.html1_vscr_pos = 0				# scroll position (how do i better..)

		self.mdview = mdview()				# mdview class

		self.mdview.arguments()
		self.mdview.openfile()

		icon = wx.Icon(self.mdview.apppath + '/nyacom.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(icon)

		self.savedlg = wx.FileDialog(self, "Save HTML",	# save dialog
						self.mdview.filepath,
						self.mdview.filename + '.html',
						"HTML files (*.html)|*.html|ALL (*.*)|*.*", 
						wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		
		## Menu Bar
		#self.frame_1_menubar = wx.MenuBar()
		#wxglade_tmp_menu = wx.Menu()
		#wxglade_tmp_menu.Append(wx.ID_ANY, "Export", "", wx.ITEM_NORMAL)
		#wxglade_tmp_menu.Append(wx.ID_ANY, "Quit", "", wx.ITEM_NORMAL)
		#self.frame_1_menubar.Append(wxglade_tmp_menu, "File")
		#wxglade_tmp_menu = wx.Menu()
		#wxglade_tmp_menu.Append(wx.ID_ANY, "Zoom In", "", wx.ITEM_NORMAL)
		#wxglade_tmp_menu.Append(wx.ID_ANY, "Zoom Out", "", wx.ITEM_NORMAL)
		#self.frame_1_menubar.Append(wxglade_tmp_menu, "View")
		#self.SetMenuBar(self.frame_1_menubar)
		## Menu Bar end

		self.__set_properties()
		self.__do_layout()

	def __set_properties(self):
		self.SetTitle("Meow!")
		self.SetSize((800, 900))

		try:
			self.html_1.EnableContextMenu(False)	# since 2.9.5

		except AttributeError:
			print "Disabling context menu failed"

		self.html_1.EnableHistory(False)

                # Events
                self.html_1.Bind(wx.EVT_KEY_DOWN, self.html1_onKeyPress)
		self.html_1.Bind(wx.html2.EVT_WEBVIEW_LOADED, self.html_1_loaded)

	def __do_layout(self):
		sizer_1 = wx.BoxSizer(wx.VERTICAL)
		sizer_1.Add(self.html_1, 1, wx.EXPAND, 0)

		self.SetSizer(sizer_1)
		self.Layout()

		self.SetTitle("Meow! - " + self.mdview.filename)

		self.html_1.SetPage(self.mdview.html, 
				"file://" + self.mdview.filepath + "/")

	def html_1_loaded(self, ev):

		# revert scroll.. 
		# (teach me how can I better control for scroll...

		self.html_1.SetScrollPos(wx.VERTICAL, self.html1_vscr_pos - 1, True)	# revert scroll pos
		self.html_1.SetScrollPos(wx.VERTICAL, self.html1_vscr_pos + 1, True)	# revert scroll pos

		#self.html_1.ScrollPages(1)	# revert scroll pos
		ev.Skip

        def html1_onKeyPress(self, ev):     # WebView keypress event handler
                keycode = ev.GetKeyCode()
#                print keycode

		if (keycode == 82):	# 'r' (refesh)

			self.html1_vscr_pos = self.html_1.GetScrollPos(wx.VERTICAL) # save scroll pos

			self.mdview.openfile()

			self.html_1.SetPage(self.mdview.html, 
					"file://" + self.mdview.filepath + "/")

		if (keycode == 61):	# '+'
			zoom = self.html_1.GetZoom()
			if (zoom < 4):
				self.html_1.SetZoom(self.html_1.GetZoom()+1)

		if (keycode == 45):	# '-'
			zoom = self.html_1.GetZoom()
			if (zoom > 0):
				self.html_1.SetZoom(zoom-1)

		if (keycode == 74):	# 'j'
			self.html_1.ScrollLines(1)	# scroll down
			
		if (keycode == 75):	# 'k'
			self.html_1.ScrollLines(-1)	# scroll up

		if (keycode == 81):	# 'q'
			self.Close()

		if (keycode == 80):	# 'p'
			self.html_1.Print()		# scroll up

		if (keycode == 83):	# 's'
			if (self.savedlg.ShowModal() == wx.ID_OK):	# save
				self.mdview.savefile(self.savedlg.Path)

		if (ev.ControlDown() and keycode == 68):	# 'd'
			self.html_1.PageDown()		# page down
			
		if (ev.ControlDown() and keycode == 85):	# 'u'
			self.html_1.PageUp()		# page up

                ev.Skip

#------------------------------------------------------------------------------
if __name__ == "__main__":

	app = wx.App(False)

	frame = frame_1(None, wx.ID_ANY, "")
	frame.Show()

	app.MainLoop()

