import subprocess,re,glob,collections,sys
APPLY = '--apply' in sys.argv
def hdr(txt):
    m=re.match(r'---\n(.*?)\n---',txt,re.S); return m
def tags(h,k):
    m=re.search(r'^%s: (.*)$'%k,h,re.M); return [t.strip() for t in m.group(1).split(',') if t.strip()] if m else []
INTL_HR={'hr.2.1','hr.2.2','hr.2.3','hr.2.5','hr.2.6','hr.1.3'}
TARGETS={'inv.7.2':{'hr.2.7','hr.2.8','hr.2.9','hr.2.10'},'inv.7.3':{'hr.2.9','hr.2.10','hr.2.11'},'inv.6.3':{'hr.2.7'},'inv.6.6':{'hr.2.4'}}
removed=collections.Counter(); files=0
for f in glob.glob('evidence/*/*.md'):
    try: old=subprocess.run(['git','show','3d104a4:'+f],capture_output=True,text=True,check=True).stdout
    except subprocess.CalledProcessError: continue   # record created later: hand-tagged, leave it
    src=open(f,encoding='utf-8').read(); m=hdr(src); h=m.group(1)
    oh=hdr(old).group(1)
    oldtags=set(tags(oh,'core')+tags(oh,'support'))
    core=tags(h,'core'); sup=tags(h,'support')
    typ=re.search(r'^type: (.*)$',h,re.M).group(1).strip()
    drop=set()
    for t,src_tags in TARGETS.items():
        if t in sup and t not in oldtags:          # added by pass 2
            if t=='inv.6.6':
                intl = typ=='international' or bool(set(core+sup)&INTL_HR) or any(c.startswith('crime.6') for c in core+sup)
                if not intl: drop.add(t)
            else:
                if not (set(core)&src_tags): drop.add(t)   # source hr tag was only a support tag
    if drop:
        files+=1
        for d in drop: removed[d]+=1
        if APPLY:
            nsup=[t for t in sup if t not in drop]
            h2=re.sub(r'^support: .*$','support: '+', '.join(nsup),h,flags=re.M)
            open(f,'w',encoding='utf-8').write(src[:m.start(1)]+h2+src[m.end(1):])
print('files',files,dict(removed))
