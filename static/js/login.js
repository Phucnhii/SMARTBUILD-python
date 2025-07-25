document.addEventListener("DOMContentLoaded", function () {
    const closeBtn = document.getElementById("closeBtn");

    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        history.back();
      });
    }
  });

  /*Animation login*/ 
  lottie.loadAnimation({
    container: document.getElementById('lottie-branding'),
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: '/static/lottie/koala_login.json' // dùng file local
  });

