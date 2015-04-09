import ROOT

# -----------------------------------------------------------------------------------------------------------
def applyTo(obj,method,style):
    res = getattr(obj,method)()
    apply(res,style)

# -----------------------------------------------------------------------------------------------------------
def xtitle(h,tit):
    h.GetXaxis().SetTitle(tit)

# -----------------------------------------------------------------------------------------------------------
def ytitle(h,tit):
    ## print "ytitle", h.GetName(), tit
    h.GetYaxis().SetTitle( tit % { "binw" : h.GetBinWidth(0) } )
    # h.GetYaxis().SetTitle(tit)

# -----------------------------------------------------------------------------------------------------------
def ztitle(h,tit):
    h.GetZaxis().SetTitle(tit)

# -----------------------------------------------------------------------------------------------------------
def logy(h,ymin=None):
    if h.IsA().InheritsFrom(ROOT.TPad.Class()):
        h.SetLogy()
        if ymin:
            h.ymin = ymin

# -----------------------------------------------------------------------------------------------------------
def scaleFonts(h,scale):
    ## print "scaleFonts", scale
    for ax in h.GetXaxis(),h.GetYaxis(),h.GetZaxis():
        ax.SetTitleSize(ax.GetTitleSize()*scale)
        ax.SetLabelSize(ax.GetLabelSize()*scale)

    for ax in h.GetYaxis(),:
        ax.SetTitleOffset(ax.GetTitleOffset()/scale)
        

# -----------------------------------------------------------------------------------------------------------
def colors(h,color):
    h.SetMarkerColor(color)
    h.SetLineColor(color)
    h.SetFillColor(color)

# -----------------------------------------------------------------------------------------------------------
def legopt(h,opt):
    h.legopt = opt

# -----------------------------------------------------------------------------------------------------------
def xrange(h,xmin,xmax):
    h.GetXaxis().SetRangeUser(xmin,xmax)
    
# -----------------------------------------------------------------------------------------------------------
def yrange(h,xmin,xmax):
    h.GetYaxis().SetRangeUser(xmin,xmax)

# -----------------------------------------------------------------------------------------------------------
def zrange(h,xmin,xmax):
    h.GetZaxis().SetRangeUser(xmin,xmax)

# -----------------------------------------------------------------------------------------------------------
def mvStatBox(h,prev=None,vert=-1,horiz=0.):
    ROOT.gPad.Update()
    st = h.FindObject('stats')
    st.SetLineColor(h.GetLineColor())
    st.SetTextColor(h.GetLineColor())

    if prev:
        shiftx = (prev.GetX2NDC() - st.GetX1NDC())*horiz
        shifty = (prev.GetY2NDC() - st.GetY1NDC())*vert

        st.SetX1NDC(st.GetX1NDC()+shiftx)
        st.SetX2NDC(st.GetX2NDC()+shiftx)

        st.SetY1NDC(st.GetY1NDC()+shifty)
        st.SetY2NDC(st.GetY2NDC()+shifty)

    ROOT.gPad.Update()
    return st

# -----------------------------------------------------------------------------------------------------------
def addCmsLumi(canv,period,pos,extraText=None):
    if extraText:
        ROOT.writeExtraText = True
        if type(extraText) == str and extraText != "":
            ROOT.extraText = extraText
    ROOT.CMS_lumi(canv,period,pos)


# -----------------------------------------------------------------------------------------------------------
def printIntegral(h,xmin=None,xmax=None):
    bmin=-1
    bmax=-1
    if xmin:
        bmin = h.FindBin(xmin)
    if xmax:
        bmax = h.FindBin(xmax)

    print("Integral %s(%s,%s): %1.3g" % (h.GetName(), str(xmin), str(xmax), h.Integral(bmin,bmax) ))
        
# -----------------------------------------------------------------------------------------------------------
def apply(h,modifs):
    for method in modifs:
        raw = method
        
        args = None
        ret = None
        if type(method) == tuple or type(method) == list:
            method, args = method
        if type(method) == unicode:
            method = str(method)

        if type(method) == str:
            if hasattr(h,method):
                method = getattr(h,method)
            else:
                method = globals()[method]

        exceptions = []
        try:
            if args == None:
                try:
                    ret = method(h)
                except Exception as e:
                    exceptions.append(e)
                    ret = method()
            else:
                if not ( type(args) == tuple or type(args) == list ):
                    args = [args]
                for i,a in enumerate(args):
                    if type(a) == unicode or type(a) == str:
                        if a.startswith("k") or a.startswith("my") and hasattr(ROOT,a):
                            try:
                                args[i] = getattr(ROOT,a)
                            except Exception as e:
                                print e
                try:
                    ret = method(h,*args)
                except Exception as e:
                    exceptions.append(e)
                    ret = method(*args)
        except Exception as e:
            exceptions.append(e)
            exc = "\n".join( str(e) for e in exceptions)
            raise Exception("Failed to apply %s to %s. Got following exceptions:\n%s" % ( str(raw), str(h), exc ))
        
    return h
