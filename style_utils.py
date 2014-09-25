import ROOT

# -----------------------------------------------------------------------------------------------------------
def xtitle(h,tit):
    h.GetXaxis().SetTitle(tit)

# -----------------------------------------------------------------------------------------------------------
def ytitle(h,tit):
    h.GetYaxis().SetTitle( tit % { "binw" : h.GetBinWidth(0) } )
    # h.GetYaxis().SetTitle(tit)

# -----------------------------------------------------------------------------------------------------------
def ztitle(h,tit):
    h.GetZaxis().SetTitle(tit)

# -----------------------------------------------------------------------------------------------------------
def colors(h,color):
    h.SetMarkerColor(color)
    h.SetLineColor(color)
    h.SetFillColor(color)

# -----------------------------------------------------------------------------------------------------------
def legopt(h,opt):
    h.legopt = opt

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
