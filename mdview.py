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
# Valuables
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
TOK_BRANK	= 30
TOK_PLAIN	= 31

#------------------------------------------------------------------------------
# Class .md parser
#------------------------------------------------------------------------------
class mdParseClass:
	def __init__(self):
		self.toks = []

		# ^^^^^ Upper is match high priolity ^^^^^
		self.toks.append(mdToken(r"^\s*-+()\s*$", TOK_SETEXH2))	# setex h2
		self.toks.append(mdToken(r"^\s*=+()\s*$", TOK_SETEXH1))	# setex h1
		self.toks.append(mdToken(r"^\s*([_\-\*])\s*\1\s*\1\s*\1*$", TOK_HR))	# hr

		self.toks.append(mdToken(r"^\s{,4}######\s*(.*)[#\s\t]*$", TOK_ATHXH6))	# atx h6
		self.toks.append(mdToken(r"^\s{,4}#####\s*(.*)[#\s\t]*$", TOK_ATHXH5))	# atx h5
		self.toks.append(mdToken(r"^\s{,4}####\s*(.*)[#\s\t]*$", TOK_ATHXH4))	# atx h4
		self.toks.append(mdToken(r"^\s{,4}###\s*(.*)[#\s\t]*$", TOK_ATHXH3))	# atx h3
		self.toks.append(mdToken(r"^\s{,4}##\s*(.*)[#\s\t]*$", TOK_ATHXH2))	# atx h2
		self.toks.append(mdToken(r"^\s{,4}#\s*(.*)[#\s\t]*$",	TOK_ATHXH1))	# atx h1


		self.toks.append(mdToken(r"^[0-9]+\.[\s\t]+(.*)$", TOK_NLSTSPC0))		# num list
		self.toks.append(mdToken(r"^\t[0-9]+\.[\s\t]+(.*)$", TOK_NLSTTAB1))		# num list
		self.toks.append(mdToken(r"^\s[0-9]+\.[\s\t]+(.*)$", TOK_NLSTSPC1))		# num list
		self.toks.append(mdToken(r"^\t\t[0-9]+\.[\s\t]+(.*)$", TOK_NLSTTAB2))		# num list
		self.toks.append(mdToken(r"^\s\s[0-9]+\.[\s\t]+(.*)$", TOK_NLSTSPC2))		# num list
		self.toks.append(mdToken(r"^\t\t\t[0-9]+\.[\s\t]+(.*)$", TOK_NLSTTAB3))		# num list
		self.toks.append(mdToken(r"^\s\s\s[0-9]+\.[\s\t]+(.*)$", TOK_NLSTSPC3))		# num list
		self.toks.append(mdToken(r"^\t\t\t\t[0-9]+\.[\s\t]+(.*)$", TOK_NLSTTAB4))	# num list
		self.toks.append(mdToken(r"^\s\s\s\s[0-9]+\.[\s\t]+(.*)$", TOK_NLSTSPC4))	# num list

		self.toks.append(mdToken(r"^[\*\-\+][\s\t]+(.*)$", TOK_LSTSPC0))		# disk list
		self.toks.append(mdToken(r"^\t[\*\-\+][\s\t]+(.*)$", TOK_LSTTAB1))		# disk list
		self.toks.append(mdToken(r"^\s[\*\-\+][\s\t]+(.*)$", TOK_LSTSPC1))		# disk list
		self.toks.append(mdToken(r"^\t\t[\*\-\+][\s\t]+(.*)$", TOK_LSTTAB2))		# disk list
		self.toks.append(mdToken(r"^\s\s[\*\-\+][\s\t]+(.*)$", TOK_LSTSPC2))		# disk list
		self.toks.append(mdToken(r"^\t\t\t[\*\-\+][\s\t]+(.*)$", TOK_LSTTAB3))		# disk list
		self.toks.append(mdToken(r"^\s\s\s[\*\-\+][\s\t]+(.*)$", TOK_LSTSPC3))		# disk list
		self.toks.append(mdToken(r"^\t\t\t\t[\*\-\+][\s\t]+(.*)$", TOK_LSTTAB4))	# disk list
		self.toks.append(mdToken(r"^\s\s\s\s[\*\-\+][\s\t]+(.*)9", TOK_LSTSPC4))	# disk list

		self.toks.append(mdToken(r"^\s{,4}\|(.*)\|[\s\t]*$", TOK_TABLE))	# table

		self.toks.append(mdToken(r"^\s{,4}```s*(.*)$",		TOK_PRE1))	# pre 1
		self.toks.append(mdToken(r"^\s{4}(.*)$",		TOK_PRE2))	# pre 2

		self.toks.append(mdToken(r"^\n()$",			TOK_BRANK))	# brank
		self.toks.append(mdToken(r"^.*$",			TOK_PLAIN))	# plain


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

	def appendHeader(self, s):
		s.append('<html>\n')
		s.append('<head>\n')
		s.append('<link rel="stylesheet" type="text/css" href="default.css">\n')
		s.append('</head>\n')

	def line2html(self, s):
		s = re.sub(r"\\[#*-_+](.*)", 		r'\1', s)	# escape
		s = re.sub(r"\s__(.*)__(\s|$)", 	r' <strong>\1</strong>', s)	# bold
		s = re.sub(r"\s\*\*(.*)\*\*(\s|$)", 	r' <strong>\1</strong>', s)	# bold
		s = re.sub(r"\s_(.*)_(\s|$)", 		r' <em>\1</em>', s)		# italic
		s = re.sub(r"\s\*(.*)*(\s|$)", 		r' <em>\1</em>', s)		# italic
		s = re.sub(r"\s\`(.*)\`(\s|$)",		r' <code>\1</code>', s)		# code
		s = re.sub(r"\s~~(.*)~~(\s|$)", 	r' <s>\1</s>', s)		# strike
		s = re.sub(r"\s\s$", 			r' <br>\n', s)			# nr

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


	def tableblock(self, lines, s):
		i = 0

		tcn = 0
		thn = 0
		tdn = 0

		l, v, t = lines[i]		# table headers 
                th = re.split(r"\|", l)[1:-1]   # take slices
		thn = len(th)
		# s.append("thn:" + str(th) + str(thn))

		if (i+2 < len(lines)):		# table column format check
			l, v, t = lines[i+1]
			tcn = len(re.split(r"-{3,}\|", l)) - 1
			#s.append("tcn:" + str(tcn))
                else:
                    return 0

		if (thn == tcn):		# if number of header and columns are same
			s.append("<table>\n")
			s.append("<tr>\n")

			for val in th:          # table column
				s.append("<th>" + val + "</th>\n")

			s.append("</tr>\n")

			i += 2                  # table data
			s.append("<tr>\n")

			while (i < len(lines)):
				l, v, t = lines[i]
				td = re.split(r"\|", l)[1:-1]
				tdn = len(td)
				
				if (thn == tdn):
					for val in td:
						s.append("<td>" + val + "</td>\n")
				else:
					break

				i += 1

			s.append("</tr>\n")

                else:
                    return 0

