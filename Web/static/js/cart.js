function addToCart(id) {
  var quantity = document.getElementById("quantity").value;
  // Gửi yêu cầu AJAX đến Flask
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/add_to_cart/" + id + "?quantity=" + quantity, true);
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      alert("The product has been added to cart.");
    }
  };
  xhr.send();
}

document.addEventListener("DOMContentLoaded", function () {
  var cart = JSON.parse(localStorage.getItem("cart")) || [];
  cart.forEach(function (item) {
    var productElement = document.getElementById("quantity-" + item.id);
    if (productElement) {
      productElement.value = item.quantity;
    }
  });
});

function removeFromCart(productId) {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/remove_from_cart", true);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      var response = JSON.parse(xhr.responseText);
      if (response.status === "success") {
        location.reload(); // Cập nhật trang sau khi xóa sản phẩm
      } else {
        alert("Error when deleting product: " + response.message);
      }
    }
  };
  xhr.send(JSON.stringify({ product_id: productId }));
}

function updateCart() {
  var cart = JSON.parse(localStorage.getItem("cart")) || [];
  var updatedCart = [];
  var quantityInputs = document.querySelectorAll(
    '.quantity-selector input[type="number"]'
  );

  quantityInputs.forEach(function (input) {
    var productId = input.getAttribute("data-product-id");
    var productQuantity = parseInt(input.value);
    if (!isNaN(productQuantity) && productQuantity >= 1) {
      var existingItem = cart.find((item) => item.id === productId);
      if (existingItem) {
        existingItem.quantity = productQuantity;
      } else {
        // Handle new item addition to cart here if necessary
      }
      updatedCart.push(existingItem);
    }
  });
}

function updateTotalAmount() {
  var cart = JSON.parse(localStorage.getItem("cart")) || [];
  var totalAmount = 0;

  cart.forEach(function (item) {
    var productPrice = parseFloat(item.price.replace("$", ""));
    totalAmount += productPrice * item.quantity;
  });

  var totalAmountElement = document.getElementById("total-amount");
  if (totalAmountElement) {
    totalAmountElement.textContent = totalAmount.toLocaleString("vi-VN", {
      style: "currency",
      currency: "USD",
    });
  }
}

document.addEventListener("DOMContentLoaded", function () {
  var quantityInputs = document.querySelectorAll(
    '.quantity-selector input[type="number"]'
  );
  quantityInputs.forEach(function (input) {
    input.addEventListener("change", function () {
      updateCart();
    });
  });

  var checkoutButton = document.getElementById("checkout-button");
  if (checkoutButton) {
    checkoutButton.addEventListener("click", function () {
      window.location.href = "/checkout";
    });
  }

  updateTotalAmount();
});

document.addEventListener("DOMContentLoaded", function () {
  // Cập nhật trạng thái nút khi trang tải xong
  updateSubmitButtonState();

  // Thêm sự kiện để cập nhật trạng thái nút mỗi khi có sự thay đổi trong các trường nhập liệu
  var inputFields = document.querySelectorAll("#payment-form input, #payment-form select");
  inputFields.forEach(function (input) {
    input.addEventListener("change", updateSubmitButtonState);
  });

  // Thêm sự kiện ngăn chặn hành vi mặc định của form và gửi dữ liệu qua AJAX
  var paymentForm = document.getElementById("payment-form");
  if (paymentForm) {
    paymentForm.addEventListener("submit", processPayment);
  }
});

function updateSubmitButtonState() {
  var isAllFilled = true;
  var inputFields = document.querySelectorAll("#payment-form input, #payment-form select");

  // Kiểm tra từng trường nhập liệu
  inputFields.forEach(function (input) {
    if (input.value === "") {
      isAllFilled = false;
    }
  });

  // Kích hoạt hoặc vô hiệu hóa nút "Confirm"
  var confirmButton = document.getElementById("payment-button");
  confirmButton.disabled = !isAllFilled;
}

function processPayment(event) {
  event.preventDefault(); // Ngăn chặn form gửi theo cách truyền thống

  // Lấy dữ liệu từ form
  var formData = {
    fullName: document.getElementById("full-name").value,
    phone: document.getElementById("phone").value,
    address: document.getElementById("address").value,
    paymentMethod: document.getElementById("payment-method").value,
    // Đảm bảo rằng tất cả các trường dữ liệu đều được thu thập đúng
  };

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/process_payment", true);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      // Hiển thị thông báo khi nhận được phản hồi thành công từ server
      alert("Order Success. Thank you for using our service.");
      // Chuyển hướng người dùng đến trang khác
      window.location.href = "/dashboard";
    }
  };

  xhr.send(JSON.stringify(formData));
}