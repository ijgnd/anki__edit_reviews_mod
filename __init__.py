# -*- coding: utf-8 -*-
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
# this is an extension of the add-on Edit Field During Review, https://ankiweb.net/shared/info/1020366288
#      by Nickolay <kelciour@gmail.com> (2019, copyright)
 

# this add-on requires that you have TinyMCE in your folder program folder
# Download the latest version, e.g. http://download.tiny.cloud/tinymce/community/tinymce_4.9.2.zip
# From this zipfile extract the subfolder tinymce that contains tinymce.min.js
# put this folder into your program folder into the subfolder "web"
# In Windows it must look like this:
# C:\Program Files\Anki\web\tinymce\tinymce.min.js
# For Linux for the compiled version from Ankiweb:
# /path/to/Anki21/bin/web/tinymce/tinymce.min.js


# at the moment this add-on overwrites some built-in functions of Anki. Fixes
# for this are welcome.
# use it at your own risk.
# feedback or improvements are very welcome.


# If you want to you can load tinymce into your editor component. Uncomment 
# the last line for this. Then the editor is unusable. This is NOT working.


from anki.hooks import addHook, wrap
from aqt.reviewer import Reviewer
import aqt
from aqt import mw
from aqt.utils import showInfo
import anki.notes

def getfieldindex(model,fieldname):
    for c, f in enumerate(model['flds']):
        if f['name'] == fieldname:
            return c

def reload_config(c):
    global config
    global ceA
    config = c
    ceA = config['extractActions']
    for name in ceA:
        model = mw.col.models.byName(ceA[name]['notetype'])
        ceA[name]['mid'] = model['id']
        ceA[name]['fdx'] = getfieldindex(model,ceA[name]['field'])   #field index
        ceA[name]['did'] = mw.col.decks.id(ceA[name]['deck'])  


def load_config(c):
    addHook('profileLoaded', lambda: reload_config(c))

load_config(mw.addonManager.getConfig(__name__))
mw.addonManager.setConfigUpdatedAction(__name__,reload_config) 


