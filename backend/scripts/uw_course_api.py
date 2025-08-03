#!/usr/bin/env python3
from __future__ import annotations
import sys,subprocess,importlib.util,argparse,json,time
from pathlib import Path
from datetime import datetime,timezone
import requests
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

s=requests.Session()
VERSION="1.0.0";VERSION_BANNER=f"UW Course Data Helper {VERSION} by Hassam Nizami";print(VERSION_BANNER)
P=["requests","rich"];m=[p for p in P if importlib.util.find_spec(p) is None]
if m:
 print("Missing required packages:"+",".join(m))
 c=input("Install missing packages now? [y/N]:").strip().lower()
 if c=="y":
  try:subprocess.check_call([sys.executable,"-m","pip","install","--upgrade","pip"]+m)
  except subprocess.CalledProcessError:
   print("\nAutomatic installation failed.");print("Please install the missing packages manually by running:");print(f"  {sys.executable} -m pip install {' '.join(m)}");sys.exit(1)
  r=[p for p in P if importlib.util.find_spec(p) is None]
  if r:print("\nStill missing packages:"+",".join(r));print("Please install them manually by running:");print(f"  {sys.executable} -m pip install {' '.join(r)}");sys.exit(1)
  print("\nAll dependencies installed successfully—continuing.")
 else:
  print("\nCannot continue without installing required packages.");print(f"Install them manually with:\n  {sys.executable} -m pip install "+",".join(m));sys.exit(1)

U="https://static.uwcourses.com";ROOT=Path("c-data");DEFAULT_DIR=ROOT

def a(n):
 for u in("B","KB","MB","GB","TB"):
  if n<1024:return f"{n:.2f}{u}"
  n/=1024
 return f"{n:.2f}PB"

