# TODO: properly handle enumerated nodes

import json
import os.path
import sys
import re

from props import PropertyNode, root

# internal dict() tree parsing routine
def parseDict(pynode, newdict, basepath):
    if 'include' in newdict:
        # include file handling before anything else (follow up
        # entries implicitely overwrite the include file values.)
        if re.match('^/', newdict['include']):
            file = newdict['include']
        else:
            file = os.path.join(basepath, newdict['include'])
        print 'include:', file
        load(file, pynode)
    for tag in newdict:
        if type(newdict[tag]) is dict:
            if not tag in pynode.__dict__:
                node = PropertyNode()
                pynode.__dict__[tag] = node
            else:
                node = pynode.__dict__[tag]
            parseDict(node, newdict[tag], basepath)
        elif type(newdict[tag]) is list:
            pynode.__dict__[tag] = []
            for ele in newdict[tag]:
                if type(ele) is dict:
                    newnode = PropertyNode()
                    pynode.__dict__[tag].append(newnode)
                    parseDict(newnode, ele, basepath)
                else:
                    pynode.__dict__[tag].append(ele)
        elif type(newdict[tag]) is unicode:
            if tag == 'include':
                # already handled
                pass
            else:
                # normal case
                print 'normal case:', tag, newdict[tag]
                pynode.__dict__[tag] = newdict[tag]
        else:
            print 'skipping:', tag, type(newdict[tag])
                
# load a json file and create a property tree rooted at the given node
# supports "mytag": "include=relative_file_path.json"
def load(filename, pynode):
    print "loading:", filename
    try:
        f = open(filename, 'r')
        file = f.read()
        # support // style comments in json files (by removing them
        # before passing the file to the json parser)
        file = re.sub('\n\s*//.*\n', '\n', file)
        print file
        newdict = json.loads(file)
        f.close()
    except:
        print filename + ": json load error:\n" + str(sys.exc_info()[1])
        return

    path = os.path.dirname(filename)
    print "path:", path
    parseDict(pynode, newdict, path)

def buildDict(root, pynode):
    for child in pynode.__dict__:
        print child
        node = pynode.__dict__[child]
        if isinstance(node, PropertyNode):
            root[child] = dict()
            buildDict(root[child], node)
        elif type(node) is list:
            root[child] = []
            for i, ele in enumerate(node):
                if isinstance(ele, PropertyNode):
                    newdict = dict()
                    root[child].append( newdict )
                    buildDict(newdict, ele)
                else:
                    root[child].append(str(ele))
   
        elif type(child) is str:
            root[child] = str(node)
        else:
            print "skipping:", child, ":", str(node)
        
# save the property tree starting at pynode into a json xml file.
def save(filename, pynode=root):
    root = dict()
    buildDict(root, pynode)
    try:
        f = open(filename, 'w')
        json.dump(root, f, indent=2, sort_keys=True)
        f.close()
    except:
        print filename + ": json save error:\n" + str(sys.exc_info()[1])
        return