myTinyCode =""" 
<script>
tinymce.init({
selector: '.wysiwyg',
inline: true,
visual : false,
    plugins: [
        'autolink',                // format links as hyperlinks
        'colorpicker',             // https://www.tiny.cloud/docs/plugins/colorpicker/ 
        // 'contextmenu',             // add contextmenu
        'hr',                      // insert horizontal rule button
        'image',                   // insert image button
        'link',                    // add hyperlinks
        'lists',                   // add numbered and bulleted lists
        'paste',                   // filter/cleanup content pasted from MS Word - needs config; 
        'table',                   // table management functionality
        'textcolor',               // forecolor/backcolor button
        'textpattern',             // e.g. type "**text**" and text will be bold: pattern match+replace 
        ],
    setup: function(editor) {
        highlight(editor, tinymce, 'highlightGreen',"#00ff00",'alt+w','GR');
        highlight(editor, tinymce, 'highlightBlue',"#00ffff",'alt+e','BL'); 
        highlight(editor, tinymce, 'highlightRed',"#fd9796",'alt+r','RE'); 
        highlight(editor, tinymce, 'highlightYellow',"#ffff00",'alt+q','YE');

        editor.addShortcut("Ctrl+107", 'Superscript', 'Superscript');
        editor.addShortcut("Ctrl+187", 'Subscript', 'Subscript');
        editor.addShortcut("Ctrl+r", 'RemoveFormat', 'RemoveFormat');
        editor.addShortcut('Ctrl+M', 'indent', 'Indent');                       
        editor.addShortcut('Ctrl+Shift+M', 'outdent', 'Outdent');               
        editor.addShortcut('F11', 'InsertUnorderedList', 'InsertUnorderedList');
        editor.addShortcut('123', 'InsertOrderedList', 'InsertOrderedList');   //F12

        editor.addCommand('DirectCutToNew', function() {
            let selected_text = editor.selection.getContent({ format: 'html' });
            tinyMCE.execCommand("delete", "user_interface", selected_text)
            pycmd("DirectCutToNew#" + $(this).data("field") + "#" + selected_text);
        });
        editor.addShortcut('Alt+x', 'DirectCutToNew', 'DirectCutToNew'); 
        editor.addButton('DirectCutToNew', {
                text: 'x',
                tooltip: 'extract to new note' + '(' + 'Alt + X' + ')',
                icon: false,
                cmd: 'DirectCutToNew',
        });

        editor.addCommand('cutToAdd', function() {
            let selected_text = editor.selection.getContent({ format: 'html' });
            tinyMCE.execCommand("delete", "user_interface", selected_text)
            pycmd("cutToAdd#" + $(this).data("field") + "#" + selected_text);
        });
        editor.addShortcut('Alt+Shift+x', 'cutToAdd', 'cutToAdd'); 
        editor.addButton('cutToAdd', {
                text: 'xA',
                tooltip: 'extract to Add window' + '(' + 'Alt + Shift + X' + ')',
                icon: false,
                cmd: 'cutToAdd',
        });

        editor.addCommand('directCOPYtoNew', function() {
            let selected_text = editor.selection.getContent({ format: 'html' });
            pycmd("directCOPYtoNew#" + $(this).data("field") + "#" + selected_text);
        });
        editor.addShortcut('Alt+D', 'directCOPYtoNew', 'directCOPYtoNew'); 
        editor.addButton('directCOPYtoNew', {
                text: 'c',
                tooltip: 'copy to new note' + '(' + 'Alt+D' + ')',
                icon: false,
                cmd: 'directCOPYtoNew',
        });

        editor.addCommand('copyToAdd', function() {
            let selected_text = editor.selection.getContent({ format: 'html' });
            pycmd("copyToAdd#" + $(this).data("field") + "#" + selected_text);
        });
        editor.addShortcut('Alt+Shift+D', 'copyToAdd', 'copyToAdd'); 
        editor.addButton('copyToAdd', {
                text: 'cA',
                tooltip: 'copy to add window' + '(' + 'Alt + Shift + X' + ')',
                icon: false,
                cmd: 'copyToAdd',
        });

    }, 
    toolbar1: "undo redo | forecolor backcolor | alignleft alignjustify | bullist numlist outdent indent table",
    toolbar2: "bold italic underline strikethrough removeformat | highlightYellow highlightGreen highlightBlue highlightRed DirectCutToNew cutToAdd directCOPYtoNew copyToAdd",
});

function highlight(editor, tinymce, name, color, key, buttontext){
    editor.addCommand(name, function () {
        let n = tinymce.activeEditor.selection.getNode();
        let c = tinymce.activeEditor.dom.getStyle(n, 'background-color', true);
        if (c ==color) {
            nc = "transparent";
        }
        else{
            nc =color;
        }
        tinymce.activeEditor.execCommand('HiliteColor', false, nc);
    });  
    editor.addShortcut(key, name, name);  
    editor.addButton(name, {
        text: buttontext,
        tooltip: name + '(' + key + ')',
        icon: false,
        cmd: name,
    });
}
</script>
"""


def open_in_add_window(val):
    newNote = mw.col.newNote()
    newNote.fields[ceA['toAddWindow']['fdx']] = val
    tags = ceA['toAddWindow']['tags']
    newNote.tags = [t for t in tags.split(" ") if t] 
    deckname = ceA['toAddWindow']['deck']
    modelname = ceA['toAddWindow']['notetype']
    
    addCards = aqt.dialogs.open('AddCards', mw.window())
    addCards.editor.setNote(newNote, focusTo=0)
    addCards.deckChooser.setDeckName(deckname)
    addCards.modelChooser.models.setText(modelname)
    addCards.activateWindow()


