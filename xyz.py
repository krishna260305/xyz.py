import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Red Ball Game", page_icon="🔴", layout="wide")

st.title("🔴 Red Ball")
st.caption("Arrow keys / WASD to move & jump — collect stars, reach the flag!")

GAME_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#1a1a2e; display:flex; flex-direction:column; align-items:center; font-family:monospace; }
  #hud { display:flex; justify-content:space-between; width:700px; padding:6px 12px;
         background:#111; color:#fff; font-size:13px; font-weight:bold; border-radius:8px 8px 0 0; }
  canvas { display:block; border-radius:0; border:2px solid #333; }
  #btns { display:flex; gap:8px; justify-content:space-between; width:700px;
          padding:8px 12px; background:#0d0d20; border-radius:0 0 8px 8px; }
  .cb { background:#2a2a50; color:#eee; border:1.5px solid #444; border-radius:8px;
        font-size:18px; cursor:pointer; flex:1; height:48px;
        display:flex; align-items:center; justify-content:center;
        touch-action:manipulation; -webkit-tap-highlight-color:transparent;
        user-select:none; }
  .cb:active,.cb.pressed { background:#e63030; border-color:#ff6060; color:#fff; }
  #overlay { position:absolute; inset:0; background:rgba(0,0,0,.78);
             display:flex; flex-direction:column; align-items:center;
             justify-content:center; gap:14px; border-radius:8px; }
  #overlay h2 { color:#fff; font-size:26px; }
  #overlay p  { color:#bbb; font-size:13px; text-align:center; line-height:1.6; }
  #overlay button { background:#e63030; color:#fff; border:none; border-radius:8px;
                    padding:10px 32px; font-size:15px; font-weight:bold; cursor:pointer; }
  #overlay button:hover { background:#c02020; }
  #wrap { position:relative; width:700px; }
</style>
</head>
<body>
<div id="hud">
  <span id="hLives">&#10084; &#10084; &#10084;</span>
  <span id="hStars">&#9733; 0 / 0</span>
  <span id="hLevel">Level 1</span>
</div>
<div id="wrap">
  <canvas id="gc" width="700" height="400"></canvas>
  <div id="overlay">
    <h2>&#128308; RED BALL</h2>
    <p>Arrow keys or WASD to move &amp; jump<br>Collect stars &#9733; then reach the flag!<br>Mobile: use buttons below</p>
    <button id="startBtn">&#9654; Play</button>
  </div>
</div>
<div id="btns">
  <button class="cb" id="bL">&#9664;</button>
  <button class="cb" id="bJ" style="flex:2">&#9650; Jump</button>
  <button class="cb" id="bR">&#9654;</button>
</div>

<script>
const canvas = document.getElementById('gc');
const ctx = canvas.getContext('2d');
const W = 700, H = 400;

const K = {left:false, right:false, jump:false};
let jumpConsumed = false;

function btn(id, key) {
  const el = document.getElementById(id);
  const set = v => { K[key]=v; el.classList.toggle('pressed',v); };
  ['pointerdown','touchstart'].forEach(ev => el.addEventListener(ev, e=>{e.preventDefault();set(true);},{passive:false}));
  ['pointerup','pointerleave','touchend','touchcancel'].forEach(ev => el.addEventListener(ev, e=>{e.preventDefault();set(false);},{passive:false}));
}
btn('bL','left'); btn('bR','right'); btn('bJ','jump');

document.addEventListener('keydown', e => {
  if(e.key==='ArrowLeft'||e.key==='a') K.left=true;
  if(e.key==='ArrowRight'||e.key==='d') K.right=true;
  if(e.key==='ArrowUp'||e.key===' '||e.key==='w') K.jump=true;
  if(['ArrowLeft','ArrowRight','ArrowUp',' '].includes(e.key)) e.preventDefault();
});
document.addEventListener('keyup', e => {
  if(e.key==='ArrowLeft'||e.key==='a') K.left=false;
  if(e.key==='ArrowRight'||e.key==='d') K.right=false;
  if(e.key==='ArrowUp'||e.key===' '||e.key==='w'){K.jump=false;jumpConsumed=false;}
});

