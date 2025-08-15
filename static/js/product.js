  // Darkmode
  const darkModeBtnDesktop = document.getElementById('darkModeButton-desktop');
  const darkModeBtnMobile = document.getElementById('darkModeButton');

  function setDarkMode(enabled) {
    if (enabled) {
      document.body.classList.add('dark-mode');
      localStorage.setItem('theme', 'dark');
      darkModeBtnDesktop.textContent = '🌝';
      darkModeBtnMobile.textContent = '🌝';
    } else {
      document.body.classList.remove('dark-mode');
      localStorage.setItem('theme', 'light');
      darkModeBtnDesktop.textContent = '🌚';
      darkModeBtnMobile.textContent = '🌚';
    }
  }

  function toggleDarkMode() {
    const isDark = document.body.classList.contains('dark-mode');
    setDarkMode(!isDark);
  }

  darkModeBtnDesktop.addEventListener('click', toggleDarkMode);
  darkModeBtnMobile.addEventListener('click', toggleDarkMode);

  window.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setDarkMode(savedTheme === 'dark');
  });


    // Trạng thái đăng nhập giả lập
    let isLoggedIn = false; // Thay đổi thành true để test chức năng đã đăng nhập

    // Danh sách sản phẩm quan tâm
    let interestedProducts = new Set();

    // Dữ liệu sản phẩm chi tiết
    const productDetails = {
      1: {
        title: "Xi măng công nghệ nano Đài Loan",
        image: "/static/img/index2.jpg",
        description: "Xi măng Đài Loan cao cấp được sản xuất theo công nghệ hiện đại, đảm bảo chất lượng vượt trội cho mọi công trình. Sản phẩm có độ bền cao, thời gian đông kết ổn định và khả năng chống thấm tốt.",
        specs: `
          <h4>Thông số kỹ thuật chi tiết:</h4>
          <ul class="spec-list">
            <li><span>Cường độ nén 28 ngày:</span> <span>≥ 42.5 MPa</span></li>
            <li><span>Thời gian bắt đầu đông kết:</span> <span>≥ 45 phút</span></li>
            <li><span>Thời gian kết thúc đông kết:</span> <span>≤ 10 giờ</span></li>
            <li><span>Độ mịn (Blaine):</span> <span>≥ 350 m²/kg</span></li>
            <li><span>Độ ổn định thể tích:</span> <span>≤ 10 mm</span></li>
            <li><span>Hàm lượng SO₃:</span> <span>≤ 3.5%</span></li>
          </ul>
        `
      },
      2: {
        title: "Máy trộn beton tự động JZC350",
        image: "/static/img/index2.jpg",
        description: "Máy trộn beton JZC350 là thiết bị không thể thiếu trong các công trình xây dựng. Với công nghệ tự động hóa cao, máy đảm bảo chất lượng beton đồng nhất và tiết kiệm thời gian thi công.",
        specs: `
          <h4>Thông số kỹ thuật chi tiết:</h4>
          <ul class="spec-list">
            <li><span>Dung tích trộn: </span> <span>350L</span></li>
            <li><span>Dung tích nạp liệu: </span> <span>560L</span></li>
            <li><span>Công suất động cơ: </span> <span>18.5 kW</span></li>
            <li><span>Năng suất lý thuyết: </span> <span>14 m³/h</span></li>
            <li><span>Tốc độ quay thùng trộn: </span> <span>23 vòng/phút</span></li>
            <li><span>Kích thước: </span> <span>3100×2200×3200mm</span></li>
          </ul>
        `
      },
      3: {
        title: "Hệ thống IoT giám sát công trình",
        image: "/static/img/index2.jpg",
        description: "Hệ thống IoT thông minh giúp giám sát và quản lý công trình 24/7. Tích hợp cảm biến hiện đại, cung cấp dữ liệu thời gian thực về tình trạng công trình.",
        specs: `
          <h4>Tính năng chi tiết:</h4>
          <ul class="spec-list">
            <li><span>Giám sát nhiệt độ và độ ẩm</span></li>
            <li><span>Theo dõi độ rung và nghiêng</span></li>
            <li><span>Cảnh báo qua SMS/Email</span></li>
            <li><span>Dashboard trực tuyến</span></li>
            <li><span>Lưu trữ dữ liệu cloud</span></li>
            <li><span>Tương thích mobile app</span></li>
          </ul>
        `
      },
      4: {
        title: "Gạch không nung siêu nhẹ",
        image: "/static/img/index2.jpg",
        description: "Gạch không nung thân thiện với môi trường, được sản xuất từ tro bay và vôi. Sản phẩm có trọng lượng nhẹ, cách nhiệt tốt và dễ thi công.",
        specs: `
          <h4>Thông số kỹ thuật chi tiết:</h4>
          <ul class="spec-list">
            <li><span>Kích thước tiêu chuẩn: </span> <span>200×100×60mm</span></li>
            <li><span>Cường độ nén: </span> <span>≥ 4.0 MPa</span></li>
            <li><span>Khối lượng riêng khô: </span> <span>≤ 1400 kg/m³</span></li>
            <li><span>Hệ số dẫn nhiệt: </span> <span>≤ 0.18 W/m.K</span></li>
            <li><span>Độ hút nước: </span> <span>≤ 20%</span></li>
            <li><span>Độ co ngót khô: </span> <span>≤ 0.5 mm/m</span></li>
          </ul>
        `
      },
      5: {
        title: "Bộ thiết bị bảo hộ lao động",
        image: "/static/img/index2.jpg",
        description: "Bộ thiết bị bảo hộ lao động đầy đủ đạt tiêu chuẩn quốc tế, đảm bảo an toàn tối đa cho người lao động trong môi trường xây dựng.",
        specs: `
          <h4>Bao gồm các sản phẩm:</h4>
          <ul class="spec-list">
            <li><span>Mũ bảo hiểm ABS chống va đập</span></li>
            <li><span>Giày bảo hộ chống đinh, chống trượt</span></li>
            <li><span>Găng tay bảo hộ chống cắt</span></li>
            <li><span>Kính bảo hộ chống bụi</span></li>
            <li><span>Áo phản quang</span></li>
            <li><span>Khẩu trang lọc bụi</span></li>
          </ul>
        `
      },
      6: {
        title: "Cần cẩu tháp QTZ80",
        image: "/static/img/index2.jpg",
        description: "Cần cẩu tháp QTZ80 với thiết kế hiện đại, khả năng nâng hạ mạnh mẽ, phù hợp cho các công trình cao tầng và công trình lớn.",
        specs: `
          <h4>Thông số kỹ thuật chi tiết:</h4>
          <ul class="spec-list">
            <li><span>Tải trọng định mức: </span> <span>8000 kg</span></li>
            <li><span>Tầm với tối đa: </span> <span>56m</span></li>
            <li><span>Chiều cao nâng tối đa: </span> <span>180m</span></li>
            <li><span>Tốc độ nâng: </span> <span>0-80 m/phút</span></li>
            <li><span>Tốc độ quay: </span> <span>0-0.8 vòng/phút</span></li>
            <li><span>Công suất động cơ: </span> <span>45 kW</span></li>
          </ul>
        `
      },
      7: {
        title: "Drone khảo sát địa hình 4K",
        image: "/static/img/index2.jpg",
        description: "Drone chuyên dụng cho khảo sát địa hình và giám sát tiến độ công trình với camera 4K, GPS chính xác và thời gian bay dài.",
        specs: `
          <h4>Tính năng chi tiết:</h4>
          <ul class="spec-list">
            <li><span>Camera 4K Ultra HD</span></li>
            <li><span>Thời gian bay:</span> <span>45 phút</span></li>
            <li><span>Tầm bay:</span> <span>7 km</span></li>
            <li><span>GPS RTK độ chính xác cao</span></li>
            <li><span>Chống nước IP43</span></li>
            <li><span>Tự động lập bản đồ 3D</span></li>
          </ul>
        `
      },
      8: {
        title: "Thép không gỉ SUS304",
        image: "/static/img/index2.jpg",
        description: "Thép không gỉ SUS304 chất lượng cao, chống ăn mòn tốt, phù hợp cho các công trình trong môi trường khắc nghiệt và ven biển.",
        specs: `
          <h4>Thông số kỹ thuật chi tiết:</h4>
          <ul class="spec-list">
            <li><span>Thành phần: </span> <span>18% Cr, 8% Ni</span></li>
            <li><span>Cường độ chịu kéo: </span> <span>≥ 520 MPa</span></li>
            <li><span>Giới hạn chảy: </span> <span>≥ 205 MPa</span></li>
            <li><span>Độ giãn dài: </span> <span>≥ 40%</span></li>
            <li><span>Độ cứng: </span> <span>≤ 200 HB</span></li>
            <li><span>Nhiệt độ làm việc: </span> <span>-196°C đến +800°C</span></li>
          </ul>
        `
      }
    };

    // Xử lý bộ lọc sản phẩm
    const filterBtns = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');

    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        // Remove active class from all buttons
        filterBtns.forEach(b => b.classList.remove('active'));
        // Add active class to clicked button
        btn.classList.add('active');

        const category = btn.getAttribute('data-category');
        
        productCards.forEach(card => {
          if (category === 'all' || card.getAttribute('data-category') === category) {
            card.style.display = 'block';
            card.style.animation = 'fadeIn 0.5s ease-in-out';
          } else {
            card.style.display = 'none';
          }
        });
      });
    });

    // Xử lý nút quan tâm sản phẩm
    function handleInterestClick(productId, button) {
      if (!isLoggedIn) {
        showLoginPrompt();
        return;
      }

      if (interestedProducts.has(productId)) {
        // Bỏ quan tâm
        interestedProducts.delete(productId);
        button.classList.remove('interested');
        button.querySelector('.interest-text').textContent = 'Quan tâm';
        showNotification('Đã bỏ quan tâm sản phẩm!', 'error');
      } else {
        // Thêm vào danh sách quan tâm
        interestedProducts.add(productId);
        button.classList.add('interested');
        button.querySelector('.interest-text').textContent = 'Đã quan tâm';
        showNotification('Đã thêm vào danh sách quan tâm!');
      }
    }

    // Gắn sự kiện cho tất cả nút quan tâm
    document.querySelectorAll('.btn-interest').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const productId = btn.getAttribute('data-product');
        handleInterestClick(productId, btn);
      });
    });