def direct_create_new_note(val):
    c = ceA['createNewNote'] # createNewNote toAddWindow
    newNote = mw.col.newNote()
    newNote.mid = c['mid']    #model id
    tags = c['tags']
    newNote.tags = [t for t in tags.split(" ") if t]   # see tags.py
    newNote.fields[c['fdx']] = val
    print(dir(newNote))
    newNote.flush()
    mw.col.addNote(newNote)
    #nid = newNote.id   #reinsert new nid as a reference?


def edit(txt, extra, context, field, fullname):
    #txt = """<%s contenteditable="true" data-field="%s">%s</%s>""" % (config['tag'], field, txt, config['tag'])
    txt = """<%s id="my-wysiwyg" class="wysiwyg" contenteditable="true" data-field="%s">%s</%s>""" % (config['tag'], field, txt, config['tag'])
    txt += """<script>"""
    txt += """
            $("[contenteditable=true][data-field='%s']").blur(function() {
                pycmd("ankisave#" + $(this).data("field") + "#" + $(this).html());
            });
        """ % field
    if config['tag'] == "span":
        txt += """
            $("[contenteditable=true][data-field='%s']").keydown(function(evt) {
                if (evt.keyCode == 8) {
                    evt.stopPropagation();
                }
            });
        """ % field
    txt += """
            $("[contenteditable=true][data-field='%s']").focus(function() {
                pycmd("ankisave!speedfocus#");
            });
        """ % field
    txt += """</script>"""
    txt += myTinyCode
    return txt

addHook('fmod_edit', edit)


def myLinkHandler(reviewer, url):
    if url.startswith("ankisave#"):
        fld, val = url.replace("ankisave#", "").split("#", 1)
        reviewer.card.note()[fld] = val
        reviewer.card.note().flush()
        reviewer.card.q(reload=True)
    elif url.startswith("ankisave!speedfocus#"):
        mw.reviewer.bottom.web.eval("""
            clearTimeout(autoAnswerTimeout);
            clearTimeout(autoAlertTimeout);
            clearTimeout(autoAgainTimeout);
        """)
    elif url.startswith("DirectCutToNew#"):
        fld, val = url.replace("DirectCutToNew#", "").split("#", 1)
        nid = direct_create_new_note(val)
    elif url.startswith("cutToAdd#"):
        fld, val = url.replace("cutToAdd#", "").split("#", 1)
        nid = open_in_add_window(val)
    elif url.startswith("directCOPYtoNew#"):
        fld, val = url.replace("directCOPYtoNew#", "").split("#", 1)
        nid = direct_create_new_note(val)
    elif url.startswith("copyToAdd#"):
        fld, val = url.replace("copyToAdd#", "").split("#", 1)
        nid = open_in_add_window(val)
    else:
        origLinkHandler(reviewer, url)

origLinkHandler = Reviewer._linkHandler
Reviewer._linkHandler = myLinkHandler



def onDirectCutSelection():
    mw.reviewer.web.eval("tinymce.activeEditor.execCommand('DirectCutToNew', 'user_interface', '');")  

def onAddCutSelection():
    mw.reviewer.web.eval("tinymce.activeEditor.execCommand('cutToAdd', 'user_interface', '');")  

def onDirectCopySelection():
    mw.reviewer.web.eval("tinymce.activeEditor.execCommand('directCOPYtoNew', 'user_interface', '');")  

def onAddCopySelection():
    mw.reviewer.web.eval("tinymce.activeEditor.execCommand('copyToAdd', 'user_interface', '');")  
    


#from https://ankiweb.net/shared/info/281854631
def _reviewerContextMenu(view, menu):
    if mw.state != "review":
        return
    self = mw.reviewer
    opts = [
       [_("cut direct"), "", onDirectCutSelection],
       [_("copy direct"), "", onDirectCopySelection],
       [_("cut to window"), "", onAddCutSelection],
       [_("copy to window"), "", onAddCopySelection],
    ]
    self._addMenuItems(menu, [None, ])
    self._addMenuItems(menu, opts)
addHook('AnkiWebView.contextMenuEvent', _reviewerContextMenu)