const LEVELS = [
  {
    bgTop:'#5bb8f5', bgBot:'#a8daf7',
    plats:[[0,340,200,40],[220,340,160,40],[420,340,180,40],[640,340,200,40],
           [880,300,160,40],[1080,260,120,40],[1240,300,160,40],[1440,340,200,40],
           [1680,300,140,40],[1860,340,300,40]],
    stars:[[120,305],[310,305],[500,305],[700,305],[890,255],[1100,215],[1270,255],[1490,295],[1710,255]],
    spikes:[[390,340],[610,340],[1205,300]],
    flag:[2060,285], start:[50,300]
  },
  {
    bgTop:'#ff9a5c', bgBot:'#ffcc88',
    plats:[[0,340,120,40],[160,300,100,40],[300,260,100,40],[440,220,100,40],[580,260,100,40],
           [720,300,100,40],[860,260,100,40],[1000,220,100,40],[1140,180,120,40],
           [1310,220,100,40],[1460,260,120,40],[1630,300,120,40],[1800,340,300,40]],
    stars:[[170,255],[310,215],[450,175],[590,215],[730,255],[870,215],[1010,175],[1150,135],[1320,175],[1470,215]],
    spikes:[[140,340],[280,300],[560,260],[840,300]],
    flag:[1990,280], start:[40,300]
  },
  {
    bgTop:'#1a1a3e', bgBot:'#2a2a5e',
    plats:[[0,340,80,40],[120,310,80,40],[250,280,80,40],[380,250,80,40],[510,220,80,40],
           [640,250,80,40],[770,280,80,40],[900,250,80,40],[1030,220,80,40],[1160,190,80,40],
           [1290,160,80,40],[1420,130,80,40],[1570,160,120,40],[1730,200,140,40],[1920,340,260,40]],
    stars:[[125,265],[255,235],[385,205],[515,175],[645,205],[775,235],[905,205],[1035,175],[1165,145],[1295,115],[1425,85],[1580,115]],
    spikes:[[100,340],[240,310],[370,280],[630,250],[760,280]],
    flag:[2070,280], start:[30,295]
  }
];

let level=0, lives=3, running=false;
let ball, plats, stars, spikes, flag, cam, tick, raf, last=0;

function makeBall(sx, sy) {
  return {x:parseFloat(sx),y:parseFloat(sy),vx:0,vy:0,r:15,onGround:false,dead:false,deadTimer:0};
}

function loadLevel() {
  const L = LEVELS[level];
  ball  = makeBall(L.start[0], L.start[1]);
  plats = L.plats;
  stars = L.stars.map(s=>({x:s[0],y:s[1],got:false}));
  spikes= L.spikes;
  flag  = {x:L.flag[0],y:L.flag[1],done:false,wave:0};
  cam   = {x:0};
  tick  = 0;
  jumpConsumed = false;
  updateHUD();
}

function updateHUD() {
  document.getElementById('hLives').textContent = '❤ '.repeat(lives).trim() || '☠';
  document.getElementById('hStars').textContent = '★ '+stars.filter(s=>s.got).length+' / '+stars.length;
  document.getElementById('hLevel').textContent = 'Level '+(level+1);
}

function showOverlay(title, sub, btnText) {
  const o = document.getElementById('overlay');
  o.style.display = 'flex';
  o.innerHTML = `<h2>${title}</h2><p>${sub}</p><button id="startBtn">${btnText}</button>`;
  document.getElementById('startBtn').onclick = startGame;
}

function startGame() {
  document.getElementById('overlay').style.display = 'none';
  lives=3; level=0;
  loadLevel();
  if(raf) cancelAnimationFrame(raf);
  running=true; last=performance.now();
  raf = requestAnimationFrame(frame);
}
document.getElementById('startBtn').onclick = startGame;