document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".btn-info");

  buttons.forEach(btn => {
    btn.addEventListener("click", function () {
      const productId = parseInt(this.getAttribute("data-product-id"), 10);
      showProductDetails(productId);
    });
  });
});

function showProductDetails(productId) {
  const product = productDetails[productId];
  if (!product) return;

  document.getElementById('modalImage').src = product.image;
  document.getElementById('modalTitle').textContent = product.title;
  document.getElementById('modalDescription').textContent = product.description;
  document.getElementById('modalSpecs').innerHTML = product.specs;
  
  const modalBtn = document.getElementById('modalInterestBtn');
  modalBtn.setAttribute('data-product', productId);

  if (interestedProducts.has(productId)) {
    modalBtn.classList.add('interested');
    modalBtn.querySelector('.interest-text').textContent = 'Đã quan tâm';
  } else {
    modalBtn.classList.remove('interested');
    modalBtn.querySelector('.interest-text').textContent = 'Quan tâm';
  }

  document.getElementById('productModal').style.display = 'block';
}


    // Đóng modal
document.addEventListener("DOMContentLoaded", function () {
  const modalCloseBtn = document.getElementById("modalCloseBtn");
  const productModal = document.getElementById("productModal");

  modalCloseBtn.addEventListener("click", function () {
    productModal.style.display = "none";
  });
});
    // Xử lý nút quan tâm trong modal
    document.getElementById('modalInterestBtn').addEventListener('click', (e) => {
      const productId = e.target.closest('button').getAttribute('data-product');
      const button = e.target.closest('button');
      handleInterestClick(productId, button);
      
      // Cập nhật nút quan tâm trong grid
      const gridBtn = document.querySelector(`.btn-interest[data-product="${productId}"]`);
      if (gridBtn) {
        if (interestedProducts.has(productId)) {
          gridBtn.classList.add('interested');
          gridBtn.querySelector('.interest-text').textContent = 'Đã quan tâm';
        } else {
          gridBtn.classList.remove('interested');
          gridBtn.querySelector('.interest-text').textContent = 'Quan tâm';
        }
      }
    });

    // Hiển thị thông báo đăng nhập
    function showLoginPrompt() {
      document.getElementById('loginPrompt').style.display = 'block';
    }

    // Đóng thông báo đăng nhập
    function closeLoginPrompt() {
      document.getElementById('loginPrompt').style.display = 'none';
    }

    // Hiển thị notification
    function showNotification(message, type = 'success') {
      const notification = document.getElementById('notification');
      notification.textContent = message;
      notification.className = `notification ${type} show`;
      
      setTimeout(() => {
        notification.classList.remove('show');
      }, 3000);
    }

    // Đóng modal khi click bên ngoài
