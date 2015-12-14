#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#------------------------------------------------------------------------------
# Meowkdown viewer
# Kazuei HIRONAKA <kzh@nyacom.net>
# 2015 (C)
#------------------------------------------------------------------------------

import wx
import wx.html2
import gettext
import os
import sys
import re
import math

# import frame1

#------------------------------------------------------------------------------
# Constant values
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

		self.toks.append(mdToken(r'^\s{,4}```s*(.*)$',		TOK_PRE1))	# pre 1
		self.toks.append(mdToken(r'^\s{4}(.*)$',		TOK_PRE2))	# pre 2

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

	def appendHeader(self, s):
		s.append('<html>\n')
		s.append('<head>\n')

		s.append('<style type="text/css">\n')
		s.append('<!--\n')
		s.append(self.css)
		s.append('-->\n')
		s.append('</style>\n')

		#s.append('<link rel="stylesheet" type="text/css" href="default.css">\n')
		s.append('</head>\n')

	def refline2html(self, m):
		if (m.lastindex > 1):
			return r'<a href="' + self.ref[m.group(2)] + '">' + m.group(1) + '</a>'

		return r'<a href="' + self.ref[m.group(1)] + '">' + m.group(1) + '</a>'

	def imgrefline2html(self, m):
		if (m.lastindex > 2):
			return r'<img src="' + self.ref[m.group(1)] + '"' + m.group(2) + '>'

		return r'<img src="' + self.ref[m.group(1)] + '">'
		

	def line2html(self, s):
		s = re.sub(r'\\[#*-_+](.*)', 		r'\1', s)	# escape

		s = re.sub(r'<(http://.*)>(\s|$)',		r'<a href="\1" target="_blank">\1</a>', s)		# auto link (URI)
		s = re.sub(r'<(.*@.*)>(\s|$)',			r'<a href="mailto:\1" target="_blank">\1</a>', s)	# auto link (mail)

		s = re.sub(r'!\[(.*)@(.*)\]\((.*)\s+"(.*)"\)(\s|$)',	r'<img src="\3" alt="\1" title="\4" \2', s)	# img with name and tag
		s = re.sub(r'!\[(.*)\]\((.*)\s+"(.*)"\)(\s|$)',		r'<img src="\2" alt="\1" title="\3">', s)	# img with name

		s = re.sub(r'!\[(.*)@(.*)\]\((.*)\)(\s|$)',		r'<img src="\3" \2>', s)		# img
		s = re.sub(r'!\[(.*)\]\((.*)\)(\s|$)',			r'<img src="\2">', s)			# img

		s = re.sub(r'!\[(.*)@(.*)\](\s|$)',		self.imgrefline2html, s)			# img with ref
		s = re.sub(r'!\[(.*)\](\s|$)',			self.imgrefline2html, s)			# img with ref
		s = re.sub(r'!\[(.*)\](\s|$)',			self.imgrefline2html, s)			# img with ref

		s = re.sub(r'\[(.*)\]\((.*)\s+"(.*)"\)(\s|$)',	r'<a href="\2" target="_blank" title="\3">\1</a>', s)	# link with name
		s = re.sub(r'\[(.*)\]\((.*)\)(\s|$)',		r'<a href="\2" target="_blank">\1</a>', s)	# link

		s = re.sub(r'\[(.*)\]\[\](\s|$)',		self.refline2html, s)	# ref link
		s = re.sub(r'\[(.*)\]\[(.*)\](\s|$)',		self.refline2html, s)	# ref link

		s = re.sub(r'\s__(.*)__(\s|$)', 	r'<strong>\1</strong>', s)	# bold
		s = re.sub(r'\s\*\*(.*)\*\*(\s|$)', 	r'<strong>\1</strong>', s)	# bold
		s = re.sub(r'\s_(.*)_(\s|$)', 		r'<em>\1</em>', s)		# italic
		s = re.sub(r'\s\*(.*)*(\s|$)', 		r'<em>\1</em>', s)		# italic
		s = re.sub(r'\s\`(.*)\`(\s|$)',		r'<code>\1</code>', s)		# code
		s = re.sub(r'\s~~(.*)~~(\s|$)', 	r'<s>\1</s>', s)		# strike
		s = re.sub(r'\s\s$', 			r'<br>\n', s)			# nr

		return s.rstrip('\n\r')

	def numlist(self, lines, s):
		i = 0
		s.append("<ol>\n")

		while (i < len(lines)):
			l, v, t = lines[i]	# current

			if ((t >= TOK_NLSTSPC0 and t <= TOK_NLSTTAB4) or t == TOK_BRANK):
				if (i+1 < len(lines)):
					if (t != TOK_BRANK):
						s.append("<li>" + self.line2html(v) + "</li>\n")

					ll, vv, tt = lines[i+1]	# lookup next level

					if (tt >= TOK_NLSTSPC0 and tt <= TOK_NLSTTAB4):
						if (tt > t):	# deeper level
							i += self.numlist(lines[i+1:], s) + 1
							break
						elif (tt < t):	# less level
                                                        s.append("</ol>\n")

					elif (tt == TOK_BRANK):
						s.append("<br>\n")

					elif (tt >= TOK_LSTSPC0 and tt <= TOK_LSTTAB4):
						if (tt > (t-9)): # more deeper
							i += self.disklist(lines[i:], s) + 1
						else:
							break;

					else:
						break

			else:
				break

			i += 1

		s.append("</ol>\n")
		
		return i


	def disklist(self, lines, s):
		i = 0
		s.append("<ul>\n")

		while (i < len(lines)):
			l, v, t = lines[i]	# current

			if ((t >= TOK_LSTSPC0 and t <= TOK_LSTTAB4) or t == TOK_BRANK):
				if (i+1 < len(lines)):
					if (t != TOK_BRANK):
						s.append("<li>" + self.line2html(v) + "</li>\n")

					ll, vv, tt = lines[i+1]	# lookup next level

					if (tt >= TOK_LSTSPC0 and tt <= TOK_LSTTAB4):
						if (tt > t):	# deeper level
							i += self.disklist(lines[i+1:], s) + 1
							break
						elif (tt < t):	# less level
                                                        s.append("</ul>\n")

					elif (tt == TOK_BRANK):
						s.append("<br>\n")

					elif (tt >= TOK_NLSTSPC0 and tt <= TOK_NLSTTAB4):
						if (tt > (t+9)): # more deeper
							i += self.numlist(lines[i+1:], s) + 1
						else:
							break

					else:
						break

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
		s.append("<pre>\n")

		while (i < len(lines)):
			l, v, t = lines[i]

			if (t == TOK_PRE1):
				i += 1
				break

			else:
				s.append(l + "\n")

			i += 1

		s.append("</pre>\n")

		return i


	def spacedpreblock(self, lines, s):
		i = 0
		s.append("<pre>\n")

		while (i < len(lines)):
			l, v, t = lines[i]

			if (t == TOK_PRE2):
				s.append(l + "\n")

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

			if (t == TOK_SETEXH1 or t == TOK_SETEXH2):
				htmlbuf.append("<hr>\n")

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
				if (i+1 < len(lines)):
					i += self.quotedpreblock(lines[i+1:], htmlbuf)
				else:	# EOF
					htmlbuf.append("<pre>" + self.line2html(l) + "</pre>\n")

			if (t == TOK_PRE2):	# spaced pre block
				if (i+1 < len(lines)):
					i += self.spacedpreblock(lines[i:], htmlbuf)
				else:	# EOF
					htmlbuf.append("<pre>" + self.line2html(l) + "</pre>\n")


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
				#htmlbuf.append("<h4>" + v + "</h4>\n")
				#continue
				#self.py += self.lh

			i += 1

		htmlbuf.append("</html>\n")

		#print ''.join(htmlbuf)

		return ''.join(htmlbuf)

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
class mdview:
	def __init__(self):
		self.filename = ""
		self.cssfile = "./default.css"
		self.html = ""

	def arguments(self):
		argvs = sys.argv		# arguments
		argc = len(argvs)		# arguments

		if (argc < 2):
			print "Usage: python %s filename" % argvs[0]
			quit()

		self.filename = argvs[1]


	def openfile(self):
		try:
			f = open(self.filename)	# open file

		except IOError:
			print "Can not read %s" % argvs[1]
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
		
		# read css class
		try:
			f = open(self.cssfile)	# default
			h.css += f.read()
			f.close()
		
		except IOError:
			h.css = ""

		self.html = h.toHtml(lines)

		return

