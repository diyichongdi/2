# -*- coding: utf-8 -*-
import json, re
from data import E, CAT_LABEL, GROUP_LABEL

# ---------- 电子排布 (Aufbau + 常见例外) ----------
ORDER = [("1s",2),("2s",2),("2p",6),("3s",2),("3p",6),("4s",2),("3d",10),("4p",6),
         ("5s",2),("4d",10),("5p",6),("6s",2),("4f",14),("5d",10),("6p",6),
         ("7s",2),("5f",14),("6d",10),("7p",6)]
CAP = {"s":2,"p":6,"d":10,"f":14}
EXC = {
 24:[("3d",1),("4s",-1)], 29:[("3d",1),("4s",-1)],
 41:[("4d",1),("5s",-1)], 42:[("4d",1),("5s",-1)], 44:[("4d",1),("5s",-1)],
 45:[("4d",1),("5s",-1)], 46:[("4d",2),("5s",-2)], 47:[("4d",1),("5s",-1)],
 57:[("4f",-1),("5d",1)], 58:[("4f",-1),("5d",1)], 64:[("4f",-1),("5d",1)],
 78:[("5d",1),("6s",-1)], 79:[("5d",1),("6s",-1)],
 89:[("5f",-1),("6d",1)], 90:[("5f",-2),("6d",2)], 91:[("5f",-1),("6d",1)],
 92:[("5f",-1),("6d",1)], 93:[("5f",-1),("6d",1)], 96:[("5f",-1),("6d",1)],
}
SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
def sup(n): return str(n).translate(SUP)
NOBLE = [(2,"He"),(10,"Ne"),(18,"Ar"),(36,"Kr"),(54,"Xe"),(86,"Rn")]

def orbitals(z):
    counts, left = [], z
    for orb, cap in ORDER:
        if left <= 0: break
        take = min(cap, left)
        counts.append([orb, take]); left -= take
    return counts

def config_of(z):
    counts = orbitals(z)
    if z in EXC:
        d = {o:c for o,c in counts}
        for orb,delta in EXC[z]:
            d[orb] = d.get(orb,0)+delta
        # 过滤为 0 的轨道，按 (主量子数, 角量子数) 排序（教材写法 3d 在 4s 前）
        counts = [[o,c] for o,c in d.items() if c>0]
        counts.sort(key=lambda x: (int(x[0][0]), {"s":0,"p":1,"d":2,"f":3}[x[0][1]]))
    # 找核
    core_sym, core_counts = "", []
    for nz, sym in NOBLE:
        if nz < z:
            core_sym = sym; core_counts = orbitals(nz)
    # 去掉核轨道
    core_map = {o:c for o,c in core_counts}
    rest = []
    for o,c in counts:
        if core_map.get(o,0) > 0:
            core_map[o] -= c
        else:
            rest.append([o,c])
    parts = []
    if core_sym: parts.append(f"[{core_sym}]")
    rest.sort(key=lambda x: (int(x[0][0]), {"s":0,"p":1,"d":2,"f":3}[x[0][1]]))
    for o,c in rest: parts.append(f"{o}{sup(c)}")
    return " ".join(parts)

def shells_of(z):
    counts = orbitals(z)
    if z in EXC:
        d = {o:c for o,c in counts}
        for orb,delta in EXC[z]: d[orb]=d.get(orb,0)+delta
        counts = [[o,c] for o,c in d.items() if c>0]
    sh = {}
    for o,c in counts:
        n = int(o[0]); sh[n] = sh.get(n,0)+c
    return [sh[k] for k in sorted(sh)]

# ---------- 位置 ----------
def period_of(z):
    for lo,hi,p in [(1,2,1),(3,10,2),(11,18,3),(19,36,4),(37,54,5),(55,86,6),(87,118,7)]:
        if lo <= z <= hi: return p
    return 7

def pos_of(z, group):
    if 57 <= z <= 71: return (9, 3 + (z-57))
    if 89 <= z <= 103: return (10, 3 + (z-89))
    return (period_of(z), group)