# this is a minimal modification of code from aqt/reviewer.py from anki from 2019-01 which is
#     Copyright: Damien Elmes <anki@ichi2.net>
#     License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
#     from https://github.com/dae/anki/blob/master/aqt/reviewer.py#L133
def _initWeb(self):
        self._reps = 0
        # main window
        self.web.stdHtml(self.revHtml(),
                         css=["reviewer.css"],
                         js=["jquery.js",
                             "browsersel.js",
                             "mathjax/conf.js",
                             "mathjax/MathJax.js",
                             "reviewer.js",
                             "tinymce/tinymce.min.js"])   # mod: added tinymce
        # show answer / ease buttons
        self.bottom.web.show()
        self.bottom.web.stdHtml(
            self._bottomHTML(),
            css=["toolbar-bottom.css", "reviewer-bottom.css"],
            js=["jquery.js", "reviewer-bottom.js"]
        )
Reviewer._initWeb=_initWeb



##############Card Preview in Card Templates Window 
#prevent message "Invalid HTML on card: ReferenceError: tinymce is not defined"

from aqt.clayout import CardLayout
from aqt.webview import AnkiWebView
# this is a minimal modification of code from aqt/clayout.py from anki from 2019-01 which is
#     Copyright: Damien Elmes <anki@ichi2.net>
#     License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
#     from https://github.com/dae/anki/blob/master/aqt/clayout.py#L179
def setupWebviews(self):
    pform = self.pform
    pform.frontWeb = AnkiWebView()
    pform.frontPrevBox.addWidget(pform.frontWeb)
    pform.backWeb = AnkiWebView()
    pform.backPrevBox.addWidget(pform.backWeb)
    jsinc = ["jquery.js","browsersel.js",
                "mathjax/conf.js", "mathjax/MathJax.js",
                "reviewer.js", "tinymce/tinymce.min.js"]    # mod: added tinymce
    pform.frontWeb.stdHtml(self.mw.reviewer.revHtml(),
                            css=["reviewer.css"],
                            js=jsinc)
    pform.backWeb.stdHtml(self.mw.reviewer.revHtml(),
                            css=["reviewer.css"],
                            js=jsinc)
CardLayout.setupWebviews=setupWebviews




##############Card Preview from Browser
#prevent message "Invalid HTML on card: ReferenceError: tinymce is not defined"

from aqt.browser import Browser
# this is a minimal modification of code from aqt/browser.py from anki from 2019-01 which is
#     Copyright: Damien Elmes <anki@ichi2.net>
#     License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
#     from https://github.com/dae/anki/blob/master/aqt/browser.py#L1354
def _setupPreviewWebview(self):
    jsinc = ["jquery.js","browsersel.js",
                "mathjax/conf.js", "mathjax/MathJax.js",
                "reviewer.js", "tinymce/tinymce.min.js"]   # mod: added tinymce
    self._previewWeb.stdHtml(self.mw.reviewer.revHtml(),
                                css=["reviewer.css"],
                                js=jsinc)
Browser._setupPreviewWebview=_setupPreviewWebview




##############Add Window
#just to illustrate my problem:

# this is a minimal modification of code from aqt/editor.py from anki from 2019-01 which is
#     Copyright: Damien Elmes <anki@ichi2.net>
#     License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
#     https://github.com/dae/anki/blob/master/aqt/editor.py#L33 _html
#     https://github.com/dae/anki/blob/master/aqt/editor.py#L69 setupWeb

### Code from Anki:
    # _html = """
    # <style>
    # html { background: %s; }
    # #topbutsOuter { background: %s; }
    # </style>
    # <div id="topbutsOuter"><div id="topbuts" class="clearfix">%s</div></div>
    # <div id="fields"></div>
    # <div id="dupes" style="display:none;"><a href="#" onclick="pycmd('dupes');return false;">%s</a></div>
    # """
