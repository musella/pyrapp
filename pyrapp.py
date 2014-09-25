from optparse import OptionParser, make_option
import sys
import json
import os

from optpars_utils import ScratchAppend, Load
from fnmatch import fnmatch

from pprint import pprint

# -----------------------------------------------------------------------------
class PyRApp(object):
    
    def __init__(self,option_list,defaults=None):
        self.objs_ = []
        self.canvs_ = []

        opt_list=[
            make_option("-I","--interactive",
                        action="store_true", dest="interactive",
                        default=sys.flags.interactive,
                        help="default: %default", metavar=""
                        ),
            make_option("-b","--non-interactive",
                        action="store_false", dest="interactive",
                        help="default: %default", metavar=""
                        ),
            make_option("-s","--save",
                        action="store_true", dest="save",
                        default=False,
                        help="default: %default", metavar=""
                        ),
            make_option("--saveas",
                        action="callback", dest="saveas", type="string", callback=ScratchAppend(),
                        default=["png","root"],
                        help="default: %default", metavar=""
                        ),
            make_option("--savebw",
                        action="store_true", dest="savebw", default=False,
                        help="default: %default",
                        ),
            make_option("-o","--outdir",
                        action="store", type="string", dest="outdir", default=None,
                        help="default: %default",
                        ),
            make_option("--load",
                        action="callback", dest="__opts__", type="string", callback=Load(), metavar="JSON",
                        help="default: %default"
                        ),
            make_option("--styles",
                        action="callback", dest="styles", type="string", callback=Load(), metavar="JSON",
                        default={},
                        help="default: %default"
                        ),
            make_option("-v","--verbose",
                        action="store_true", dest="verbose",
                        default=False,
                        help="default: %default"
                        )
            ] + option_list
        
        parser = OptionParser(option_list=opt_list)
        
        (self.options, self.args) = parser.parse_args()

        if self.options.verbose:
            print ( json.dumps( self.options.__dict__,indent=4,sort_keys=True) )  
            
        if not self.options.interactive:
            sys.argv.append("-b")
            if self.options.outdir:
                self.options.save = True
        if not self.options.outdir:
            self.options.outdir = os.getcwd()
        else:
            try:
                os.mkdir(self.options.outdir)
            except:
                pass
            
        
        global ROOT, style_utils
        import ROOT
        import style_utils
        
    def run(self):
        self.__call__(self.options,self.args)
        if self.options.save:
            self.save()
            
    def save(self):
        for c in self.canvs_:
            c.Modified()
            for fmt in self.options.saveas:
                c.SaveAs("%s/%s.%s" % ( self.options.outdir, c.GetName(), fmt ) )
            if self.options.savebw:
                c.SetGrayscale(True)
                for fmt in self.options.saveas:
                    if not fmt in ["C","root"]:
                        c.SaveAs("%s/%s_bw.%s" % ( self.options.outdir, c.GetName(), fmt ) )
                c.SetGrayscale(False)

    def keep(self,objs,format=False):
        if type(objs) == list:
            for obj in objs:
                self.keep(obj,format)
            return

        self.objs_.append(objs)
        if objs.IsA().InheritsFrom("TCanvas"):
            self.canvs_.append(objs)
        if format:
            for key,st in self.options.styles.iteritems():
                if fnmatch(objs.GetName(),key):
                    style_utils.apply(objs,st)
                                            
    def getStyle(self,key):
        if key in self.options.styles:
            return self.options.styles[key]
        return None

    def setStyle(self,key,style,replace=False):
        if key in self.options.styles and not replace:
            self.options.styles[key].extend( style )
        else:
            self.options.styles[key] = style
        
# -----------------------------------------------------------------------------------------------------------
class Test(PyRApp):

    def __init__(self):
        super(Test,self).__init__(option_list=[
            make_option("-t","--test",
                        action="store", dest="test", type="int",
                        default=None,
                        help="default: %default", metavar=""
                        ),
            make_option("-l","--loadmap",
                        action="callback", dest="loadmap", type="string", callback=options.Load(),
                        default={}
                        ),
            ])
        

    def __call__(self,options,args):

        print self.__dict__
        print ROOT

        options.styles["h"]=[ ("SetLineColor","kRed"), ("SetFillColor","kOrange") ]
        
        hist = ROOT.TH1F("h","h",101,-5.05,5.05)

        hist.FillRandom("gaus",1000)
        hist.Fit("gaus")

        canv = ROOT.TCanvas("canv","canv")
        self.keep([hist,canv],format=True)
        
        canv.cd()
        
        style_utils.apply( hist.GetListOfFunctions().At(0), [("SetLineWidth",2),("SetLineColor","kBlack")] )
        hist.Draw()

        
# -----------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    test = Test()
    test.run()
    
    