function frame(ts) {
  raf = requestAnimationFrame(frame);
  if(!running) return;
  const dt = Math.min((ts-last)/16.67, 3);
  last = ts;
  tick += dt;
  update(dt);
  draw();
}

function update(dt) {
  if(ball.dead) {
    ball.deadTimer -= dt;
    ball.vy += 0.5*dt; ball.y += ball.vy*dt;
    if(ball.deadTimer<=0) {
      lives--;
      if(lives<=0){running=false;showOverlay('💀 Game Over','All lives lost!','↩ Try Again');return;}
      loadLevel();
    }
    return;
  }

  const spd=4.5;
  if(K.left)       ball.vx = Math.max(ball.vx-2*dt,-spd);
  else if(K.right) ball.vx = Math.min(ball.vx+2*dt, spd);
  else             ball.vx *= Math.pow(0.75,dt);

  if(K.jump && !jumpConsumed && ball.onGround){
    ball.vy=-12; jumpConsumed=true; ball.onGround=false;
  }
  if(!K.jump) jumpConsumed=false;

  ball.vy = Math.min(ball.vy+0.55*dt, 16);
  ball.x += ball.vx*dt;
  ball.y += ball.vy*dt;
  ball.onGround = false;

  for(const [px,py,pw,ph] of plats) {
    if(ball.x+ball.r>px && ball.x-ball.r<px+pw && ball.y+ball.r>py && ball.y-ball.r<py+ph){
      const ot=(ball.y+ball.r)-py, ob=(py+ph)-(ball.y-ball.r);
      const ol=(ball.x+ball.r)-px, or2=(px+pw)-(ball.x-ball.r);
      const m=Math.min(ot,ob,ol,or2);
      if(m===ot&&ball.vy>=0){ball.y=py-ball.r;ball.vy=0;ball.onGround=true;}
      else if(m===ob&&ball.vy<0){ball.y=py+ph+ball.r;ball.vy=0;}
      else if(m===ol){ball.x=px-ball.r;ball.vx=0;}
      else{ball.x=px+pw+ball.r;ball.vx=0;}
    }
  }

  for(const s of stars) {
    if(!s.got && Math.hypot(ball.x-s.x,ball.y-s.y)<ball.r+12){s.got=true;updateHUD();}
  }
  for(const [sx,sy] of spikes) {
    if(Math.hypot(ball.x-(sx+15),ball.y-(sy-8))<ball.r+10){ball.dead=true;ball.deadTimer=55;ball.vy=-8;break;}
  }
  if(!flag.done){
    flag.wave = Math.sin(tick*0.07)*5;
    if(Math.hypot(ball.x-flag.x,ball.y-flag.y)<ball.r+22){
      flag.done=true;
      setTimeout(()=>{
        level++;
        if(level>=LEVELS.length){running=false;showOverlay('🏆 You Win!','All 3 levels cleared!','🔄 Play Again');}
        else{loadLevel();}
      },500);
    }
  }
  if(ball.y>H+80){ball.dead=true;ball.deadTimer=55;ball.vy=-8;}

  const tx = ball.x - W*0.35;
  cam.x += (tx-cam.x)*0.12*dt;
  cam.x = Math.max(0, cam.x);
}

function drawStar(x,y,r=9){
  ctx.beginPath();
  for(let i=0;i<5;i++){
    const a=i*Math.PI*4/5-Math.PI/2, b=a+Math.PI*2/5;
    i===0?ctx.moveTo(x+Math.cos(a)*r,y+Math.sin(a)*r):ctx.lineTo(x+Math.cos(a)*r,y+Math.sin(a)*r);
    ctx.lineTo(x+Math.cos(b)*(r*0.45),y+Math.sin(b)*(r*0.45));
  }
  ctx.closePath();
  ctx.fillStyle='#FFD700'; ctx.fill();
  ctx.strokeStyle='#FFA500'; ctx.lineWidth=1.5; ctx.stroke();
}

