document.addEventListener("DOMContentLoaded", function () {
    const closeBtn = document.getElementById("closeBtn");

    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        history.back();
      });
    }
  });

document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.querySelector(".login-input");
  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault(); // ngăn form reload trang

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();
      console.log("Response data:", data);
      if (res.ok) {
        console.log("Login successful, data:", data);
        alert(data.message);
        window.location.href = "/"; // chuyển trang sau khi login
      } else {
        alert(data.error);
      }
    } catch (error) {
      console.error("Connection error:", error);
      alert("There was a connection error");
    }
  });
});

  /*Animation login*/ 
  lottie.loadAnimation({
    container: document.getElementById('lottie-branding'),
    renderer: 'svg',
    loop: true,
    autoplay: true,
    path: '/static/lottie/koala_login.json' // dùng file local
  });