#	def main(self):
#		self.arguments()
#		self.openfile()
#	
#		# wx Application main
#		app = wx.App(False)
#		f = frame_1(None, wx.ID_ANY, "");
#
#		f.html_1.SetPage(self.html, "file://" + os.path.dirname(os.path.abspath(self.filename))+ "/")
#
#		f.Show()			# show main dialog
#		app.MainLoop()
#

#------------------------------------------------------------------------------
class frame_1(wx.Frame):
	def __init__(self, *args, **kwds):
		# begin wxGlade: frame_1.__init__
		kwds["style"] = wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, *args, **kwds)
		#self.panel_1 = wx.Panel(self, wx.ID_ANY)
		#self.html_1 = wx.html.HtmlWindow(self, wx.ID_ANY)
		self.html_1 = wx.html2.WebView.New(self)

		self.mdview = mdview()
		
		# Menu Bar
		self.frame_1_menubar = wx.MenuBar()
		wxglade_tmp_menu = wx.Menu()
		wxglade_tmp_menu.Append(wx.ID_ANY, "Export", "", wx.ITEM_NORMAL)
		wxglade_tmp_menu.Append(wx.ID_ANY, "Quit", "", wx.ITEM_NORMAL)
		self.frame_1_menubar.Append(wxglade_tmp_menu, "File")
		wxglade_tmp_menu = wx.Menu()
		wxglade_tmp_menu.Append(wx.ID_ANY, "Zoom In", "", wx.ITEM_NORMAL)
		wxglade_tmp_menu.Append(wx.ID_ANY, "Zoom Out", "", wx.ITEM_NORMAL)
		self.frame_1_menubar.Append(wxglade_tmp_menu, "View")
		self.SetMenuBar(self.frame_1_menubar)
		# Menu Bar end

                # Events
                self.html_1.Bind(wx.EVT_KEY_DOWN, self.html1_onKeyPress)
		self.Bind(wx.EVT_SCROLL, self.html1_scroll)

		self.__set_properties()
		self.__do_layout()

	def __set_properties(self):
		# begin wxGlade: frame_1.__set_propertier
		self.SetTitle("Meow!")
		self.SetSize((700, 800))
		#self.html_1.LoadURL("file:///index.html")
		#self.html_1.SetPage(r"Meowkdown view")
		#self.panel_1.SetBackgroundColour(wx.Colour(255, 255, 255))
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: frame_1.__do_layout
		sizer_1 = wx.BoxSizer(wx.VERTICAL)
		sizer_1.Add(self.html_1, 1, wx.EXPAND, 0)
		self.SetSizer(sizer_1)
		self.Layout()
		# end wxGlade

		self.mdview.arguments()

		self.mdview.openfile()
		self.SetTitle("Meow! - " + self.mdview.filename)

		self.html_1.SetPage(self.mdview.html, 
				"file://" + os.path.dirname(os.path.abspath(self.mdview.filename))+ "/")

	def html1_scroll(self, ev):
		print "scroll"
		ev.Skip

        def html1_onKeyPress(self, ev):     # WebView keypress event handler
                keycode = ev.GetKeyCode()

		if (keycode == 82):	# 'r'
			pos = self.html_1.GetScrollPos(wx.HORIZONTAL)
			print str(pos)

#			self.mdview.openfile()
#			self.html_1.SetPage(self.mdview.html, 
#					"file://" + os.path.dirname(os.path.abspath(self.mdview.filename))+ "/")

#			self.html_1.SetScrollPos(100)

#		if (keycode == 61):	# '+'
#			print self.html_1.GetScrollPos()
#			self.html_1

                print keycode
                ev.Skip

#------------------------------------------------------------------------------
if __name__ == "__main__":

	app = wx.App(False)

	frame = frame_1(None, wx.ID_ANY, "")
	frame.Show()

	app.MainLoop()

#	m = mdview()
#	m.main()