function draw(){
  const L = LEVELS[level];
  const g = ctx.createLinearGradient(0,0,0,H);
  g.addColorStop(0,L.bgTop); g.addColorStop(1,L.bgBot);
  ctx.fillStyle=g; ctx.fillRect(0,0,W,H);

  // clouds
  ctx.fillStyle='rgba(255,255,255,0.65)';
  for(let i=0;i<4;i++){
    const cx=((i*190+80-cam.x*0.25)%920+920)%920;
    const cy=45+i*22, s=18+i*4;
    ctx.beginPath();ctx.arc(cx,cy,s,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.arc(cx+s*1.4,cy,s*0.8,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.arc(cx-s*1.2,cy,s*0.7,0,Math.PI*2);ctx.fill();
  }

  ctx.save();
  ctx.translate(-Math.round(cam.x),0);

  // platforms
  for(const [px,py,pw,ph] of plats){
    ctx.fillStyle='#4a8a32'; ctx.fillRect(px,py,pw,8);
    ctx.fillStyle='#7a5230'; ctx.fillRect(px,py+8,pw,ph-8);
    ctx.fillStyle='#5caa3a';
    for(let gx=px+5;gx<px+pw-4;gx+=9){
      ctx.fillRect(gx,py-2,2,3); ctx.fillRect(gx+3,py-3,2,4);
    }
  }

  // stars
  for(const s of stars){
    if(s.got) continue;
    const bob=Math.sin(tick*0.05+s.x)*4;
    drawStar(s.x, s.y+bob);
  }

  // spikes
  ctx.fillStyle='#aaa';
  for(const [sx,sy] of spikes){
    ctx.beginPath();
    ctx.moveTo(sx,sy);ctx.lineTo(sx+15,sy-22);ctx.lineTo(sx+30,sy);
    ctx.closePath();ctx.fill();
    ctx.strokeStyle='#777';ctx.lineWidth=1;ctx.stroke();
  }

  // flag
  if(!flag.done){
    ctx.fillStyle='#888'; ctx.fillRect(flag.x-2,flag.y-55,4,55);
    ctx.fillStyle='#e63030';
    ctx.beginPath();
    ctx.moveTo(flag.x+2,flag.y-55);
    ctx.lineTo(flag.x+26,flag.y-47+flag.wave);
    ctx.lineTo(flag.x+2,flag.y-38+flag.wave*0.5);
    ctx.closePath(); ctx.fill();
    ctx.fillStyle='#fff'; ctx.font='bold 10px monospace';
    ctx.fillText('END',flag.x+5,flag.y-43+flag.wave*0.5);
  }

  // ball
  if(!ball.dead || Math.floor(ball.deadTimer/5)%2===0){
    const bx=ball.x, by=ball.y, r=ball.r;
    ctx.beginPath(); ctx.arc(bx,by,r,0,Math.PI*2);
    ctx.fillStyle='#dc2828'; ctx.fill();
    ctx.strokeStyle='#8b0000'; ctx.lineWidth=2; ctx.stroke();
    ctx.beginPath(); ctx.arc(bx-4,by-4,5,0,Math.PI*2);
    ctx.fillStyle='rgba(255,120,120,0.55)'; ctx.fill();
    const ex=ball.vx>0.5?3:ball.vx<-0.5?-3:0;
    ctx.fillStyle='#fff';
    ctx.beginPath();ctx.arc(bx+ex-5,by+1,3.5,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.arc(bx+ex+5,by+1,3.5,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='#222';
    ctx.beginPath();ctx.arc(bx+ex-5,by+1,1.8,0,Math.PI*2);ctx.fill();
    ctx.beginPath();ctx.arc(bx+ex+5,by+1,1.8,0,Math.PI*2);ctx.fill();
  }

  ctx.restore();
}
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=540, scrolling=False)

st.markdown("---")
st.markdown(
    "**Controls:** Arrow keys or WASD to move | Space / Up to jump | "
    "Mobile: use the on-screen buttons"
)
col1, col2, col3 = st.columns(3)
col1.info("⭐ Collect all stars")
col2.warning("⚠️ Avoid spikes")
col3.success("🏁 Reach the flag to advance")