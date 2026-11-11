window.L=(function(){
 function Ev(){this._h={}} 
 const layer=()=>({addTo(g){(g._l||(g._l=[])).push(this);this._g=g;if(this._el&&g._c)g._c.appendChild(this._el);return this},remove(){},bringToFront(){return this},setStyle(){return this}});
 const L={
  map(id,o){const c=document.getElementById(id);c.style.background='#cde';const m={_loaded:false,_c:c,_z:13,_h:{},on(e,f){this._h[e]=f},invalidateSize(){},fitBounds(){this._z=15;this._loaded=true},setView(ll,z){this._loaded=true;this._z=z;this._ll=ll},panTo(ll){this._ll=ll},getZoom(){return this._z},removeLayer(){}};return m},
  control:{zoom:()=>({addTo(){}})},
  tileLayer:()=>({addTo(){}}),
  layerGroup(){const g=layer();g._l=[];g.clearLayers=function(){this._l=[]};g.removeLayer=function(){};return g},
  polyline(a,o){const p=layer();p._a=a.slice();p.addLatLng=function(x){this._a.push(x)};p.getLatLngs=function(){return this._a};p.setLatLngs=function(a){this._a=a};return p},
  divIcon:(o)=>o,
  polygon(a,o){const p=layer();p._a=a;return p},
  marker(ll,o){const m=layer();m._ll=ll;const el=document.createElement('div');el.innerHTML=o.icon.html;el.style.cssText='position:absolute;left:45%;top:40%;z-index:999';m._el=el;m.getElement=()=>(m._map&&m._map._loaded?el:undefined);m.setLatLng=function(x){this._ll=x};
    m.addTo=function(g){this._map=g._c?g:null;const c=g._c||document.getElementById('map');if(o.zIndexOffset)c.appendChild(el);return this};return m},
  latLngBounds:(a)=>a
 };return L})();
