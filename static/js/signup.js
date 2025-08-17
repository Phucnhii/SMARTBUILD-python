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

    // Password strength checker
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const strengthBar = document.getElementById('strengthBar');
    const submitBtn = document.getElementById('submitBtn');

    function checkPasswordStrength(password) {
      let strength = 0;
      if (password.length >= 8) strength++;
      if (/[a-z]/.test(password)) strength++;
      if (/[A-Z]/.test(password)) strength++;
      if (/[0-9]/.test(password)) strength++;
      if (/[^A-Za-z0-9]/.test(password)) strength++;

      return strength;
    }

    function updatePasswordStrength() {
      const password = passwordInput.value;
      const strength = checkPasswordStrength(password);
      
      let width = 0;
      let className = '';
      
      if (strength <= 2) {
        width = 33;
        className = 'strength-weak';
      } else if (strength <= 4) {
        width = 66;
        className = 'strength-medium';
      } else {
        width = 100;
        className = 'strength-strong';
      }
      
      strengthBar.style.width = width + '%';
      strengthBar.className = 'password-strength-bar ' + className;
    }

    function validateForm() {
      const password = passwordInput.value;
      const confirmPassword = confirmPasswordInput.value;
      const agreeTerms = document.getElementById('agreeTerms').checked;
      
      let isValid = true;
      
      // Reset styles
      passwordInput.style.borderColor = '#ccc';
      confirmPasswordInput.style.borderColor = '#ccc';
      
      // Check password strength
      if (checkPasswordStrength(password) < 3) {
        passwordInput.style.borderColor = '#f44336';
        isValid = false;
      }
      
      // Check password match
      if (password !== confirmPassword && confirmPassword !== '') {
        confirmPasswordInput.style.borderColor = '#f44336';
        isValid = false;
      } else if (password === confirmPassword && password !== '') {
        confirmPasswordInput.style.borderColor = '#4caf50';
      }
      
    // Update submit button
      submitBtn.disabled = !isValid || !agreeTerms;
    }

    passwordInput.addEventListener('input', () => {
      updatePasswordStrength();
      validateForm();
    });

    confirmPasswordInput.addEventListener('input', validateForm);
    document.getElementById('agreeTerms').addEventListener('change', validateForm);

    // Form submission
document.getElementById("signupForm").addEventListener("submit", async function (e) {
  e.preventDefault(); // Ngăn reload trang

  const firstName = document.getElementById("firstName").value.trim();
  const lastName = document.getElementById("lastName").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;

  if (password !== confirmPassword) {
    alert("Passwords do not match");
    return;
  }

  try {
    const response = await fetch("/api/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        firstName,
        lastName,
        email,
        password
      })
    });

    const data = await response.json();

    if (response.ok) {
      alert("Registration successful");
      window.location.href = "/"; // chuyển sang login
    } else {
      alert("Fail" + data.error);
    }
  } catch (err) {
    console.error("Error:", err);
    alert("Something went wrong. Please try again later.");
  }
});
