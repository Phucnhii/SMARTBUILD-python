const uploadForm = document.getElementById("uploadForm");
const resultDiv = document.getElementById("result");

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById("image");
  if (!fileInput.files.length) return;

  const formData = new FormData();
  formData.append("image", fileInput.files[0]);

  resultDiv.innerHTML = "<p class='text-gray-600'>Đang xử lý...</p>";

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();

    if (data.error) throw new Error(data.error);

    resultDiv.innerHTML = `
      <div class="bg-white shadow rounded-lg p-4 mt-4">
        <p><strong>Phát hiện:</strong> ${data.label} (${data.confidence * 100}% chính xác)</p>
        <p class="mt-2 font-semibold">Giải pháp gợi ý:</p>
        <ul style="padding-left: 24px; list-style-type: disc;">
          ${data.recommendations.map((r) => `<li>${r}</li>`).join("")}
        </ul>
      </div>`;
      resultDiv.style.display = "block";
  } catch (err) {
    resultDiv.innerHTML = `<p class='text-red-600'>Lỗi: ${err.message}</p>`;
    resultDiv.style.display = "block";
  }
});

// Hiện ảnh
const imageInput = document.getElementById('image');
const previewImage = document.getElementById('previewImage');

imageInput.addEventListener('change', function () {
  const file = this.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      previewImage.src = e.target.result;
      previewImage.style.display = 'block'; // hiện ảnh
    };
    reader.readAsDataURL(file);
  } else {
    previewImage.src = '';
    previewImage.style.display = 'none';
  }
});

//Chế độ tối/sáng
  const darkModeBtn = document.getElementById('darkModeButton');

  function setDarkMode(enabled) {
    if (enabled) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('theme', 'dark');
      darkModeBtn.textContent = '🌝'; // đổi thành icon sáng
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('theme', 'light');
      darkModeBtn.textContent = '🌚'; // đổi lại icon tối
    }
  }

  darkModeBtn.addEventListener('click', () => {
    const isDark = document.body.classList.contains('dark-mode');
    setDarkMode(!isDark);
  });

  // Load trạng thái từ localStorage
  window.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setDarkMode(savedTheme === 'dark');
  });


