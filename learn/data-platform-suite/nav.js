
(function(){
  var top=document.querySelector('.top'),side=document.querySelector('.side');
  function fit(){document.documentElement.style.setProperty('--toph',top.offsetHeight+'px')}
  fit();window.addEventListener('resize',fit);
  var m=document.querySelector('.menu');if(m)m.onclick=function(){side.classList.toggle('open')};
  var on=side.querySelector('a.on');if(on)on.scrollIntoView({block:'center'});
  document.addEventListener('keydown',function(e){
    if(e.target.tagName==='INPUT')return;
    var a=e.key==='ArrowRight'?document.querySelector('.pn .nx'):e.key==='ArrowLeft'?document.querySelector('.pn .pv'):null;
    if(a)location.href=a.getAttribute('href');
  });
})();