document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("productModal");
  const loginPrompt = document.getElementById("loginPrompt");

  // Đóng modal khi click ra ngoài
  window.addEventListener("click", function (e) {
    if (e.target === modal) {
      modal.style.display = "none";
    }
    if (e.target === loginPrompt) {
      loginPrompt.style.display = "none";
    }
  });
});


    // Xử lý smooth scroll cho banner button
    document.querySelector('.banner-button').addEventListener('click', (e) => {
      e.preventDefault();
      document.getElementById('products').scrollIntoView({
        behavior: 'smooth'
      });
    });

    // Xử lý hamburger menu cho responsive
    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.querySelector('.nav-links');

    // Animation khi load trang
    window.addEventListener('load', () => {
      document.querySelector('.container').style.animation = 'fadeIn 0.8s ease-in-out';
    });

    // Cập nhật trạng thái đăng nhập từ server (giả lập)
    // Trong thực tế, bạn sẽ kiểm tra session/token từ backend
    function checkLoginStatus() {
      // Giả lập kiểm tra đăng nhập
      // isLoggedIn = checkUserSession(); 
      
      // Cập nhật giao diện dựa trên trạng thái đăng nhập
      updateUIForLoginStatus();
    }

    function updateUIForLoginStatus() {
      const loginButtons = document.querySelectorAll('.login-desktop, .login-mobile a');
      
      if (isLoggedIn) {
        loginButtons.forEach(btn => {
          if (btn.tagName === 'A') {
            btn.textContent = 'Tài khoản 👤';
            btn.href = '/profile';
          } else {
            btn.textContent = 'Tài khoản 👤';
          }
        });
      }
    }

    // Khởi tạo khi trang load
    document.addEventListener('DOMContentLoaded', () => {
      checkLoginStatus();
      
      // Animation cho product cards
      const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeIn 0.6s ease-in-out';
          }
        });
      });

      productCards.forEach((card) => {
        observer.observe(card);
      });
    });

    // Test function để chuyển đổi trạng thái đăng nhập (chỉ để demo)
    function toggleLoginStatus() {
      isLoggedIn = !isLoggedIn;
      updateUIForLoginStatus();
      
      if (isLoggedIn) {
        showNotification('Đã đăng nhập thành công!');
      } else {
        showNotification('Đã đăng xuất!', 'error');
        interestedProducts.clear();
        // Reset tất cả nút quan tâm
        document.querySelectorAll('.btn-interest').forEach(btn => {
          btn.classList.remove('interested');
          btn.querySelector('.interest-text').textContent = 'Quan tâm';
        });
      }
    }

// Ẩn pop up khi bấm hủy
document.addEventListener("DOMContentLoaded", function () {
  const loginPrompt = document.getElementById("loginPrompt");
  const cancelBtn = document.getElementById("cancelLogin");

  function closeLoginPrompt() {
    loginPrompt.style.display = "none";
  }

  cancelBtn.addEventListener("click", closeLoginPrompt);

  // Nếu muốn test mở popup
  // setTimeout(showLoginPrompt, 500);
});