def block_of(z, group, cat):
    if cat in ("lanthanide","actinide"): return "f"
    if z == 2 or group in (1,2): return "s"
    if 3 <= group <= 12: return "d"
    return "p"

ELEMENTS = []
for (z,sym,cn,en,mass,cat,group,ox,state,mp,bp,density,eneg,notes,uses) in E:
    row, col = pos_of(z, group)
    ELEMENTS.append({
        "z":z, "sym":sym, "cn":cn, "en":en, "mass":mass, "cat":cat,
        "period":period_of(z), "group":group, "glabel":GROUP_LABEL[group],
        "row":row, "col":col, "block":block_of(z,group,cat),
        "ox":ox, "state":state, "mp":mp, "bp":bp, "density":density, "eneg":eneg,
        "config":config_of(z) + ("（预测）" if z>=104 else ""),
        "shells":shells_of(z), "notes":notes, "uses":uses, "new": z>=113,
    })

DATA_JS = json.dumps(ELEMENTS, ensure_ascii=False, separators=(",",":"))
CAT_JS  = json.dumps(CAT_LABEL, ensure_ascii=False, separators=(",",":"))
COLORS = {
 "alkali":"#ff6b81","alkaline":"#ffa94d","transition":"#4dabf7","posttrans":"#20c997",
 "metalloid":"#9775fa","nonmetal":"#51cf66","halogen":"#fcc419","noble":"#22b8cf",
 "lanthanide":"#e64980","actinide":"#e8590c",
}
COLORS_JS = json.dumps(COLORS, ensure_ascii=False)

