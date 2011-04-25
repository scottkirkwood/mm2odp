#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Convert a Mind Map File into an Open Office (odp) presentation.

If you create a mind map with FreeMind the title of the mind-map (center circle)
will be the title of the slide.

A top level node called "__meta__" can be used to set the metadata for 
the presentation.  The immediate children are keys and it's first child is a value.
  title: Title of presentation, not needed since I get it from the top node
  subtitle: Witty subtitle of the presentation
  author: You probably want to change this.
  company: And this
  template: which subdirectory to use under the "ui" directory, 'default' is default
  presdate: Date of the presentation
  content_type: defaults to 'application/xhtml+xml; charset=utf-8'
  header:
  footer:

This code badly needs to be merged with mm2s5, since they are almost the same.
This code is slightly more general.
"""

__author__ = 'scottkirkwood@google.com (Scott Kirkwood)'

import re
import os
import sys
from optparse import OptionParser
try:
    from xml.etree.ElementTree import XML
except ImportError:
    from elementtree.ElementTree import XML
import update_odp

class Mm2Odp:
  def __init__(self):
    self.et_in = None
    self.meta = {
      'title' : 'Title',
      'subtitle': '',
      'author' : 'Your Name',
      'company' : 'Your Company',
      'template' : 'default',
      'presdate' : 'Today',
      'content_type' : 'application/xhtml+xml; charset=utf-8',
      'header' : '',
      'footer' : None,
      'generator' : 'mm2odp.py',
    }
    self.pages = []
    
  def open(self, infilename):
    """ Open the .mm file and create an elementtree."""
    infile = file(infilename).read()
    self.et_in = self.xmlparse(infile)
    self.pages = self.convert()

  def write(self, tempate_filename, out_filename):
    """Write out the lines, written as a convenience function.
    
    Writing out the HTML in correct UTF-8 format is a little tricky."""
    
    odp = update_odp.UpdateOdp(self.meta, self.pages)
    odp.ReadWrite(tempate_filename, out_filename)
    
  def xmlparse(self, text):
    """import the XML text into self.et_in."""
    return  XML(text)
    
  def convert(self):
    """Convert self.et_in to a HTML as a list of lines in ODP format."""

    self._grab_meta()

    presentation = self.et_in.find('node')
    pages = []
     
    for page in presentation.findall('node'):
      # Skip the __meta__ node, if any
      if page.attrib['TEXT'] == '__meta__':
        continue
      
      attribs = self._get_list_attributes(page)
      if 'skip' in attribs:
        continue

      title = page.attrib['TEXT']
      pages.append((title, self._doList(page, 0)))
       
    return pages
  
  def _get_list_attributes(self, page):
    """ If there's a special icon, return some attributes
      Also, handle HTML markup a bit differently
    """
    ret = {}
    
    for icon in page.findall('icon'):
      type = icon.attrib['BUILTIN']
      if type == 'button_ok':
        ret['no_ul'] = True
      elif type == "stop": # Stop light icon
        ret['ul_class'] = "incremental"
      elif type == 'button_cancel':
        ret['skip'] = True
      elif type == 'full-1':
        ret['ol'] = True

    # Special case, if the first node starts with <
    # Then we'll assume markup and not do 
    # a <ul> etc.
    node = page.find('node')
    if node != None and \
      (node.attrib['TEXT'].startswith('<') or 
      node.attrib['TEXT'] == '__table__'):
      ret['no_ul'] = True
    
    return ret
    
  def _grab_meta(self):
    """ Grab a "page" called __meta__, if any """
    
    titles = self.et_in.find('node').attrib['TEXT'].split('\n')
    
    self.meta['title'] = titles[0]
    if len(titles) > 1:
      self.meta['subtitle'] = titles[1]
    for cur_node in self.et_in.getiterator('node'):
      if 'TEXT' in cur_node.attrib and cur_node.attrib['TEXT'] == '__meta__':
        for sub_attrib in cur_node.findall('node'):
          key = sub_attrib.attrib['TEXT']
          sub_value = sub_attrib.find('node')
          value = sub_value.attrib['TEXT']
          self.meta[key] = value
    
    if self.meta['footer'] == None:
      self.meta['footer'] = '<h1>%(company)s</h2><h2>%(title)s</h2>' % self.meta
    
  def _doList(self, sub, depth):
    """ Recurse this list of items 
    
    Code is a little messier than I would like."""
    lines = [] 
    if sub == None or len(sub) == 0:
      return
    
    attribs =  self._get_list_attributes(sub)

    for line in sub.findall('node'):
      text = line.attrib['TEXT']
      lines.append(text)
      if len(line) != 0:
        lines.append(self._doList(line, depth + 1))

    return lines

def parse_command_line():
  usage = """%prog [-t template.odp] <mmfile> [output.odp]
    From a FreeMind (.mm) document (see http://freemind.sourceforge.net/wiki/index.php/Main_Page)
    the main node will be the title page and the top level nodes will be pages.
    Levels below that are nested lines.

    -t Source odp template to use.  Should have two pages the first it the title
    page the other is a normal presentation page with sample nestings.
    output.odp is optional, if not give we will use the mm file, changing .mm to .odp.
    """
  usage = '\n'.join([s.lstrip() for s in usage.split('\n')])
  parser = OptionParser(usage)
  parser.add_option('-t', dest='template', default='template.odp',
                    help='Template ODP to use, must have two pages')
  (options, args) = parser.parse_args()
  if len(args) == 0:
    parser.print_usage()
    sys.exit(-1)
  
  infile = args[0]
  if not infile.endswith('.mm'):
    print "Input file must end with '.mm'"
    parser.print_usage()
    sys.exit(-1)
      
  if len(args) == 1:
    outfile = infile.replace('.mm', '.odp')
  elif len(args) == 2:
    outfile = args[1]
  else:
    parser.print_usage()
    sys.exit(-1)
  template = options.template
   
  mm2odp = Mm2Odp()
  mm2odp.open(infile)
  print 'From "%s" to "%s" using template "%s"' % (infile, outfile, template)
  mm2odp.write(template, outfile)

if __name__ == "__main__":
  parse_command_line()