#
#		# TR
#
#		while (i < len(lines)):
#			l, v, t = lines[i]
#
#			if (t == TOK_TABLE):
#				s.append(l + "\n")
#
#			else:
#				i -= 1
#				break
#
#			i += 1
#
		s.append("</table>\n")

		return i


	def toHtml(self, lines):
		htmlbuf = []
		self.appendHeader(htmlbuf)			# Append header

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
				if (i+1 < len(lines)):
					i += self.tableblock(lines[i:], htmlbuf)
				else:
					htmlbuf.append("<p>" + self.line2html(l) + "</p>\n")

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

		print ''.join(htmlbuf)

		return ''.join(htmlbuf)

#------------------------------------------------------------------------------
class frame_1(wx.Frame):
	def __init__(self, *args, **kwds):
		# begin wxGlade: frame_1.__init__
		kwds["style"] = wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, *args, **kwds)
		#self.panel_1 = wx.Panel(self, wx.ID_ANY)
		#self.panel_1 = mdPanel(self)
		#self.html_1 = wx.html.HtmlWindow(self, wx.ID_ANY)
		#self.html_1 = mdHtmlView(self)
		self.html_1 = wx.html2.WebView.New(self)
		
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

		self.__set_properties()
		self.__do_layout()

	def __set_properties(self):
		# begin wxGlade: frame_1.__set_properties
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

        def html1_onKeyPress(self, ev):     # WebView keypress event handler
                keycode = ev.GetKeyCode()
                print keycode
                ev.Skip

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
if __name__ == "__main__":

	argvs = sys.argv		# arguments
	argc = len(argvs)		# arguments

	if (argc < 2):
		print "Usage: python %s filename" % argvs[0]
		quit()

	try:
		f = open(argvs[1])	# open file
	except IOError:
		print "Can not read %s" % argvs[1]
		quit()

	p = mdParseClass()
	lines = [];			# line buffer

	# Parse lines
	line = f.readline()
	while line:
		lines.append(p.line_parse(line))
		line = f.readline()	# next line

	f.close				# close file
	h = md2HTML()

	# Render to device context

	# wx Application main
	app = wx.App(False)
	f = frame_1(None, wx.ID_ANY, "");

	pwd = os.path.dirname(os.path.abspath(__file__))
	f.html_1.SetPage(h.toHtml(lines), "file://" + pwd + "/")

	#f.html_1.LoadURL(h.toHtml(lines)"")

	f.Show()
	app.MainLoop()