TPL = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>元素周期表 · 高中化学</title>
<style>
:root{
  --cell: clamp(42px, min(4.5vw, 7.3vh), 104px);
  --gap: clamp(3px, .42vw, 8px);
  --ink: #e8ecf7;
  --muted: #93a0bb;
  --glass: rgba(14,18,30,.62);
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent;}
html,body{height:100%;}
body{
  margin:0; background:#05060c; color:var(--ink);
  font-family:"Segoe UI","SimSun-ExtB","Microsoft YaHei","PingFang SC","Hiragino Sans GB","Source Han Sans SC",sans-serif;
  overflow:hidden; user-select:none;
}
/* ===== 动态背景 ===== */
.bg{position:fixed;inset:0;z-index:-3;overflow:hidden;background:
  radial-gradient(1200px 800px at 20% 10%, #0b1024 0%, #05060c 60%),
  radial-gradient(1000px 700px at 85% 90%, #0a0f1e 0%, #05060c 55%);
}
.blob{position:absolute;border-radius:50%;filter:blur(70px);opacity:.5;mix-blend-mode:screen;will-change:transform;}
.bg::after{content:"";position:absolute;inset:-30%;background:conic-gradient(from 0deg at 50% 50%,rgba(99,102,241,.07),transparent 60deg,rgba(34,211,238,.06) 120deg,transparent 180deg,rgba(236,72,153,.06) 240deg,transparent 300deg,rgba(99,102,241,.07) 360deg);animation:spin 90s linear infinite;opacity:.9;}
@keyframes spin{to{transform:rotate(360deg)}}
.sheen{position:absolute;inset:0;background:linear-gradient(115deg,transparent 34%,rgba(255,255,255,.05) 47%,transparent 60%);background-size:240% 240%;animation:sheen 16s ease-in-out infinite;}
@keyframes sheen{0%,100%{background-position:110% 0}50%{background-position:-10% 0}}
.b1{width:56vw;height:56vw;left:-12vw;top:-18vw;background:radial-gradient(circle at 40% 40%,#5b21b6,transparent 68%);animation:float1 46s ease-in-out infinite;}
.b2{width:52vw;height:52vw;right:-16vw;top:8vh;background:radial-gradient(circle at 60% 40%,#0e7490,transparent 68%);animation:float2 54s ease-in-out infinite;}
.b3{width:48vw;height:48vw;left:18vw;bottom:-24vw;background:radial-gradient(circle at 50% 50%,#9d174d,transparent 70%);animation:float3 62s ease-in-out infinite;}
.b4{width:40vw;height:40vw;right:10vw;bottom:-10vw;background:radial-gradient(circle at 50% 50%,#1e3a8a,transparent 70%);animation:float1 70s ease-in-out infinite reverse;}
@keyframes float1{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(6vw,4vh) scale(1.12)}}
@keyframes float2{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(-5vw,6vh) scale(1.08)}}
@keyframes float3{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(4vw,-5vh) scale(1.15)}}
.gridlines{position:fixed;inset:0;z-index:-2;pointer-events:none;opacity:.16;
  background-image:linear-gradient(rgba(120,160,255,.10) 1px,transparent 1px),linear-gradient(90deg,rgba(120,160,255,.10) 1px,transparent 1px);
  background-size:44px 44px;
  mask-image:radial-gradient(ellipse at 50% 45%,#000 0%,transparent 72%);
  -webkit-mask-image:radial-gradient(ellipse at 50% 45%,#000 0%,transparent 72%);
  animation:gridpan 40s linear infinite;
}
@keyframes gridpan{from{background-position:0 0,0 0}to{background-position:0 44px,44px 0}}
#stars{position:fixed;inset:0;z-index:-2;pointer-events:none;opacity:.55;}
.vignette{position:fixed;inset:0;z-index:-1;pointer-events:none;
  background:radial-gradient(ellipse at 50% 50%,transparent 55%,rgba(0,0,0,.55) 100%);}

/* ===== 顶栏 ===== */
.wrap{position:relative;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:clamp(12px,2.2vh,26px) clamp(10px,2vw,28px) 10px;}
.head{width:min(96vw,1780px);display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:clamp(8px,1.4vh,18px);}
.title{font-size:clamp(20px,2.5vw,34px);font-weight:800;letter-spacing:.06em;margin:0;
  background:linear-gradient(100deg,#a5b4fc,#67e8f9 45%,#f0abfc 90%);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 0 18px rgba(99,102,241,.35));
}
.sub{font-size:clamp(10px,1vw,13px);color:var(--muted);letter-spacing:.14em;margin-top:4px;}
.legend{display:flex;gap:6px 12px;flex-wrap:wrap;justify-content:flex-end;max-width:62%;}
.chip{display:inline-flex;align-items:center;gap:6px;font-size:clamp(9px,.82vw,12px);color:#c7d2ea;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.07);padding:3px 9px;border-radius:999px;}
.dot{width:9px;height:9px;border-radius:50%;box-shadow:0 0 10px currentColor;}
.newtag{font-size:8px;padding:1px 4px;border-radius:4px;background:linear-gradient(90deg,#f472b6,#fb923c);color:#fff;margin-left:2px;letter-spacing:0;}

/* ===== 周期表 ===== */
.pt{display:grid;
  grid-template-columns:repeat(18,var(--cell));
  grid-template-rows:repeat(7,var(--cell)) 13px repeat(2,var(--cell));
  gap:var(--gap);
  justify-content:center;
}
.cell{
  position:relative;border-radius:9px;border:1px solid rgba(255,255,255,.085);
  background:linear-gradient(160deg,rgba(255,255,255,.045),rgba(255,255,255,.012) 55%,rgba(0,0,0,.18));
  color:var(--ink);cursor:pointer;padding:4px 5px;text-align:center;overflow:hidden;
  display:flex;flex-direction:column;justify-content:center;align-items:center;
  transition:transform .22s cubic-bezier(.2,.7,.3,1),box-shadow .22s,border-color .22s,background .22s;
  opacity:0;transform:translateY(14px) scale(.97);
  animation:pop .5s cubic-bezier(.2,.7,.3,1) forwards;animation-delay:var(--d);
  will-change:transform,opacity;
}
.cell::before{content:"";position:absolute;left:0;top:0;height:2px;width:100%;background:linear-gradient(90deg,transparent,var(--c),transparent);opacity:.55;}
.cell::after{content:"";position:absolute;inset:0;background:radial-gradient(120% 90% at 50% 0%,color-mix(in srgb,var(--c) 16%,transparent),transparent 60%);opacity:.55;pointer-events:none;}
@keyframes pop{to{opacity:1;transform:translateY(0) scale(1)}}
.cell .num{position:absolute;top:4px;left:6px;font-size:clamp(7px,.62vw,11px);color:#8b98b6;}
.cell .sym{position:relative;font-size:clamp(13px,1.42vw,27px);font-weight:800;line-height:1;letter-spacing:.02em;color:var(--c);text-shadow:0 0 14px color-mix(in srgb,var(--c) 55%,transparent);margin-top:2px;}
.cell .cn{position:relative;font-size:clamp(8px,.72vw,12px);color:#b9c4dc;margin-top:2px;white-space:nowrap;}
.cell .m{position:absolute;bottom:3px;right:6px;font-size:clamp(6px,.55vw,9px);color:#7f8bab;}
.cell.small .sym{font-size:clamp(10px,1.05vw,19px);}
.cell:hover{z-index:3;transform:translateY(-4px) scale(1.07);border-color:var(--c);
  box-shadow:0 0 0 1px var(--c),0 10px 34px color-mix(in srgb,var(--c) 38%,transparent),inset 0 0 22px color-mix(in srgb,var(--c) 16%,transparent);}
.cell.active{z-index:4;transform:translateY(-3px) scale(1.05);border-color:var(--c);
  box-shadow:0 0 0 1.5px var(--c),0 0 34px color-mix(in srgb,var(--c) 55%,transparent);}
.placeholder{
  grid-column:3;border-radius:9px;border:1px dashed rgba(255,255,255,.16);
  background:rgba(255,255,255,.025);color:#8ea0c4;font-size:clamp(8px,.72vw,12px);
  display:flex;align-items:center;justify-content:center;letter-spacing:.05em;
}
.fgap{grid-column:1/-1;grid-row:8;}
.blocklabel{grid-column:1/3;align-self:center;color:#6f7ea3;font-size:clamp(8px,.7vw,11px);letter-spacing:.12em;}

/* ===== 详情面板 ===== */
.scrim{position:fixed;inset:0;background:rgba(3,5,10,.5);opacity:0;pointer-events:none;transition:opacity .3s;z-index:20;}
.scrim.show{opacity:1;pointer-events:auto;}
.detail{
  position:fixed;top:0;right:0;height:100vh;width:min(440px,94vw);z-index:30;
  transform:translateX(104%);transition:transform .4s cubic-bezier(.22,.8,.28,1);
  background:linear-gradient(165deg,rgba(19,24,40,.94),rgba(9,12,22,.96));
  border-left:1px solid rgba(255,255,255,.1);
  box-shadow:-30px 0 80px rgba(0,0,0,.55);
  display:flex;flex-direction:column;overflow:hidden;
  backdrop-filter:blur(22px);-webkit-backdrop-filter:blur(22px);
}
.detail.open{transform:translateX(0);}
.d-accent{height:3px;width:100%;background:linear-gradient(90deg,var(--c,#4dabf7),transparent);}
.d-body{padding:18px 20px 22px;overflow-y:auto;flex:1;}
.d-top{display:flex;align-items:center;gap:16px;}
.d-sym{font-size:clamp(44px,5vw,64px);font-weight:900;line-height:.95;color:var(--c,#4dabf7);text-shadow:0 0 26px color-mix(in srgb,var(--c,#4dabf7) 55%,transparent);}
.d-id{flex:1;}
.d-cn{font-size:19px;font-weight:700;}
.d-en{font-size:12px;color:var(--muted);letter-spacing:.06em;}
.d-cat{display:inline-block;margin-top:6px;font-size:11px;padding:2px 9px;border-radius:999px;background:color-mix(in srgb,var(--c,#4dabf7) 18%,transparent);color:var(--c,#4dabf7);border:1px solid color-mix(in srgb,var(--c,#4dabf7) 40%,transparent);}
.d-close{position:absolute;top:14px;right:14px;width:34px;height:34px;border-radius:10px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.05);color:#cbd5ea;font-size:18px;cursor:pointer;line-height:1;display:flex;align-items:center;justify-content:center;}
.d-close:hover{background:rgba(255,255,255,.12);}
.d-sec{margin-top:18px;}
.d-sec h3{font-size:11px;font-weight:600;letter-spacing:.16em;color:#7d8db3;margin:0 0 8px;text-transform:uppercase;}
.kv{display:grid;grid-template-columns:1fr 1fr;gap:8px 12px;}
.kv .item{background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.06);border-radius:9px;padding:7px 10px;}
.kv .k{font-size:10px;color:#7d8db3;}
.kv .v{font-size:13px;font-weight:600;margin-top:2px;word-break:break-word;}
.chips{display:flex;flex-wrap:wrap;gap:6px;}
.tchip{font-size:11px;padding:3px 9px;border-radius:999px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);color:#cdd7ee;}
.config{font-family:"Cascadia Code","Consolas",monospace;font-size:13px;line-height:1.6;color:#dbe6ff;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.07);border-radius:10px;padding:10px 12px;}
.shell{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;}
.shell .k{font-size:11px;color:#8b9ab8;margin-right:2px;}
.shell .s{font-size:11px;font-weight:700;padding:2px 7px;border-radius:7px;background:color-mix(in srgb,var(--c,#4dabf7) 14%,transparent);color:color-mix(in srgb,var(--c,#4dabf7) 80%,#fff);border:1px solid color-mix(in srgb,var(--c,#4dabf7) 30%,transparent);}
.notes{margin:0;padding-left:16px;display:flex;flex-direction:column;gap:7px;}
.notes li{font-size:12.5px;line-height:1.62;color:#cbd5ea;}
.notes li::marker{color:var(--c,#4dabf7);}
.uses{font-size:12.5px;line-height:1.7;color:#b7c2dc;}

.hint{position:fixed;left:50%;bottom:10px;transform:translateX(-50%);font-size:11px;letter-spacing:.16em;color:#6d7a99;z-index:5;pointer-events:none;}
.count{position:fixed;right:22px;bottom:12px;font-size:11px;color:#5f6b8a;letter-spacing:.1em;z-index:5;}

@media (max-width:760px){
  .legend{max-width:100%;justify-content:flex-start;}
  .detail{top:auto;bottom:0;right:0;left:0;width:100%;height:78vh;transform:translateY(106%);border-left:0;border-top:1px solid rgba(255,255,255,.12);border-radius:18px 18px 0 0;}
  .detail.open{transform:translateY(0);}
  .cell .m{display:none;}
}
@media (prefers-reduced-motion:reduce){
  .cell{animation:none;opacity:1;transform:none;}
  .blob,.gridlines{animation:none;}
}
</style>
</head>
<body>
<div class="bg"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div><div class="blob b4"></div><div class="sheen"></div></div>
<div class="gridlines"></div>
<canvas id="stars"></canvas>
<div class="vignette"></div>

<div class="wrap">
  <div class="head">
    <div>
      <h1 class="title">元素周期表</h1>
      <div class="sub">PERIODIC TABLE OF ELEMENTS · 高中化学 · 118 种元素（含 2016 最新命名 113–118 号）</div>
    </div>
    <div class="legend" id="legend"></div>
  </div>
  <div class="pt" id="pt"></div>
  <div class="hint">点击任意元素查看高中化学详解 · Click an element</div>
  <div class="count">共 <span id="cnt">118</span> 种元素 · 数据截至 IUPAC 2016 命名</div>
</div>

<div class="scrim" id="scrim"></div>
<aside class="detail" id="detail" aria-hidden="true">
  <div class="d-accent" id="dAccent"></div>
  <button class="d-close" id="dClose" aria-label="关闭">×</button>
  <div class="d-body" id="dBody"></div>
</aside>

<script>
const ELEMENTS = __DATA__;
const CATLABEL = __CAT__;
const COLORS = __COLORS__;

/* ===== 构建周期表 ===== */
const pt = document.getElementById('pt');
const legend = document.getElementById('legend');
Object.entries(CATLABEL).forEach(([k,v])=>{
  const c = document.createElement('span'); c.className='chip';
  c.innerHTML = `<span class="dot" style="background:${COLORS[k]};color:${COLORS[k]}"></span>${v}`;
  legend.appendChild(c);
});

ELEMENTS.forEach((el, i)=>{
  const btn = document.createElement('button');
  btn.className = 'cell';
  btn.dataset.z = el.z;
  btn.style.gridColumn = el.col;
  btn.style.gridRow = el.row;
  btn.style.setProperty('--c', COLORS[el.cat]);
  btn.style.setProperty('--d', (i*14)+'ms');
  btn.setAttribute('aria-label', `${el.z} ${el.cn} ${el.sym}`);
  btn.innerHTML = `<span class="num">${el.z}</span><span class="sym">${el.sym}</span><span class="cn">${el.cn}${el.new?'<span class="newtag">新</span>':''}</span><span class="m">${el.mass}</span>`;
  btn.addEventListener('click', ()=>openDetail(el.z));
  pt.appendChild(btn);
});

/* 镧系/锕系占位 + 间隔 */
const ph1 = document.createElement('div'); ph1.className='placeholder'; ph1.style.gridRow=6; ph1.textContent='57–71 镧系';
const ph2 = document.createElement('div'); ph2.className='placeholder'; ph2.style.gridRow=7; ph2.textContent='89–103 锕系';
const gap = document.createElement('div'); gap.className='fgap';
pt.append(ph1, ph2, gap);
document.getElementById('cnt').textContent = ELEMENTS.length;

/* ===== 详情 ===== */
const detail = document.getElementById('detail');
const scrim = document.getElementById('scrim');
const dBody = document.getElementById('dBody');
const dAccent = document.getElementById('dAccent');
let activeCell = null;

function openDetail(z){
  const el = ELEMENTS.find(e=>e.z===z);
  if(!el) return;
  const c = COLORS[el.cat];
  detail.style.setProperty('--c', c);
  dAccent.style.background = `linear-gradient(90deg,${c},transparent)`;
  const newBadge = el.new ? `<span class="newtag">最新命名</span>` : '';
  dBody.innerHTML = `
    <div class="d-top">
      <div class="d-sym">${el.sym}</div>
      <div class="d-id">
        <div class="d-cn">${el.cn} ${newBadge}</div>
        <div class="d-en">${el.en}</div>
        <div class="d-cat">${CATLABEL[el.cat]}</div>
      </div>
    </div>
    <div class="d-sec">
      <h3>基本信息</h3>
      <div class="kv">
        <div class="item"><div class="k">原子序数</div><div class="v">${el.z}</div></div>
        <div class="item"><div class="k">相对原子质量</div><div class="v">${el.mass}</div></div>
        <div class="item"><div class="k">周期 / 族</div><div class="v">第 ${el.period} 周期 · ${el.glabel}族</div></div>
        <div class="item"><div class="k">元素分区</div><div class="v">${el.block} 区</div></div>
        <div class="item"><div class="k">常见化合价</div><div class="v">${el.ox}</div></div>
        <div class="item"><div class="k">常温状态</div><div class="v">${el.state}</div></div>
      </div>
    </div>
    <div class="d-sec">
      <h3>电子排布</h3>
      <div class="config">${el.config}</div>
      <div class="shell">${el.shells.map((n,i)=>`<span class="k">${'KLMNOPQ'[i]}</span><span class="s">${n}</span>`).join('')}</div>
    </div>
    <div class="d-sec">
      <h3>物理性质</h3>
      <div class="kv">
        <div class="item"><div class="k">熔点</div><div class="v">${el.mp}</div></div>
        <div class="item"><div class="k">沸点</div><div class="v">${el.bp}</div></div>
        <div class="item"><div class="k">密度</div><div class="v">${el.density}</div></div>
        <div class="item"><div class="k">电负性(Pauling)</div><div class="v">${el.eneg}</div></div>
      </div>
    </div>
    <div class="d-sec">
      <h3>高中化学要点</h3>
      <ul class="notes">${el.notes.map(n=>`<li>${n}</li>`).join('')}</ul>
    </div>
    <div class="d-sec">
      <h3>主要用途</h3>
      <div class="uses">${el.uses}</div>
    </div>`;
  detail.classList.add('open');
  detail.setAttribute('aria-hidden','false');
  scrim.classList.add('show');
  if(activeCell) activeCell.classList.remove('active');
  activeCell = [...pt.querySelectorAll('.cell')].find(b=>+b.dataset.z===z);
  if(activeCell) activeCell.classList.add('active');
}

function closeDetail(){
  detail.classList.remove('open');
  detail.setAttribute('aria-hidden','true');
  scrim.classList.remove('show');
  if(activeCell){activeCell.classList.remove('active');activeCell=null;}
}
document.getElementById('dClose').addEventListener('click', closeDetail);
scrim.addEventListener('click', closeDetail);
document.addEventListener('keydown', e=>{ if(e.key==='Escape') closeDetail(); });

/* ===== 星空 & 视差 ===== */
const cv = document.getElementById('stars');
const ctx = cv.getContext('2d');
let W=0,H=0, stars=[], last=0;
const DPR = Math.min(window.devicePixelRatio||1, 2);
function resize(){
  W = cv.width = Math.floor(innerWidth*DPR);
  H = cv.height = Math.floor(innerHeight*DPR);
  cv.style.width = innerWidth+'px'; cv.style.height = innerHeight+'px';
  const n = Math.min(110, Math.floor(innerWidth/16));
  stars = Array.from({length:n},()=>({
    x:Math.random()*W, y:Math.random()*H,
    r:(Math.random()*1.4+.3)*DPR,
    v:(Math.random()*.28+.06)*DPR,
    a:Math.random()*.5+.25,
    ph:Math.random()*Math.PI*2
  }));
}
addEventListener('resize', resize); resize();
function frame(t){
  requestAnimationFrame(frame);
  if(document.hidden) return;
  if(t-last < 33) return; // ~30fps 上限，降低壁纸占用
  last = t;
  ctx.clearRect(0,0,W,H);
  for(const s of stars){
    s.y -= s.v; if(s.y < -4){ s.y = H+4; s.x = Math.random()*W; }
    const tw = .55 + .45*Math.sin(t/900 + s.ph);
    ctx.beginPath();
    ctx.globalAlpha = s.a*tw;
    ctx.fillStyle = '#bcd2ff';
    ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}
requestAnimationFrame(frame);

const blobs = [...document.querySelectorAll('.blob')];
let mx=0,my=0;
addEventListener('mousemove', e=>{
  mx = (e.clientX/innerWidth - .5);
  my = (e.clientY/innerHeight - .5);
});
(function parallax(){
  requestAnimationFrame(parallax);
  blobs.forEach((b,i)=>{
    const k = (i+1)*7;
    b.style.marginLeft = (mx*k)+'px';
    b.style.marginTop = (my*k)+'px';
  });
})();
</script>
</body>
</html>
"""

html = (TPL.replace("__DATA__", DATA_JS)
           .replace("__CAT__", CAT_JS)
           .replace("__COLORS__", COLORS_JS))

with open("index.html","w",encoding="utf-8") as f:
    f.write(html)

# Wallpaper Engine 工程文件
project = {
  "type": "web",
  "file": "index.html",
  "preview": "preview.jpg",
  "title": "元素周期表 · 高中化学",
  "contentrating": "Everyone",
  "tags": ["化学","教育","科技"],
  "description": "动态元素周期表壁纸，含 118 种元素与 113-118 号最新命名，点击元素查看高中化学详解。",
  "general": {"properties": {}}
}
with open("project.json","w",encoding="utf-8") as f:
    json.dump(project, f, ensure_ascii=False, indent=2)

# 完整性自检
assert len(ELEMENTS)==118, len(ELEMENTS)
assert len({e['z'] for e in ELEMENTS})==118
for e in ELEMENTS:
    for k in ("sym","cn","en","mass","config","shells","notes","uses"):
        assert e[k] not in (None,""), (e['z'],k)
print("OK elements:", len(ELEMENTS))
print("index.html bytes:", len(html.encode("utf-8")))
print("sample Fe config:", next(e for e in ELEMENTS if e['z']==26)['config'])
print("sample Cu shells:", next(e for e in ELEMENTS if e['z']==29)['shells'])
print("sample Og config:", next(e for e in ELEMENTS if e['z']==118)['config'])