### My version
_html = """
<style>
html { background: %s; }
#topbutsOuter { background: %s; }
</style>

<script>
tinymce.init({
selector: '.wysiwyg',
inline: true,
visual : false,
plugins: [
    "noneditable table code fullscreen"
],
toolbar1: "undo redo | styleselect | bold italic underline strikethrough removeformat | forecolor backcolor | alignleft alignjustify | bullist numlist outdent indent | link image | ",
toolbar2: "alignleft alignjustify | bullist numlist outdent indent | link image | table",
noneditable_noneditable_class: "fname",
});
</script>

<div id="topbutsOuter"><div id="topbuts" class="clearfix">%s</div></div>
<div id="fields" class="wysiwyg"></div>
<div id="dupes" style="display:none;"><a href="#" onclick="pycmd('dupes');return false;">%s</a></div>
"""


from aqt.editor import Editor, EditorWebView
from anki.hooks import runFilter
from aqt.utils import shortcut
def setupWeb(self):
    self.web = EditorWebView(self.widget, self)
    self.web.title = "editor"
    self.web.allowDrops = True
    self.web.onBridgeCmd = self.onBridgeCmd
    self.outerLayout.addWidget(self.web, 1)

    righttopbtns = list()
    righttopbtns.append(self._addButton('text_bold', 'bold', _("Bold text (Ctrl+B)"), id='bold'))
    righttopbtns.append(self._addButton('text_italic', 'italic', _("Italic text (Ctrl+I)"), id='italic'))
    righttopbtns.append(self._addButton('text_under', 'underline', _("Underline text (Ctrl+U)"), id='underline'))
    righttopbtns.append(self._addButton('text_super', 'super', _("Superscript (Ctrl++)"), id='superscript'))
    righttopbtns.append(self._addButton('text_sub', 'sub', _("Subscript (Ctrl+=)"), id='subscript'))
    righttopbtns.append(self._addButton('text_clear', 'clear', _("Remove formatting (Ctrl+R)")))
    # The color selection buttons do not use an icon so the HTML must be specified manually
    tip = _("Set foreground colour (F7)")
    righttopbtns.append('''<button tabindex=-1 class=linkb title="{}"
        type="button" onclick="pycmd('colour');return false;">
        <div id=forecolor style="display:inline-block; background: #000;border-radius: 5px;"
        class=topbut></div></button>'''.format(tip))
    tip = _("Change colour (F8)")
    righttopbtns.append('''<button tabindex=-1 class=linkb title="{}"
        type="button" onclick="pycmd('changeCol');return false;">
        <div style="display:inline-block; border-radius: 5px;"
        class="topbut rainbow"></div></button>'''.format(tip))
    righttopbtns.append(self._addButton('text_cloze', 'cloze', _("Cloze deletion (Ctrl+Shift+C)")))
    righttopbtns.append(self._addButton('paperclip', 'attach', _("Attach pictures/audio/video (F3)")))
    righttopbtns.append(self._addButton('media-record', 'record', _("Record audio (F5)")))
    righttopbtns.append(self._addButton('more', 'more'))
    righttopbtns = runFilter("setupEditorButtons", righttopbtns, self)
    topbuts = """
        <div id="topbutsleft" style="float:left;">
            <button title='%(fldsTitle)s' onclick="pycmd('fields')">%(flds)s...</button>
            <button title='%(cardsTitle)s' onclick="pycmd('cards')">%(cards)s...</button>
        </div>
        <div id="topbutsright" style="float:right;">
            %(rightbts)s
        </div>
    """ % dict(flds=_("Fields"), cards=_("Cards"), rightbts="".join(righttopbtns),
                fldsTitle=_("Customize Fields"),
                cardsTitle=shortcut(_("Customize Card Templates (Ctrl+L)")))
    bgcol = self.mw.app.palette().window().color().name()
    # then load page
    self.web.stdHtml(_html % (
        bgcol, bgcol,
        topbuts,
        _("Show Duplicates")),
                        css=["editor.css"],
                        js=["jquery.js", "editor.js", "tinymce/tinymce.min.js" ])   # mod: added tinymce
#Editor.setupWeb=setupWeb

