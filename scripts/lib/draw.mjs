// Minimal 3x5 bitmap font for digits, plus marker drawing on RGBA buffers.
const FONT = {
  '0':['111','101','101','101','111'],
  '1':['010','110','010','010','111'],
  '2':['111','001','111','100','111'],
  '3':['111','001','111','001','111'],
  '4':['101','101','111','001','001'],
  '5':['111','100','111','001','111'],
  '6':['111','100','111','101','111'],
  '7':['111','001','010','010','010'],
  '8':['111','101','111','101','111'],
  '9':['111','101','111','001','111'],
};
export function drawText(img, x, y, text, r,g,b, scale=2){
  const {data,width,height}=img; let cx=x;
  for(const ch of String(text)){
    const glyph=FONT[ch]; if(!glyph){cx+=4*scale;continue;}
    for(let gy=0;gy<5;gy++)for(let gx=0;gx<3;gx++){
      if(glyph[gy][gx]==='1'){
        for(let sy=0;sy<scale;sy++)for(let sx=0;sx<scale;sx++){
          const px=cx+gx*scale+sx, py=y+gy*scale+sy;
          if(px<0||py<0||px>=width||py>=height)continue;
          const i=(py*width+px)*4; data[i]=r;data[i+1]=g;data[i+2]=b;data[i+3]=255;
        }
      }
    }
    cx+=4*scale;
  }
}
export function drawDot(img,x,y,r,g,b,rad=2){
  const {data,width,height}=img;
  for(let dy=-rad;dy<=rad;dy++)for(let dx=-rad;dx<=rad;dx++){
    if(dx*dx+dy*dy>rad*rad)continue;
    const px=x+dx,py=y+dy; if(px<0||py<0||px>=width||py>=height)continue;
    const i=(py*width+px)*4; data[i]=r;data[i+1]=g;data[i+2]=b;data[i+3]=255;
  }
}
// crop normalized rect from full-res image and scale up by factor
export function cropScaled(img, x0,y0,x1,y1, outW){
  const sx0=Math.floor(x0*img.width), sy0=Math.floor(y0*img.height);
  const sw=Math.floor((x1-x0)*img.width), sh=Math.floor((y1-y0)*img.height);
  const scale=outW/sw; const w=outW, h=Math.round(sh*scale);
  const out=new Uint8Array(w*h*4);
  for(let y=0;y<h;y++){const syf=sy0+y/scale; const sy=Math.min(img.height-1,Math.floor(syf));
    for(let x=0;x<w;x++){const sx=Math.min(img.width-1,Math.floor(sx0+x/scale));
      const si=(sy*img.width+sx)*4, di=(y*w+x)*4;
      out[di]=img.data[si];out[di+1]=img.data[si+1];out[di+2]=img.data[si+2];out[di+3]=255;}}
  return {data:out,width:w,height:h, map:(px,py)=>({x:(sx0+px/scale)/img.width, y:(sy0+py/scale)/img.height})};
}