def bb(s):
 if s<1:return f"{int(s*1000)}ms"
 if s<60:return f"{s:.2f}s"
 m=int(s//60);ss=int(s%60);return f"{m}:{ss:02d}"

def c(p):
 r=s.get(U+p,timeout=10);r.raise_for_status();return r.json()

def d(o,e,i=2):
 e.parent.mkdir(parents=True,exist_ok=True)
 if i is None:t=json.dumps(o,separators=("," ,":"))
 else:t=json.dumps(o,indent=i)
 e.write_text(t,encoding="utf-8")

write_json=d

def e(_):print(json.dumps(c("/update.json"),indent=2))

def f(x):
 p=c("/subjects.json")
 if x.code:
  q=x.code.upper()
  if q not in p:sys.exit(f"ERROR: subject code '{q}' not found")
  print(f"{q}: {p[q]}")
 else:print(json.dumps(p,indent=2))

def g(_):print(json.dumps(c("/terms.json"),indent=2))

def h(x):
 t=x.course_code.replace("/","_").replace(" ","_").upper()
 p=c(f"/course/{t}.json")
 if x.field:
  v2=p
  for y in x.field.split("."):
   v2=v2[int(y)] if isinstance(v2,list) and y.isdigit() else v2[y]
  p=v2
 s2=json.dumps(p,indent=2)
 if x.stdout:print(s2)
 else:
  q=Path(x.out) if x.out else DEFAULT_DIR/f"{t}.json"
  d(p,q,2);print(f"Saved to {q}")

def i(x):
 ts=c("/update.json")["updated_on"]
 I=2 if x.pretty else None
 subs=c("/subjects.json");d(subs,ROOT/"names"/"subjects.json",I);print(f"Saved subjects list to {ROOT/'names'/'subjects.json'}")
 C=ROOT/"courses";C.mkdir(parents=True,exist_ok=True)
 fs=[p for p in C.glob("*.json") if p.name!="info_log.json"];E=sorted(p.stem for p in fs)
 if x.reset:
  for p in fs:p.unlink()
  E=[];fs=[]
 tot=0
 if x.update_existing:
  dt=datetime.fromisoformat(ts.replace("Z","+00:00"))
  stale=E[:] if x.force else [p for p in fs if datetime.fromtimestamp(p.stat().st_mtime,timezone.utc)<=dt]
  n=len(stale)
  if n:
   with Live(refresh_per_second=4) as L:
    for idx,u in enumerate(sorted(stale),1):
     p2=c(f"/course/{u}.json");d(p2,C/f"{u}.json",I);tot+=1;L.update(Text.assemble(("Updated "+str(idx)+" of "+str(n)+" outdated files","bold green")))
   print()
 last=E[-1] if E else None
 a0=b0=0
 if last:
  p0,num=last.rsplit("_",1)
  if p0 in subs and num.isdigit():
   a0=list(subs).index(p0);b0=int(num)+1
   if b0>=1000:a0+=1;b0=0
 fs2=[p for p in C.glob("*.json") if p.name!="info_log.json"]
 if fs2:
  o=min(fs2,key=lambda p:p.stat().st_mtime);on,o_time=o.name,datetime.fromtimestamp(o.stat().st_mtime,timezone.utc).isoformat()
 else:on,o_time="<none>",""
 if x.dev:print("Downloading all courses")
 t0=time.monotonic();tb=0;se=0;total=len(subs)*1000-(a0*1000+b0)
 with Live(refresh_per_second=4) as L:
  for ii,sb in enumerate(list(subs)[a0:],a0):
   nn=b0 if ii==a0 else 0
   for num in range(nn,1000):
    code=f"{sb}_{num}"
    el=time.monotonic()-t0;spd=tb/el if el>0 else 0
    parts=[]
    if x.dev:
     eta=(el/(tot+1))*(total-(tot+1));parts+=[(("API updated: "),"bold"),ts,("\n",""),("Oldest file: ","bold"),on,(" (",""),o_time,(")\n",""),("Last updated: ","bold"),last or"<none>",("\n","")]
    else:parts+=[(("Last saved: "),"bold"),last or"<none>",("\n","")]
    parts+=[(("Current trying: "),"bold"),code,("\n",""),("Downloaded: ","bold"),a(tb),(" @ "),a(spd)+"/s"]
    if x.dev:parts+=[("\nETA: "),bb(eta)]
    L.update(Panel(Text.assemble(*parts),title="Progress"))
    try:r=s.get(f"{U}/course/{code}.json",timeout=10);r.raise_for_status()
    except requests.HTTPError:continue
    tb+=len(r.content);d(r.json(),C/f"{code}.json",I);tot+=1;se+=1;last=code
 print()
 F=[p for p in C.glob("*.json") if p.name!="info_log.json"]
 if F:
  o2=min(F,key=lambda p:p.stat().st_mtime);info={"oldest_file":o2.name,"oldest_mtime":datetime.fromtimestamp(o2.stat().st_mtime,timezone.utc).isoformat()}
 else:info={"oldest_file":None,"oldest_mtime":None}
 d(info,C/"info_log.json",I);print(f"Downloads complete: {tot} courses saved to {C}")

def j(_):
 tests=[]
 try:d1=c("/update.json");assert isinstance(d1,dict) and "updated_on" in d1;tests.append(("update.json","pass"))
 except Exception as e:tests.append(("update.json",f"fail:{e}"))
 try:s1=c("/subjects.json");assert isinstance(s1,dict) and s1;tests.append(("subjects.json","pass"))
 except Exception as e:tests.append(("subjects.json",f"fail:{e}"))
 try:t1=c("/terms.json");assert isinstance(t1,dict) and t1;tests.append(("terms.json","pass"))
 except Exception as e:tests.append(("terms.json",f"fail:{e}"))
 try:c1=c("/course/COMPSCI_300.json");assert isinstance(c1,dict) and "course_reference" in c1 and "course_title" in c1;tests.append(("course COMPSCI_300","pass"))
 except Exception as e:tests.append(("course COMPSCI_300",f"fail:{e}"))
 try:tmp=DEFAULT_DIR/"test_write.json";d({"test":123},tmp);assert json.loads(tmp.read_text(encoding="utf-8"))=={"test":123};tmp.unlink();tests.append(("write_json","pass"))
 except Exception as e:tests.append(("write_json",f"fail:{e}"))
 try:dh=build_parser(dev_mode=True).format_help();nh=build_parser(dev_mode=False).format_help();assert any(l.strip().startswith("update") for l in dh.splitlines());assert any(l.strip().startswith("test") for l in dh.splitlines());assert not any(l.strip().startswith("update") for l in nh.splitlines());assert not any(l.strip().startswith("test") for l in nh.splitlines());tests.append(("help menu flags","pass"))
 except AssertionError as e:tests.append(("help menu flags",f"fail:{e}"))
 except Exception as e:tests.append(("help menu flags",f"fail:{e}"))
 try:pth=ROOT/"courses"/"info_log.json";sample={"oldest_file":"X.json","oldest_mtime":"2025-08-01T00:00:00Z"};d(sample,pth);rb=json.loads(pth.read_text(encoding="utf-8"));pth.unlink();assert set(rb.keys())=={"oldest_file","oldest_mtime"};tests.append(("info_log format","pass"))
 except Exception as e:tests.append(("info_log format",f"fail:{e}"))
 try:assert VERSION_BANNER=="UW Course Data Helper 1.0.0 by Hassam Nizami";tests.append(("version banner","pass"))
 except AssertionError:tests.append(("version banner",f"fail: expected '{VERSION_BANNER}'"))
 for n,r in tests:print(f"{n}:{r}")

def build_parser(dev_mode):
 p=argparse.ArgumentParser(prog="uw_course_api.py",description="UW Course Data Fetcher",formatter_class=argparse.RawTextHelpFormatter,epilog=("Commands:\n  update\n  test") if dev_mode else ("Commands:\n  course\n  all"))
 p.add_argument("-d","--dev",action="store_true");p.add_argument("--pretty",action="store_true")
 sp=p.add_subparsers(dest="command")
 if dev_mode:
  sp.add_parser("update").set_defaults(func=e)
  ps=sp.add_parser("subjects");ps.add_argument("-c","--code");ps.set_defaults(func=f)
  sp.add_parser("terms").set_defaults(func=g)
  sp.add_parser("test").set_defaults(func=j)
 pc=sp.add_parser("course");pc.add_argument("course_code");pc.add_argument("-f","--field");pc.add_argument("--stdout",action="store_true");pc.add_argument("--out");pc.set_defaults(func=h)
 pa=sp.add_parser("all");pa.add_argument("-u","--update-existing",action="store_true");pa.add_argument("-r","--reset",action="store_true");pa.add_argument("-f","--force",action="store_true");pa.set_defaults(func=i)
 return p

def main():
 e=argparse.ArgumentParser(add_help=False);e.add_argument("-d","--dev",action="store_true");ka,rs=e.parse_known_args()
 ap=build_parser(ka.dev);a=ap.parse_args(rs);a.dev=ka.dev
 if not a.command:ap.print_help();sys.exit(0)
 if a.dev:print("** Developer mode enabled **")
 try:a.func(a)
 except requests.HTTPError as e:code=e.response.status_code;sys.exit(f"ERROR HTTP {code}:{'not found' if code==404 else e}")
 except Exception as e:sys.exit(f"ERROR:{e}")

if __name__=="__main__":main()
