from xml.dom.minidom import *

class Entry:
    def __init__(self, id=0, questions=[]):
        self.id = id
        self.questions = questions[:]
    def _to_xml(self, d):
        e = d.createElement('entry')
        e.setAttribute('id', str(self.id))
        for q in self.questions:
            e.appendChild(q._to_xml(d))
        return e
    def _from_xml(self, e):
        try:
            self.id = int(e.getAttribute('id'))
        except:
            pass
            
        self.questions = []
        qxmls = e.getElementsByTagName('question')
        for qxml in qxmls:
            new_q = Question()
            new_q._from_xml(qxml)
            self.questions.append(new_q)

class Question:
    def __init__(self, q_type='', completed=False, prompt=None, response=None, choices=[]):
        self.q_type = q_type
        self.completed = completed
        self.prompt = prompt
        self.response = response
        self.choices = choices[:]
    def _to_xml(self, d):
        e = d.createElement('question')
        e.setAttribute('type', str(self.q_type))
        e.setAttribute('completed', str(self.completed))
        if self.prompt:
            p = d.createElement('prompt')
            t = d.createTextNode(str(self.prompt))
            p.appendChild(t)
            e.appendChild(p)
        if self.response:
            r = d.createElement('response')
            t = d.createTextNode(str(self.response))
            r.appendChild(t)
            e.appendChild(r)
        for c in self.choices:
            e.appendChild(c._to_xml(d))
        return e
            
    def _from_xml(self, e):
        self.q_type = e.getAttribute('type')
        self.completed = _parse_bool(e.getAttribute('completed'))
        pxmls = e.getElementsByTagName('prompt')
        if len(pxmls) >= 1:
            self.prompt = ''
            for n in pxmls[0].childNodes:
                if n.nodeType == n.TEXT_NODE:
                    self.prompt = self.prompt + n.nodeValue.strip()
        rxmls = e.getElementsByTagName('response')
        if len(rxmls) >= 1:
            self.response = ''
            for n in rxmls[0].childNodes:
                if n.nodeType == n.TEXT_NODE:
                    self.response = self.response + n.nodeValue.strip()
        self.choices = []
        cxmls = e.getElementsByTagName('choice')
        for cxml in cxmls:
            new_c = Choice()
            new_c._from_xml(cxml)
            self.choices.append(new_c)

class Choice:
    def __init__(self, value='', response=False):
        self.value = value
        self.response = response
    def _to_xml(self, d):
        e = d.createElement('choice')
        e.setAttribute('response', str(self.response))
        t = d.createTextNode(str(self.value))
        e.appendChild(t)
        return e
    def _from_xml(self, e):
        self.response = _parse_bool(e.getAttribute('response'))
        self.value = ''
        for n in e.childNodes:
            if n.nodeType == n.TEXT_NODE:
                self.value = self.value + n.nodeValue.strip()
        
def parse_entry_from_file(filename):
    f = None
    result = None

    try:
        f = file(filename, 'r')
    except:
        return result
        
    try:
        x = f.read()
        d = parseString(x)
        entries = d.getElementsByTagName('entry')
        if len(entries) > 0:
            e = Entry()
            e._from_xml(entries[0])
            result = e
    except:
        pass
    
    if f:
        try:
            f.close()
        except:
            pass
            
    return result

def write_entry_to_file(e, filename):
    f = None
    result = False

    try:
        f = file(filename, 'w')
    except:
        return result
        
    try:
        d = getDOMImplementation().createDocument(None, None, None)
        d.appendChild(e._to_xml(d))
        f.write(d.toprettyxml())
        result = True
    except:
        pass

    if f:
        try:
            f.close()
        except:
            pass
            
    return result
    
def _parse_bool(s):
    if s.lower() == 'true':
        return True
    else:
        return False
