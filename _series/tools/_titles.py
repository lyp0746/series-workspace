import glob,io,re,os,sys
w=io.open(sys.argv[2],'w',encoding='utf-8',newline='\n')
for b in sys.argv[1].split(','):
    w.write(f"== {b}\n")
    for f in sorted(glob.glob(f'{b}/source/ch*.html')):
        t=io.open(f,encoding='utf-8').read()
        m=re.search(r'<h2[^>]*>([^<]*)</h2>',t)
        n=len(re.findall(r'[\u4e00-\u9fff]',re.sub(r'<[^>]+>','',t)))
        w.write(f"{os.path.basename(f)}|{m.group(1) if m else '?'}|{n//1000}k|{len(re.findall('<h3',t))}节\n")
w.close()
