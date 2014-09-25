
from pyrapp import *


# -----------------------------------------------------------------------------------------------------------
def rename(h,cmap):
    ## print "renaming ", h.GetName()
    toks = h.GetName().split("_")
    cat = None
    for t in toks:
        if t in cmap:
            cat = t
            ## print "cat: ", cat
            break
    if cat:
        newname = h.GetName().replace(cat,cmap[cat])
        h.SetName(newname)

    ## print "renamed ", h.GetName()

# -----------------------------------------------------------------------------------------------------------
class PlotApp(PyRApp):

    def __init__(self,option_list=[]):
        super(PlotApp,self).__init__(option_list=[
            make_option("-c","--categories",dest="categories",action="callback",callback=ScratchAppend(),
                        default=[],help="default: %default"),
            make_option("-l","--labels",dest="labels",action="callback",callback=Load(),metavar="JSON",
                        default={},help="default: %default"),
            make_option("-p","--plots",dest="plots",action="callback",callback=Load(),metavar="JSON",
                        default=[],help="default: %default"),
            make_option("-t","--template",dest="template",action="store",type="string",
                        default="%(name)s_%(cat)s_%(sample)s",help="default: %default"),
            make_option("--data",dest="data",action="callback",callback=Load(),metavar="JSON",
                        default=None,help="default: %default"),
            make_option("--sig",dest="sig",action="callback",callback=Load(),metavar="JSON",
                        default=None,help="default: %default"),
            make_option("--bkg",dest="bkg",action="callback",callback=Load(),metavar="JSON",
                        default=None,help="default: %default"),
            make_option("-i","--infile",dest="infile",action="store",type="string",
                        default=None,help="default: %default"),
            make_option("--data-file",dest="data_file",action="store",type="string",
                        default=None,help="default: %default"),
            make_option("--sig-file",dest="sig_file",action="store",type="string",
                        default=None,help="default: %default"),
            make_option("--bkg-file",dest="bkg_file",action="store",type="string",
                        default=None,help="default: %default"),
            ]+option_list)
        

        self.data_ = None
        self.sig_  = None
        self.bkg_  = None
        self.tfiles_ = {}
        
        global ROOT, style_utils
        import ROOT
        import style_utils

    def __call__(self,options,args):

        self.template_ = options.template

        self.data_ = self.openDataset(self.data_,options.data_file,options.infile,options.data)
        self.sig_  = self.openDataset(self.sig_ ,options.sig_file ,options.infile,options.sig )
        self.bkg_  = self.openDataset(self.bkg_ ,options.bkg_file ,options.infile,options.bkg )
        
        
        self.setStyle("*", [(rename,options.labels)] )
        self.setStyle("*_legend",[("SetFillStyle",0),("SetLineColor","kWhite"),("SetShadowColor","kWhite")] )
        
        self.dataMcComparison(options,args)

    def openDataset(self,dst,fname,default,extra):
        global ROOT
        
        if not fname:
            fname = default
        if (not dst) and fname and extra:
            if not fname in self.tfiles_:
                self.tfiles_[fname] = ROOT.TFile.Open(fname)
            fin = self.tfiles_[fname]
            return fin,extra
        
        return dst
    
    def dataMcComparison(self,options,args):
        data  = self.data_;
        bkg   = self.bkg_;
        sig   = self.sig_;
        plots = options.plots
        categories = options.categories
        
        # loop over categories
        for cat in categories:
            if type(cat) == int: 
                catname = "cat%d" % cat
            else:
                catname = cat

            # loop over plots
            for plot in plots:

                plotname, plotmodifs, drawopts, legPos = plot
                if drawopts == None:
                    drawopts = options.drawopts
                if legPos == None:
                    legPos = options.legpos
                    
                drawmethod, dataopt, bkgopt, sigopt = drawopts

                bkghists = []
                sighists = []
                datahists = []
                
                # read background MC
                if bkg != None:
                    bkgfile, bkgprocs = bkg
                    bkghists = [ self.readProcess(bkgfile,*subprocs,plot=plotname,plotmodifs=plotmodifs,category=catname) for subprocs in bkgprocs ]
                    
                # read signal MC
                if sig != None:
                    sigfile, sigprocs = sig
                    sighists = [ self.readProcess(sigfile,*subprocs,plot=plotname,plotmodifs=plotmodifs,category=catname) for subprocs in sigprocs ]
                    
                # read data
                if data != None:
                    datafile, dataprocs = data
                    datahists = [ self.readProcess(datafile,*subprocs,plot=plotname,plotmodifs=plotmodifs,category=catname) for subprocs in dataprocs ]
                    
                # collect histograms
                allhists = datahists+bkghists+sighists
                if len(allhists) == 0:
                    print "Nothing to plot for %s %s" % (plotname,catname)
                    continue
                self.keep(allhists)
                
                # make empty frame histogram for convenience
                frame = allhists[0].Clone("%s_%s_frame" % (plotname,catname) )
                frame.Reset("ICE")
                frame.SetEntries(0)
                self.keep(frame,True)
                ymax = 0.
                ymin = 0.
                
                # allocate canvas and legend and draw frame
                canv,leg = self.makeCanvAndLeg("%s_%s" % ( plotname, catname), legPos )
                frame.Draw()
            
                # draw background first
                if len(bkghists) > 0:
                    bkgstk = self.makeStack("bkg_%s_%s" % ( plotname, catname), bkghists)
                    ymax = max(ymax,self.drawStack(bkgstk,drawmethod,"%s SAME"%bkgopt))
                    
                # then data
                if len(datahists) > 0:
                    datastk = self.makeStack("data_%s_%s" % ( plotname, catname),datahists)
                    ymax = max(ymax,self.drawStack(datastk,drawmethod,"%s SAME"%dataopt))
            
                # and finally signal
                if len(sighists) > 0:
                    sigstk = self.makeStack("sig_%s_%s" % ( plotname, catname),sighists)
                    ymax = max(ymax,self.drawStack(sigstk,drawmethod,"%s SAME"%sigopt))
            
                # make legend
                for h in allhists:
                    legopt = "f"
                    if hasattr(h,"legopt"):
                        legopt = h.legopt
                    leg.AddEntry(h,"",legopt)
            
                # adjust yaxis
                frame.GetYaxis().SetRangeUser(ymin,ymax*1.2)
                leg.Draw("same")
                canv.RedrawAxis()
            
                # if needed draw inset with zoom-in
                ##   DrawInset[rngmin,rngmax,posx1,posy1,posx2,posy2]
                if "DrawInset" in drawmethod:
                    inset =  [ float(f) for f in drawmethod.split("DrawInset")[1].split("[")[1].split("]")[0].split(",") ]
                    rng = inset[0:2]
                    pos = inset[2:]
                    
                    padname = "%s_%s_inset" % ( plotname, catname)
                    pad = ROOT.TPad(padname, padname, *pos)
                    self.keep(pad,True)
                    pad.Draw("")
                    pad.SetFillStyle(0)
                    
                    pad.cd()
                    padframe = frame.Clone()
                    padframe.GetXaxis().SetRangeUser(*rng)
                    padframe.GetYaxis().SetRangeUser(ymin,ymax*1.2)
                    padframe.Draw()
                    self.keep(padframe)
                    
                    if len(bkghists) > 0:
                        self.drawStack(bkgstk,"Draw",bkgopt+" same")
                    
                    if len(datahists) > 0:
                        self.drawStack(datastk,"Draw",dataopt+" same")
                        
                    if len(sighists) > 0:
                        self.drawStack(sigstk,"Draw",sigopt+" same")
            
                    pad.RedrawAxis()
                            
                # FIXME ratio plots
                
    #
    # Read histograms for a given process, applying manipulators
    #
    def readProcess(self,fin,name,title,style,subproc,plot,plotmodifs,category):

        names = subproc.keys()
        histos = self.readHistos(fin,plot,samples=names,cat=category)
        for iplot in range(len(histos)):
            h = histos[iplot]
            hname = names[iplot]
            h = style_utils.apply(h,subproc[hname])
        
        sum = histos[0].Clone(name)
        sum.SetTitle(title)
        
        for h in histos[1:]:
            sum.Add(h)

        self.keep(sum,True)
        sum = style_utils.apply(sum,plotmodifs)
        sum = style_utils.apply(sum,style)
        
        return sum

    #
    # Read plots from globe histogram files
    #
    def readHistos(self,fin, name, cat="cat0", samples=[]):
    
        ret = []
        for s in samples:
            nam = self.template_ % { "name" : name, "cat" : cat, "sample" : s }
            h = fin.Get(nam)
            h.GetXaxis().SetTitle(  h.GetXaxis().GetTitle().replace("@"," ") )
            ret.append(h)
            
        return ret

    #
    # Make THStack out of python list
    #
    def makeStack(self,name,histos):
        stk = ROOT.THStack()
        for h in histos:
            stk.Add(h)
        self.keep(stk)
        return stk


    #
    # Build envelope of variations
    #
    def makeEnvelope(self,name,histos):
        
        nominal = histos[0]
        errPlus  = nominal.Clone( "%s_ErrPlus" % name )
        errMinus = nominal.Clone( "%s_ErrMinus" % name )

        style = self.getStyle("envelope")
        if style:
            style_utils.apply( errPlus,  style )
            style_utils.apply( errMinus, style )
            
        for ibin in range(nominal.GetNbinsX()):
            hist = ROOT.TH1F("hist","hist",11,-5.,5.)
            hist.Reset("ICE")
            hist.Sumw2()
            points = []
            
            plus  = nominal.GetBinContent(ibin+1)
            minus = nominal.GetBinContent(ibin+1)
            nom   = nominal.GetBinContent(ibin+1)
            err   = nominal.GetBinError(ibin+1)
            
            points.append( [nom,err] )
            hist.Fill(nom)
            for h in histos[1:]:
                content =  h.GetBinContent(ibin+1)
                err     =  h.GetBinError(ibin+1)
                hist.Fill(content)
                points.append( [content,err] )
                if content < minus:
                    minus = content
                if content > plus:
                    plus = content
    
            if hist.GetRMS() == 0.:
                errPlus.SetBinContent(ibin+1,plus)
                errMinus.SetBinContent(ibin+1,minus)
                continue
                
            hist2 = ROOT.TH1F("hist2","hist2",11,hist.GetMean()-5.*hist.GetRMS(),hist.GetMean()+5.*hist.GetRMS())
            hist2.Sumw2()
            for p,e in points:
                hist2.Fill(p)
                
            func = ROOT.TF1("func","[0]*exp( -0.5*pow( (x-[1])/( (x>=0)*[2] + (x<=0)*[3] ) ,2.) )",hist2.GetMean()-5.*hist2.GetRMS(),hist2.GetMean()+5.*hist2.GetRMS())
            func.SetParameters(len(histos),hist2.GetMean(),hist2.GetRMS(), hist2.GetRMS())

            stat = int( hist2.Fit( func, "L" ) )
            if stat == 0:
                errPlus.SetBinContent(ibin+1, max(nom,func.GetParameter(1)+fabs(func.GetParameter(2))))
                errMinus.SetBinContent(ibin+1,min(nom,func.GetParameter(1)-fabs(func.GetParameter(3))))
            else:
                errPlus.SetBinContent(ibin+1,plus)
                errMinus.SetBinContent(ibin+1,minus)

        self.keep([errPlus,errMinus,nominal])
        return self.makeStack(name,[errPlus,errMinus,nominal])

    #
    # Prepare canvas and legend
    #
    def makeCanvAndLeg(self,name,legPos):
        canv = ROOT.TCanvas(name)
        leg  = ROOT.TLegend(*legPos)
        leg.SetName("%s_legend" % name)
        
        self.keep( [canv,leg], True )
        return canv,leg


    #
    # Draw a THStack
    #
    def drawStack(self,stk, method, option):
        ymax = 0.
        if "DrawNormalized" in method:
            rng = None
            if "[" in method:
                rng = [ float(f) for f in method.split("DrawNormalized")[1].split("[")[1].split("]")[0].split(",") ]
            histos = [ stk.GetStack().At(0) ]
            if "nostack" in option:
                histos = stk.GetHists()
                option = option.replace("nostack","")
            for h in histos:
                h.SetFillStyle(0)
                h.SetLineWidth(2)
                bmin = -1
                bmax = -1
                if rng:
                    bmin = h.FindBin(rng[0])
                    bmax = h.FindBin(rng[1])
                h.Scale(1./h.Integral(bmin,bmax))
                h.Draw("%s SAME" % option)
                ymax = max(ymax, h.GetMaximum()) 
        else:
            getattr(stk,method.split(",")[0])("%s" % option)
            ymax = stk.GetMaximum(option)
            
        return ymax

if __name__ == "__main__":

    app = PlotApp()

    app.run()
