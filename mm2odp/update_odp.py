#!/usr/bin/env python
#

"""Modify an open office document.

Specifically designed to modify an OpenOffice Presentation.
"""

__author__ = 'scott@google.com (scottkirkwood))'

import sys
import zipfile
import copy

try:
  import xml.etree.ElementTree as ET # Python 2.5
except:
  try:
    import cElementTree as ET # Faster
  except:
    import elementtree.ElementTree as ET

NS_OFFICE = '{urn:oasis:names:tc:opendocument:xmlns:office:1.0}'
NS_DRAW = '{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}'
NS_TEXT = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}'

def dump(elems):
  lines = []
  for elem in elems.getiterator():
    lines.append(str(elem))
  return '\n'.join(lines)

class UpdateOdp:
  def __init__(self, meta, pageitems):
    """ctor

    Args:
      pageitems: list of [(slide-title, [listitems, ...]), ...]
    """
    self.meta = meta
    self.pages = pageitems

  def ReadWrite(self, infname, outfname):
    """Read in in fname, and write out to out fname.

    infname and outfname must be different, the idea is that infname is a
    'template' and outfname is the final version.
    """
    z_in = zipfile.ZipFile(infname, 'r')
    z_out = zipfile.ZipFile(outfname, 'w')
    for info in z_in.infolist():
      text = z_in.read(info.filename)
      text = self.CallBack(info, text)
      z_out.writestr(info, text)
    z_out.close()
    z_in.close()
     
  def CallBack(self, zipinfo, text):
    if zipinfo.filename == 'content.xml':
      et = ET.fromstring(text)
      et = self.UpdateContent(et)
      text = ET.tostring(et)
      text = text.encode('utf-8', 'xmlcharrefreplace')
    return text

  def UpdateContent(self, et):
    """Update content.xml.

    Pure function, no side effects.

    Args:
      text: text representation of content.xml.
    Returns:
      Elementtree
    """
    presentation = et.find('.//%sbody/%spresentation' % (NS_OFFICE, NS_OFFICE))
    page_copy = copy.deepcopy(presentation[1])
    del presentation[1:]
    texts = presentation[0].findall('.//%sp' % (NS_TEXT))
    for index, text in enumerate(texts):
      if index == 0:
        text.text = self.meta['title']
      elif index == 1:
        text.text = self.meta['subtitle']
      elif index == 2:
        text.text = self.meta['author']

    for page in self.pages:
      title = page[0]
      items = page[1]
      page_copycopy = copy.deepcopy(page_copy)
      text_boxes = page_copycopy.findall('.//%stext-box' % NS_DRAW)
      textp = text_boxes[0].findall('.//%sp' % NS_TEXT)
      textp[0].text = title
      list_copy = copy.deepcopy(text_boxes[1].find('.//%slist' % NS_TEXT))
      del text_boxes[1][0:]

      self._recurse_items(items, list_copy, text_boxes[1], 1)

      presentation.append(page_copycopy)
    return et

  def _recurse_items(self, items, list_copy, text_box, depth):
    """Search for line items of a certain depth.
    """
    findp = './/%sp' % NS_TEXT
    for item in items:
      if isinstance(item, list):
        tofind = '%slist-item' % NS_TEXT
        stylename = '%sstyle-name' % NS_TEXT
        list_copycopy = copy.deepcopy(list_copy)

        for node in list_copycopy.getiterator():
          if node.tag == tofind: 
            if len(node.getchildren()):
              node.remove(node.getchildren()[0])
            else:
              raise 'Unable to find any child nodes for "%s"' % node
            newsubnode = copy.deepcopy(list_copy)
            del newsubnode.attrib[stylename]
            textp = newsubnode.findall(findp)
            if textp:
              textp = textp[0]
              text = textp.attrib[stylename]
              text = text[0:-1] + str(int(text[-1]) + 1)
              textp.attrib[stylename] = text
              textp.text = ''
              node.append(newsubnode)
            else:
              raise 'Unable to find2 "%s" in "%s"' % (findp,
                                                     dump(newsubnode))
            break
        self._recurse_items(item, list_copycopy, text_box, depth + 1)
      else:
        list_copycopy = copy.deepcopy(list_copy)
        textp = list_copycopy.findall(findp)
        if textp:
          textp = textp[0]
          textp.text = item
        else:
          raise 'Unable to find "%s" in "%s"' % (findp,
                                                 dump(list_copycopy))
        text_box.append(list_copycopy)

def main(argv):
  import optparse

  parser = optparse.OptionParser()
  options, args = parser.parse_args()
  meta = {
    'title' : 'My title',
  }
  pages = [
    ('Page 1', ['Line 1', 'Line 2']),
    ('Page 2', ['Line 3', 'Line 4']),
  ]
  update_odf = UpdateOdp(meta, pages)
  update_odf.ReadWrite('template.odp', 'sample-out.odp')

if __name__ == '__main__':
  main(sys.argv)
